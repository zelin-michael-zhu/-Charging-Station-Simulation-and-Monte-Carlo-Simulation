/**
 * app.js — 前端逻辑与神经枢纽
 * 职责：绑定滑块事件 → 发起 POST 请求 → 解析结果 → 更新 DOM + 图表
 */

const API_BASE = "http://localhost:8000";

// ── DOM 引用 ────────────────────────────────────────────────────────────────
const sfeeSlider  = document.getElementById("sfee");
const ecostSlider = document.getElementById("ecost");
const occSlider   = document.getElementById("occ");
const wcostSlider = document.getElementById("wcost");

const sfeeVal  = document.getElementById("sfee-val");
const ecostVal = document.getElementById("ecost-val");
const occVal   = document.getElementById("occ-val");
const wcostVal = document.getElementById("wcost-val");

const statusDot  = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");

const kpiVar   = document.getElementById("kpi-var");
const kpiMean  = document.getElementById("kpi-mean");
const kpiStd   = document.getElementById("kpi-std");
const kpiLoss  = document.getElementById("kpi-loss");
const kpiDwellPenalty = document.getElementById("kpi-dwell-penalty");
const kpiPeakWait = document.getElementById("kpi-peak-wait");
const kpiPeakUtil = document.getElementById("kpi-peak-util");
const kpiCongestionState = document.getElementById("kpi-congestion-state");
const kpiCongestionCard = document.getElementById("kpi-congestion-card");

const pC       = document.getElementById("p-c");
const pLambda  = document.getElementById("p-lambda");
const pMu      = document.getElementById("p-mu");
const pRho     = document.getElementById("p-rho");
const pCv      = document.getElementById("p-cv");
const pFactor  = document.getElementById("p-factor");
const pWcost   = document.getElementById("p-wcost");
const pSessions= document.getElementById("p-sessions");
const pWaitBase= document.getElementById("p-wait-base");
const pWait    = document.getElementById("p-wait");
const pSojourn = document.getElementById("p-sojourn");
const chartSub = document.getElementById("chart-sub-info");

// ── ECharts 初始化 ──────────────────────────────────────────────────────────
const chartDom = document.getElementById("profit-chart");
const myChart  = echarts.init(chartDom, null, { renderer: "svg" });
const heroMean = document.getElementById("hero-mean");

// 白底科技风图表骨架
const baseOption = {
  backgroundColor: "transparent",
  animation: true,
  animationDuration: 400,
  animationEasing: "cubicOut",
  grid: { top: 20, right: 24, bottom: 48, left: 60 },
  tooltip: {
    trigger: "axis",
    axisPointer: { type: "shadow" },
    backgroundColor: "rgba(30,41,59,0.90)",
    borderColor: "rgba(255,255,255,0.32)",
    textStyle: { color: "#ffffff", fontSize: 12 },
    formatter: (params) => {
      const p = params[0];
      return `利润区间：${p.name}<br/>频次：<b>${p.value}</b> 次`;
    },
  },
  xAxis: {
    type: "category",
    name: "日净利润（元）",
    nameLocation: "middle",
    nameGap: 32,
    nameTextStyle: { color: "#64748b", fontSize: 11 },
    axisLine: { lineStyle: { color: "#cbd5e1" } },
    axisTick: { show: false },
    axisLabel: { color: "#475569", fontSize: 10, rotate: 20 },
    splitLine: { show: false },
    data: [],
  },
  yAxis: {
    type: "value",
    name: "频次",
    nameTextStyle: { color: "#64748b", fontSize: 11 },
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: "#475569", fontSize: 10 },
    splitLine: { lineStyle: { color: "#e2e8f0" } },
  },
  series: [
    {
      name: "利润频次",
      type: "bar",
      barMaxWidth: 24,
      itemStyle: {
        color: (params) => {
          // 正利润蓝绿，负利润橙红
          const label = params.name;
          const mid = parseFloat(label.split("~")[0]) || 0;
          return mid >= 0
            ? new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "rgba(59,130,246,0.88)" },
                { offset: 1, color: "rgba(59,130,246,0.32)" },
              ])
            : new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: "rgba(239,68,68,0.88)" },
                { offset: 1, color: "rgba(239,68,68,0.30)" },
              ]);
        },
        borderRadius: [4, 4, 0, 0],
      },
      data: [],
    },
    // VaR 参考线（markLine）
    {
      name: "VaR",
      type: "bar",
      data: [],
      markLine: {
        silent: true,
        symbol: "none",
        lineStyle: { color: "#f87171", type: "dashed", width: 1.5 },
        label: {
          formatter: "5% VaR",
          color: "#f87171",
          fontSize: 11,
          position: "insideEndTop",
        },
        data: [{ name: "VaR", xAxis: 0 }],
      },
    },
  ],
  markArea: {},
};

myChart.setOption(baseOption);
window.addEventListener("resize", () => myChart.resize());


// ── 辅助：将利润数组分箱为直方图 ───────────────────────────────────────────
function buildHistogram(profits, bins = 30) {
  const minP = Math.min(...profits);
  const maxP = Math.max(...profits);
  const width = (maxP - minP) / bins;

  const counts = new Array(bins).fill(0);
  profits.forEach((p) => {
    let idx = Math.floor((p - minP) / width);
    if (idx >= bins) idx = bins - 1;
    counts[idx]++;
  });

  const labels = Array.from({ length: bins }, (_, i) => {
    const lo = Math.round(minP + i * width);
    const hi = Math.round(minP + (i + 1) * width);
    return `${lo}~${hi}`;
  });

  return { labels, counts, binWidth: width, minP };
}


// ── 设置状态指示 ────────────────────────────────────────────────────────────
function setStatus(state, msg) {
  statusDot.className = `dot dot-${state}`;
  statusText.textContent = msg;
}


// ── 核心：发请求 + 更新页面 ─────────────────────────────────────────────────
let debounceTimer = null;

async function runSimulation() {
  const sfee  = parseFloat(sfeeSlider.value) / 100;
  const ecost = parseFloat(ecostSlider.value) / 100;
  const occ   = parseFloat(occSlider.value)  / 100;
  const wcost = parseFloat(wcostSlider.value) / 100;

  setStatus("loading", "计算中…");
  document.querySelector(".results-section").classList.add("loading-overlay");

  try {
    const resp = await fetch(`${API_BASE}/api/run-simulation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        service_fee_change:        sfee,
        electricity_cost_change:   ecost,
        occupancy_change:          occ,
        dwell_cost_change:         wcost,
      }),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }

    const data = await resp.json();
    updateUI(data);
    setStatus("ok", `计算完成 · ${new Date().toLocaleTimeString()}`);
  } catch (e) {
    setStatus("idle", `错误：${e.message}。请确保后端在 8000 端口运行。`);
    console.error(e);
  } finally {
    document.querySelector(".results-section").classList.remove("loading-overlay");
  }
}


// ── 更新 UI ─────────────────────────────────────────────────────────────────
function updateUI(data) {
  // KPI 数字
  kpiVar.textContent  = fmt(data.var_5pct);
  kpiMean.textContent = fmt(data.mean_profit);
  kpiStd.textContent  = fmt(data.std_profit);
  kpiLoss.textContent = (data.prob_loss * 100).toFixed(1) + "%";
  kpiDwellPenalty.textContent = fmt2(data.mean_dwell_penalty ?? 0);
  kpiPeakWait.textContent = fmt2(data.peak_wait_minutes ?? 0);
  kpiPeakUtil.textContent = `利用率 ${(data.peak_utilization * 100).toFixed(1)}%`;
  if (heroMean) {
    heroMean.textContent = fmt(data.mean_profit);
  }

  // 根据 VaR 正负变色
  kpiVar.style.color = data.var_5pct >= 0 ? "#10b981" : "#ef4444";
  kpiMean.style.color = data.mean_profit >= 0 ? "#10b981" : "#ef4444";
  kpiStd.style.color = "#334155";
  kpiLoss.style.color = "#f59e0b";
  kpiDwellPenalty.style.color = "#334155";

  const thresholdMinutes = 5.0;
  const occIncrease = parseFloat(occSlider.value) > 0;
  const peakWait = data.peak_wait_minutes ?? 0;
  const isCritical = occIncrease && peakWait > thresholdMinutes;

  kpiPeakWait.classList.toggle("danger-value", isCritical);
  kpiPeakWait.classList.toggle("danger-blink", isCritical);
  kpiCongestionCard.style.borderColor = isCritical
    ? "rgba(239,68,68,0.8)"
    : "rgba(248,113,113,0.35)";
  kpiCongestionState.textContent = isCritical
    ? `告警：高峰排队超过 ${thresholdMinutes.toFixed(0)} 分钟，系统逼近拥堵崩溃`
    : "状态：高峰通行可控";
  kpiCongestionState.style.color = isCritical ? "#b91c1c" : "#b45309";

  // 排队参数
  pC.textContent        = data.c + " 桩";
  pLambda.textContent   = data.lambda_rate.toFixed(3) + " 次/h";
  pMu.textContent       = data.mu.toFixed(3) + " 次/h";
  pRho.textContent      = (data.utilization * 100).toFixed(1) + "%";
  pCv.textContent       = (data.service_time_cv ?? 1).toFixed(3);
  pFactor.textContent   = (data.mgc_correction_factor ?? 1).toFixed(4);
  pWcost.textContent    = (data.dwell_cost_per_minute ?? 0).toFixed(3) + " 元/车·分";
  pSessions.textContent = data.daily_sessions.toFixed(0) + " 次";
  pWaitBase.textContent = (data.mean_wait_minutes_baseline ?? data.mean_wait_minutes).toFixed(2) + " 分钟";
  pWait.textContent     = data.mean_wait_minutes.toFixed(2) + " 分钟";
  if (pSojourn) {
    pSojourn.textContent = (data.mean_sojourn_minutes ?? data.mean_wait_minutes).toFixed(1) + " 分钟";
  }

  // 副标题
  chartSub.textContent =
    `VaR 5% = ${fmt(data.var_5pct)} 元  |  期望 = ${fmt(data.mean_profit)} 元  |  在站时间成本 = ${fmt2(data.mean_dwell_penalty ?? 0)} 元`;

  // 直方图
  const { labels, counts, binWidth, minP } = buildHistogram(data.histogram_data, 32);

  // 找到 VaR 对应的 bin 索引
  const varBinIdx = Math.min(
    Math.max(0, Math.floor((data.var_5pct - minP) / binWidth)),
    labels.length - 1
  );

  myChart.setOption({
    xAxis:  { data: labels },
    series: [
      { data: counts },
      {
        data: [],
        markLine: {
          data: [{ name: "5% VaR", xAxis: varBinIdx }],
          silent: true,
          symbol: "none",
          lineStyle: { color: "#f87171", type: "dashed", width: 1.8 },
          label: {
            formatter: `5% VaR\n${fmt(data.var_5pct)}元`,
            color: "#f87171",
            fontSize: 11,
            position: "insideEndTop",
          },
        },
      },
    ],
  });
}


// ── 格式化数字 ───────────────────────────────────────────────────────────────
function fmt(n) {
  return n.toLocaleString("zh-CN", { maximumFractionDigits: 0 });
}

function fmt2(n) {
  return n.toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}


// ── 防抖监听滑块 ─────────────────────────────────────────────────────────────
function onSliderInput() {
  sfeeVal.textContent  = sfeeSlider.value  > 0 ? "+" + sfeeSlider.value  + "%" : sfeeSlider.value  + "%";
  ecostVal.textContent = ecostSlider.value > 0 ? "+" + ecostSlider.value + "%" : ecostSlider.value + "%";
  occVal.textContent   = occSlider.value   > 0 ? "+" + occSlider.value   + "%" : occSlider.value   + "%";
  wcostVal.textContent = wcostSlider.value > 0 ? "+" + wcostSlider.value + "%" : wcostSlider.value + "%";

  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(runSimulation, 380);
}

sfeeSlider.addEventListener("input",  onSliderInput);
ecostSlider.addEventListener("input", onSliderInput);
occSlider.addEventListener("input",   onSliderInput);
wcostSlider.addEventListener("input", onSliderInput);

// 初始加载
runSimulation();
