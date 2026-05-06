"""
queuing_model.py — M/M/c 排队论计算器
职责：根据 λ、μ、c 计算系统利用率、排队等待时间、总在站时间及有效服务车辆数。

输出两类时间指标：
- queue_waiting_time_minutes (W_q): 纯排队等待时间，用于服务质量解读。
- dwell_time_minutes (W = W_q + 1/μ): 总在站时间，用于财务模型中的在站时间机会成本扣减。
"""

import math
from dataclasses import dataclass


@dataclass
class QueueResult:
    rho: float           # 系统利用率 ρ = λ/(c·μ)
    erlang_c: float      # 等待概率（Erlang C 值）
    queue_waiting_time_minutes: float    # 平均排队等待时间 W_q（分钟，M/G/c 修正后，不含服务时间）
    wq_mmc_minutes: float  # 平均排队等待时间（分钟，M/M/c 基线）
    dwell_time_minutes: float   # 总在站时长 W（分钟，= W_q + 1/μ·60，含排队等待 + 充电服务时间）
    mgc_correction_factor: float  # Lee-Longton 修正系数
    lq: float            # 平均排队长度
    effective_lambda: float  # 实际有效到达率（次/小时）
    daily_sessions: float    # 每日有效服务次数（次/天）


class QueuingSimulator:
    """M/G/c 近似排队系统，内部保留 M/M/c 基线。"""

    def __init__(self, lam: float, mu: float, c: int, service_time_cv: float = 1.0):
        """
        Parameters
        ----------
        lam : 到达率（次/小时）
        mu  : 单桩服务率（次/小时）= 1/平均充电时长
        c   : 充电桩数量
        service_time_cv : 服务时间变异系数，CV=1 时退化为 M/M/c
        """
        self.lam = lam
        self.mu  = mu
        self.c   = c
        self.service_time_cv = max(service_time_cv, 0.0)

    def _mgc_correction_factor(self) -> float:
        """Lee-Longton/Allen-Cunneen 风格修正：M/G/c 等待时间近似。"""
        return (1.0 + self.service_time_cv ** 2) / 2.0

    def _erlang_c(self) -> tuple[float, float]:
        """
        计算 Erlang C 公式及 P0。
        返回 (erlang_c, P0)。
        若 ρ >= 1（队列不稳定），返回 (1.0, 0.0)。
        """
        lam, mu, c = self.lam, self.mu, self.c
        rho = lam / (c * mu)

        if rho >= 1.0:
            return 1.0, 0.0

        a = lam / mu  # 流量强度（offered traffic）

        # 计算 P0 分母中的累加项：Σ_{n=0}^{c-1} a^n/n!
        sum_terms = sum(a**n / math.factorial(n) for n in range(c))

        # 最后一项：a^c/c! * 1/(1-ρ)
        last_term = (a**c / math.factorial(c)) * (1.0 / (1.0 - rho))

        p0 = 1.0 / (sum_terms + last_term)

        # Erlang C = (a^c / c!) * 1/(1-ρ) * P0
        erlang_c_val = last_term * p0

        return erlang_c_val, p0

    def compute(self) -> QueueResult:
        """执行 M/M/c 基线计算，并输出 M/G/c 修正结果。"""
        lam, mu, c = self.lam, self.mu, self.c
        rho = lam / (c * mu)

        erlang_c_val, _ = self._erlang_c()

        # 平均等待时间（小时）
        if rho < 1.0:
            wq_mmc_hours = erlang_c_val / (c * mu * (1.0 - rho))
        else:
            wq_mmc_hours = float("inf")

        correction_factor = self._mgc_correction_factor()
        wq_mgc_hours = (
            wq_mmc_hours * correction_factor if wq_mmc_hours != float("inf") else float("inf")
        )

        wq_mmc_minutes = wq_mmc_hours * 60.0 if wq_mmc_hours != float("inf") else 999.0
        wq_mgc_minutes = wq_mgc_hours * 60.0 if wq_mgc_hours != float("inf") else 999.0

        # 总在站时长 W = Wq + 1/μ（排队等待 + 充电服务时间）
        # 即使系统空闲 Wq≈0，充电本身仍需 1/μ 小时，是客户的真实时间成本
        mean_service_minutes = (1.0 / mu) * 60.0
        w_mgc_minutes = wq_mgc_minutes + mean_service_minutes if wq_mgc_minutes != 999.0 else 999.0

        # 平均排队长度
        lq = lam * wq_mgc_hours if wq_mgc_hours != float("inf") else float("inf")

        # 有效到达率（M/M/c 无阻塞，全部顾客最终被服务）
        effective_lambda = min(lam, c * mu * 0.999)

        daily_sessions = effective_lambda * 24.0

        return QueueResult(
            rho=rho,
            erlang_c=erlang_c_val,
            queue_waiting_time_minutes=min(wq_mgc_minutes, 999.0),
            wq_mmc_minutes=min(wq_mmc_minutes, 999.0),
            dwell_time_minutes=min(w_mgc_minutes, 999.0),
            mgc_correction_factor=correction_factor,
            lq=min(lq, 9999.0) if lq != float("inf") else 9999.0,
            effective_lambda=effective_lambda,
            daily_sessions=daily_sessions,
        )
