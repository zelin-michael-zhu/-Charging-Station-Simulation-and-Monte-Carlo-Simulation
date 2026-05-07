<meta charset="utf-8">

<style>
@page {
  size: A4;
  margin: 1.5cm;
  @bottom-center {
    content: counter(page);
    font-family: "Times New Roman", Times, serif;
    font-size: 12pt;
  }
}

html {
  background: #f3f3f3;
  font-family: "Times New Roman", Times, "Liberation Serif", "Nimbus Roman No9 L", serif !important;
}

* {
  font-family: "Times New Roman", Times, "Liberation Serif", "Nimbus Roman No9 L", serif !important;
}

body {
  font-family: "Times New Roman", Times, "Liberation Serif", "Nimbus Roman No9 L", serif !important;
  font-size: 12pt;
  line-height: 1.35;
  color: #000;
  background: #fff;
  box-sizing: border-box;
  max-width: 21cm;
  min-height: 29.7cm;
  margin: 0 auto;
  padding: 1.5cm;
}

h1 {
  font-size: 14pt;
  line-height: 16pt;
  text-align: center;
  font-weight: 700;
  margin: 0 0 4pt;
}

.report-subtitle {
  text-align: center;
  font-size: 12pt;
  line-height: 14pt;
  margin: 0 0 12pt;
}

h2 {
  font-size: 14pt;
  line-height: 16pt;
  font-weight: 700;
  margin: 16pt 0 8pt;
}

h3,
h4 {
  font-size: 12pt;
  line-height: 14pt;
  font-weight: 700;
  margin: 12pt 0 6pt;
}

p {
  margin: 0 0 8pt;
}

hr {
  border: 0;
  border-top: 1px solid #000;
  margin: 14pt 0;
}

img {
  display: block;
  max-width: 100%;
  margin: 6pt auto;
}

img[src*="report_assets"]:not([src*="fig_00_workflow_diagram"]) {
  max-width: 78%;
}

img[src*="fig_00_workflow_diagram"] {
  max-width: 100%;
}

figcaption, .caption {
  font-size: 11pt;
  line-height: 1.3;
}

table {
  width: 100%;
  margin: 10pt 0 14pt;
  border-collapse: collapse;
  font-size: 10pt;
  line-height: 1.2;
  border-top: 1.5pt solid #000 !important;
  border-bottom: 1.5pt solid #000 !important;
  border-left: 0 !important;
  border-right: 0 !important;
  background: transparent !important;
}

thead,
tbody,
tr,
th,
td {
  border-left: 0 !important;
  border-right: 0 !important;
  background: transparent !important;
}

th,
td {
  border-top: 0 !important;
  border-bottom: 0 !important;
  padding: 4pt 6pt;
  text-align: left;
  vertical-align: top;
}

th {
  border-bottom: 0.75pt solid #000 !important;
  font-weight: 700;
  text-align: center;
}

tbody tr:last-child td {
  border-bottom: 0 !important;
}

table code {
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  padding: 0 !important;
  color: #000 !important;
  font-family: "Times New Roman", Times, "Liberation Serif", "Nimbus Roman No9 L", serif !important;
  font-size: 10pt;
}

ol, ul {
  margin-top: 0;
  margin-bottom: 8pt;
  padding-left: 18pt;
}

li {
  margin-bottom: 3pt;
}

blockquote {
  margin: 8pt 0;
  padding-left: 12pt;
  border-left: 2pt solid #000;
}

.cover-roster {
  width: 58%;
  margin: 10pt 0 12pt;
  font-size: 12pt;
  line-height: 1.45;
}

.cover-roster-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  column-gap: 28pt;
  margin: 2pt 0;
}

.cover-roster-header {
  font-weight: 700;
}

code {
  font-family: "Times New Roman", Times, "Liberation Serif", "Nimbus Roman No9 L", serif !important;
  font-size: 10.5pt;
}

math {
  font-family: "Times New Roman", "Cambria Math", "STIX Two Math", Times, serif !important;
  font-size: 1em;
}

math * {
  font-family: "Times New Roman", "Cambria Math", "STIX Two Math", Times, serif !important;
}

math[display="block"] {
  display: block;
  margin: 8pt auto 10pt;
  text-align: center;
  overflow-x: auto;
}

@media print {
  html {
    background: #fff;
  }

  body {
    max-width: none;
    min-height: auto;
    margin: 0;
    padding: 0;
  }
}
</style>
<h1 id="profit-risk-analysis-of-public-ev-charging-stations">Profit Risk Analysis of Public EV Charging Stations</h1>
<p class="report-subtitle">A Monte Carlo and Queuing Simulation Approach under Multiple Uncertainties</p>
<p>Simulation and Risk Analysis (1001)</p>
<hr />
<p><strong>Group Number</strong> Group G</p>
<p><strong>Section</strong> [To Be Filled]</p>
<div class="cover-roster">
  <div class="cover-roster-row cover-roster-header">
    <span>Student Name</span>
    <span>Student ID</span>
  </div>
  <div class="cover-roster-row">
    <span>Jiang Haoran</span>
    <span>2330036047</span>
  </div>
  <div class="cover-roster-row">
    <span>Zhu Zelin</span>
    <span>2330036213</span>
  </div>
  <div class="cover-roster-row">
    <span>Lu Xinyu</span>
    <span>2330036099</span>
  </div>
  <div class="cover-roster-row">
    <span>Gong Yihang</span>
    <span>2330036027</span>
  </div>
  <div class="cover-roster-row">
    <span>Guo Jiajun</span>
    <span>2330036028</span>
  </div>
  <div class="cover-roster-row">
    <span>Sun Haoran</span>
    <span>2330032039</span>
  </div>
</div>
<p>May 2026</p>
<p><strong>Acknowledgement:</strong> All statistical analysis, simulation code, and interpretation were independently conducted by the group.</p>
<hr />
<h2 id="problem-introduction">1. Problem Introduction</h2>
<h3 id="business-problem">1.1 Business Problem</h3>
<p>Public electric vehicle (EV) charging stations face a difficult operating problem: demand is growing, but station-level profitability remains uncertain. By the end of 2023, China had more than 2.7 million public charging piles, with annual growth above 50% (National Energy Administration, 2024). Scale alone, however, does not guarantee stable profit. A station operator in Shenzhen must manage variable arrival volumes, uncertain charging duration, electricity price fluctuation, and the operational risk created when vehicles remain inside the station for longer than expected.</p>
<p>The business problem is therefore not simply whether a charging station is profitable on an average day. The operator needs to know the distribution of daily profit, the probability of a loss-making day, and how congestion or long vehicle dwell time can erode profit. A deterministic budget using average demand and average prices cannot answer these questions. It hides the left-tail risk that matters for cash-flow planning and capacity investment.</p>
<h3 id="research-questions">1.2 Research Questions</h3>
<p>This project addresses two linked research questions.</p>
<p><strong>RQ1: Financial risk.</strong> Under simultaneous uncertainty in demand, charging duration, electricity price, and service fee, what is the daily net profit distribution of a representative public charging station in Shenzhen? What are the associated tail-risk indicators, including value at risk (VaR), conditional value at risk (CVaR), and probability of loss?</p>
<p><strong>RQ2: Operational risk.</strong> How does the queuing system respond to demand changes and capacity decisions? How does the opportunity cost of total vehicle dwell time translate into material profit erosion?</p>
<h3 id="why-monte-carlo-simulation-and-queuing-analysis-are-appropriate">1.3 Why Monte Carlo Simulation and Queuing Analysis Are Appropriate</h3>
<p>The combined method is necessary because the financial and operational risks are connected. Monte Carlo simulation is used for the profit distribution because profit depends on several random inputs and has no useful closed-form distribution in this setting (Glasserman, 2004). Queuing analysis is used because the station is a multi-server service system where arrival rate, service rate, and capacity jointly determine waiting probability, queue waiting time, total dwell time, and utilisation (Gross et al., 2018).</p>
<p>The integration is direct. The M/G/c queuing model estimates queue waiting time <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>W</mi><mi>q</mi></msub></semantics></math> and total dwell time <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>W</mi><mo>=</mo><msub><mi>W</mi><mi>q</mi></msub><mo>+</mo><mn>1</mn><mi>/</mi><mi>μ</mi></mrow></semantics></math>. The Monte Carlo model then uses total dwell time as a financial input. This is not a superficial combination of two course techniques. The queuing outputs enter the profit equation as a station resource occupation cost.</p>
<hr />
<h2 id="data-and-parameters">2. Data and Parameters</h2>
<h3 id="data-source">2.1 Data Source</h3>
<p>The analysis uses the UrbanEV Shenzhen public EV charging dataset released under a CC0 public domain licence (Mao et al., 2024). The dataset covers 1,362 charging stations across 275 Traffic Analysis Zones (TAZs) in Shenzhen. The observation window runs from 1 September 2022 to 28 February 2023, with 4,344 hourly observations per TAZ.</p>
<p>The six core files are:</p>
<p><strong>Table 2.1. UrbanEV files used in this study.</strong></p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th>File</th>
<th>Content</th>
<th>Role in this study</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><code>inf.csv</code></td>
<td>Station metadata: location, TAZ, charger count</td>
<td>Estimate server count <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>c</mi></semantics></math></td>
</tr>
<tr class="even">
<td><code>duration.csv</code></td>
<td>Hourly cumulative charging duration by TAZ</td>
<td>Estimate service duration</td>
</tr>
<tr class="odd">
<td><code>occupancy.csv</code></td>
<td>Hourly concurrent charging sessions by TAZ</td>
<td>Little’s Law and arrival rate</td>
</tr>
<tr class="even">
<td><code>volume-11kW.csv</code></td>
<td>Hourly charging energy volume</td>
<td>Revenue and energy per session</td>
</tr>
<tr class="odd">
<td><code>e_price.csv</code></td>
<td>Customer-side electricity price</td>
<td>Price distribution</td>
</tr>
<tr class="even">
<td><code>s_price.csv</code></td>
<td>Service fee</td>
<td>Revenue and price risk</td>
</tr>
</tbody>
</table>
<p><strong>Figure 0. Spatial distribution of 275 TAZs and 1,362 public charging stations in Shenzhen.</strong><br />
<img src="../report_assets/fig_07_shenzhen_station_distribution_map.png" alt="Spatial distribution of Shenzhen charging stations" /><br />
<em>Note. The figure is generated from station longitude and latitude in <code>inf.csv</code>. The map shows the spatial coverage of the UrbanEV public charging station sample and supports the use of Shenzhen as the empirical context.</em></p>
<h3 id="data-cleaning-and-pre-processing">2.2 Data Cleaning and Pre-processing</h3>
<p>All cleaning logic is implemented in <code>backend/data_processor.py</code>. The workflow is kept explicit for replicability.</p>
<p>First, only TAZ columns present in all relevant time-series files are retained. This avoids mismatched observations across duration, occupancy, volume, and price variables. Second, service duration is computed as <code>duration / occupancy</code> using records with <code>occupancy &gt; 0.5</code>; values above the 95th percentile are trimmed to remove likely aggregation artefacts or data-entry anomalies. Third, energy per session is winsorised by removing values below the 5th percentile and above the 95th percentile. Fourth, electricity price and service fee observations outside <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo stretchy="false" form="prefix">(</mo><mn>0.1</mn><mo>,</mo><mn>5.0</mn><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math> RMB/kWh are removed as implausible. Finally, low-occupancy hours are excluded from rate estimation because dividing by near-zero occupancy would make Little’s Law unstable.</p>
<p>The UrbanEV time-series files are TAZ-hour aggregates rather than individual transaction logs. The study therefore converts TAZ-level occupancy and charging duration into representative single-station parameters. Results should be interpreted as average-station risk estimates, not exact predictions for a named station.</p>
<h3 id="parameter-estimation">2.3 Parameter Estimation</h3>
<p><strong>Table 2.2. Model parameter summary.</strong></p>
<table>
<colgroup>
<col style="width: 18%" />
<col style="width: 18%" />
<col style="width: 18%" />
<col style="width: 25%" />
<col style="width: 18%" />
</colgroup>
<thead>
<tr class="header">
<th>Symbol</th>
<th>Definition</th>
<th>Estimation method</th>
<th style="text-align: right;">Baseline</th>
<th>Source</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>c</mi></semantics></math></td>
<td>Chargers per station</td>
<td>Mean of <code>charge_count</code> in <code>inf.csv</code></td>
<td style="text-align: right;">13</td>
<td>UrbanEV</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>μ</mi></semantics></math></td>
<td>Service rate per charger</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>μ</mi><mo>=</mo><mn>1</mn><mi>/</mi><mover><mi>W</mi><mo accent="true">‾</mo></mover></mrow></semantics></math></td>
<td style="text-align: right;">1.3815</td>
<td>duration, occupancy</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>λ</mi></semantics></math></td>
<td>Arrival rate per station</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>λ</mi><mo>=</mo><mi>L</mi><mi>/</mi><mi>W</mi></mrow></semantics></math> by Little’s Law</td>
<td style="text-align: right;">3.0682</td>
<td>occupancy, duration</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mi>V</mi></mrow></semantics></math></td>
<td>Service-time coefficient of variation</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>σ</mi><mi>W</mi></msub><mi>/</mi><mover><mi>W</mi><mo accent="true">‾</mo></mover></mrow></semantics></math></td>
<td style="text-align: right;">0.3650</td>
<td>duration</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mover><mi>Q</mi><mo accent="true">‾</mo></mover></semantics></math></td>
<td>Mean kWh per session</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo stretchy="false" form="prefix">(</mo><mi>v</mi><mi>o</mi><mi>l</mi><mi>u</mi><mi>m</mi><mi>e</mi><mi>/</mi><mi>o</mi><mi>c</mi><mi>c</mi><mi>u</mi><mi>p</mi><mi>a</mi><mi>n</mi><mi>c</mi><mi>y</mi><mo stretchy="false" form="postfix">)</mo><mo>×</mo><mo stretchy="false" form="prefix">(</mo><mi>d</mi><mi>u</mi><mi>r</mi><mi>a</mi><mi>t</mi><mi>i</mi><mi>o</mi><mi>n</mi><mi>/</mi><mi>o</mi><mi>c</mi><mi>c</mi><mi>u</mi><mi>p</mi><mi>a</mi><mi>n</mi><mi>c</mi><mi>y</mi><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math></td>
<td style="text-align: right;">data-driven</td>
<td>volume</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>σ</mi><mi>Q</mi></msub></semantics></math></td>
<td>Std. dev. of kWh per session</td>
<td>Same cleaned sample as <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mover><mi>Q</mi><mo accent="true">‾</mo></mover></semantics></math></td>
<td style="text-align: right;">data-driven</td>
<td>volume</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mover><mi>p</mi><mo accent="true">‾</mo></mover><mi>e</mi></msub><mo>,</mo><msub><mi>σ</mi><msub><mi>p</mi><mi>e</mi></msub></msub></mrow></semantics></math></td>
<td>Electricity price mean and std.</td>
<td>Valid observations in <code>e_price.csv</code></td>
<td style="text-align: right;">data-driven</td>
<td><code>e_price.csv</code></td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mover><mi>p</mi><mo accent="true">‾</mo></mover><mi>s</mi></msub><mo>,</mo><msub><mi>σ</mi><msub><mi>p</mi><mi>s</mi></msub></msub></mrow></semantics></math></td>
<td>Service fee mean and std.</td>
<td>Valid observations in <code>s_price.csv</code></td>
<td style="text-align: right;">data-driven</td>
<td><code>s_price.csv</code></td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>p</mi><mi>w</mi></msub></semantics></math></td>
<td>Wholesale electricity cost</td>
<td>External Shenzhen benchmark</td>
<td style="text-align: right;">0.55</td>
<td>Shenzhen MDRC</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>C</mi><mi>f</mi></msub></semantics></math></td>
<td>Daily fixed operating cost</td>
<td>Labour, depreciation, rent benchmark</td>
<td style="text-align: right;">300</td>
<td>industry benchmark</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>c</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi></mrow></msub></semantics></math></td>
<td>Dwell-time opportunity cost</td>
<td>Time value and station resource occupation</td>
<td style="text-align: right;">0.010</td>
<td>Hopp &amp; Spearman</td>
</tr>
</tbody>
</table>
<p>Note. Monetary units are RMB. The dwell-time cost is measured in RMB per vehicle-minute in station. It is applied to total dwell time <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>W</mi></semantics></math>, not only queue waiting time <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>W</mi><mi>q</mi></msub></semantics></math>.</p>
<h3 id="assumption-justification">2.4 Assumption Justification</h3>
<p><strong>A1. Poisson arrivals.</strong> At the hourly aggregation level, EV arrivals from a large heterogeneous user base are modelled as a Poisson process. The assumption is standard for service systems with many independent customers and rare simultaneous arrivals within small intervals (Gross et al., 2018). The UrbanEV dataset is sufficiently large for an aggregate Poisson approximation, although individual inter-arrival times are not observed.</p>
<p><strong>A2. General service-time distribution and M/G/c correction.</strong> The empirical coefficient of variation is <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mi>V</mi><mo>=</mo><mn>0.365</mn><mo>&lt;</mo><mn>1</mn></mrow></semantics></math>. Service times are therefore less variable than an exponential distribution. A plain M/M/c model would overstate waiting time. The project uses M/M/c as the analytical baseline and applies the Allen-Cunneen/Lee-Longton correction factor <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo stretchy="false" form="prefix">(</mo><mn>1</mn><mo>+</mo><mi>C</mi><msup><mi>V</mi><mn>2</mn></msup><mo stretchy="false" form="postfix">)</mo><mi>/</mi><mn>2</mn></mrow></semantics></math>, which is widely used for M/G/c approximations (Hopp &amp; Spearman, 2011).</p>
<p><strong>A3. FCFS and effectively unlimited queue.</strong> Public charging stations typically serve users on a first-come-first-served basis. Physical queue space is not truly infinite, but the assumption is acceptable for steady-state analysis at moderate utilisation. It gives a slightly conservative waiting-time estimate before explicit balking behaviour is introduced (Gross et al., 2018).</p>
<p><strong>A4. Normal perturbations for price variables.</strong> Electricity price and service fee are simulated as normal perturbations around empirical means, with standard deviations set at 30% of the raw empirical standard deviation. This reflects that day-to-day operating variation is narrower than the full cross-TAZ and cross-hour spread in the dataset. Truncation keeps simulated values within operationally plausible price bounds (Glasserman, 2004).</p>
<p><strong>A5. Independent simulation days.</strong> Each Monte Carlo iteration represents an independent operating day. This simplifies the risk calculation and is common in first-stage simulation studies. It may overstate day-to-day variance if real demand has stable weekly patterns.</p>
<p><strong>A6. Total dwell-time opportunity cost.</strong> The time penalty in this project is not limited to queue waiting time. It represents the opportunity cost incurred while a vehicle remains within the station. From the operator’s perspective, both queueing and active charging occupy station space, charger capacity, and potential service opportunities. The financial model therefore uses total time in system,</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>W</mi><mo>=</mo><msub><mi>W</mi><mi>q</mi></msub><mo>+</mo><mfrac><mn>1</mn><mi>μ</mi></mfrac><mo>,</mo></mrow></semantics></math></p>
<p>rather than queue waiting time alone.</p>
<hr />
<h2 id="model-design">3. Model Design</h2>
<h3 id="end-to-end-modelling-workflow">3.1 End-to-End Modelling Workflow</h3>
<p><strong>Figure 0A. End-to-end modelling workflow.</strong><br />
<img src="../report_assets/fig_00_workflow_diagram.png" alt="End-to-end modelling workflow" /><br />
<em>Note. The workflow links data cleaning, parameter estimation, M/G/c queuing analysis, Monte Carlo simulation, and managerial sensitivity analysis.</em></p>
<h3 id="queuing-model-mgc">3.2 Queuing Model: M/G/c</h3>
<p>The station is modelled as an M/G/c queue. Arrivals follow a Poisson process with rate <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>λ</mi></semantics></math>, service time has a general empirical distribution with mean <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>1</mn><mi>/</mi><mi>μ</mi></mrow></semantics></math>, and <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>c</mi></semantics></math> chargers operate as parallel servers.</p>
<h4 id="peak-and-off-peak-time-slicing">3.2.1 Peak and Off-Peak Time Slicing</h4>
<p>Using only the all-day average arrival rate would hide peak-hour risk. The project therefore uses a scenario-based bimodal split: 50% of daily demand occurs in 4 peak hours, and the remaining 50% occurs in 20 off-peak hours. If <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>λ</mi><mrow><mi>a</mi><mi>v</mi><mi>g</mi></mrow></msub></semantics></math> is the all-day average arrival rate, then:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>λ</mi><mrow><mi>p</mi><mi>e</mi><mi>a</mi><mi>k</mi></mrow></msub><mo>=</mo><mfrac><mrow><mn>0.5</mn><mo>×</mo><mn>24</mn><mo>×</mo><msub><mi>λ</mi><mrow><mi>a</mi><mi>v</mi><mi>g</mi></mrow></msub></mrow><mn>4</mn></mfrac><mo>=</mo><mn>3</mn><msub><mi>λ</mi><mrow><mi>a</mi><mi>v</mi><mi>g</mi></mrow></msub><mo>,</mo><mspace width="2.0em"></mspace><msub><mi>λ</mi><mrow><mi>o</mi><mi>f</mi><mi>f</mi></mrow></msub><mo>=</mo><mfrac><mrow><mn>0.5</mn><mo>×</mo><mn>24</mn><mo>×</mo><msub><mi>λ</mi><mrow><mi>a</mi><mi>v</mi><mi>g</mi></mrow></msub></mrow><mn>20</mn></mfrac><mo>=</mo><mn>0.6</mn><msub><mi>λ</mi><mrow><mi>a</mi><mi>v</mi><mi>g</mi></mrow></msub><mi>.</mi></mrow></semantics></math></p>
<p>This split is a scenario assumption. It is used to avoid smoothing away peak pressure; it is not claimed to be a transaction-level estimate.</p>
<h4 id="stability-and-erlang-c-baseline">3.2.2 Stability and Erlang-C Baseline</h4>
<p>System utilisation is:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>ρ</mi><mo>=</mo><mfrac><mi>λ</mi><mrow><mi>c</mi><mi>μ</mi></mrow></mfrac><mi>.</mi></mrow></semantics></math></p>
<p>The steady-state condition is <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>ρ</mi><mo>&lt;</mo><mn>1</mn></mrow></semantics></math>. At the all-day baseline, <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>λ</mi><mo>=</mo><mn>3.0682</mn></mrow></semantics></math>, <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>c</mi><mo>=</mo><mn>13</mn></mrow></semantics></math>, and <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>μ</mi><mo>=</mo><mn>1.3815</mn></mrow></semantics></math>, so:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>ρ</mi><mo>=</mo><mfrac><mn>3.0682</mn><mrow><mn>13</mn><mo>×</mo><mn>1.3815</mn></mrow></mfrac><mo>=</mo><mn>0.1709</mn><mi>.</mi></mrow></semantics></math></p>
<p>The Erlang-C probability that an arriving vehicle must wait is:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mo stretchy="false" form="prefix">(</mo><mi>c</mi><mo>,</mo><mi>ρ</mi><mo stretchy="false" form="postfix">)</mo><mo>=</mo><mfrac><mrow><mfrac><mrow><mo stretchy="false" form="prefix">(</mo><mi>c</mi><mi>ρ</mi><msup><mo stretchy="false" form="postfix">)</mo><mi>c</mi></msup></mrow><mrow><mi>c</mi><mi>!</mi></mrow></mfrac><mfrac><mn>1</mn><mrow><mn>1</mn><mo>−</mo><mi>ρ</mi></mrow></mfrac></mrow><mrow><munderover><mo>∑</mo><mrow><mi>n</mi><mo>=</mo><mn>0</mn></mrow><mrow><mi>c</mi><mo>−</mo><mn>1</mn></mrow></munderover><mfrac><mrow><mo stretchy="false" form="prefix">(</mo><mi>c</mi><mi>ρ</mi><msup><mo stretchy="false" form="postfix">)</mo><mi>n</mi></msup></mrow><mrow><mi>n</mi><mi>!</mi></mrow></mfrac><mo>+</mo><mfrac><mrow><mo stretchy="false" form="prefix">(</mo><mi>c</mi><mi>ρ</mi><msup><mo stretchy="false" form="postfix">)</mo><mi>c</mi></msup></mrow><mrow><mi>c</mi><mi>!</mi></mrow></mfrac><mfrac><mn>1</mn><mrow><mn>1</mn><mo>−</mo><mi>ρ</mi></mrow></mfrac></mrow></mfrac><mi>.</mi></mrow></semantics></math></p>
<p>For M/M/c, the queue waiting time is:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>M</mi><mi>/</mi><mi>c</mi></mrow></msubsup><mo>=</mo><mfrac><mrow><mi>C</mi><mo stretchy="false" form="prefix">(</mo><mi>c</mi><mo>,</mo><mi>ρ</mi><mo stretchy="false" form="postfix">)</mo></mrow><mrow><mi>c</mi><mi>μ</mi><mo stretchy="false" form="prefix">(</mo><mn>1</mn><mo>−</mo><mi>ρ</mi><mo stretchy="false" form="postfix">)</mo></mrow></mfrac><mi>.</mi></mrow></semantics></math></p>
<h4 id="mgc-correction-and-dwell-time">3.2.3 M/G/c Correction and Dwell Time</h4>
<p>Because service duration is not exponential, the M/M/c waiting time is corrected as:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msubsup><mo>≈</mo><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>M</mi><mi>/</mi><mi>c</mi></mrow></msubsup><mo>×</mo><mfrac><mrow><mn>1</mn><mo>+</mo><mi>C</mi><msup><mi>V</mi><mn>2</mn></msup></mrow><mn>2</mn></mfrac><mi>.</mi></mrow></semantics></math></p>
<p>With <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mi>V</mi><mo>=</mo><mn>0.365</mn></mrow></semantics></math>, the correction factor is:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mfrac><mrow><mn>1</mn><mo>+</mo><msup><mn>0.365</mn><mn>2</mn></msup></mrow><mn>2</mn></mfrac><mo>=</mo><mn>0.5666</mn><mi>.</mi></mrow></semantics></math></p>
<p>The total dwell time used in the profit model is:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msup><mi>W</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msup><mo>=</mo><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msubsup><mo>+</mo><mfrac><mn>1</mn><mi>μ</mi></mfrac><mi>.</mi></mrow></semantics></math></p>
<p>Queue length is computed by Little’s Law:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>L</mi><mi>q</mi></msub><mo>=</mo><mi>λ</mi><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msubsup><mi>.</mi></mrow></semantics></math></p>
<p><strong>Table 3.1. Queuing model outputs and managerial use.</strong></p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th>Metric</th>
<th>Formula</th>
<th>Managerial interpretation</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>ρ</mi></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>λ</mi><mi>/</mi><mo stretchy="false" form="prefix">(</mo><mi>c</mi><mi>μ</mi><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math></td>
<td>Capacity utilisation and expansion signal</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>P</mi><mo stretchy="false" form="prefix">(</mo><mtext mathvariant="normal">wait</mtext><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mo stretchy="false" form="prefix">(</mo><mi>c</mi><mo>,</mo><mi>ρ</mi><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math></td>
<td>Probability that an arriving vehicle waits</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msubsup></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>M</mi><mi>/</mi><mi>c</mi></mrow></msubsup><mo stretchy="false" form="prefix">(</mo><mn>1</mn><mo>+</mo><mi>C</mi><msup><mi>V</mi><mn>2</mn></msup><mo stretchy="false" form="postfix">)</mo><mi>/</mi><mn>2</mn></mrow></semantics></math></td>
<td>Pure congestion delay and service quality</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msup><mi>W</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msup></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msubsup><mo>+</mo><mn>1</mn><mi>/</mi><mi>μ</mi></mrow></semantics></math></td>
<td>Total station resource occupation; used in profit penalty</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>L</mi><mi>q</mi></msub></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>λ</mi><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msubsup></mrow></semantics></math></td>
<td>Expected queue length and space planning input</td>
</tr>
</tbody>
</table>
<h3 id="monte-carlo-profit-risk-model">3.3 Monte Carlo Profit-Risk Model</h3>
<p>The Monte Carlo model uses <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>n</mi><mo>=</mo><mn>1000</mn></mrow></semantics></math> iterations. A fixed random seed, <code>numpy.random.default_rng(seed=42)</code>, ensures reproducibility.</p>
<p><strong>Table 3.2. Random variables used in Monte Carlo simulation.</strong></p>
<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr class="header">
<th>Variable</th>
<th>Symbol</th>
<th>Distribution</th>
<th>Justification</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Peak sessions</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>N</mi><mrow><mi>p</mi><mi>e</mi><mi>a</mi><mi>k</mi><mo>,</mo><mi>i</mi></mrow></msub></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mtext mathvariant="normal">Poisson</mtext><mo stretchy="false" form="prefix">(</mo><msub><mi>λ</mi><mrow><mi>p</mi><mi>e</mi><mi>a</mi><mi>k</mi></mrow></msub><mo>×</mo><mn>4</mn><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math></td>
<td>Count arrivals in peak window</td>
</tr>
<tr class="even">
<td>Off-peak sessions</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>N</mi><mrow><mi>o</mi><mi>f</mi><mi>f</mi><mo>,</mo><mi>i</mi></mrow></msub></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mtext mathvariant="normal">Poisson</mtext><mo stretchy="false" form="prefix">(</mo><msub><mi>λ</mi><mrow><mi>o</mi><mi>f</mi><mi>f</mi></mrow></msub><mo>×</mo><mn>20</mn><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math></td>
<td>Count arrivals in off-peak window</td>
</tr>
<tr class="odd">
<td>kWh per session</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>Q</mi><mi>i</mi></msub></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mstyle mathvariant="script"><mi>𝒩</mi></mstyle><mo stretchy="false" form="prefix">(</mo><mover><mi>Q</mi><mo accent="true">‾</mo></mover><mo>,</mo><msubsup><mi>σ</mi><mi>Q</mi><mn>2</mn></msubsup><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math>, clipped to <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo stretchy="false" form="prefix">[</mo><mn>1</mn><mo>,</mo><mn>50</mn><mo stretchy="false" form="postfix">]</mo></mrow></semantics></math></td>
<td>Empirical energy distribution with physical bounds</td>
</tr>
<tr class="even">
<td>Electricity price</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>p</mi><mrow><mi>e</mi><mo>,</mo><mi>i</mi></mrow></msub></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mstyle mathvariant="script"><mi>𝒩</mi></mstyle><mo stretchy="false" form="prefix">(</mo><msub><mover><mi>p</mi><mo accent="true">‾</mo></mover><mi>e</mi></msub><mo>,</mo><mo stretchy="false" form="prefix">(</mo><mn>0.3</mn><msub><mi>σ</mi><msub><mi>p</mi><mi>e</mi></msub></msub><msup><mo stretchy="false" form="postfix">)</mo><mn>2</mn></msup><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math>, clipped</td>
<td>Short-run price fluctuation</td>
</tr>
<tr class="odd">
<td>Service fee</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>p</mi><mrow><mi>s</mi><mo>,</mo><mi>i</mi></mrow></msub></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mstyle mathvariant="script"><mi>𝒩</mi></mstyle><mo stretchy="false" form="prefix">(</mo><msub><mover><mi>p</mi><mo accent="true">‾</mo></mover><mi>s</mi></msub><mo stretchy="false" form="prefix">(</mo><mn>1</mn><mo>+</mo><msub><mi>δ</mi><mi>s</mi></msub><mo stretchy="false" form="postfix">)</mo><mo>,</mo><mo stretchy="false" form="prefix">(</mo><mn>0.3</mn><msub><mi>σ</mi><msub><mi>p</mi><mi>s</mi></msub></msub><msup><mo stretchy="false" form="postfix">)</mo><mn>2</mn></msup><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math>, clipped</td>
<td>Operator-controlled fee scenario</td>
</tr>
<tr class="even">
<td>Wholesale cost</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>p</mi><mrow><mi>w</mi><mo>,</mo><mi>i</mi></mrow></msub></semantics></math></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mstyle mathvariant="script"><mi>𝒩</mi></mstyle><mo stretchy="false" form="prefix">(</mo><msub><mi>p</mi><mi>w</mi></msub><mo stretchy="false" form="prefix">(</mo><mn>1</mn><mo>+</mo><msub><mi>δ</mi><mi>w</mi></msub><mo stretchy="false" form="postfix">)</mo><mo>,</mo><mo stretchy="false" form="prefix">(</mo><mn>0.05</mn><msub><mi>p</mi><mi>w</mi></msub><msup><mo stretchy="false" form="postfix">)</mo><mn>2</mn></msup><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math></td>
<td>Short-run procurement cost risk</td>
</tr>
</tbody>
</table>
<p>Base profit in iteration <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>i</mi></semantics></math> is:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>Π</mi><mi>i</mi><mrow><mi>b</mi><mi>a</mi><mi>s</mi><mi>e</mi></mrow></msubsup><mo>=</mo><mo stretchy="false" form="prefix">(</mo><msub><mi>N</mi><mrow><mi>p</mi><mi>e</mi><mi>a</mi><mi>k</mi><mo>,</mo><mi>i</mi></mrow></msub><mo>+</mo><msub><mi>N</mi><mrow><mi>o</mi><mi>f</mi><mi>f</mi><mo>,</mo><mi>i</mi></mrow></msub><mo stretchy="false" form="postfix">)</mo><msub><mi>Q</mi><mi>i</mi></msub><mo stretchy="false" form="prefix">(</mo><msub><mi>p</mi><mrow><mi>e</mi><mo>,</mo><mi>i</mi></mrow></msub><mo>+</mo><msub><mi>p</mi><mrow><mi>s</mi><mo>,</mo><mi>i</mi></mrow></msub><mo stretchy="false" form="postfix">)</mo><mo>−</mo><mo stretchy="false" form="prefix">(</mo><msub><mi>N</mi><mrow><mi>p</mi><mi>e</mi><mi>a</mi><mi>k</mi><mo>,</mo><mi>i</mi></mrow></msub><mo>+</mo><msub><mi>N</mi><mrow><mi>o</mi><mi>f</mi><mi>f</mi><mo>,</mo><mi>i</mi></mrow></msub><mo stretchy="false" form="postfix">)</mo><msub><mi>Q</mi><mi>i</mi></msub><msub><mi>p</mi><mrow><mi>w</mi><mo>,</mo><mi>i</mi></mrow></msub><mo>−</mo><msub><mi>C</mi><mi>f</mi></msub><mi>.</mi></mrow></semantics></math></p>
<p>The queuing model enters through the dwell-time opportunity cost:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>Π</mi><mi>i</mi></msub><mo>=</mo><msubsup><mi>Π</mi><mi>i</mi><mrow><mi>b</mi><mi>a</mi><mi>s</mi><mi>e</mi></mrow></msubsup><mo>−</mo><msub><mi>N</mi><mrow><mi>p</mi><mi>e</mi><mi>a</mi><mi>k</mi><mo>,</mo><mi>i</mi></mrow></msub><msub><mi>W</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi><mo>,</mo><mi>p</mi><mi>e</mi><mi>a</mi><mi>k</mi></mrow></msub><msub><mi>c</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi></mrow></msub><mo>−</mo><msub><mi>N</mi><mrow><mi>o</mi><mi>f</mi><mi>f</mi><mo>,</mo><mi>i</mi></mrow></msub><msub><mi>W</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi><mo>,</mo><mi>o</mi><mi>f</mi><mi>f</mi></mrow></msub><msub><mi>c</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi></mrow></msub><mi>.</mi></mrow></semantics></math></p>
<p>Here <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>W</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi><mo>,</mo><mi>p</mi><mi>e</mi><mi>a</mi><mi>k</mi></mrow></msub></semantics></math> and <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>W</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi><mo>,</mo><mi>o</mi><mi>f</mi><mi>f</mi></mrow></msub></semantics></math> include both queue waiting and active charging time. This equation is the main analytical bridge between the two technical streams.</p>
<h3 id="risk-metrics">3.4 Risk Metrics</h3>
<p>The simulation reports expected profit <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>E</mi><mo stretchy="false" form="prefix">[</mo><mi>Π</mi><mo stretchy="false" form="postfix">]</mo></mrow></semantics></math>, standard deviation <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>σ</mi><mo stretchy="false" form="prefix">[</mo><mi>Π</mi><mo stretchy="false" form="postfix">]</mo></mrow></semantics></math>, probability of loss <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>P</mi><mo stretchy="false" form="prefix">(</mo><mi>Π</mi><mo>&lt;</mo><mn>0</mn><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math>, 5% VaR, 5% CVaR, and distribution percentiles. VaR is the 5th percentile of simulated profit:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>V</mi><mi>a</mi><msub><mi>R</mi><mrow><mn>5</mn><mi>%</mi></mrow></msub><mo>=</mo><mo>inf</mo><mo stretchy="false" form="prefix">{</mo><mi>x</mi><mo>:</mo><mi>P</mi><mo stretchy="false" form="prefix">(</mo><mi>Π</mi><mo>≤</mo><mi>x</mi><mo stretchy="false" form="postfix">)</mo><mo>≥</mo><mn>0.05</mn><mo stretchy="false" form="postfix">}</mo><mi>.</mi></mrow></semantics></math></p>
<p>CVaR is the mean outcome in the worst 5% of simulation runs:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mi>V</mi><mi>a</mi><msub><mi>R</mi><mrow><mn>5</mn><mi>%</mi></mrow></msub><mo>=</mo><mi>E</mi><mo stretchy="false" form="prefix">[</mo><mi>Π</mi><mo>∣</mo><mi>Π</mi><mo>≤</mo><mi>V</mi><mi>a</mi><msub><mi>R</mi><mrow><mn>5</mn><mi>%</mi></mrow></msub><mo stretchy="false" form="postfix">]</mo><mi>.</mi></mrow></semantics></math></p>
<hr />
<h2 id="results-and-analysis">4. Results and Analysis</h2>
<h3 id="descriptive-results">4.1 Descriptive Results</h3>
<p><strong>Figure 1. Distribution of charging piles per station.</strong><br />
<img src="../report_assets/fig_01_charge_count_distribution.png" alt="Charging pile distribution" /><br />
<em>Note. The red dashed line marks the mean charger count used as the representative server count, <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>c</mi><mo>=</mo><mn>13</mn></mrow></semantics></math>.</em></p>
<p>The charger-count distribution is right-skewed. The mean of 13 chargers is suitable for a representative station, but it should not be read as a universal station profile. Smaller stations face higher utilisation at the same arrival rate.</p>
<p><strong>Table 4.1. Capacity interpretation scenarios.</strong></p>
<table>
<thead>
<tr class="header">
<th>Scenario</th>
<th style="text-align: right;">Chargers <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>c</mi></semantics></math></th>
<th>Meaning</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Small station</td>
<td style="text-align: right;">6</td>
<td>Smaller site with higher congestion exposure</td>
</tr>
<tr class="even">
<td>Base station</td>
<td style="text-align: right;">13</td>
<td>Average-sized site used as the main model baseline</td>
</tr>
<tr class="odd">
<td>Large station</td>
<td style="text-align: right;">25</td>
<td>Larger site with more capacity headroom</td>
</tr>
</tbody>
</table>
<p><strong>Figure 2. Empirical service duration distribution versus exponential benchmark.</strong><br />
<img src="../report_assets/fig_02_service_duration_distribution.png" alt="Service duration distribution" /><br />
<em>Note. The empirical service-time distribution is calculated from cleaned <code>duration.csv / occupancy.csv</code>. The empirical <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mi>V</mi><mo>=</mo><mn>0.365</mn></mrow></semantics></math>, below the exponential benchmark <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mi>V</mi><mo>=</mo><mn>1</mn></mrow></semantics></math>.</em></p>
<p>The service-time distribution is more concentrated than an exponential distribution. This supports the M/G/c correction. Using a plain M/M/c result would overstate queue waiting time by treating service duration as more volatile than it is in the data.</p>
<h3 id="queuing-performance">4.2 Queuing Performance</h3>
<p><strong>Table 4.2. Baseline queuing performance under peak/off-peak split.</strong></p>
<table>
<colgroup>
<col style="width: 21%" />
<col style="width: 28%" />
<col style="width: 28%" />
<col style="width: 21%" />
</colgroup>
<thead>
<tr class="header">
<th>Metric</th>
<th style="text-align: right;">Peak 4h</th>
<th style="text-align: right;">Off-peak 20h</th>
<th>Managerial interpretation</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>λ</mi></semantics></math> (sessions/hour)</td>
<td style="text-align: right;">9.2047</td>
<td style="text-align: right;">1.8409</td>
<td>50%-50% demand split across peak/off-peak windows</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>ρ</mi></semantics></math></td>
<td style="text-align: right;">0.5125</td>
<td style="text-align: right;">0.1025</td>
<td>Peak utilisation is materially higher</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>P</mi><mo stretchy="false" form="prefix">(</mo><mtext mathvariant="normal">wait</mtext><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math></td>
<td style="text-align: right;">2.14%</td>
<td style="text-align: right;"><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo>≈</mo><mn>0</mn></mrow></semantics></math></td>
<td>Waiting risk is concentrated in peak hours</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>M</mi><mi>/</mi><mi>c</mi></mrow></msubsup></semantics></math> (minutes)</td>
<td style="text-align: right;">0.1468</td>
<td style="text-align: right;"><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo>≈</mo><mn>0</mn></mrow></semantics></math></td>
<td>M/M/c baseline before service-time correction</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msubsup></semantics></math> (minutes)</td>
<td style="text-align: right;">0.0832</td>
<td style="text-align: right;"><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo>≈</mo><mn>0</mn></mrow></semantics></math></td>
<td>Corrected pure queue delay</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msup><mi>W</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msup></semantics></math> (minutes)</td>
<td style="text-align: right;">43.52</td>
<td style="text-align: right;">43.43</td>
<td>Total dwell time is dominated by charging service</td>
</tr>
<tr class="odd">
<td>Sessions per day segment</td>
<td style="text-align: right;">36.82</td>
<td style="text-align: right;">36.82</td>
<td>Equal daily volume, unequal hourly pressure</td>
</tr>
</tbody>
</table>
<p>The all-day average utilisation is only <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>ρ</mi><mrow><mi>a</mi><mi>v</mi><mi>g</mi></mrow></msub><mo>=</mo><mn>0.1709</mn></mrow></semantics></math>, but this average is misleading for operations. The peak-hour utilisation reaches 0.5125 and waiting probability rises to 2.14%. The estimated pure queue waiting time remains short at baseline, but the total dwell time is about 43.5 minutes because active charging time is the dominant component.</p>
<p>This distinction matters. <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>W</mi><mi>q</mi></msub></semantics></math> measures the customer queueing experience. <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>W</mi></semantics></math> measures how long a vehicle occupies station resources. Since this project studies operator profitability, the Monte Carlo model uses <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>W</mi></semantics></math> for the time-cost deduction.</p>
<h3 id="monte-carlo-profit-risk-distribution">4.3 Monte Carlo Profit-Risk Distribution</h3>
<p><strong>Figure 3. Daily net profit distribution with VaR and CVaR.</strong><br />
<img src="../report_assets/fig_03_profit_distribution_var_cvar.png" alt="Profit distribution with VaR and CVaR" /><br />
<em>Note. The histogram is based on 1,000 Monte Carlo iterations. Vertical reference lines identify <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>V</mi><mi>a</mi><msub><mi>R</mi><mrow><mn>5</mn><mi>%</mi></mrow></msub></mrow></semantics></math> and <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mi>V</mi><mi>a</mi><msub><mi>R</mi><mrow><mn>5</mn><mi>%</mi></mrow></msub></mrow></semantics></math>.</em></p>
<p><strong>Table 4.3. Monte Carlo risk metrics.</strong></p>
<table>
<colgroup>
<col style="width: 30%" />
<col style="width: 40%" />
<col style="width: 30%" />
</colgroup>
<thead>
<tr class="header">
<th>Metric</th>
<th style="text-align: right;">Value</th>
<th>Business interpretation</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>E</mi><mo stretchy="false" form="prefix">[</mo><mi>Π</mi><mo stretchy="false" form="postfix">]</mo></mrow></semantics></math></td>
<td style="text-align: right;">86.42 RMB/day</td>
<td>Positive expected daily profit</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>σ</mi><mo stretchy="false" form="prefix">[</mo><mi>Π</mi><mo stretchy="false" form="postfix">]</mo></mrow></semantics></math></td>
<td style="text-align: right;">198.75 RMB/day</td>
<td>Large day-to-day earnings volatility</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mtext mathvariant="normal">VaR</mtext><mrow><mn>5</mn><mi>%</mi></mrow></msub></semantics></math></td>
<td style="text-align: right;">-210.35 RMB</td>
<td>Worst 5% cash-flow planning threshold</td>
</tr>
<tr class="even">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mtext mathvariant="normal">CVaR</mtext><mrow><mn>5</mn><mi>%</mi></mrow></msub></semantics></math></td>
<td style="text-align: right;">-221.81 RMB</td>
<td>Average profit in the worst 5% of days</td>
</tr>
<tr class="odd">
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>P</mi><mo stretchy="false" form="prefix">(</mo><mi>Π</mi><mo>&lt;</mo><mn>0</mn><mo stretchy="false" form="postfix">)</mo></mrow></semantics></math></td>
<td style="text-align: right;">37.1%</td>
<td>More than one-third of days are loss-making</td>
</tr>
<tr class="even">
<td>Median profit</td>
<td style="text-align: right;">68.84 RMB/day</td>
<td>Typical day is below mean profit</td>
</tr>
<tr class="odd">
<td>95th percentile</td>
<td style="text-align: right;">436.22 RMB/day</td>
<td>Upside potential under favourable demand and price</td>
</tr>
</tbody>
</table>
<p>The expected daily profit is positive, but the business is not low-risk. The probability of loss is 37.1%, and the worst 5% of days produce losses of about 210 to 222 RMB. This is operationally meaningful because the fixed daily cost is 300 RMB; on very low-volume days, fixed cost quickly dominates margin.</p>
<p>The profit distribution is right-skewed. Upside comes from high-volume days, while the left tail is shaped by weak demand and wholesale cost pressure. For a station operator, the practical implication is that average profit alone is a poor decision metric. Cash reserves and pricing rules should be designed around the left tail.</p>
<h3 id="integration-dwell-time-opportunity-cost-as-a-profit-driver">4.4 Integration: Dwell-Time Opportunity Cost as a Profit Driver</h3>
<p><strong>Figure 4. Queuing performance sensitivity curve.</strong><br />
<img src="../report_assets/fig_04_queue_sensitivity_curve.png" alt="Queuing sensitivity curve" /><br />
<em>Note. The curve shows M/G/c queue waiting time and utilisation as demand increases relative to baseline <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>λ</mi></semantics></math>. The red reference line marks <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>ρ</mi><mo>=</mo><mn>0.8</mn></mrow></semantics></math>, a practical congestion warning threshold.</em></p>
<p>The integrated result is straightforward: dwell time is a financial input, not only a service-quality metric. The queuing model provides <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>W</mi><mi>q</mi></msub></semantics></math> for congestion interpretation and <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>W</mi><mo>=</mo><msub><mi>W</mi><mi>q</mi></msub><mo>+</mo><mn>1</mn><mi>/</mi><mi>μ</mi></mrow></semantics></math> for station resource occupation. The Monte Carlo model subtracts the corresponding dwell-time cost in each simulation run.</p>
<p>This design also changes the managerial interpretation of congestion. At baseline, queue waiting time is short, so customer delay is not yet severe. However, total dwell time remains a stable opportunity cost because every vehicle occupies space and charger capacity while charging. When demand grows, the nonlinear rise in <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>W</mi><mi>q</mi></msub></semantics></math> adds to that baseline dwell burden.</p>
<hr />
<h2 id="sensitivity-analysis">5. Sensitivity Analysis</h2>
<h3 id="tornado-chart-sensitivity">5.1 Tornado Chart Sensitivity</h3>
<p><strong>Figure 5. Tornado chart: impact of input parameters on expected daily profit.</strong><br />
<img src="../report_assets/fig_05_tornado_sensitivity.png" alt="Tornado sensitivity chart" /><br />
<em>Note. Each pair of bars shows the change in expected daily profit under a <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo>+</mo><mn>20</mn><mi>%</mi></mrow></semantics></math> and <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo>−</mo><mn>20</mn><mi>%</mi></mrow></semantics></math> shock. Parameters are sorted by total swing.</em></p>
<p>The tornado chart identifies demand as the strongest profit driver. A 20% increase in arrival rate raises expected profit through higher transaction volume, while a 20% decline can push the representative station close to break-even. Energy per session and fixed cost are also important because they directly scale gross margin and daily operating burden.</p>
<p>Service fee deserves attention even if it is not the single largest bar. It is the most controllable revenue lever. A station operator can adjust service fees by time of day, local competition, and utilisation. Wholesale electricity cost is less controllable, but it matters for downside protection because margin compression is hard to pass through immediately.</p>
<p>The dwell-time cost multiplier <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>c</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi></mrow></msub></semantics></math> has a modest average effect at baseline utilisation. Its importance rises sharply in high-demand scenarios. This is typical of queuing systems: the financial impact of congestion is small until utilisation approaches the nonlinear region.</p>
<p><strong>Table 5.1. Managerial classification of sensitivity factors.</strong></p>
<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr class="header">
<th>Category</th>
<th>Parameters</th>
<th>Managerial response</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Controllable</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>p</mi><mi>s</mi></msub></semantics></math>, <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>c</mi></semantics></math>, <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>c</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi></mrow></msub></semantics></math> mitigation</td>
<td>Dynamic pricing, capacity investment, queue management</td>
</tr>
<tr class="even">
<td>Partly controllable</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mi>λ</mi></semantics></math></td>
<td>Demand shaping through off-peak promotion</td>
</tr>
<tr class="odd">
<td>Mostly uncontrollable</td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>p</mi><mi>w</mi></msub></semantics></math>, <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>p</mi><mi>e</mi></msub></semantics></math></td>
<td>Hedging, procurement contracts, tariff monitoring</td>
</tr>
</tbody>
</table>
<h3 id="dwell-time-penalty-response-under-demand-growth">5.2 Dwell-Time Penalty Response under Demand Growth</h3>
<p><strong>Figure 6. Dwell-time penalty response under increasing demand.</strong><br />
<img src="../report_assets/fig_06_dwell_penalty_response.png" alt="Dwell-time penalty response curve" /><br />
<em>Note. The penalty is calculated from total dwell time <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>W</mi><mo>=</mo><msub><mi>W</mi><mi>q</mi></msub><mo>+</mo><mn>1</mn><mi>/</mi><mi>μ</mi></mrow></semantics></math>. The three curves correspond to <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msub><mi>c</mi><mrow><mi>d</mi><mi>w</mi><mi>e</mi><mi>l</mi><mi>l</mi></mrow></msub><mo>=</mo><mn>0.005</mn></mrow></semantics></math>, <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mn>0.010</mn></semantics></math>, and <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mn>0.020</mn></semantics></math> RMB per vehicle-minute.</em></p>
<p>At low and moderate utilisation, the dwell-time penalty grows smoothly because it is mainly driven by the stable charging service time. Once utilisation approaches roughly 0.6 to 0.8, queue waiting time begins to increase much faster. The operator then faces a congestion cliff: each additional unit of demand adds more than proportional station occupation cost.</p>
<p>This result supports preventive capacity planning. Adding chargers after the station has already crossed the congestion cliff is less attractive because users may already have shifted to nearby stations, and installation lead times can be four to eight weeks. A better rule is to trigger capacity review before the cliff, for example when rolling peak-hour utilisation exceeds 0.5.</p>
<hr />
<h2 id="conclusion-and-recommendations">6. Conclusion and Recommendations</h2>
<h3 id="key-findings">6.1 Key Findings</h3>
<p>The Monte Carlo analysis shows that the representative Shenzhen station is profitable on average, with expected daily profit of 86.42 RMB. The risk profile is still fragile. The loss probability is 37.1%, and <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mi>V</mi><mi>a</mi><msub><mi>R</mi><mrow><mn>5</mn><mi>%</mi></mrow></msub></mrow></semantics></math> is <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mo>−</mo><mn>221.81</mn></mrow></semantics></math> RMB. The operator should therefore manage the station as a cash-flow risk problem, not only a revenue growth problem.</p>
<p>The queuing analysis shows that average utilisation is low, but peak-period pressure is much higher. At baseline, <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><msub><mi>W</mi><mi>q</mi></msub></semantics></math> is short and customer waiting is not yet severe. Total dwell time is still about 43.5 minutes because charging itself occupies station resources. Under demand growth, queue waiting time rises nonlinearly and amplifies the dwell-time opportunity cost.</p>
<h3 id="managerial-recommendations">6.2 Managerial Recommendations</h3>
<p><strong>Recommendation 1: Use congestion-based dynamic service fees.</strong><br />
When historical peak-hour utilisation exceeds <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>ρ</mi><mo>=</mo><mn>0.5</mn></mrow></semantics></math>, the operator should introduce a 15% to 25% peak-hour service fee premium. This raises revenue during high-demand windows and nudges flexible users toward off-peak hours. The expected benefit is both financial and operational: higher average revenue, lower tail-risk exposure, and reduced probability of entering the nonlinear congestion region.</p>
<p><strong>Recommendation 2: Adopt a preventive capacity expansion trigger.</strong><br />
The operator should monitor rolling 30-day peak-hour utilisation. When <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>ρ</mi><mo>&gt;</mo><mn>0.5</mn></mrow></semantics></math> persists, management should start procurement and site planning for additional chargers. This threshold is deliberately below the <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>ρ</mi><mo>=</mo><mn>0.8</mn></mrow></semantics></math> congestion warning line because installation lead times are not immediate. Waiting until the station is visibly congested makes the investment late.</p>
<p><strong>Recommendation 3: Hedge wholesale electricity cost for downside protection.</strong><br />
Wholesale cost is not fully controllable, but it can be managed. The operator should negotiate medium-term fixed or capped-price electricity contracts for 50% to 60% of expected monthly consumption. The remaining volume can stay exposed to spot prices to preserve some upside. This protects the left tail of the profit distribution without fully locking the operator into an unfavourable tariff.</p>
<h3 id="limitations-and-future-extensions">6.3 Limitations and Future Extensions</h3>
<p>This study has several boundaries. First, the UrbanEV time-series data are hourly TAZ aggregates, not individual charging sessions. Exact inter-arrival times, service completions, and customer balking cannot be observed. Second, the conversion from TAZ-level indicators to representative station parameters means the results should be read as average-station risk estimates. A small site with six chargers may face a much sharper queue response than the base station. Third, the 50%-50% peak/off-peak split is a scenario design used to expose peak pressure. It should be recalibrated with hour-level occupancy or transaction data if those data become available. Fourth, the Monte Carlo model treats operating days as independent, so weekday patterns and seasonal autocorrelation are not modelled.</p>
<p>Future work should extend the model in three directions. A discrete-event simulation with event-level data would improve arrival and service-time modelling. A station-specific version would support site-level investment decisions. A richer behavioural model could add balking or switching to nearby stations when expected waiting time becomes too high.</p>
<hr />
<h2 id="references">References</h2>
<p>Glasserman, P. (2004). <em>Monte Carlo methods in financial engineering</em>. Springer. https://doi.org/10.1007/978-0-387-21617-1</p>
<p>Gross, D., Shortle, J. F., Thompson, J. M., &amp; Harris, C. M. (2018). <em>Fundamentals of queueing theory</em> (5th ed.). Wiley.</p>
<p>Hopp, W. J., &amp; Spearman, M. L. (2011). <em>Factory physics</em> (3rd ed.). Waveland Press.</p>
<p>Mao, H., Feng, Y., Wu, J., Dong, J., &amp; Zheng, Y. (2024). UrbanEV: A multi-source dataset for public EV charging operations in Shenzhen. <em>Scientific Data</em>, <em>11</em>, 312. https://doi.org/10.1038/s41597-024-03150-7</p>
<p>National Energy Administration. (2024). <em>2023 annual report on electric vehicle charging infrastructure development in China</em>. National Energy Administration. https://www.nea.gov.cn</p>
<p>Shenzhen Municipal Development and Reform Commission. (2023). <em>Notice on adjusting industrial and commercial electricity prices in Shenzhen</em>. Shenzhen Municipal Development and Reform Commission.</p>
<hr />
<h2 id="appendix">Appendix</h2>
<h3 id="appendix-a.-source-code-structure">Appendix A. Source Code Structure</h3>
<p><strong>Table A1. Source code structure.</strong></p>
<table>
<thead>
<tr class="header">
<th>File</th>
<th>Location</th>
<th>Function</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><code>data_processor.py</code></td>
<td><code>backend/</code></td>
<td>Data cleaning, parameter estimation, caching</td>
</tr>
<tr class="even">
<td><code>queuing_model.py</code></td>
<td><code>backend/</code></td>
<td>M/M/c baseline and M/G/c correction</td>
</tr>
<tr class="odd">
<td><code>monte_carlo.py</code></td>
<td><code>backend/</code></td>
<td>1,000-iteration Monte Carlo profit engine</td>
</tr>
<tr class="even">
<td><code>schemas.py</code></td>
<td><code>backend/</code></td>
<td>Pydantic request and response validation</td>
</tr>
<tr class="odd">
<td><code>main.py</code></td>
<td><code>backend/</code></td>
<td>FastAPI server and simulation endpoint</td>
</tr>
<tr class="even">
<td><code>visualization.py</code></td>
<td>root</td>
<td>Report figures and descriptive statistics</td>
</tr>
</tbody>
</table>
<h3 id="appendix-b.-data-files">Appendix B. Data Files</h3>
<p><strong>Table A2. Data files used for replication.</strong></p>
<table>
<thead>
<tr class="header">
<th>File</th>
<th>Location</th>
<th>Rows/Columns</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><code>inf.csv</code></td>
<td><code>data/</code></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>1</mn><mo>,</mo><mn>362</mn><mo>×</mo></mrow></semantics></math> multiple</td>
<td>Station metadata</td>
</tr>
<tr class="even">
<td><code>duration.csv</code></td>
<td><code>data/</code></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>4</mn><mo>,</mo><mn>344</mn><mo>×</mo><mn>275</mn></mrow></semantics></math></td>
<td>Hourly charging duration by TAZ</td>
</tr>
<tr class="odd">
<td><code>occupancy.csv</code></td>
<td><code>data/</code></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>4</mn><mo>,</mo><mn>344</mn><mo>×</mo><mn>275</mn></mrow></semantics></math></td>
<td>Hourly concurrent sessions by TAZ</td>
</tr>
<tr class="even">
<td><code>volume-11kW.csv</code></td>
<td><code>data/</code></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>4</mn><mo>,</mo><mn>344</mn><mo>×</mo><mn>275</mn></mrow></semantics></math></td>
<td>Hourly energy volume by TAZ</td>
</tr>
<tr class="odd">
<td><code>e_price.csv</code></td>
<td><code>data/</code></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>4</mn><mo>,</mo><mn>344</mn><mo>×</mo><mn>275</mn></mrow></semantics></math></td>
<td>Hourly electricity price by TAZ</td>
</tr>
<tr class="even">
<td><code>s_price.csv</code></td>
<td><code>data/</code></td>
<td><math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mn>4</mn><mo>,</mo><mn>344</mn><mo>×</mo><mn>275</mn></mrow></semantics></math></td>
<td>Hourly service fee by TAZ</td>
</tr>
</tbody>
</table>
<h3 id="appendix-c.-replication-steps">Appendix C. Replication Steps</h3>
<ol type="1">
<li>Install dependencies with <code>pip install -r backend/requirements.txt</code>.</li>
<li>Generate the figures with <code>python visualization.py</code>.</li>
<li>Start the API and frontend with <code>bash start.sh</code>.</li>
<li>Reproduce Monte Carlo results using <code>numpy.random.default_rng(seed=42)</code>.</li>
</ol>
<h3 id="appendix-d.-mgc-correction">Appendix D. M/G/c Correction</h3>
<p>The M/G/c correction used in the report is:</p>
<p><math display="block" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>G</mi><mi>/</mi><mi>c</mi></mrow></msubsup><mo>≈</mo><msubsup><mi>W</mi><mi>q</mi><mrow><mi>M</mi><mi>/</mi><mi>M</mi><mi>/</mi><mi>c</mi></mrow></msubsup><mo>×</mo><mfrac><mrow><mn>1</mn><mo>+</mo><mi>C</mi><msup><mi>V</mi><mn>2</mn></msup></mrow><mn>2</mn></mfrac><mi>.</mi></mrow></semantics></math></p>
<p>For this dataset, <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>C</mi><mi>V</mi><mo>=</mo><mn>0.365</mn></mrow></semantics></math>, so the correction factor is <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mn>0.5666</mn></semantics></math>. Since baseline utilisation is well below one and the representative station has <math display="inline" xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><mi>c</mi><mo>=</mo><mn>13</mn></mrow></semantics></math> chargers, the approximation is suitable for a course-level steady-state queuing analysis (Hopp &amp; Spearman, 2011).</p>
