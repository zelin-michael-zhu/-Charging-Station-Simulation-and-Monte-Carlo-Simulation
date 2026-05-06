# 充电站仿真和蒙特卡洛模拟

基于排队论（M/G/c）与蒙特卡洛模拟的深圳电动汽车公共充电站财务风险分析系统。

## 项目简介

本项目构建了一个完整的 EV 充电站运营仿真框架，涵盖：

- **双模态分时排队模型**：区分高峰（4h）与平峰（20h）到达率，采用 M/G/c 排队系统量化排队表现与总在站时间成本
- **蒙特卡洛财务风险仿真**：10,000 次迭代，输出利润分布、VaR（95%）、CVaR（95%）
- **实时 Web 可视化大屏**：FastAPI 后端 + 原生 JS 前端，含高峰拥堵预警卡
- **多场景敏感性分析**：占用率变化、在站时间机会成本系数、龙卷风图分析

## 数据来源

本项目所用充电站位置与充电桩数据来源于 **UrbanEV** 开放数据集：

> IntelligentSystemsLab. *UrbanEV: A Large-Scale Dataset for Urban Electric Vehicle Charging Behavior Analysis*.
> GitHub: [https://github.com/IntelligentSystemsLab/UrbanEV](https://github.com/IntelligentSystemsLab/UrbanEV)

数据文件说明：

| 文件 | 说明 |
|------|------|
| `data/inf.csv` | 深圳充电站信息（经纬度、充电桩数、TAZ 编号） |
| `data/duration.csv` | 充电时长数据 |
| `data/occupancy.csv` | 充电桩占用率 |
| `data/volume-11kW.csv` | 11kW 桩日充电量 |
| `data/e_price.csv` / `s_price.csv` | 电价与服务费 |

## 项目结构

```
├── backend/
│   ├── data_processor.py   # 基准参数提取
│   ├── main.py             # FastAPI API 编排
│   ├── monte_carlo.py      # 蒙特卡洛仿真引擎
│   ├── queuing_model.py    # M/G/c 排队模型
│   └── schemas.py          # Pydantic 响应模型
├── frontend/
│   ├── index.html          # 可视化大屏
│   ├── app.js              # 前端交互逻辑
│   └── style.css
├── data/                   # UrbanEV 原始数据（见上表）
├── report/                 # 课程报告（中/英文）
├── report_assets/          # 图表输出
├── notebooks/
│   └── teaching_demo.ipynb # 教学演示 Notebook
├── visualization.py        # 报告图与统计生成脚本
└── start.sh                # 一键启动脚本
```

## 快速启动

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 启动服务（后端 + 前端）
bash start.sh

# 或手动启动
cd backend && uvicorn main:app --reload --port 8000
# 浏览器打开 frontend/index.html
```

## 生成报告图表

```bash
# 生成全部图表和描述性统计表
python visualization.py

# 轻量验证核心函数并仅生成 fig_06（推荐用于调试）
python visualization.py --fast --n-iter 100

# 跳过地图生成（避免网络或显示相关延迟）
python visualization.py --skip-map

# 只生成在站时间惩罚响应图
python visualization.py --only-fig6
```

## 核心模型参数（基准）

| 参数 | 值 | 说明 |
|------|----|------|
| 高峰到达率 λ_peak | 9.2047 次/h | 50% 日流量集中于 4h |
| 平峰到达率 λ_off | 1.8409 次/h | 50% 日流量分散于 20h |
| 服务率 μ | 0.9174 次/h/桩 | 1/均值服务时长 |
| 平均充电桩数 c | 12.09 桩/站 | 来自 UrbanEV inf.csv |
| 在站时间机会成本 c_dwell | 0.010 元/车·分钟 | 基于总在站时长 W = W_q + 1/μ |

## 技术栈

- **后端**：Python 3.11+，FastAPI，NumPy，Pandas，SciPy
- **前端**：原生 HTML/CSS/JavaScript
- **可视化**：Matplotlib，SciPy KDE

## 学术致谢

感谢 IntelligentSystemsLab 团队提供 UrbanEV 开放数据集，使本项目的深圳充电站空间分析成为可能。
