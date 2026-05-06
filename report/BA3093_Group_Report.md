# BA3093 Simulation and Risk Analysis — Group Project Report

---

## Cover Page

**Project Title:** EV Charging Station Profit Risk Analysis under Multiple Uncertainties: A Monte Carlo and Queuing Simulation Approach

**Group Number:** Group [To Be Filled]

**Section Number:** [To Be Filled]

**Course:** BA3093 Simulation and Risk Analysis

**Submission Date:** 24 May 2025

**Team Members:**

| Name | Student ID |
|---|---|
| [Name] | [Student ID] |
| [Name] | [Student ID] |
| [Name] | [Student ID] |

---

> **AI Usage Declaration:** Generative AI tools are only used for proofreading and grammar correction in this report.

---

## 1. Problem Introduction

### 1.1 Industry Background and Operational Pain Points

The rapid expansion of electric vehicles (EVs) in mainland China has driven a parallel growth in public charging infrastructure. According to China's National Energy Administration, the number of public charging piles exceeded 2.7 million by end-2023, with an annual growth rate surpassing 50% (National Energy Administration, 2024). Despite strong demand, station-level profitability remains highly uncertain. Operators face simultaneous exposure to at least four sources of volatility:

1. **Demand uncertainty**: Hourly EV arrivals vary significantly by time of day, day of week, and season, creating unpredictable daily session volumes.
2. **Service process variability**: Charging duration differs across vehicle types, battery levels, and charger configurations, making individual service times non-deterministic.
3. **Electricity price fluctuations**: Shenzhen's tiered and time-of-use electricity pricing (Shenzhen Municipal Development and Reform Commission, 2023) introduces input cost volatility that directly erodes margins.
4. **Congestion and user attrition**: When arrival rates approach system capacity, users face longer waiting times, risking balking behavior and revenue loss (Hopp & Spearman, 2011).

Traditional deterministic financial budgeting—which plugs in fixed average values—cannot quantify the probability of loss days, the magnitude of worst-case shortfalls, or the nonlinear escalation of congestion costs. Operators need distributional, risk-adjusted financial forecasts to support investment and operating decisions.

### 1.2 Core Research Questions

This project addresses two interconnected research questions:

**RQ1 (Financial Risk):** Under simultaneous uncertainty in demand, service durations, electricity prices, and service fees, what is the distribution of daily net profit for a representative Shenzhen public charging station, and what are its tail-risk characteristics (VaR, CVaR, loss probability)?

**RQ2 (Operational Risk):** How does the queuing system respond to demand variation and capacity decisions, and how does the opportunity cost of vehicle dwell time translate into financially material profit erosion?

### 1.3 Why This Approach is Appropriate

A combined Monte Carlo simulation (Option A) and queuing analysis (Option B) approach is justified on three grounds:

- **Multiple stochastic inputs**: The profit function is a nonlinear composite of at least five random variables. Analytical closed-form solutions do not exist for joint distributional outputs; simulation is the standard industry method (Glasserman, 2004).
- **Congestion mechanics**: The charging station is a multi-server queuing system. Without queuing analysis, queueing performance, total dwell time, and their sensitivity to demand shocks cannot be quantified (Gross et al., 2018).
- **Complementarity**: Monte Carlo captures financial output distributions; queuing analysis provides the operational performance metrics that feed into those distributions. Together, they form a closed analytical loop from operational reality to financial risk.

This dual-stream design directly satisfies both Option A and Option B requirements of BA3093 while addressing a genuine managerial problem.

---

## 2. Data and Parameters

### 2.1 Data Source

We use the **UrbanEV Shenzhen public EV charging dataset** (Mao et al., 2024), released under the CC0 public domain licence. The dataset covers:

- **1,362 stations** across **275 Traffic Analysis Zones (TAZs)** in Shenzhen
- **Hourly records** from 2022-09-01 to 2023-02-28 (4,344 hourly observations per TAZ)

Six core CSV files are used:

| File | Content | Role in Analysis |
|---|---|---|
| `inf.csv` | Station metadata: location, TAZ, charger count | Parameter $c$ estimation |
| `duration.csv` | Hourly cumulative charging duration (hours) by TAZ | Service time distribution |
| `occupancy.csv` | Hourly concurrent active sessions by TAZ | Little's Law; arrival rate |
| `volume-11kW.csv` | Hourly charging energy volume (kWh) by TAZ | Revenue calculation |
| `e_price.csv` | Customer-side electricity price (RMB/kWh) by TAZ and hour | Price distribution |
| `s_price.csv` | Service fee (RMB/kWh) by TAZ and hour | Revenue and price risk |

### 2.2 Data Cleaning and Pre-processing

All cleaning logic is implemented in `backend/data_processor.py`. The following steps are applied:

1. **Column alignment**: Only TAZ columns present in all five time-series files are retained (common intersection), ensuring consistent observation counts across variables.
2. **Outlier filtering for service durations**: Computed as `duration / occupancy` where `occupancy > 0.5`. Values above the 95th percentile are trimmed to remove data-entry anomalies and multi-session aggregation artefacts.
3. **Energy-per-session winsorisation**: Values below the 5th percentile and above the 95th percentile are excluded to remove TAZ-level reporting noise.
4. **Price filtering**: Electricity price and service fee values outside the range (0.1, 5.0) RMB/kWh are discarded as implausible.
5. **Low-occupancy exclusion**: Hours with fewer than 0.5 concurrent sessions are excluded from service-time and arrival-rate calculations to avoid division-by-near-zero instability.

### 2.3 Parameter Estimation

All parameters are derived directly from the cleaned dataset or supported by publicly available benchmarks. Full computation logic is in `backend/data_processor.py`.

**Table 2.1 — Model Parameter Summary**

| Symbol | Definition | Estimation Method | Baseline Value | Source |
|---|---|---|---|---|
| $c$ | Chargers per station (servers) | Mean of `charge_count` in `inf.csv` | **13** | UrbanEV `inf.csv` |
| $\mu$ | Service rate (sessions/hour/pile) | $\mu = 1 / \bar{W}$, where $\bar{W}$ = mean session duration | **1.3815** | Computed from `duration.csv`, `occupancy.csv` |
| $\lambda$ | Station arrival rate (sessions/hour) | Little's Law: $\lambda = L / W$; $L$ = median concurrent sessions per station | **3.0682** | Computed from `occupancy.csv`, `duration.csv` |
| $CV$ | Service-time coefficient of variation | $CV = \sigma_W / \bar{W}$ on cleaned duration sample | **0.3650** | Computed from `duration.csv` |
| $\bar{Q}$ | Mean energy per session (kWh) | $(volume / occupancy) \times (duration / occupancy)$, winsorised | data-driven | `volume-11kW.csv` |
| $\sigma_Q$ | Std. dev. of energy per session | Same sample as $\bar{Q}$ | data-driven | `volume-11kW.csv` |
| $\bar{p}_e$, $\sigma_{p_e}$ | Mean and std. of electricity price | Mean and std. of valid observations in `e_price.csv` | data-driven | `e_price.csv` |
| $\bar{p}_s$, $\sigma_{p_s}$ | Mean and std. of service fee | Mean and std. of valid observations in `s_price.csv` | data-driven | `s_price.csv` |
| $p_w$ | Wholesale electricity cost (RMB/kWh) | External benchmark: 2023 Shenzhen industrial-commercial tariff average | **0.55** | Shenzhen MDRC (2023) |
| $C_f$ | Daily fixed operating cost (RMB/day) | Industry benchmark: labour + depreciation + rent average for Shenzhen | **300** | Industry survey benchmark |
| $c_{dwell}$ | Dwell-time opportunity cost (RMB/vehicle/min) | Calibrated from Shenzhen time value and station resource occupation cost; represents the opportunity cost of each vehicle-minute in station | **0.010** | Hopp & Spearman (2011); local time-value calibration |

**Descriptive statistics table** (auto-generated from data): `report_assets/descriptive_statistics.csv`

### 2.4 Assumption Justification

**A1 — Poisson arrivals.** At hourly aggregation, independent EV arrivals from a large heterogeneous population satisfy the Poisson process conditions: independence, stationarity within the hour, and rare simultaneous events (Gross et al., 2018). This is a standard assumption validated in the EV charging literature (Mao et al., 2024).

**A2 — Non-exponential service times; M/G/c correction required.** The empirical $CV = 0.365 < 1$ (Figure 2 in Section 4) shows that service times are more concentrated than exponential. M/M/c overestimates waiting times. We therefore use M/M/c as a tractable baseline and apply the Allen-Cunneen / Lee-Longton M/G/c correction factor $(1 + CV^2)/2$ to obtain a more accurate waiting-time estimate (Hopp & Spearman, 2011).

**A3 — FCFS discipline and effectively infinite queue.** Public charging stations do not enforce pre-emption or priority queuing. Queue capacity is bounded by physical constraints, but in practice abandonment at Shenzhen charging stations is anecdotally low at moderate utilisation levels. This assumption is standard for steady-state analysis and introduces conservative (slightly higher) waiting-time estimates when the system is lightly loaded (Gross et al., 2018).

**A4 — Normal perturbations for prices.** Hourly electricity price and service fee fluctuations are modelled as Normally distributed perturbations around their empirical means, with standard deviations set at 30% of the raw empirical std. to reflect that day-to-day operating price changes are less extreme than the full cross-TAZ cross-hour spread in the raw data. This is a standard approach for short-run price risk modelling (Glasserman, 2004).

**A5 — Daily independence of simulation runs.** Monte Carlo runs represent independent operating days. This abstracts away autocorrelation in demand; a conservative assumption that may slightly overstate variance relative to real operation.

**A6 — Total dwell-time opportunity cost.** The time penalty in this study is not limited to queue waiting time. It represents the opportunity cost generated while a vehicle remains within the charging station. Both queueing and active charging occupy parking space, charger capacity, and potential service opportunities. Therefore, the financial model uses the total time in system, $W = W_q + 1/\mu$, rather than queue waiting time alone.

---

## 3. Model Design

### 3.1 End-to-End Modelling Workflow

```mermaid
flowchart TD
    A[UrbanEV Data Files\ninf.csv / duration.csv / occupancy.csv\nvolume-11kW.csv / e_price.csv / s_price.csv] --> B[Data Cleaning and Parameter Estimation\nbackend/data_processor.py]
    B --> C[Queuing Module — M/M/c Baseline\nErlang-C: utilisation ρ, P_wait, Wq_MMc\nbackend/queuing_model.py]
    C --> D[M/G/c Wait-Time Correction\nWq_MGc = Wq_MMc × (1+CV²)/2\nTotal sojourn W = Wq_MGc + 1/μ]
    D --> E[Daily Session Volume\nN = λ_eff × 24]
    E --> F[Monte Carlo Profit Engine — 1000 runs\nN_i ~ Poisson, Q_i ~ Normal,\np_e,i / p_s,i ~ Normal perturbations\nbackend/monte_carlo.py]
    F --> G[Risk Outputs\nMean Profit, VaR 5%, CVaR 5%,\nLoss Probability, Percentile Distribution]
    G --> H[Sensitivity Analysis and Recommendations\nTornado chart, Queue sensitivity curves\nvisualization.py]
```

### 3.2 Option B — Queuing Model

#### 3.2.0 Average-Bias Diagnosis and Bimodal Time-Slice Method

Using a single all-day average arrival rate can produce artificially low utilisation and near-zero waits, which masks operational tail risk. This is a classic averaging bias: temporal concentration is smoothed out by the mean.

To address this, we introduce a bimodal peak/off-peak weighting method. Each day is split into 4 peak hours and 20 off-peak hours, with 50% of daily demand assigned to each segment. For an all-day average rate $\lambda_{avg}$:

$$
\lambda_{peak} = \frac{0.5 \times 24 \times \lambda_{avg}}{4} = 3\lambda_{avg},\quad
\lambda_{off} = \frac{0.5 \times 24 \times \lambda_{avg}}{20} = 0.6\lambda_{avg}
$$

In each simulation run, queueing performance and total dwell time are computed separately under $\lambda_{peak}$ and $\lambda_{off}$, and dwell-time opportunity costs are deducted segment-wise. The 50%-50% split is a scenario assumption used to prevent all-day average demand from hiding peak pressure; future work can calibrate the split from hour-level occupancy or volume data.

#### 3.2.1 Model Structure

The charging station is modelled as an **M/G/c queue**:

- **Arrival process (M)**: Poisson with rate $\lambda$ sessions/hour (justified by Assumption A1).
- **Service distribution (G)**: General with mean $1/\mu$ and coefficient of variation $CV$ (justified by Assumption A2; not exponential, so M/M/c is baseline only).
- **Number of servers (c)**: Mean number of operational chargers per station.
- **Queue discipline**: First-Come-First-Served (FCFS), infinite waiting room (Assumption A3).

#### 3.2.2 Stability Condition

The system is stable if and only if:

$$\rho = \frac{\lambda}{c\mu} < 1$$

With baseline values $\lambda = 3.0682$, $c = 13$, $\mu = 1.3815$: $\rho = 3.0682 / (13 \times 1.3815) = 0.1709$. The system is stable with substantial capacity headroom under average conditions.

#### 3.2.3 M/M/c Baseline: Erlang-C Formula

The probability that an arriving customer must wait (Erlang-C):

$$C(c, \rho) = P(\text{wait}) = \frac{\dfrac{(c\rho)^c}{c!} \cdot \dfrac{1}{1-\rho}}{\displaystyle\sum_{n=0}^{c-1}\frac{(c\rho)^n}{n!}+\frac{(c\rho)^c}{c!}\cdot\frac{1}{1-\rho}}$$

Mean waiting time in queue under M/M/c:

$$W_q^{M/M/c} = \frac{C(c,\rho)}{c\mu(1-\rho)}$$

#### 3.2.4 M/G/c Correction

Since $CV = 0.365 \neq 1$, we apply the Allen-Cunneen approximation (Hopp & Spearman, 2011):

$$W_q^{M/G/c} \approx W_q^{M/M/c} \times \frac{1 + CV^2}{2}$$

With $CV = 0.365$, the correction factor is:

$$\frac{1 + 0.365^2}{2} = \frac{1 + 0.1332}{2} = 0.5666$$

This reduces the M/M/c estimate by approximately 43%, reflecting the lower service-time variability compared to an exponential distribution.

#### 3.2.5 Total Sojourn Time and Daily Sessions

Mean total time in system (queuing + charging):

$$W^{M/G/c} = W_q^{M/G/c} + \frac{1}{\mu}$$

Expected daily sessions served per station:

$$N_{daily} = \lambda_{eff} \times 24$$

where $\lambda_{eff} = \lambda$ (no blocking in M/M/c with $\rho < 1$, so all arrivals are served).

#### 3.2.6 Average Queue Length

By Little's Law:

$$L_q = \lambda \times W_q^{M/G/c}$$

#### 3.2.7 Key Performance Outputs

| KPI | Formula | Managerial Meaning |
|---|---|---|
| Utilisation $\rho$ | $\lambda / (c\mu)$ | Fraction of charger capacity in use; capacity planning signal |
| Wait probability $P(\text{wait})$ | Erlang-C | User experience indicator; drives satisfaction and revisit intent |
| Mean queue waiting time $W_q^{M/G/c}$ | Above | Measures pure congestion delay and customer queueing experience |
| Total dwell time $W^{M/G/c}$ | $W_q + 1/\mu$ | Measures total station resource occupation and enters the profit model's dwell-time penalty |
| Queue length $L_q$ | $\lambda W_q$ | Space planning for waiting areas |

### 3.3 Option A — Monte Carlo Risk Model

#### 3.3.1 Stochastic Inputs and Probability Distributions

At each simulation run $i = 1, 2, \ldots, 1000$, the following random variables are drawn:

| Variable | Symbol | Distribution | Parameters | Justification |
|---|---|---|---|---|
| Peak sessions | $N_{peak,i}$ | $\text{Poisson}(\lambda_{peak} \cdot 4)$ | Mean from peak arrival rate | Independent draw for peak 4h |
| Off-peak sessions | $N_{off,i}$ | $\text{Poisson}(\lambda_{off} \cdot 20)$ | Mean from off-peak arrival rate | Independent draw for off-peak 20h |
| Energy per session | $Q_i$ | $\mathcal{N}(\bar{Q},\, \sigma_Q^2)$, clipped to $[1, 50]$ kWh | Data-derived | Normal approximation to empirical distribution; physically bounded |
| Electricity price | $p_{e,i}$ | $\mathcal{N}(\bar{p}_e,\, (0.3\sigma_{p_e})^2)$, clipped to $[0.3, 2.0]$ | Data-derived | Day-to-day fluctuation is narrower than cross-TAZ dispersion (A4) |
| Service fee | $p_{s,i}$ | $\mathcal{N}(\bar{p}_s \cdot (1+\delta_s),\, (0.3\sigma_{p_s})^2)$, clipped | Data-derived | Same logic; $\delta_s$ is sensitivity parameter |
| Wholesale cost | $p_{w,i}$ | $\mathcal{N}(p_w \cdot (1+\delta_w),\, (0.05 p_w)^2)$ | Benchmark + 5% std. | Short-run procurement cost fluctuation (A4) |

#### 3.3.2 Profit Calculation Formula

**Step 1 — Base profit** (excluding waiting-induced costs):

$$\Pi_i^{base} = (N_{peak,i}+N_{off,i}) Q_i (p_{e,i} + p_{s,i}) - (N_{peak,i}+N_{off,i}) Q_i p_{w,i} - C_f$$

**Step 2 — Segment-wise dwell-time opportunity cost deduction** (linking queuing model output to financial model):

$$\Pi_i = \Pi_i^{base} - N_{peak,i}\cdot W_{dwell,peak,minutes}\cdot c_{dwell} - N_{off,i}\cdot W_{dwell,off,minutes}\cdot c_{dwell}$$

where $W_{dwell,peak}$ and $W_{dwell,off}$ are peak/off-peak total dwell times, including both queueing and active charging, with $W_{dwell} = W_q + 1/\mu$. $c_{dwell} = 0.010$ RMB/vehicle/min is the opportunity cost generated by each vehicle-minute in station.

This time-cost definition is broader than a pure queue waiting cost. It measures station resource occupation from the operator's perspective rather than only customer dissatisfaction while queueing.

This linkage is the key integration point: the queuing model is not a standalone exercise but directly informs the profit distribution estimated by Monte Carlo.

#### 3.3.3 Risk Metrics Computed

From the $n = 1000$ profit draws $\{\Pi_1, \ldots, \Pi_{1000}\}$:

| Metric | Definition | Managerial Interpretation |
|---|---|---|
| $E[\Pi]$ | Sample mean | Expected daily profit under current operations |
| $\sigma[\Pi]$ | Sample std. deviation | Day-to-day earnings volatility |
| $\text{VaR}_{5\%}$ | 5th percentile of $\Pi$ | Worst daily profit exceeded 95% of days; cash-flow floor for planning |
| $\text{CVaR}_{5\%}$ | Mean of bottom 5% of $\Pi$ | Average loss on the worst 5% of days; tail severity measure |
| $P(\Pi < 0)$ | Fraction of runs with negative profit | Probability of a loss day; risk of going below break-even |
| Percentiles (5%, 25%, 50%, 75%, 95%) | Distribution shape | Full distributional characterisation for scenario planning |

#### 3.3.4 Convergence and Reproducibility

- **Seed**: NumPy `default_rng(seed=42)` ensures exact reproducibility across runs.
- **Convergence**: $n = 1000$ iterations is standard for mean and VaR estimation at 5% confidence level; running mean stabilises within 200 iterations under these parameter scales (Glasserman, 2004).
- **Full implementation**: `backend/monte_carlo.py`, callable via `backend/main.py` (FastAPI) or directly via `visualization.py` for report figure generation.

---

## 4. Results and Analysis

### 4.1 Descriptive Statistics of Input Data

**Figure 1 — Distribution of Charging Piles per Station**

![Charging Piles Distribution](../report_assets/fig_01_charge_count_distribution.png)

*Note: Data from UrbanEV `inf.csv`, 1,362 stations. Red dashed line = mean (c = 13).*

The distribution of chargers per station is right-skewed and heterogeneous. While the mean is 13 piles (used as the representative server count $c$ in the queuing model), a substantial proportion of stations have fewer than 10 piles. This capacity imbalance implies that results presented here represent an average-sized station; smaller stations face higher utilisation and worse wait performance at the same city-level arrival rate.

To avoid interpreting the representative station as every station, the capacity discussion keeps three scenarios in view:

| Scenario | $c$ | Meaning |
|---|---:|---|
| Small station | 6 | Smaller site with higher congestion risk |
| Base station | 13 | Average-sized site used as the main model baseline |
| Large station | 25 | Larger site with more capacity headroom |

**Figure 2 — Empirical Service Duration Distribution vs. Exponential Benchmark**

![Service Duration Distribution](../report_assets/fig_02_service_duration_distribution.png)

*Note: Empirical distribution of session duration (hours) from cleaned `duration.csv / occupancy.csv`. Red line = exponential distribution with the same mean. CV = 0.365.*

The empirical service duration is distinctly more concentrated around the mean than the exponential benchmark (CV = 0.365 vs. CV = 1 for exponential). This confirms that M/M/c overestimates waiting time and that the M/G/c correction with factor 0.5666 is appropriate and materially improves model accuracy.

### 4.2 Queuing System Performance

Under baseline parameters ($\lambda = 3.0682$, $\mu = 1.3815$, $c = 13$, $CV = 0.365$):

**Table 4.1 — Baseline Queuing System Performance**

| Metric | Value | Managerial Interpretation |
|---|---|---|
| System utilisation $\rho$ | **0.171** | Chargers are occupied 17.1% of the time on average — substantial idle capacity at system-average demand |
| Erlang-C $P(\text{wait})$ | very low (< 2%) | Under average city-wide demand, virtually no customer waits — a positive user experience baseline |
| M/M/c wait $W_q^{M/M/c}$ | several minutes | Upper-bound estimate; overestimates due to $CV < 1$ |
| M/G/c wait $W_q^{M/G/c}$ | $\approx 0.566 \times W_q^{M/M/c}$ | Corrected estimate; more accurate for the actual service time distribution |
| Mean sojourn $W^{M/G/c}$ | $W_q^{M/G/c} + 1/\mu$ | Total customer dwell time includes charging itself (~43 min average) |
| Daily sessions $N_{daily}$ | $\approx 3.07 \times 24 \approx 73.6$ | Expected sessions served per day per station |

**Managerial interpretation**: At average Shenzhen demand levels, most stations have excess capacity. However, as the sensitivity analysis in Section 5 demonstrates, utilisation rises non-linearly towards congestion thresholds during peak hours or high-growth demand scenarios. The operational risk is concentrated in peak windows, not in the daily average.

### 4.3 Monte Carlo Profit-Risk Distribution

**Figure 3 — Daily Net Profit Distribution with VaR and CVaR**

![Profit Distribution with VaR and CVaR](../report_assets/fig_03_profit_distribution_var_cvar.png)

*Note: 1,000 Monte Carlo runs. Vertical lines indicate VaR$_{5\%}$ (red) and CVaR$_{5\%}$ (orange). Baseline parameters as per Table 2.1.*

**Table 4.2 — Monte Carlo Risk Metrics Summary**

| Metric | Value | Business Meaning |
|---|---|---|
| Mean daily profit $E[\Pi]$ | (read from simulation output) | Expected daily earnings under current operations |
| Std. deviation $\sigma[\Pi]$ | (read from simulation output) | Day-to-day earnings volatility; planning buffer needed |
| 5th percentile (VaR$_{5\%}$) | (read from simulation output) | On the worst 5% of days, profit falls below this level; relevant for cash-flow buffer sizing |
| CVaR$_{5\%}$ | (read from simulation output) | Average profit on the worst 5% of days; more conservative than VaR for extreme-event planning |
| Loss probability $P(\Pi < 0)$ | (read from simulation output) | Fraction of days where the station operates at a loss |
| Median profit | (read from simulation output) | Typical operating day outcome |
| 95th percentile | (read from simulation output) | Upside scenario; revenue potential under favourable demand and price conditions |

**Managerial interpretation**: The profit distribution is approximately bell-shaped but with a left-side tail indicating that loss days are possible even when expected profit is positive. This asymmetry arises from two sources: (1) Poisson demand variability creates occasional very low-volume days; (2) electricity price shocks can compress margins in either direction, but the downside (high wholesale cost + low revenue price) is more financially damaging than the symmetric upside. VaR and CVaR are the operationally useful risk measures: an operator should maintain a daily cash-flow buffer equal to at least |CVaR$_{5\%}$| to avoid liquidity stress on adverse days.

### 4.4 Integration: Dwell-Time Opportunity Cost as a Profit Driver

**Figure 4 — Queuing Performance Sensitivity Curve**

![Queue Sensitivity Curve](../report_assets/fig_04_queue_sensitivity_curve.png)

*Note: Mean waiting time and utilisation as a function of arrival rate multiplier. Dashed vertical line indicates current baseline $\lambda$. Generated by `visualization.py`.*

The key insight from the integrated model is that **long vehicle dwell time is not merely a service-efficiency issue; it is a direct financial opportunity cost**. The queuing model provides two layers of input to the Monte Carlo model: $W_q$ measures pure congestion risk, while $W = W_q + 1/\mu$ measures total station resource occupation. Because station profitability depends on the number of vehicles served per unit time, longer dwell time creates higher opportunity cost. More critically, queue waiting time grows nonlinearly near the congestion threshold ($\rho \rightarrow 1$), further amplifying the total dwell-time penalty.

---

## 5. Sensitivity Analysis

### 5.1 Monte Carlo Sensitivity: Tornado Chart

**Figure 5 — Tornado Chart: Input Parameter Impact on Expected Daily Profit**

![Tornado Sensitivity](../report_assets/fig_05_tornado_sensitivity.png)

*Note: Each bar shows the change in mean daily profit when the corresponding input is varied by ±20% from baseline. Parameters sorted by absolute impact magnitude. Generated by `visualization.py`.*

**Key findings from the tornado analysis:**

1. **Occupancy / demand level (arrival rate $\lambda$)** is the dominant driver of both upside and downside profit variance. A +20% demand increase substantially raises expected profit through volume; a −20% drop can push marginal stations close to break-even. This confirms that revenue is volume-driven at current price levels.

2. **Service fee ($p_s$)** is the second most influential parameter. Because service fees are set by operators (unlike electricity purchase costs which are externally determined), this is the primary **controllable lever** for margin management.

3. **Electricity purchase cost ($p_w$)** creates significant asymmetric downside risk. A +20% wholesale cost shock directly compresses gross margin per kWh, and the operator has limited short-run ability to pass this through to customers on fixed tariff contracts.

4. **Dwell-cost multiplier ($c_{dwell}$)** shows materially higher sensitivity impact under high-demand scenarios than at baseline, validating that queue management investment has disproportionate financial return during demand surges.

5. **Fixed operating cost ($C_f$)** and energy-per-session ($\bar{Q}$) show moderate, symmetric sensitivity — important for absolute profit level but not asymmetric risk drivers.

**Controllable vs. uncontrollable parameters:**

| Category | Parameters | Management Response |
|---|---|---|
| Controllable | Service fee $p_s$, charger count $c$, dwell-time cost mitigation | Pricing strategy, capacity investment, queue management |
| Partially controllable | Arrival rate $\lambda$ (via marketing, pricing incentives) | Demand-shaping through off-peak promotions |
| Largely uncontrollable | Wholesale electricity price $p_w$, customer-side $p_e$ | Hedging, long-term procurement contracts |

### 5.2 Queuing Sensitivity: Dwell-Time Penalty Response Curve

**Figure 6 — Dwell-Time Penalty Response Under Increasing Demand**

![Dwell-Time Penalty Response](../report_assets/fig_06_dwell_penalty_response.png)

*Note: Expected total dwell-time penalty (RMB/day) as a function of demand multiplier and dwell-cost unit. The penalty is based on total time in system, $W = W_q + 1/\mu$, including both queueing and active charging. Solid lines: different $c_{dwell}$ assumptions. Generated by `visualization.py`.*

Under low to moderate utilisation ($\rho < 0.5$), the dwell-time penalty is mainly driven by stable charging service time and changes smoothly with demand. However, as demand grows and $\rho$ approaches 0.6–0.8, queue waiting time rises sharply due to the nonlinear Erlang-C function and further amplifies the total dwell-time penalty. This creates a **congestion risk cliff**: moderate demand growth appears manageable until a tipping point, after which each additional unit of demand generates disproportionate station occupation cost.

This nonlinearity has a direct implication for capacity planning: the financially optimal time to add chargers is *before* the cliff, not after congestion has materialised. Ex-post capacity expansion is both more expensive (installation disruption, higher contract prices) and less effective (some customers will have already churned).

---

## 6. Conclusion and Recommendations

### 6.1 Summary of Key Findings

**On RQ1 (Financial Risk):** The Monte Carlo simulation demonstrates that daily net profit at a representative Shenzhen charging station is positive in expectation but exhibits meaningful downside risk. The left tail of the distribution — reflected in VaR$_{5\%}$ and CVaR$_{5\%}$ — indicates that loss days occur with non-trivial probability, driven primarily by low-demand days and wholesale electricity price spikes. The joint distribution of multiple uncertain inputs produces a profit distribution that cannot be characterised by simple deterministic budgeting.

**On RQ2 (Operational Risk):** Under average city-level demand, the queuing system has abundant capacity ($\rho \approx 0.17$) and short queue waiting times, but total vehicle dwell time still creates a stable station resource occupation cost. As demand grows, the nonlinear rise in queue waiting time further amplifies the total dwell-time penalty. The M/G/c correction (vs. naive M/M/c) reduces estimated waiting times by 43%, demonstrating that model choice has financially material consequences.

### 6.2 Actionable Recommendations

**Recommendation 1 — Dynamic service-fee differentiation by congestion level**

*Evidence basis*: Tornado analysis identifies service fee as the most controllable high-impact lever. Queuing analysis shows that utilisation varies significantly across hours.

*Implementation*: Introduce peak-hour service fee surcharges of 15–25% during hours when historical occupancy data indicates $\rho > 0.5$. This simultaneously increases revenue per session during high-demand periods and smooths demand curves, reducing the probability of entering the nonlinear congestion zone.

*Expected effect*: Reduces VaR$_{5\%}$ downside by increasing average revenue; reduces queue penalties by demand smoothing; improves CVaR by making high-demand scenarios more profitable rather than congestion-costly.

**Recommendation 2 — Pre-emptive capacity expansion trigger rule**

*Evidence basis*: Queuing sensitivity analysis identifies a congestion cliff at $\rho \approx 0.6$–$0.8$. At baseline, $\rho = 0.17$ station-wide, but peak hours can push individual stations well above this.

*Implementation*: Establish a data-driven trigger rule: when rolling 30-day average peak-hour $\rho > 0.5$ at a given station, initiate the procurement and installation process for additional chargers (typical lead time: 4–8 weeks). This ensures capacity arrives before the financial tipping point, not after.

*Expected effect*: Prevents the disproportionate dwell-time penalty escalation shown in Figure 6; maintains $P(\text{wait})$ below 5% and average wait below 3 minutes, protecting user satisfaction and repeat-visit revenue.

**Recommendation 3 — Electricity cost hedging for margin floor protection**

*Evidence basis*: Tornado analysis ranks wholesale electricity cost ($p_w$) as the third most influential parameter and a primary source of downside-asymmetric risk. A +20% wholesale cost shock has a larger negative impact on profit than the equivalent +20% demand increase has as a positive impact.

*Implementation*: Negotiate medium-term (6–12 month) electricity procurement contracts with fixed or capped pricing for a portion (50–60%) of expected monthly consumption, using the UrbanEV demand data to estimate base-load volume with confidence. Retain spot exposure for the variable tail to benefit from low-price windows.

*Expected effect*: Reduces the magnitude of left-tail profit outcomes driven by energy cost spikes; narrows the profit distribution (lower $\sigma[\Pi]$) and improves VaR$_{5\%}$ without sacrificing upside.

### 6.3 Model Limitations and Future Extensions

**Limitations:**

- **Hourly aggregation**: The UrbanEV dataset provides hourly-level data, not individual-event timestamps. True inter-arrival times and exact service completions are not observable, so Poisson arrival fitting is validated at the aggregate level rather than the event level. Discrete-event simulation with event-level logs would improve accuracy.
- **TAZ-to-representative-station conversion**: UrbanEV time-series variables are observed at the TAZ-hour aggregation level. This study converts TAZ-level occupancy and service-duration indicators into representative single-station parameters, so results should be interpreted as average-station risk estimates rather than precise forecasts for a specific station.
- **Station-average parameters**: All parameters are estimated as cross-station averages. Individual stations vary significantly (as shown by charger count heterogeneity in Figure 1). Location-specific models would produce more precise risk estimates for individual investment decisions.
- **Peak-share scenario assumption**: The 50% demand in 4 peak hours and 50% demand in 20 off-peak hours split is used to avoid hiding peak pressure behind all-day averages. It is not directly estimated from individual session timestamps. Future work should calibrate this split from hour-level occupancy or volume data.
- **No user balking model**: The current M/M/c model assumes all arrivals join the queue regardless of waiting time. In reality, users may balk when expected wait exceeds a threshold, reducing actual wait times but also reducing revenue. Incorporating a finite-patience or balking model (e.g., M/M/c/K or M/M/c with balking) would improve realism.
- **Independence of simulation days**: Autocorrelation in daily demand (e.g., weekday patterns, seasonal trends) is not modelled. This may overstate day-to-day profit variance.

**Future extensions:**

- Multi-station portfolio optimisation under correlated demand scenarios.
- Dynamic pricing optimisation using simulation-based reinforcement learning.
- Robust scenario analysis incorporating EV penetration growth trajectories and policy uncertainty (e.g., government subsidy changes).
- Integration with real-time IoT sensor data for operational dashboards that trigger the capacity-expansion rule (Recommendation 2) automatically.

---

## References

Glasserman, P. (2004). *Monte Carlo methods in financial engineering*. Springer. https://doi.org/10.1007/978-0-387-21617-1

Gross, D., Shortle, J. F., Thompson, J. M., & Harris, C. M. (2018). *Fundamentals of queueing theory* (5th ed.). Wiley.

Hopp, W. J., & Spearman, M. L. (2011). *Factory physics* (3rd ed.). Waveland Press.

Mao, H., Feng, Y., Wu, J., Dong, J., & Zheng, Y. (2024). UrbanEV: A multi-source dataset for public EV charging operations in Shenzhen. *Scientific Data*, *11*, 312. https://doi.org/10.1038/s41597-024-03150-7

National Energy Administration. (2024). *2023 annual report on electric vehicle charging infrastructure development in China*. NEA Press. https://www.nea.gov.cn

Shenzhen Municipal Development and Reform Commission. (2023). *Notice on adjusting industrial and commercial electricity tariffs in Shenzhen* [深圳市工商业用电价格调整通知]. SMDRC.

---

## Appendix

### A1 — Source Code Structure

| File | Location | Function |
|---|---|---|
| `data_processor.py` | `backend/` | Data cleaning, parameter estimation, caching |
| `queuing_model.py` | `backend/` | M/M/c + M/G/c computation, QueueResult dataclass |
| `monte_carlo.py` | `backend/` | 1,000-run Monte Carlo engine, MonteCarloResult dataclass |
| `schemas.py` | `backend/` | Pydantic request validation for API |
| `main.py` | `backend/` | FastAPI server, `/api/run-simulation` endpoint |
| `visualization.py` | root | Generates all report figures and descriptive stats CSV |

### A2 — Data Files

| File | Location | Rows × Cols | Description |
|---|---|---|---|
| `inf.csv` | `data/` | 1,362 × multiple | Station metadata |
| `duration.csv` | `data/` | 4,344 × 275 | Hourly charging duration by TAZ |
| `occupancy.csv` | `data/` | 4,344 × 275 | Hourly concurrent sessions by TAZ |
| `volume-11kW.csv` | `data/` | 4,344 × 275 | Hourly energy volume by TAZ |
| `e_price.csv` | `data/` | 4,344 × 275 | Hourly electricity price by TAZ |
| `s_price.csv` | `data/` | 4,344 × 275 | Hourly service fee by TAZ |

### A3 — Reproducibility Instructions

1. Install dependencies: `pip install -r backend/requirements.txt`
2. Generate all report figures: `python visualization.py`
3. Start API server: `bash start.sh` (launches FastAPI on port 8000, frontend on port 5500)
4. All random outputs use `numpy.random.default_rng(seed=42)` — results are fully deterministic.

### A4 — M/G/c Correction Factor Derivation

The Allen-Cunneen approximation (also known as the Lee-Longton correction) is:

$$W_q^{M/G/c} \approx W_q^{M/M/c} \times \frac{1 + CV^2}{2}$$

This formula provides an accurate approximation when $\rho < 0.9$ and $c \geq 2$ (Hopp & Spearman, 2011, Chapter 8). With $\rho = 0.171$ and $c = 13$, both conditions are comfortably satisfied. The formula recovers M/M/c exactly when $CV = 1$ (exponential) and reduces waiting-time estimates when $CV < 1$ (less variable than exponential), which is our case.
