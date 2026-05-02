"""
data_processor.py — 数据提炼厂
职责：读取 data/ 目录下的 CSV，清洗并计算排队模型与蒙特卡洛所需的全部基准参数。
结果缓存到模块级字典，只在首次调用时计算一次。
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

_cache: dict = {}


def load_baseline_data() -> dict:
    """
    返回基准参数字典，字段说明：
      c                  : int   — 平均充电桩数（来自 inf.csv charge_count 均值）
      mu                 : float — 单桩服务率（次/小时），= 1 / 平均充电时长(h)
      lambda_rate        : float — 单站到达率（次/小时），由 Little 定律推导
      mean_session_duration: float — 平均充电时长（小时）
            service_time_cv    : float — 单次充电时长变异系数，用于 M/G/c 修正
      mean_kwh           : float — 单次充电平均电量（kWh）
      std_kwh            : float — 单次充电电量标准差（kWh）
      mean_e_price       : float — 客户侧平均电价（元/kWh，来自 e_price.csv）
      mean_s_price       : float — 平均服务费（元/kWh，来自 s_price.csv）
      std_e_price        : float — 电价标准差
      std_s_price        : float — 服务费标准差
    wait_cost_per_minute: float — 每分钟等待隐性成本（元/车·分钟）
      wholesale_price    : float — ★补全参数★ 电站购电批发价（元/kWh）
                                   依据：2023 深圳工商业电价市场均值 ≈ 0.55 元/kWh
      daily_fixed_cost   : float — ★补全参数★ 单站日固定运营成本（元）
                                   依据：人工 + 折旧 + 租金市场均值 ≈ 300 元/天
    """
    if _cache:
        return _cache

    # ── 1. 站点元数据 ──────────────────────────────────────────────────────────
    df_inf = pd.read_csv(os.path.join(DATA_DIR, "inf.csv"))
    mean_charge_count = df_inf["charge_count"].mean()
    # 275 个 TAZ 共 1362 座站，每 TAZ 平均站数
    n_stations = len(df_inf)

    # ── 2. 时序数据（4344 行 × 275 列 TAZ） ─────────────────────────────────
    df_dur = pd.read_csv(os.path.join(DATA_DIR, "duration.csv"), index_col=0)
    df_occ = pd.read_csv(os.path.join(DATA_DIR, "occupancy.csv"), index_col=0)
    df_vol = pd.read_csv(os.path.join(DATA_DIR, "volume-11kW.csv"), index_col=0)
    df_ep  = pd.read_csv(os.path.join(DATA_DIR, "e_price.csv"),    index_col=0)
    df_sp  = pd.read_csv(os.path.join(DATA_DIR, "s_price.csv"),    index_col=0)

    # 对齐列（取公共 TAZ）
    common_cols = df_dur.columns.intersection(df_occ.columns).intersection(df_vol.columns)
    df_dur = df_dur[common_cols]
    df_occ = df_occ[common_cols]
    df_vol = df_vol[common_cols]
    n_taz = len(common_cols)

    dur_vals = df_dur.values.flatten().astype(float)
    occ_vals = df_occ.values.flatten().astype(float)
    vol_vals = df_vol.values.flatten().astype(float)
    ep_vals  = df_ep.values.flatten().astype(float)
    sp_vals  = df_sp.values.flatten().astype(float)

    # ── 3. 平均充电时长（h/次）：duration_sum / concurrent_sessions ──────────
    valid_mask = (occ_vals > 0.5) & (dur_vals > 0) & np.isfinite(occ_vals) & np.isfinite(dur_vals)
    session_durations = dur_vals[valid_mask] / occ_vals[valid_mask]   # h/次
    # 去除极端离群值（95th percentile 以上）
    p95 = np.percentile(session_durations, 95)
    session_durations = session_durations[session_durations <= p95]
    mean_session_duration = float(np.mean(session_durations))         # h/次
    service_time_cv = float(np.std(session_durations) / mean_session_duration)
    mu = 1.0 / mean_session_duration                                  # 次/h/桩

    # ── 4. 到达率 λ（次/h/站）：由 Little 定律 λ = L / W ────────────────────
    # L = 每 TAZ 平均并发充电数，W = 平均充电时长
    occ_positive = occ_vals[occ_vals > 0.5]
    mean_L_taz   = float(np.median(occ_positive))                    # 每 TAZ 并发数
    stations_per_taz = n_stations / n_taz                            # ~4.95 站/TAZ
    mean_L_station = mean_L_taz / stations_per_taz                   # 每站并发数
    lambda_rate    = mean_L_station / mean_session_duration           # 次/h/站

    # ── 5. 单次充电电量（kWh/次）────────────────────────────────────────────
    vol_mask = valid_mask & np.isfinite(vol_vals) & (vol_vals > 0)
    # kWh/h/并发会话 × 充电时长 = kWh/次
    kwh_per_session_vals = (vol_vals[vol_mask] / occ_vals[vol_mask]) * (
        dur_vals[vol_mask] / occ_vals[vol_mask]
    )
    p5_kwh, p95_kwh = np.percentile(kwh_per_session_vals, [5, 95])
    kwh_clean = kwh_per_session_vals[
        (kwh_per_session_vals >= p5_kwh) & (kwh_per_session_vals <= p95_kwh)
    ]
    mean_kwh = float(np.mean(kwh_clean))
    std_kwh  = float(np.std(kwh_clean))

    # ── 6. 电价与服务费 ──────────────────────────────────────────────────────
    valid_ep = ep_vals[(ep_vals > 0.1) & (ep_vals < 5) & np.isfinite(ep_vals)]
    valid_sp = sp_vals[(sp_vals > 0.1) & (sp_vals < 5) & np.isfinite(sp_vals)]
    mean_e_price = float(np.mean(valid_ep))
    mean_s_price = float(np.mean(valid_sp))
    std_e_price  = float(np.std(valid_ep))
    std_s_price  = float(np.std(valid_sp))

    # ── 7. 写入缓存 ──────────────────────────────────────────────────────────
    _cache.update({
        "c":                    int(round(mean_charge_count)),
        "mu":                   mu,
        "lambda_rate":          lambda_rate,
        "mean_session_duration": mean_session_duration,
        "service_time_cv":      service_time_cv,
        "mean_kwh":             mean_kwh,
        "std_kwh":              std_kwh,
        "mean_e_price":         mean_e_price,
        "mean_s_price":         mean_s_price,
        "std_e_price":          std_e_price,
        "std_s_price":          std_s_price,
        "wait_cost_per_minute": 0.020,  # 元/车·分钟，基于在站总时长W(=Wq+1/μ≈43min)的隐性成本
                                        # 标定：深圳时间价值≈30元/h，充电等待折损≈4%
                                        # → 0.020×43×73.6次≈63元/天（显著但不超过利润）
        # ★ 以下两项为补全参数，依据市场均值
        "wholesale_price":      0.55,   # 元/kWh，深圳工商业购电均价
        "daily_fixed_cost":     300.0,  # 元/天，单站运营固定成本（人工+折旧+租金）
    })

    return _cache
