# 充电站净利润风险仿真 — Python 全流程讲解

> 本文档将带你逐文件、逐函数理解整个仿真系统的 Python 实现细节，适合在展示时对评委讲解每一步"数据是如何流动的"。

---

## 环境准备

```python
# 安装依赖（仅需一次）
pip install fastapi uvicorn pandas numpy scipy pydantic

# 目录结构
# 所有后端文件均在 backend/ 目录下
# 数据文件在 data/ 目录下（相对 backend/ 的路径为 ../data/）
```

---

## 第一步：数据加载 (`data_processor.py`)

```python
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 读取站点元数据
df_inf = pd.read_csv(os.path.join(DATA_DIR, "inf.csv"))

# 1362 座站，275 个 TAZ
print(df_inf.shape)        # (1362, 7)
print(df_inf.head())
#   station_id  longitude  latitude  charge_count  TAZID  area  perimeter
# 0       1001  113.784724  22.714121          20    559   ...      ...

# 平均充电桩数 c（排队模型服务台数）
c = int(round(df_inf["charge_count"].mean()))  # ≈ 14
```

### 从时序数据提取 λ 和 μ

```python
# 时序数据：4344 行 × 275 列（每列是一个 TAZ）
df_dur = pd.read_csv(os.path.join(DATA_DIR, "duration.csv"), index_col=0)
df_occ = pd.read_csv(os.path.join(DATA_DIR, "occupancy.csv"), index_col=0)

# ─── 计算单次充电平均时长（服务时间 W）────────────────────────────────
# duration[t, taz] = 该 TAZ 在 t 时段内所有会话的累计充电时长（h）
# occupancy[t, taz] = 该 TAZ 在 t 时段内平均并发会话数 L
# 所以：单次平均时长 = duration / occupancy

dur_vals = df_dur.values.flatten()
occ_vals = df_occ.values.flatten()

mask = (occ_vals > 0.5) & (dur_vals > 0)
session_durations = dur_vals[mask] / occ_vals[mask]  # h/次

# 去极端值，取中位数
p95 = np.percentile(session_durations, 95)
clean = session_durations[session_durations <= p95]
mean_W = np.median(clean)    # ≈ 1.9 小时/次

# 服务率 μ = 1/W（每桩每小时能完成多少次充电）
mu = 1.0 / mean_W            # ≈ 0.53 次/小时/桩
print(f"平均充电时长: {mean_W:.2f} h → 服务率 μ = {mu:.3f} 次/h")
```

### 用 Little 定律推导到达率 λ

```python
# Little 定律：L = λ × W
# 其中 L = 系统内平均顾客数（并发会话数，即 occupancy）
# 所以：λ = L / W

# 每 TAZ 每小时的平均并发数 L（TAZ 级别）
mean_L_taz = np.median(occ_vals[occ_vals > 0.5])  # 中位数，避免离群值

# 折算到单站（275 TAZ，1362 站 → 平均每 TAZ 约 4.95 座站）
stations_per_taz = 1362 / 275
mean_L_station = mean_L_taz / stations_per_taz

# 单站到达率
lam = mean_L_station / mean_W   # 次/h/站
print(f"单站并发数 L = {mean_L_station:.2f}")
print(f"单站到达率 λ = {lam:.3f} 次/h")
```

### 提取财务参数

```python
df_vol = pd.read_csv(os.path.join(DATA_DIR, "volume-11kW.csv"), index_col=0)
df_ep  = pd.read_csv(os.path.join(DATA_DIR, "e_price.csv"),    index_col=0)
df_sp  = pd.read_csv(os.path.join(DATA_DIR, "s_price.csv"),    index_col=0)

vol_vals = df_vol.values.flatten()

# 单次充电电量 = 每并发会话每小时充电率 × 充电时长
vol_mask = mask & np.isfinite(vol_vals) & (vol_vals > 0)
kwh_per_session = (vol_vals[vol_mask] / occ_vals[vol_mask]) * \
                  (dur_vals[vol_mask] / occ_vals[vol_mask])

# 去极端值后统计
lo, hi = np.percentile(kwh_per_session, [5, 95])
kwh_clean = kwh_per_session[(kwh_per_session >= lo) & (kwh_per_session <= hi)]

mean_kwh = np.mean(kwh_clean)   # ≈ 12 kWh/次
std_kwh  = np.std(kwh_clean)
print(f"单次电量: {mean_kwh:.1f} ± {std_kwh:.1f} kWh")

# 价格统计
ep_vals = df_ep.values.flatten()
sp_vals = df_sp.values.flatten()
mean_e_price = np.mean(ep_vals[(ep_vals > 0.1) & (ep_vals < 5)])   # ≈ 0.9 元/kWh
mean_s_price = np.mean(sp_vals[(sp_vals > 0.1) & (sp_vals < 5)])   # ≈ 0.76 元/kWh

# ★ 补全参数（原始数据未提供，依据市场均值）
wholesale_price  = 0.55  # 元/kWh，深圳工商业购电价
daily_fixed_cost = 300.0 # 元/天，单站固定运营成本
```

---

## 第二步：M/M/c 排队模型 (`queuing_model.py`)

M/M/c 模型描述：**多个服务台、泊松到达、指数服务时间、无限等待队列**。

### 核心数学公式

```python
import math

def compute_mmc(lam: float, mu: float, c: int):
    """
    M/M/c 排队系统计算。
    
    参数
    ----
    lam : 到达率（次/h）
    mu  : 单桩服务率（次/h）
    c   : 充电桩数量
    
    返回
    ----
    dict 包含 rho, erlang_c, queue_waiting_time_minutes, dwell_time_minutes, daily_sessions
    """
    rho = lam / (c * mu)   # 系统利用率（traffic intensity）
    
    if rho >= 1.0:
        # 系统不稳定，队列无限增长（实际中需扩容）
        return {
            "rho": rho,
            "erlang_c": 1.0,
            "queue_waiting_time_minutes": 9999,
            "dwell_time_minutes": 9999,
        }
    
    a = lam / mu   # offered traffic（Erlang）
    
    # ── 计算空系统概率 P0 ─────────────────────────────────────────────────
    # 分母 = Σ_{n=0}^{c-1} a^n/n! + a^c/c! × 1/(1-ρ)
    sum_part = sum(a**n / math.factorial(n) for n in range(c))
    last_part = (a**c / math.factorial(c)) / (1.0 - rho)
    P0 = 1.0 / (sum_part + last_part)
    
    # ── Erlang C 公式 = 到达时系统满员（需等待）的概率 ──────────────────
    erlang_c = last_part * P0
    
    # ── 平均等待时间 Wq（小时）────────────────────────────────────────────
    Wq = erlang_c / (c * mu * (1.0 - rho))
    
    # ── 每日有效服务次数（M/M/c 无阻塞，顾客最终都被服务）────────────────
    daily_sessions = lam * 24.0   # 次/天
    
    return {
        "rho":            rho,
        "erlang_c":       erlang_c,
        "queue_waiting_time_minutes": Wq * 60,
        "dwell_time_minutes": Wq * 60 + (1.0 / mu) * 60,
        "daily_sessions": daily_sessions,
    }

# 示例
result = compute_mmc(lam=1.5, mu=0.53, c=14)
print(f"利用率 ρ = {result['rho']:.1%}")
print(f"等待概率 C = {result['erlang_c']:.3f}")
print(f"平均排队等待 Wq = {result['queue_waiting_time_minutes']:.1f} 分钟")
print(f"总在站时长 W = {result['dwell_time_minutes']:.1f} 分钟")
print(f"日服务 = {result['daily_sessions']:.0f} 次")
```

### 用户调参后的利用率变化

```python
# 当客流量 +20% 时：
lam_adjusted = lam * (1 + 0.20)     # λ 增加 20%
result_new = compute_mmc(lam_adjusted, mu, c)
print(f"调参后利用率: {result_new['rho']:.1%} (原 {result['rho']:.1%})")
```

---

## 第三步：蒙特卡洛财务仿真 (`monte_carlo.py`)

> 当前项目已升级为 **Peak/Off-peak 双模态仿真**：
> - 高峰 4 小时承载 50% 客流，平峰 20 小时承载另外 50%
> - 每次迭代分别抽样高峰客流与平峰客流
> - 惩罚成本分开计算：高峰客流乘高峰总在站时长，平峰客流乘平峰总在站时长

核心换算公式：

$$
\lambda_{peak}=3\lambda_{avg},\quad \lambda_{off}=0.6\lambda_{avg}
$$

$$
\Pi_i = \Pi_i^{base} - N_{peak,i}W_{peak}c_{wait} - N_{off,i}W_{off}c_{wait}
$$

其中 $W_{peak}, W_{off}$ 均为“排队等待 + 固定充电服务时间”的总在站时长。

### 核心仿真循环

```python
def run_bimodal_day(peak_lambda, offpeak_lambda, mu, c, cv, rng):
    peak_sessions = rng.poisson(peak_lambda * 4)
    off_sessions = rng.poisson(offpeak_lambda * 20)

    q_peak = QueuingSimulator(peak_sessions / 4, mu, c, cv).compute()
    q_off = QueuingSimulator(off_sessions / 20, mu, c, cv).compute()

    peak_total_minutes = q_peak.w_mgc_minutes
    off_total_minutes = q_off.w_mgc_minutes
    return peak_sessions, off_sessions, peak_total_minutes, off_total_minutes
```

```python
import numpy as np

def run_monte_carlo(
    daily_sessions: float,
    mean_kwh: float,     std_kwh: float,
    mean_e_price: float, std_e_price: float,
    mean_s_price: float, std_s_price: float,
    wholesale_price: float,
    daily_fixed_cost: float,
    service_fee_change: float = 0.0,      # 用户调参：服务费变动率
    electricity_cost_change: float = 0.0, # 用户调参：购电成本变动率
    n_iter: int = 1000,
    seed: int = 42,
) -> dict:
    
    rng = np.random.default_rng(seed)
    
    # 调整价格（用户滑块参数）
    adj_s_price    = mean_s_price * (1.0 + service_fee_change)
    adj_wholesale  = wholesale_price * (1.0 + electricity_cost_change)
    
    # ── 1000 次随机采样 ──────────────────────────────────────────────────
    sessions = rng.poisson(lam=daily_sessions, size=n_iter).astype(float)
    # ↑ 泊松分布：离散随机数，反映每日到达次数的随机性
    
    kwh = np.clip(rng.normal(mean_kwh, std_kwh, n_iter), 1, 50)
    # ↑ 正态分布：每次充电量不同（电量需求差异）
    
    e_price = np.clip(rng.normal(mean_e_price, std_e_price * 0.3, n_iter), 0.3, 2.0)
    s_price = np.clip(rng.normal(adj_s_price,  std_s_price * 0.3, n_iter), 0.1, 2.0)
    wholesale = np.clip(rng.normal(adj_wholesale, adj_wholesale * 0.1, n_iter), 0.2, 1.5)
    
    # ── 财务计算（向量化，1000 次同时算）──────────────────────────────────
    total_kwh = sessions * kwh            # 日总电量
    revenue   = total_kwh * (e_price + s_price)    # 日总营收
    cost      = total_kwh * wholesale + daily_fixed_cost  # 日总成本
    profits   = revenue - cost            # 日净利润（1000 个随机结果）
    
    # ── 风险指标 ──────────────────────────────────────────────────────────
    var_5pct    = np.percentile(profits, 5)   # 5% VaR：最坏 5% 情形的日利润下限
    mean_profit = np.mean(profits)
    prob_loss   = np.mean(profits < 0)        # 亏损概率
    
    return {
        "profits":     profits.tolist(),
        "var_5pct":    float(var_5pct),
        "mean_profit": float(mean_profit),
        "prob_loss":   float(prob_loss),
    }

# 示例运行
mc_result = run_monte_carlo(
    daily_sessions=36,
    mean_kwh=12.0, std_kwh=3.5,
    mean_e_price=0.90, std_e_price=0.12,
    mean_s_price=0.76, std_s_price=0.09,
    wholesale_price=0.55,
    daily_fixed_cost=300.0,
)
print(f"期望日利润: {mc_result['mean_profit']:.0f} 元")
print(f"5% VaR:    {mc_result['var_5pct']:.0f} 元")
print(f"亏损概率:  {mc_result['prob_loss']:.1%}")
```

### 什么是 VaR（风险价值）？

```
VaR 5% = np.percentile(profits, 5)

含义：在 1000 次模拟中，有 5%（即 50 次）的情形，
      日净利润低于这个 VaR 值。

例如 VaR = -200 元，表示：在最坏的 5% 情形下，
当天将亏损至少 200 元。这是充电站运营者需要承受的
"尾部风险"预算。
```

---

## 第四步：FastAPI 接口 (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允许前端（5500 端口）跨域访问后端（8000 端口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.post("/api/run-simulation")
def run_simulation(payload: SimulationRequest):
    # 1. 取基准数据
    baseline = load_baseline_data()
    
    # 2. 根据用户调参修改 λ
    adj_lambda = baseline["lambda_rate"] * (1 + payload.occupancy_change)
    
    # 3. M/G/c 排队计算：同时保留 Wq 与总在站时长 W
    q = QueuingSimulator(adj_lambda, baseline["mu"], baseline["c"]).compute()
    
    # 4. 蒙特卡洛仿真
    mc = MonteCarloSimulator(
        peak_lambda_rate=baseline["peak_lambda_rate"],
        offpeak_lambda_rate=baseline["offpeak_lambda_rate"],
        peak_hours=baseline["peak_hours"],
        offpeak_hours=baseline["offpeak_hours"],
        mu=baseline["mu"],
        c=baseline["c"],
        service_time_cv=baseline["service_time_cv"],
        dwell_cost_per_minute=baseline["dwell_cost_per_minute"],
        service_fee_change=payload.service_fee_change,
        electricity_cost_change=payload.electricity_cost_change,
        **{k: baseline[k] for k in ["mean_kwh","std_kwh","mean_e_price",
                                     "mean_s_price","std_e_price","std_s_price",
                                     "wholesale_price","daily_fixed_cost"]}
    ).run()
    
    # 5. 打包返回 JSON
    return SimulationResponse(
        utilization=q.rho,
        mean_wait_minutes=q.queue_waiting_time_minutes,
        mean_sojourn_minutes=q.dwell_time_minutes,
        daily_sessions=q.daily_sessions,
        var_5pct=mc.var_5pct,
        mean_profit=mc.mean_profit,
        histogram_data=mc.profits,
        ...
    )
```

---

## 第五步：前端如何消费 API (`app.js` 关键片段)

```javascript
// 滑块触发 → 防抖 380ms → 发请求
slider.addEventListener('input', () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(runSimulation, 380);
});

async function runSimulation() {
  const resp = await fetch('http://localhost:8000/api/run-simulation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      service_fee_change:      parseFloat(sfeeSlider.value) / 100,
      electricity_cost_change: parseFloat(ecostSlider.value) / 100,
      occupancy_change:        parseFloat(occSlider.value) / 100,
    }),
  });
  
  const data = await resp.json();
  
  // 更新 VaR 数字（附带颜色变化）
  kpiVar.textContent = data.var_5pct.toFixed(0);
  kpiVar.style.color = data.var_5pct >= 0 ? 'green' : 'red';
  
  // 更新直方图
  const { labels, counts } = buildHistogram(data.histogram_data, 32);
  myChart.setOption({ xAxis: { data: labels }, series: [{ data: counts }] });
}
```

---

## 完整运行示例（命令行）

```bash
# 终端 1：启动后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 终端 2：启动前端静态服务
cd frontend
python -m http.server 5500

# 浏览器访问
open http://localhost:5500
```

或直接运行一键脚本：

```bash
bash start.sh
```

---

## 参数敏感性解读

| 操作 | 模型反应 | 业务含义 |
|------|---------|---------|
| 服务费 +20% | `s_price↑` → Revenue↑ → VaR↑（风险改善）| 涨价提升利润空间 |
| 购电成本 +15% | `wholesale↑` → Cost↑ → VaR↓（风险恶化）| 电价上涨侵蚀利润 |
| 客流量 +30% | `λ↑` → sessions↑，ρ↑ → 队列增长 → 如超容则 ρ>1 告警 | 需求旺盛但超容风险 |
| 客流量 -30% | `λ↓` → sessions↓ → 固定成本拖累 → 亏损概率↑ | 低峰期收入不足覆盖成本 |

---

## 关键数学概念速查

$$\lambda = \frac{L}{W} \quad \text{（Little 定律：到达率 = 系统平均顾客数 / 平均逗留时间）}$$

$$\rho = \frac{\lambda}{c \cdot \mu} \quad \text{（服务台利用率，须 < 1）}$$

$$\text{VaR}_{5\%} = F^{-1}(0.05) = \text{np.percentile(profits, 5)}$$

$$\text{Profit} = N \cdot Q \cdot (p_e + p_s - p_{wholesale}) - C_{fixed}$$

其中：$N$ = 日服务次数，$Q$ = 单次电量，$p_e$ = 客户电价，$p_s$ = 服务费，$p_{wholesale}$ = 购电成本，$C_{fixed}$ = 日固定成本。
