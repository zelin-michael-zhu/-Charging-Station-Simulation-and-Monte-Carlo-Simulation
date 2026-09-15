<p align="center">
  <img src="docs/assets/readme-hero.jpg" alt="EV charging infrastructure linking the power grid, renewable energy, charging hubs and urban logistics fleets" width="100%" />
</p>

<h1 align="center">EV Charging Supply Chain Risk Simulator</h1>

<p align="center">
  面向能源采购、充电站容量与车队履约的 M/G/c + Monte Carlo 决策沙盘
  <br />
  <em>A queueing-and-risk digital twin for resilient EV charging operations.</em>
</p>

<p align="center">
  <img alt="Python 3.9+" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white" />
  <img alt="Monte Carlo" src="https://img.shields.io/badge/Monte%20Carlo-1%2C000%20runs-7C3AED" />
  <img alt="Queueing Model" src="https://img.shields.io/badge/Queueing-M%2FG%2Fc-0EA5E9" />
  <img alt="Supply Chain Analytics" src="https://img.shields.io/badge/Focus-Supply%20Chain%20Analytics-10B981" />
</p>

<p align="center">
  <a href="#项目定位">项目定位</a> ·
  <a href="#供应链视角">供应链视角</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#模型方法">模型方法</a> ·
  <a href="#数据与基准参数">数据与基准参数</a> ·
  <a href="#下一步路线图">路线图</a>
</p>

---

## 项目定位

本项目以深圳公共充电站为场景，把 **UrbanEV 真实运营数据**、**多服务台排队模型**与**蒙特卡洛财务风险仿真**组合为一个可交互的运营决策工具。用户可以实时施加需求、服务费、购电成本和在站时间成本冲击，观察站点拥堵、利润分布与下行风险如何联动。

项目不只回答“充电站赚不赚钱”，还尝试回答一组更接近供应链管理的问题：

- 上游电力采购价格波动，会怎样传导到单站利润与尾部风险？
- 充电桩容量和服务时间波动，何时会形成中游运营瓶颈？
- 车辆排队与在站时间，如何转化为下游车队周转和履约成本？
- 面对需求增长或成本冲击，调价、扩容和运营优化的优先级是什么？

> [!NOTE]
> 当前版本是教学与情景分析模型，不是投资建议或生产级调度系统。批发电价、固定成本和时间机会成本包含显式标定假设，使用结论前应替换为目标站点的真实经营数据。

## 供应链视角

充电基础设施位于电力供应链与城市运输供应链的交汇处。这个版本将项目重新组织为一条可解释的决策链：

| 层级 | 本项目中的变量 | 典型供应链问题 | 主要输出 |
|---|---|---|---|
| 上游能源供给 | 购电批发价、电价波动 | 采购成本冲击能否被服务费吸收？ | 利润敏感性、VaR |
| 中游充电运营 | 桩数 `c`、到达率 `λ`、服务率 `μ`、服务时间 CV | 容量是否足够？瓶颈何时出现？ | 利用率、等待时间、排队长度 |
| 下游车辆履约 | 日服务次数、排队时间、总在站时间 | 充电等待是否侵蚀车队周转与履约能力？ | 在站时间惩罚、拥堵预警 |
| 网络韧性决策 | 需求、服务费、购电成本情景 | 哪些冲击最危险？应先调价、扩容还是优化作业？ | 利润分布、亏损概率、情景对比 |

```mermaid
flowchart LR
    A[电网 / 可再生能源] -->|购电价格与波动| B[能源采购]
    B --> C[充电站容量 c]
    D[车辆需求 λ] --> C
    C -->|M/G/c| E[排队与总在站时间]
    E --> F[物流车队周转 / 客户服务]
    B --> G[Monte Carlo 风险引擎]
    D --> G
    E --> G
    G --> H[利润 · VaR · 亏损概率]
    H --> I[调价 · 扩容 · 采购 · 调度]
```

这个定位保留了现有模型的可复现性，同时为后续加入储能、分时电价合同、车队交付时窗、多站点分流和供应中断情景留下接口。

## 核心能力

- **双时段需求建模**：将日需求拆分为 4 小时高峰与 20 小时平峰，分别计算拥堵水平。
- **M/G/c 排队近似**：先计算 Erlang-C 的 M/M/c 基线，再以服务时间变异系数修正等待时间。
- **风险—排队耦合**：每次 Monte Carlo 抽样都重新计算高峰与平峰排队表现，再计入在站时间成本。
- **交互式情景分析**：滑块调整服务费、购电成本、客流和在站时间成本，实时刷新结果。
- **尾部风险度量**：API 输出 5% 利润分位数（VaR）、期望利润、利润波动和亏损概率；离线图表额外展示 CVaR。
- **报告级可视化**：包含利润分布、龙卷风敏感性、需求—排队曲线、在站成本响应与深圳站点密度图。
- **教学材料完整**：提供中英文报告、演示文稿、Notebook 和 Python 教程。

## 界面与分析输出

<p align="center">
  <img src="report_assets/fig_03_profit_distribution_var_cvar.png" alt="Monte Carlo daily profit distribution with VaR and CVaR" width="49%" />
  <img src="report_assets/fig_07_shenzhen_station_distribution_map.png" alt="Spatial distribution of public charging stations in Shenzhen" width="49%" />
</p>

<p align="center">
  <sub>左：日净利润分布与尾部风险；右：深圳公共充电站空间分布。</sub>
</p>

交互式 Web 控制台提供以下指标：

- 期望日净利润、5% VaR、利润标准差与亏损概率；
- 高峰利用率、高峰等待时间与拥堵状态；
- M/M/c 基线等待、M/G/c 修正等待和总在站时间；
- 预计日服务次数与在站时间惩罚成本；
- 1,000 次模拟产生的日利润直方图。

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/zelin-michael-zhu/-Charging-Station-Simulation-and-Monte-Carlo-Simulation.git
cd ./-Charging-Station-Simulation-and-Monte-Carlo-Simulation
```

### 2. 创建虚拟环境并安装依赖

推荐 Python 3.11；代码最低需要 Python 3.9。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
```

Windows PowerShell：

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
```

### 3. 一键启动

macOS / Linux：

```bash
bash start.sh
```

启动后访问：

- Web 控制台：<http://localhost:5500>
- FastAPI 接口：<http://localhost:8000>
- Swagger 文档：<http://localhost:8000/docs>

### 手动启动

如果不使用 `start.sh`，请分别启动后端和静态前端：

```bash
# 终端 1：后端
cd backend
uvicorn main:app --reload --port 8000
```

```bash
# 终端 2：前端（从项目根目录执行）
python -m http.server 5500 --directory frontend
```

> [!TIP]
> 不建议直接双击 `frontend/index.html`。通过本地 HTTP 服务打开，可以避免浏览器的文件协议限制，并确保前端正常请求 `localhost:8000`。

## API 使用

核心端点：

```text
POST /api/run-simulation
```

请求示例：

```bash
curl -X POST http://localhost:8000/api/run-simulation \
  -H 'Content-Type: application/json' \
  -d '{
    "service_fee_change": 0.10,
    "electricity_cost_change": 0.08,
    "occupancy_change": 0.20,
    "dwell_cost_change": 0.50
  }'
```

四个输入都使用小数比例：`0.20` 表示增加 20%，`-0.10` 表示减少 10%。

| 参数 | API 合法范围 | Web 滑块范围 | 供应链含义 |
|---|---:|---:|---|
| `service_fee_change` | -90% ～ +200% | -50% ～ +100% | 下游定价 / 成本传导 |
| `electricity_cost_change` | -50% ～ +50% | -30% ～ +30% | 上游购电成本冲击 |
| `occupancy_change` | -90% ～ +200% | -50% ～ +100% | 需求或车流变化 |
| `dwell_cost_change` | -90% ～ +200% | -50% ～ +200% | 车辆周转与履约机会成本 |

响应包含排队、风险和基准回显三类字段。完整结构可在 `/docs` 查看，主要字段包括：

```json
{
  "utilization": 0.0,
  "mean_wait_minutes": 0.0,
  "mean_sojourn_minutes": 0.0,
  "daily_sessions": 0.0,
  "var_5pct": 0.0,
  "mean_profit": 0.0,
  "std_profit": 0.0,
  "prob_loss": 0.0,
  "mean_dwell_penalty": 0.0,
  "peak_utilization": 0.0,
  "peak_wait_minutes": 0.0,
  "histogram_data": []
}
```

## 模型方法

### 1. 从数据估计运营基准

项目从 `duration.csv`、`occupancy.csv` 和 `volume-11kW.csv` 的公共 TAZ 列提取观测值：

1. 以 `duration / occupancy` 估计单次服务时长，并剔除 95 分位以上的极端值；
2. 以服务时长均值的倒数估计单桩服务率 `μ`；
3. 使用 Little 定律 `λ = L / W` 估计平均单站到达率；
4. 假设 50% 日需求集中在 4 小时高峰，其余 50% 分配到 20 小时平峰；
5. 从充电量、客户电价和服务费序列估计 Monte Carlo 分布参数。

### 2. M/M/c 基线与 M/G/c 修正

对每个时段，系统利用率为：

$$
\rho = \frac{\lambda}{c\mu}
$$

先用 Erlang-C 计算 M/M/c 的等待概率和平均排队时间 `Wq`，再通过服务时间变异系数进行 Lee–Longton / Allen–Cunneen 风格近似：

$$
W_q^{M/G/c} \approx W_q^{M/M/c} \times \frac{1 + CV_s^2}{2}
$$

总在站时间同时包含排队与充电服务：

$$
W = W_q^{M/G/c} + \frac{1}{\mu}
$$

当 `ρ ≥ 1` 时，稳态排队系统失稳。实现使用上限值表达严重拥堵，避免无穷值破坏前端和财务计算。

### 3. Monte Carlo 财务风险

每次迭代分别抽样高峰和平峰服务次数，并重算对应排队时间。单站日利润定义为：

$$
\Pi = NQ(P_e + P_s) - NQ P_w - C_f - C_{dwell}
$$

其中：

- `N`：每日充电会话数，高峰与平峰分别服从 Poisson 分布；
- `Q`：单次充电量，使用截断正态分布；
- `Pe` / `Ps`：客户侧电价与服务费；
- `Pw`：购电批发价，基准周围加入 10% 标准差的随机波动；
- `Cf`：单站固定运营成本；
- `Cdwell`：高峰和平峰会话数 × 总在站时间 × 每分钟机会成本。

固定随机种子 `seed=42` 用于保证基准结果可复现。Web API 每次请求执行 1,000 次模拟。

### 4. 风险指标解释

- **Mean profit**：所有模拟情景下的平均日利润；
- **5% VaR**：日利润分布的第 5 百分位，表示 5% 较差情景的利润门槛；
- **CVaR**：低于 VaR 的尾部情景平均利润，仅在离线报告图中计算；
- **Loss probability**：模拟中 `profit < 0` 的比例；
- **Dwell-time penalty**：车辆排队与充电占用导致的时间机会成本代理量。

## 数据与基准参数

### 数据来源

数据来自 [IntelligentSystemsLab / UrbanEV](https://github.com/IntelligentSystemsLab/UrbanEV) 开放数据集，当前仓库包含：

| 文件 | 粒度与范围 | 用途 |
|---|---|---|
| `data/inf.csv` | 1,362 个深圳站点，17,532 个充电桩 | 位置、TAZ、单站桩数 |
| `data/duration.csv` | 4,344 小时 × 275 TAZ | 服务时长估计 |
| `data/occupancy.csv` | 4,344 小时 × 275 TAZ | 并发占用与到达率估计 |
| `data/volume-11kW.csv` | 4,344 小时 × 275 TAZ | 单次充电量估计 |
| `data/e_price.csv` | 4,344 小时 × 275 TAZ | 客户侧电价分布 |
| `data/s_price.csv` | 4,344 小时 × 275 TAZ | 服务费分布 |

时间范围为 **2022-09-01 00:00 至 2023-02-28 23:00**。

### 代码计算得到的基准

| 参数 | 基准值 | 说明 |
|---|---:|---|
| 充电桩数 `c` | 13 桩/站 | `charge_count` 均值 12.872 后取整 |
| 平均到达率 `λ` | 3.0682 次/h/站 | Little 定律估计 |
| 高峰到达率 `λ_peak` | 9.2047 次/h/站 | 50% 日需求集中在 4h |
| 平峰到达率 `λ_off` | 1.8409 次/h/站 | 50% 日需求分配到 20h |
| 单桩服务率 `μ` | 1.3815 次/h | 平均服务时长的倒数 |
| 平均服务时长 | 0.7239 h / 43.43 min | 清洗后样本均值 |
| 服务时间 `CV` | 0.3650 | 用于 M/G/c 修正 |
| 单次平均充电量 | 4.4963 kWh | 5%–95% 分位清洗后均值 |
| 客户侧平均电价 | 0.9512 元/kWh | 数据估计 |
| 平均服务费 | 0.7311 元/kWh | 数据估计 |
| 购电批发价 | 0.55 元/kWh | 模型标定假设 |
| 单站固定成本 | 300 元/天 | 模型标定假设 |
| 在站时间成本率 | 0.010 元/车·分钟 | 模型标定假设 |

在 `seed=42`、1,000 次模拟的当前实现下，基准情景可复现得到：

| 指标 | 结果 |
|---|---:|
| 高峰确定性利用率 | 51.25% |
| 高峰 M/G/c 平均排队时间 | 0.08 min |
| 平均日利润 | 47.54 元 |
| 5% VaR | -245.93 元 |
| 亏损概率 | 42.70% |
| 平均在站时间惩罚 | 32.00 元/天 |

这些数值是模型基准，不应被解释为深圳任一具体站点的预测。

## 生成图表与验证

生成描述性统计和全部报告图：

```bash
python visualization.py
```

常用的轻量选项：

```bash
# 核心参数验证，并生成 fig_06
python visualization.py --fast --n-iter 100

# 跳过需要网络获取行政边界的深圳地图
python visualization.py --skip-map

# 仅重新生成在站时间惩罚响应图
python visualization.py --only-fig6 --n-iter 1000
```

`visualization.py` 使用无界面 Matplotlib 后端，可在服务器和 CI 环境运行。深圳地图会尝试从公开地理边界接口获取行政区轮廓；无网络时请使用 `--skip-map`。

## 项目结构

```text
.
├── backend/
│   ├── data_processor.py    # 数据清洗与基准参数估计
│   ├── queuing_model.py     # M/M/c + M/G/c 近似
│   ├── monte_carlo.py       # 财务与尾部风险仿真
│   ├── schemas.py           # Pydantic 请求 / 响应模型
│   ├── main.py              # FastAPI 服务与接口编排
│   └── requirements.txt
├── frontend/
│   ├── index.html           # 交互式风险控制台
│   ├── app.js               # API、KPI 与 ECharts 交互
│   └── style.css            # 附加主题样式
├── data/                    # UrbanEV 站点与时序 CSV
├── notebooks/
│   └── teaching_demo.ipynb  # 教学演示 Notebook
├── report/                  # 中英文课程报告及 PDF
├── report_assets/           # 统计表与报告图表
├── docs/assets/             # README 主视觉
├── visualization.py         # 报告图与统计生成入口
├── tutorial.python.md       # Python 实现教程
├── presentation.html        # 浏览器演示稿
└── start.sh                 # 后端 + 前端一键启动
```

## 报告与教学材料

- [英文项目报告](report/BA3093_Group_Report.md)
- [中文项目报告](report/BA3093_Group_Report_CN.md)
- [Python 教程](tutorial.python.md)
- [教学 Notebook](notebooks/teaching_demo.ipynb)
- [HTML 演示稿](presentation.html)

## 下一步路线图

为了从“单站财务仿真”继续走向“充电供应链韧性决策”，建议按以下顺序扩展：

- [ ] **上游采购**：引入分时电价、长期合约、现货电价与需求响应；
- [ ] **储能协同**：加入电池储能 SOC、削峰填谷和充放电策略；
- [ ] **多站点网络**：建模站点间分流、区域容量和选址—分配问题；
- [ ] **车队履约**：引入物流任务、交付时窗、车辆 SOC 与机会成本；
- [ ] **中断风险**：模拟停电、设备故障、价格尖峰和需求激增；
- [ ] **决策优化**：在仿真外层加入服务费、扩容、采购与调度的多目标优化；
- [ ] **可信度提升**：使用真实站点成本、到达过程检验、分布拟合与样本外验证。

## 假设与限制

- 高峰 / 平峰的 50%–50% 潮汐划分是情景假设，不是从小时到达过程直接拟合；
- 当前到达过程使用 Poisson 分布，未显式建模过度离散、相关性和节假日效应；
- M/G/c 使用近似修正，不是离散事件仿真；
- `ρ ≥ 1` 时的等待时间以封顶值表示，仅适合作为拥堵预警；
- 单次充电量、电价和服务费使用截断正态近似；
- 购电批发价、固定成本和时间成本尚未由站点财务账本校准；
- 当前财务模型按“代表性单站·单日”计算，不含税费、需量电费、设备故障与融资成本；
- 固定种子便于复现，但正式分析应使用更多迭代、多个种子并报告置信区间。

## 贡献与引用

欢迎通过 Issue 或 Pull Request 贡献新的需求过程、储能模型、供应链中断情景、校准数据和可视化。

使用本项目中的数据时，请同时引用原始 [UrbanEV 数据集](https://github.com/IntelligentSystemsLab/UrbanEV)。课程报告和演示材料保留在仓库中，便于复现实验背景与分析过程。

---

<p align="center">
  Built for interpretable EV infrastructure decisions — from power procurement to fleet fulfillment.
</p>
