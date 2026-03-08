const DATA_SOURCES = {
  overview: "./data/overview.json",
  riskLatest: "./data/risk_latest.json",
  globalStory: "./data/global_story.json",
  profiles: "./data/country_profiles.json",
};

const DIMENSIONS = {
  dim1: {
    label: "疾病谱演变",
    defaultMetric: "life_expectancy",
    mapTitle: "全球疾病谱与健康结果版图",
    note: "点击国家查看寿命、疾病结构和经济卫生条件的长期变化。",
    metrics: ["life_expectancy", "ncd_share", "communicable_share", "health_exp_pct_gdp"],
  },
  dim2: {
    label: "风险归因",
    defaultMetric: "share",
    mapTitle: "全球健康风险归因地图",
    note: "选择风险因素后，地图显示该风险在各国最新年份的归因强度。",
    metrics: ["share", "attributable_deaths"],
  },
  dim3: {
    label: "资源配置",
    defaultMetric: "gap",
    mapTitle: "卫生资源缺口与效率地图",
    note: "缺口、效率和建议再分配强度在同一张地图上切换查看。",
    metrics: ["gap", "efficiency", "change_pct"],
  },
};

const METRIC_META = {
  life_expectancy: {
    label: "预期寿命",
    colorscale: [[0, "#0c1929"], [0.25, "#0e3a5e"], [0.5, "#0d6577"], [0.75, "#17a2b8"], [1, "#22d3ee"]],
    formatter: (value) => (value == null ? "—" : `${value.toFixed(1)} 岁`),
    accessor: (row) => row.life_expectancy,
  },
  ncd_share: {
    label: "非传染性疾病占比",
    colorscale: [[0, "#0c1929"], [0.25, "#1a2747"], [0.5, "#2e4070"], [0.75, "#6366f1"], [1, "#a78bfa"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.ncd_share,
  },
  communicable_share: {
    label: "传染性疾病占比",
    colorscale: [[0, "#1a1308"], [0.25, "#4a3010"], [0.5, "#7a5518"], [0.75, "#d4941a"], [1, "#fbbf24"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.communicable_share,
  },
  health_exp_pct_gdp: {
    label: "卫生支出占 GDP 比重",
    colorscale: [[0, "#071a17"], [0.25, "#0c3a32"], [0.5, "#12705f"], [0.75, "#1db99a"], [1, "#2dd4bf"]],
    formatter: (value) => formatPercentValue(value),
    accessor: (row) => row.health_exp_pct_gdp,
  },
  share: {
    label: "风险归因占比",
    colorscale: [[0, "#0c1929"], [0.25, "#2a1a4e"], [0.5, "#6b21a8"], [0.75, "#9333ea"], [1, "#c084fc"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.share,
  },
  attributable_deaths: {
    label: "风险归因死亡数",
    colorscale: [[0, "#0c1929"], [0.25, "#1e3a5f"], [0.5, "#0d6577"], [0.75, "#22d3ee"], [1, "#fbbf24"]],
    formatter: (value) => formatCompact(value),
    accessor: (row) => row.attributable_deaths,
  },
  gap: {
    label: "资源缺口",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#0c3a32"], [1, "#2dd4bf"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.gap,
    diverging: true,
  },
  efficiency: {
    label: "投入产出效率",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#0c3a32"], [1, "#2dd4bf"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.efficiency,
    diverging: true,
  },
  change_pct: {
    label: "建议再分配变化",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#1e3a5f"], [1, "#38bdf8"]],
    formatter: (value) => formatSignedPercent(value),
    accessor: (row) => row.change_pct,
    diverging: true,
  },
};

const THEME = {
  ink: "#e2e8f0",
  muted: "#94a3b8",
  dim: "#64748b",
  cyan: "#22d3ee",
  teal: "#2dd4bf",
  blue: "#38bdf8",
  amber: "#fbbf24",
  rose: "#fb7185",
  violet: "#a78bfa",
  card: "rgba(15,23,42,0.80)",
  grid: "rgba(148,163,184,0.06)",
  hover: "rgba(15,23,42,0.94)",
};

const state = {
  dimension: "dim1",
  metric: "life_expectancy",
  risk: "high_systolic_bp",
  country: "CHN",
};

const store = {
  overview: null,
  riskLatest: null,
  globalStory: null,
  profiles: null,
  overviewIndex: new Map(),
  riskIndex: new Map(),
  countryLookup: new Map(),
};

document.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadData();
    primeState();
    bindEvents();
    renderAll();
    document.body.classList.add("ready");
  } catch (error) {
    console.error(error);
    document.body.innerHTML = `<pre style="padding:24px;color:#7f1d1d;font-family:monospace;">Dashboard failed to load:\n${String(error)}</pre>`;
  }
});

async function loadData() {
  const entries = await Promise.all(
    Object.entries(DATA_SOURCES).map(async ([key, url]) => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch ${url}: ${response.status}`);
      }
      return [key, await response.json()];
    }),
  );
  for (const [key, value] of entries) {
    store[key] = value;
  }

  for (const country of store.overview.countries) {
    store.overviewIndex.set(country.iso3, country);
    const iso3Key = safeLower(country.iso3);
    const nameKey = safeLower(country.country_name);
    if (iso3Key) {
      store.countryLookup.set(iso3Key, country.iso3);
    }
    if (nameKey) {
      store.countryLookup.set(nameKey, country.iso3);
      store.countryLookup.set(`${nameKey} (${iso3Key})`, country.iso3);
    }
  }
  for (const risk of store.riskLatest.risks) {
    store.riskIndex.set(`${risk.iso3}|${risk.risk_code}`, risk);
  }
  populateCountryDatalist();
}

function primeState() {
  if (!store.overviewIndex.has(state.country)) {
    state.country = store.overview.countries[0]?.iso3 ?? "";
  }
  if (!store.riskLatest.available_risks.some((item) => item.risk_code === state.risk)) {
    state.risk = store.riskLatest.available_risks[0]?.risk_code ?? "";
  }
}

function bindEvents() {
  document.querySelectorAll("[data-dimension]").forEach((button) => {
    button.addEventListener("click", () => {
      state.dimension = button.dataset.dimension;
      state.metric = DIMENSIONS[state.dimension].defaultMetric;
      renderAll();
    });
  });

  document.getElementById("metric-select").addEventListener("change", (event) => {
    state.metric = event.target.value;
    renderAll();
  });

  document.getElementById("risk-select").addEventListener("change", (event) => {
    state.risk = event.target.value;
    renderAll();
  });

  document.getElementById("country-jump").addEventListener("click", handleCountryJump);
  document.getElementById("country-search").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleCountryJump();
    }
  });

  window.addEventListener("resize", debounce(() => {
    ["map-chart", "detail-chart", "companion-chart"].forEach((id) => {
      const node = document.getElementById(id);
      if (node && window.Plotly) {
        Plotly.Plots.resize(node);
      }
    });
  }, 140));
}

function handleCountryJump() {
  const input = document.getElementById("country-search").value.trim().toLowerCase();
  if (!input) {
    return;
  }
  const iso3 = resolveCountryInput(input);
  if (iso3) {
    state.country = iso3;
    renderPanels();
  }
}

function resolveCountryInput(input) {
  if (store.countryLookup.has(input)) {
    return store.countryLookup.get(input);
  }
  const candidate = store.overview.countries.find((country) => safeLower(country.country_name).includes(input));
  return candidate?.iso3 ?? null;
}

function populateCountryDatalist() {
  const datalist = document.getElementById("country-list");
  datalist.innerHTML = store.overview.countries
    .map((country) => `<option value="${escapeHtml(countryLabel(country))} (${country.iso3})"></option>`)
    .join("");
}

function renderAll() {
  const grid = document.querySelector(".dashboard-grid");
  if (grid) {
    grid.classList.add("dim-transition");
    requestAnimationFrame(() => {
      setTimeout(() => grid.classList.remove("dim-transition"), 150);
    });
  }
  syncControls();
  renderSummaryStrip();
  renderMap();
  renderPanels();
}

function renderPanels() {
  syncSearchField();
  const titleEl = document.getElementById("country-title");
  titleEl.classList.remove("country-flash");
  void titleEl.offsetWidth;
  titleEl.classList.add("country-flash");
  renderCountryPanel();
  renderRankingList();
  renderDetailChart();
  renderCompanionChart();
  renderContextPanel();
}

function syncControls() {
  document.querySelectorAll("[data-dimension]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.dimension === state.dimension);
  });

  const metricSelect = document.getElementById("metric-select");
  metricSelect.innerHTML = DIMENSIONS[state.dimension].metrics
    .map((metric) => `<option value="${metric}">${METRIC_META[metric].label}</option>`)
    .join("");
  metricSelect.value = state.metric;

  const riskField = document.getElementById("risk-field");
  const riskSelect = document.getElementById("risk-select");
  riskField.style.display = state.dimension === "dim2" ? "grid" : "none";
  if (state.dimension === "dim2") {
    riskSelect.innerHTML = store.riskLatest.available_risks
      .map((risk) => `<option value="${risk.risk_code}">${escapeHtml(risk.risk_name)}</option>`)
      .join("");
    riskSelect.value = state.risk;
  }

  document.getElementById("map-title").textContent = DIMENSIONS[state.dimension].mapTitle;
  document.getElementById("map-note").textContent = DIMENSIONS[state.dimension].note;
}

function syncSearchField() {
  const country = store.overviewIndex.get(state.country);
  if (country) {
    document.getElementById("country-search").value = `${countryLabel(country)} (${country.iso3})`;
  }
}

function renderSummaryStrip() {
  const summary = store.overview.summary;
  const tiles = [
    {
      value: formatShare(summary.dimension1.global_ncd_share),
      label: "2023 年全球非传染性疾病占比",
    },
    {
      value: escapeHtml(summary.dimension1.top_life_expectancy_country),
      label: "预期寿命最高国家",
    },
    {
      value: escapeHtml(summary.dimension2.top_global_risk),
      label: "全球首位风险因素",
    },
    {
      value: escapeHtml(summary.dimension3.largest_shortage_country),
      label: "资源缺口最显著国家",
    },
  ];
  document.getElementById("summary-strip").innerHTML = tiles
    .map((tile) => `<article class="summary-tile"><strong>${tile.value}</strong><span>${tile.label}</span></article>`)
    .join("");
}

function getMapRecords() {
  if (state.dimension === "dim2") {
    return store.riskLatest.risks.filter(
      (record) => record.risk_code === state.risk && METRIC_META[state.metric].accessor(record) != null,
    );
  }
  return store.overview.countries.filter((record) => METRIC_META[state.metric].accessor(record) != null);
}

function renderMap() {
  const metric = METRIC_META[state.metric];
  const records = getMapRecords();
  const values = records.map((record) => metric.accessor(record));
  const zBounds = getScaleBounds(values, metric.diverging);
  const hovertemplate = buildHoverTemplate();

  const trace = {
    type: "choropleth",
    locationmode: "ISO-3",
    locations: records.map((record) => record.iso3),
    z: values,
    text: records.map((record) => countryLabel(record)),
    hovertext: records.map((record) => buildHoverText(record)),
    colorscale: metric.colorscale,
    marker: { line: { color: "rgba(148,163,184,0.18)", width: 0.4 } },
    colorbar: {
      title: metric.label,
      thickness: 12,
      len: 0.68,
      x: 0.02,
      xanchor: "left",
      tickfont: { family: "DM Mono, monospace", size: 11, color: "#94a3b8" },
      titlefont: { family: "Noto Sans SC, sans-serif", size: 12, color: "#94a3b8" },
      outlinewidth: 0,
      borderwidth: 0,
    },
    hovertemplate,
    zmin: zBounds.zmin,
    zmax: zBounds.zmax,
    zmid: zBounds.zmid,
  };

  const layout = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 0, r: 0, t: 0, b: 0 },
    transition: { duration: 420, easing: "cubic-in-out" },
    geo: {
      projection: { type: "natural earth", scale: 1.08 },
      showframe: false,
      showcountries: true,
      countrycolor: "rgba(148,163,184,0.18)",
      showcoastlines: false,
      landcolor: "rgba(30,41,59,0.90)",
      bgcolor: "rgba(0,0,0,0)",
      lakecolor: "rgba(0,0,0,0)",
      showlakes: false,
    },
    font: { family: "Noto Sans SC, sans-serif", color: THEME.ink },
    hoverlabel: {
      bgcolor: THEME.hover,
      bordercolor: "rgba(34,211,238,0.25)",
      font: { family: "Noto Sans SC, sans-serif", color: "#e2e8f0", size: 13 },
    },
  };

  Plotly.react("map-chart", [trace], layout, {
    responsive: true,
    displayModeBar: false,
    scrollZoom: false,
  });

  const mapNode = document.getElementById("map-chart");
  if (!mapNode.dataset.bound) {
    mapNode.on("plotly_click", (event) => {
      const iso3 = event?.points?.[0]?.location;
      if (iso3) {
        state.country = iso3;
        renderPanels();
      }
    });
    mapNode.dataset.bound = "1";
  }
}

function buildHoverTemplate() {
  return "%{hovertext}<extra></extra>";
}

function buildHoverText(record) {
  if (state.dimension === "dim2") {
    return [
      `<b>${escapeHtml(countryLabel(record))}</b>`,
      `地区: ${escapeHtml(record.who_region)} / ${escapeHtml(record.wb_income)}`,
      `风险: ${escapeHtml(record.risk_name ?? getRiskName(state.risk))}`,
      `${METRIC_META[state.metric].label}: ${escapeHtml(METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(record)))}`,
      `归因死亡: ${escapeHtml(formatCompact(record.attributable_deaths))}`,
    ].join("<br>");
  }
  if (state.dimension === "dim3") {
    return [
      `<b>${escapeHtml(countryLabel(record))}</b>`,
      `地区: ${escapeHtml(record.who_region)} / ${escapeHtml(record.wb_income)}`,
      `${METRIC_META[state.metric].label}: ${escapeHtml(METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(record)))}`,
      `象限: ${escapeHtml(formatQuadrant(record.quadrant))}`,
      `缺口等级: ${escapeHtml(record.gap_grade_en ?? "—")}`,
    ].join("<br>");
  }
  return [
    `<b>${escapeHtml(countryLabel(record))}</b>`,
    `地区: ${escapeHtml(record.who_region)} / ${escapeHtml(record.wb_income)}`,
    `${METRIC_META[state.metric].label}: ${escapeHtml(METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(record)))}`,
    `主导风险: ${escapeHtml(record.top_risk_name ?? "—")}`,
    `主导风险占比: ${escapeHtml(formatShare(record.top_risk_share))}`,
  ].join("<br>");
}

function renderCountryPanel() {
  const profile = store.profiles[state.country];
  const latest = profile?.latest ?? {};
  const meta = profile?.meta ?? {};
  document.getElementById("country-title").textContent = countryLabel(meta) ?? state.country;
  document.getElementById("country-tag").textContent = `${meta.who_region ?? "NA"} / ${meta.wb_income ?? "NA"}`;

  let items = [];
  if (state.dimension === "dim1") {
    items = [
      ["预期寿命", METRIC_META.life_expectancy.formatter(latest.life_expectancy), "cyan"],
      ["传染性疾病占比", METRIC_META.communicable_share.formatter(latest.communicable_share), "amber"],
      ["非传染性疾病占比", METRIC_META.ncd_share.formatter(latest.ncd_share), "violet"],
      ["人均 GDP", formatCurrency(latest.gdp_per_capita), "teal"],
      ["卫生支出/GDP", formatPercentValue(latest.health_exp_pct_gdp), "blue"],
      ["医生密度", formatDecimal(latest.physicians_per_1000), "rose"],
    ];
  } else if (state.dimension === "dim2") {
    const selectedRisk = store.riskIndex.get(`${state.country}|${state.risk}`) ?? {};
    items = [
      ["主导风险", latest.top_risk_name ?? "—", "cyan"],
      ["主导风险占比", formatShare(latest.top_risk_share), "teal"],
      ["主导风险归因死亡", formatCompact(latest.top_risk_deaths), "rose"],
      ["当前选择风险", selectedRisk.risk_name ?? getRiskName(state.risk), "violet"],
      ["当前选择占比", formatShare(selectedRisk.share), "amber"],
      ["当前选择归因死亡", formatCompact(selectedRisk.attributable_deaths), "blue"],
    ];
  } else {
    items = [
      ["资源缺口", formatSigned(latest.gap), "rose"],
      ["缺口等级", latest.gap_grade_en ?? "—", "amber"],
      ["投入产出效率", formatSigned(latest.efficiency), "teal"],
      ["效率象限", formatQuadrant(latest.quadrant), "cyan"],
      ["建议变动", formatSignedPercent(latest.change_pct), "blue"],
      ["优化后人均支出", formatCurrency(latest.optimal), "violet"],
    ];
  }

  document.getElementById("country-metrics").innerHTML = items
    .map(
      ([label, value, accent]) =>
        `<article class="metric-tile" data-accent="${accent}"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value ?? "—")}</strong></article>`,
    )
    .join("");
}

function renderRankingList() {
  const records = getMapRecords().slice();
  const metric = METRIC_META[state.metric];
  const descending = !["gap"].includes(state.metric);
  records.sort((a, b) => {
    const av = metric.accessor(a);
    const bv = metric.accessor(b);
    return descending ? (bv ?? -Infinity) - (av ?? -Infinity) : (av ?? Infinity) - (bv ?? Infinity);
  });

  let caption = "按当前地图指标排序";
  if (state.metric === "gap") {
    caption = "资源缺口最严重";
  } else if (state.metric === "change_pct") {
    caption = "再分配优先级最高";
  } else if (state.dimension === "dim2") {
    caption = `${getRiskName(state.risk)} | ${metric.label}`;
  }
  document.getElementById("ranking-caption").textContent = caption;

  const top10 = records.slice(0, 10);
  const maxVal = Math.max(...top10.map((r) => Math.abs(metric.accessor(r) ?? 0)), 1e-9);

  document.getElementById("ranking-list").innerHTML = top10
    .map((record, index) => {
      const iso3 = record.iso3;
      const isSelected = iso3 === state.country;
      const rawVal = Math.abs(metric.accessor(record) ?? 0);
      const progress = Math.round((rawVal / maxVal) * 100);
      return `
        <button class="ranking-row ${isSelected ? "is-selected" : ""}" data-country="${iso3}" data-rank="${index + 1}" style="--progress:${progress}%;animation-delay:${index * 40}ms">
          <span class="rank-badge">${index + 1}</span>
          <span class="row-info">
            <b>${escapeHtml(countryLabel(record))}</b><br />
            <small>${escapeHtml(record.who_region ?? "NA")} / ${escapeHtml(record.wb_income ?? "NA")}</small>
          </span>
          <span class="row-value">${escapeHtml(metric.formatter(metric.accessor(record)))}</span>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll(".ranking-row").forEach((button) => {
    button.addEventListener("click", () => {
      state.country = button.dataset.country;
      renderPanels();
    });
  });
}

function renderDetailChart() {
  const profile = store.profiles[state.country];
  if (!profile) {
    return;
  }

  if (state.dimension === "dim1") {
    document.getElementById("detail-title").textContent = "国家健康结果与疾病结构";
    document.getElementById("detail-pill").textContent = "寿命与疾病谱双轴";
    renderDimension1Detail(profile);
    return;
  }
  if (state.dimension === "dim2") {
    document.getElementById("detail-title").textContent = "国家最新风险构成";
    document.getElementById("detail-pill").textContent = "最新年份 Top 6";
    renderDimension2Detail(profile);
    return;
  }

  document.getElementById("detail-title").textContent = "国家资源与结果归一化趋势";
  document.getElementById("detail-pill").textContent = "标准化后可直接比较";
  renderDimension3Detail(profile);
}

function renderDimension1Detail(profile) {
  const trend = profile.trend ?? [];
  const years = trend.map((item) => item.year);
  const traces = [
    {
      x: years,
      y: trend.map((item) => item.life_expectancy),
      name: "预期寿命",
      mode: "lines+markers",
      line: { color: THEME.cyan, width: 3 },
      marker: { size: 5 },
    },
    {
      x: years,
      y: trend.map((item) => (item.communicable_share ?? 0) * 100),
      name: "传染性疾病占比",
      mode: "lines",
      yaxis: "y2",
      line: { color: THEME.amber, width: 2.5 },
    },
    {
      x: years,
      y: trend.map((item) => (item.ncd_share ?? 0) * 100),
      name: "非传染性疾病占比",
      mode: "lines",
      yaxis: "y2",
      line: { color: THEME.violet, width: 2.5 },
    },
  ];
  Plotly.react("detail-chart", traces, baseLayout({
    yaxis: { title: "岁" },
    yaxis2: {
      overlaying: "y",
      side: "right",
      title: "%",
      gridcolor: "rgba(0,0,0,0)",
    },
  }));
}

function renderDimension2Detail(profile) {
  const risks = (profile.latest_risks ?? []).slice(0, 6).reverse();
  const traces = [
    {
      type: "bar",
      x: risks.map((item) => item.share * 100),
      y: risks.map((item) => item.risk_name),
      orientation: "h",
      marker: {
        color: risks.map((_, index) => interpolateColor(index / Math.max(risks.length - 1, 1))),
        cornerradius: 4,
      },
      customdata: risks.map((item) => item.attributable_deaths),
      hovertemplate: "<b>%{y}</b><br>占比: %{x:.2f}%<br>归因死亡: %{customdata:.0f}<extra></extra>",
    },
  ];
  Plotly.react("detail-chart", traces, baseLayout({
    xaxis: { title: "占比（%）" },
    yaxis: { automargin: true },
  }));
}

function renderDimension3Detail(profile) {
  const trend = profile.trend ?? [];
  const series = {
    "卫生支出": normalizeSeries(trend.map((item) => item.health_exp_per_capita)),
    "医生密度": normalizeSeries(trend.map((item) => item.physicians_per_1000)),
    "预期寿命": normalizeSeries(trend.map((item) => item.life_expectancy)),
  };
  const traces = Object.entries(series).map(([name, values], index) => ({
    x: trend.map((item) => item.year),
    y: values,
    mode: "lines",
    name,
    line: {
      width: 3,
      color: [THEME.teal, THEME.blue, THEME.amber][index],
    },
  }));
  Plotly.react("detail-chart", traces, baseLayout({
    yaxis: { title: "归一化指数" },
  }));
}

function renderCompanionChart() {
  if (state.dimension === "dim1") {
    document.getElementById("companion-title").textContent = "全球疾病谱转型";
    document.getElementById("companion-pill").textContent = "2000-2023";
    renderGlobalDiseaseTrend();
    return;
  }
  if (state.dimension === "dim2") {
    document.getElementById("companion-title").textContent = "全球风险流向 Sankey";
    document.getElementById("companion-pill").textContent = "风险 → WHO 地区";
    renderRiskSankey();
    return;
  }

  document.getElementById("companion-title").textContent = "建议再分配优先国家";
  document.getElementById("companion-pill").textContent = "Top 12";
  renderReallocationBar();
}

function renderGlobalDiseaseTrend() {
  const trend = store.globalStory.global_disease_trends;
  const traces = [
    lineTrace(trend, "year", "communicable_share", "传染性疾病", THEME.amber, true),
    lineTrace(trend, "year", "ncd_share", "非传染性疾病", THEME.teal, true),
    lineTrace(trend, "year", "injury_share", "伤害", THEME.rose, true),
  ];
  Plotly.react("companion-chart", traces, baseLayout({
    yaxis: { title: "全球死亡占比", tickformat: ".0%" },
  }));
}

function renderRiskSankey() {
  const sankey = store.globalStory.sankey;
  const trace = {
    type: "sankey",
    arrangement: "snap",
    node: {
      label: sankey.nodes,
      pad: 16,
      thickness: 18,
      line: { color: "rgba(148,163,184,0.12)", width: 0.5 },
      color: sankey.nodes.map((node) => (node.includes("RO") || node.includes("PRO") ? "rgba(167,139,250,0.75)" : "rgba(34,211,238,0.75)")),
    },
    link: {
      source: sankey.sources,
      target: sankey.targets,
      value: sankey.values,
      color: "rgba(148,163,184,0.08)",
    },
    hoverlabel: { font: { family: "Noto Sans SC, sans-serif", color: "#e2e8f0" }, bgcolor: "rgba(15,23,42,0.94)" },
  };
  Plotly.react("companion-chart", [trace], baseLayout({
    margin: { l: 12, r: 12, t: 10, b: 10 },
  }));
}

function renderReallocationBar() {
  const rows = store.globalStory.resource_highlights.reallocation.slice(0, 12).reverse();
  const trace = {
    type: "bar",
    x: rows.map((item) => item.change_pct),
    y: rows.map((item) => countryLabel(item)),
    orientation: "h",
    marker: { color: rows.map((item) => (item.change_pct >= 0 ? THEME.teal : THEME.rose)), cornerradius: 4 },
    hovertemplate: "<b>%{y}</b><br>建议变动: %{x:.1f}%<extra></extra>",
  };
  Plotly.react("companion-chart", [trace], baseLayout({
    xaxis: { title: "建议再分配变化（%）" },
    yaxis: { automargin: true },
  }));
}

function renderContextPanel() {
  if (state.dimension === "dim1") {
    document.getElementById("context-title").textContent = "全球极值与结构差异";
    renderDim1Context();
    return;
  }
  if (state.dimension === "dim2") {
    document.getElementById("context-title").textContent = "WHO 地区主导风险";
    renderDim2Context();
    return;
  }
  document.getElementById("context-title").textContent = "资源缺口、效率与再分配";
  renderDim3Context();
}

function renderDim1Context() {
  const countries = store.overview.countries.slice();
  const topLife = countries
    .filter((item) => item.life_expectancy != null)
    .sort((a, b) => b.life_expectancy - a.life_expectancy)
    .slice(0, 6);
  const bottomLife = countries
    .filter((item) => item.life_expectancy != null)
    .sort((a, b) => a.life_expectancy - b.life_expectancy)
    .slice(0, 6);
  const communicable = countries
    .filter((item) => item.communicable_share != null)
    .sort((a, b) => b.communicable_share - a.communicable_share)
    .slice(0, 6);
  document.getElementById("context-panel").innerHTML = renderContextColumns([
    { title: "寿命最高", items: topLife.map((item) => ({ name: countryLabel(item), value: `${formatDecimal(item.life_expectancy)} 岁` })) },
    { title: "寿命最低", items: bottomLife.map((item) => ({ name: countryLabel(item), value: `${formatDecimal(item.life_expectancy)} 岁` })) },
    { title: "传染性疾病负担最高", items: communicable.map((item) => ({ name: countryLabel(item), value: formatShare(item.communicable_share) })) },
  ]);
}

function renderDim2Context() {
  const rows = store.globalStory.region_priority;
  document.getElementById("context-panel").innerHTML = renderContextColumns(
    rows.map((row) => ({
      title: row.who_region,
      items: [
        { name: `1. ${row.primary_risk}`, value: formatShare(row.primary_share) },
        { name: `2. ${row.secondary_risk}`, value: formatShare(row.secondary_share) },
        { name: row.tertiary_risk ? `3. ${row.tertiary_risk}` : "3. —", value: row.tertiary_share ? formatShare(row.tertiary_share) : "—" },
      ],
    })),
  );
}

function renderDim3Context() {
  const highlights = store.globalStory.resource_highlights;
  document.getElementById("context-panel").innerHTML = renderContextColumns([
    {
      title: "缺口最严重",
      items: highlights.under_resourced.slice(0, 6).map((item) => ({ name: countryLabel(item), value: formatSigned(item.gap) })),
    },
    {
      title: "低投入高产出",
      items: highlights.efficient.slice(0, 6).map((item) => ({ name: countryLabel(item), value: formatSigned(item.efficiency) })),
    },
    {
      title: "再分配优先",
      items: highlights.reallocation.slice(0, 6).map((item) => ({ name: countryLabel(item), value: formatSignedPercent(item.change_pct) })),
    },
  ]);
}

function renderContextColumns(columns) {
  return `<div class="context-grid">${columns
    .map(
      (column) => `
      <section class="context-column">
        <div class="col-header"><span class="col-dot"></span><h3>${escapeHtml(column.title)}</h3></div>
        ${column.items
          .map((item) => {
            if (typeof item === "string") {
              return `<div class="context-item"><span class="ctx-name">${escapeHtml(item)}</span></div>`;
            }
            return `<div class="context-item"><span class="ctx-name">${escapeHtml(item.name)}</span><span class="ctx-value">${escapeHtml(item.value)}</span></div>`;
          })
          .join("")}
      </section>`,
    )
    .join("")}</div>`;
}

function lineTrace(records, xKey, yKey, name, color, percentage = false) {
  return {
    x: records.map((item) => item[xKey]),
    y: records.map((item) => item[yKey]),
    mode: "lines",
    name,
    line: { width: 3, color },
    hovertemplate: percentage
      ? `<b>${name}</b><br>%{x}: %{y:.1%}<extra></extra>`
      : `<b>${name}</b><br>%{x}: %{y:.2f}<extra></extra>`,
  };
}

function baseLayout(extra = {}) {
  return {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 46, r: 28, t: 8, b: 42 },
    font: { family: "Noto Sans SC, sans-serif", color: THEME.muted },
    xaxis: {
      gridcolor: THEME.grid,
      zerolinecolor: "rgba(148,163,184,0.12)",
      linecolor: THEME.grid,
      ticks: "",
      tickfont: { family: "DM Mono, monospace", size: 11, color: THEME.dim },
    },
    yaxis: {
      gridcolor: THEME.grid,
      zerolinecolor: "rgba(148,163,184,0.12)",
      linecolor: THEME.grid,
      ticks: "",
      tickfont: { family: "DM Mono, monospace", size: 11, color: THEME.dim },
    },
    legend: {
      orientation: "h",
      yanchor: "bottom",
      y: 1.03,
      xanchor: "left",
      x: 0,
      font: { color: THEME.muted, size: 12 },
    },
    hoverlabel: {
      bgcolor: THEME.hover,
      bordercolor: "rgba(34,211,238,0.20)",
      font: { family: "Noto Sans SC, sans-serif", color: "#e2e8f0", size: 13 },
    },
    transition: { duration: 420, easing: "cubic-in-out" },
    ...extra,
  };
}

function getScaleBounds(values, diverging = false) {
  const numeric = values.filter((value) => value != null && Number.isFinite(value));
  if (!numeric.length) {
    return {};
  }
  if (!diverging) {
    return { zmin: Math.min(...numeric), zmax: Math.max(...numeric) };
  }
  const bound = Math.max(...numeric.map((value) => Math.abs(value)));
  return { zmin: -bound, zmax: bound, zmid: 0 };
}

function normalizeSeries(values) {
  const numeric = values.filter((value) => value != null && Number.isFinite(value));
  if (!numeric.length) {
    return values.map(() => null);
  }
  const min = Math.min(...numeric);
  const max = Math.max(...numeric);
  return values.map((value) => {
    if (value == null || !Number.isFinite(value)) {
      return null;
    }
    if (max === min) {
      return 0.5;
    }
    return (value - min) / (max - min);
  });
}

function interpolateColor(ratio) {
  const palette = [
    "#22d3ee",
    "#38bdf8",
    "#2dd4bf",
    "#a78bfa",
    "#fbbf24",
    "#fb7185",
  ];
  const index = Math.min(palette.length - 1, Math.round(ratio * (palette.length - 1)));
  return palette[index];
}

function getRiskName(riskCode) {
  const item = store.riskLatest.available_risks.find((risk) => risk.risk_code === riskCode);
  return item?.risk_name ?? riskCode;
}

function formatQuadrant(value) {
  const map = {
    Q1_high_input_high_output: "高投入 / 高产出",
    Q2_low_input_high_output: "低投入 / 高产出",
    Q3_high_input_low_output: "高投入 / 低产出",
    Q4_low_input_low_output: "低投入 / 低产出",
  };
  return map[value] ?? "未分类";
}

function formatDecimal(value) {
  return value == null ? "—" : Number(value).toFixed(2);
}

function formatShare(value) {
  return value == null ? "—" : `${(Number(value) * 100).toFixed(1)}%`;
}

function formatPercentValue(value) {
  return value == null ? "—" : `${Number(value).toFixed(1)}%`;
}

function formatSigned(value) {
  return value == null ? "—" : `${Number(value) > 0 ? "+" : ""}${Number(value).toFixed(2)}`;
}

function formatSignedPercent(value) {
  return value == null ? "—" : `${Number(value) > 0 ? "+" : ""}${Number(value).toFixed(1)}%`;
}

function formatCurrency(value) {
  if (value == null) {
    return "—";
  }
  if (Math.abs(value) >= 1000) {
    return `$${Number(value).toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
  }
  return `$${Number(value).toFixed(0)}`;
}

function formatCompact(value) {
  if (value == null) {
    return "—";
  }
  const number = Number(value);
  if (Math.abs(number) >= 1_000_000_000) {
    return `${(number / 1_000_000_000).toFixed(2)}B`;
  }
  if (Math.abs(number) >= 1_000_000) {
    return `${(number / 1_000_000).toFixed(2)}M`;
  }
  if (Math.abs(number) >= 1_000) {
    return `${(number / 1_000).toFixed(1)}K`;
  }
  return number.toFixed(0);
}

function countryLabel(record) {
  if (!record) {
    return "Unknown";
  }
  return record.country_name ?? record.name ?? record.iso3 ?? "Unknown";
}

function safeLower(value) {
  return value == null ? "" : String(value).toLowerCase();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function debounce(fn, wait) {
  let timeout = null;
  return (...args) => {
    window.clearTimeout(timeout);
    timeout = window.setTimeout(() => fn(...args), wait);
  };
}
