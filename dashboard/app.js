const DATA_SOURCES = {
  overview: "./data/overview.json",
  riskLatest: "./data/risk_latest.json",
  globalStory: "./data/global_story.json",
  profiles: "./data/country_profiles.json",
};

const DIMENSIONS = {
  dim1: {
    label: "Disease Spectrum",
    defaultMetric: "life_expectancy",
    mapTitle: "Global Disease Spectrum & Health Outcomes",
    note: "Click a country to explore long-run life expectancy, disease structure, and health system conditions.",
    metrics: ["life_expectancy", "ncd_share", "communicable_share", "health_exp_pct_gdp"],
  },
  dim2: {
    label: "Risk Attribution",
    defaultMetric: "share",
    mapTitle: "Global Health Risk Attribution Map",
    note: "Select a risk factor to inspect how its latest attributable burden varies across countries.",
    metrics: ["share", "attributable_deaths"],
  },
  dim3: {
    label: "Optimization Lab",
    defaultMetric: "change_pct",
    mapTitle: "Scenario-Based Resource Reallocation Lab",
    note: "Switch objective and budget settings to compare donor-recipient patterns and country-level recommendations.",
    metrics: ["change_pct", "gap", "efficiency"],
  },
};

const METRIC_META = {
  life_expectancy: {
    label: "Life Expectancy",
    colorscale: [[0, "#0c1929"], [0.25, "#0e3a5e"], [0.5, "#0d6577"], [0.75, "#17a2b8"], [1, "#22d3ee"]],
    formatter: (value) => (value == null ? "N/A" : `${Number(value).toFixed(1)} yrs`),
    accessor: (row) => row.life_expectancy,
  },
  ncd_share: {
    label: "NCD Share",
    colorscale: [[0, "#0c1929"], [0.25, "#1a2747"], [0.5, "#2e4070"], [0.75, "#6366f1"], [1, "#a78bfa"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.ncd_share,
  },
  communicable_share: {
    label: "Communicable Disease Share",
    colorscale: [[0, "#1a1308"], [0.25, "#4a3010"], [0.5, "#7a5518"], [0.75, "#d4941a"], [1, "#fbbf24"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.communicable_share,
  },
  health_exp_pct_gdp: {
    label: "Health Expenditure (% GDP)",
    colorscale: [[0, "#071a17"], [0.25, "#0c3a32"], [0.5, "#12705f"], [0.75, "#1db99a"], [1, "#2dd4bf"]],
    formatter: (value) => formatPercentValue(value),
    accessor: (row) => row.health_exp_pct_gdp,
  },
  share: {
    label: "Risk Attribution Share",
    colorscale: [[0, "#0c1929"], [0.25, "#2a1a4e"], [0.5, "#6b21a8"], [0.75, "#9333ea"], [1, "#c084fc"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.share,
  },
  attributable_deaths: {
    label: "Attributable Deaths",
    colorscale: [[0, "#0c1929"], [0.25, "#1e3a5f"], [0.5, "#0d6577"], [0.75, "#22d3ee"], [1, "#fbbf24"]],
    formatter: (value) => formatCompact(value),
    accessor: (row) => row.attributable_deaths,
  },
  change_pct: {
    label: "Scenario Reallocation",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#164e63"], [1, "#22d3ee"]],
    formatter: (value) => formatSignedPercent(value),
    accessor: (row) => row.change_pct,
    diverging: true,
  },
  gap: {
    label: "Resource Gap",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#0c3a32"], [1, "#2dd4bf"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.gap,
    diverging: true,
  },
  efficiency: {
    label: "Input-Output Efficiency",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#0c3a32"], [1, "#2dd4bf"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.efficiency,
    diverging: true,
  },
};

const THEME = {
  ink: "#e2e8f0",
  inkBright: "#f8fafc",
  muted: "#94a3b8",
  dim: "#64748b",
  cyan: "#22d3ee",
  teal: "#2dd4bf",
  blue: "#38bdf8",
  amber: "#fbbf24",
  rose: "#fb7185",
  violet: "#a78bfa",
  emerald: "#34d399",
  grid: "rgba(148,163,184,0.08)",
  hover: "rgba(15,23,42,0.94)",
};

const OBJECTIVE_META = {
  max_output: {
    label: "Max Output",
    note: "Prioritizes aggregate outcome gains across the full system.",
  },
  maximin: {
    label: "Equity Maximin",
    note: "Protects lower-performing countries by improving the floor first.",
  },
};

const OBJECTIVE_ALIASES = {
  max_output: "max_output",
  maximize_aggregate_output: "max_output",
  maximize_need_weighted_health_output: "max_output",
  projected_need_weighted_allocation: "max_output",
  maximin: "maximin",
};

const state = {
  dimension: "dim1",
  metric: "life_expectancy",
  risk: "",
  country: "CHN",
  objective: "max_output",
  budgetMultiplier: 1.0,
  scenarioId: "",
  dialogOpen: false,
  dialogCountry: "",
  previousFocus: null,
};

const store = {
  overview: null,
  riskLatest: null,
  globalStory: null,
  profiles: null,
  overviewIndex: new Map(),
  riskIndex: new Map(),
  countryLookup: new Map(),
  optimizationScenarios: [],
  scenarioIndex: new Map(),
};

document.addEventListener("DOMContentLoaded", async () => {
  try {
    if (!window.Plotly) {
      throw new Error("Local Plotly bundle was not loaded.");
    }
    await loadData();
    bindEvents();
    renderAll();
    document.body.classList.add("ready");
  } catch (error) {
    console.error(error);
    renderFailure(error);
  }
});

async function loadData() {
  const entries = await Promise.all(
    Object.entries(DATA_SOURCES).map(async ([key, url]) => [key, await loadJson(url)]),
  );

  for (const [key, value] of entries) {
    store[key] = value;
  }

  for (const country of store.overview.countries ?? []) {
    store.overviewIndex.set(country.iso3, country);
    const isoKey = safeLower(country.iso3);
    const nameKey = safeLower(country.country_name);
    if (isoKey) {
      store.countryLookup.set(isoKey, country.iso3);
    }
    if (nameKey) {
      store.countryLookup.set(nameKey, country.iso3);
      store.countryLookup.set(`${nameKey} (${isoKey})`, country.iso3);
    }
  }

  for (const risk of store.riskLatest.risks ?? []) {
    store.riskIndex.set(`${risk.iso3}|${risk.risk_code}`, risk);
  }

  store.optimizationScenarios = normalizeOptimizationScenarios();
  store.scenarioIndex = new Map(
    store.optimizationScenarios.map((scenario) => [scenario.scenario_id, scenario]),
  );

  primeState();
  populateCountryDatalist();
}

async function loadJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status}`);
  }
  return response.json();
}

function primeState() {
  if (!store.overviewIndex.has(state.country)) {
    state.country = store.overview.countries?.[0]?.iso3 ?? "";
  }

  state.risk = store.riskLatest.available_risks?.[0]?.risk_code ?? "";
  syncScenarioSelection();
}

function normalizeOptimizationScenarios() {
  const rawCandidates = [
    store.globalStory?.optimization_lab?.scenarios,
    store.globalStory?.optimization_scenarios,
    store.overview?.optimization_lab?.scenarios,
    store.overview?.optimization_scenarios,
  ].find((candidate) => Array.isArray(candidate) && candidate.length > 0);

  const scenarios = (rawCandidates ?? [])
    .map((scenario, index) => normalizeScenario(scenario, index))
    .filter(Boolean);

  if (scenarios.length > 0) {
    return scenarios.sort((left, right) => {
      if (left.objective === right.objective) {
        return left.budget_multiplier - right.budget_multiplier;
      }
      return objectiveRank(left.objective) - objectiveRank(right.objective);
    });
  }

  const fallback = buildFallbackScenario();
  return fallback ? [fallback] : [];
}

function normalizeScenario(rawScenario, index) {
  const objective = normalizeObjective(rawScenario.objective ?? rawScenario.objective_name ?? rawScenario.status);
  const budgetMultiplier = normalizeBudget(rawScenario.budget_multiplier ?? rawScenario.budget ?? 1.0);
  const allocation = normalizeScenarioAllocation(
    rawScenario.allocation ?? rawScenario.optimal_allocation ?? rawScenario.rows ?? [],
  );

  if (!allocation.length) {
    return null;
  }

  const scenario = {
    scenario_id: rawScenario.scenario_id ?? makeScenarioId(objective, budgetMultiplier, index),
    objective,
    budget_multiplier: budgetMultiplier,
    objective_value: normalizeNumber(rawScenario.objective_value),
    status: rawScenario.status ?? "ready",
    label: rawScenario.label ?? `${objectiveLabel(objective)} | ${budgetLabel(budgetMultiplier)}`,
    allocation,
    summary: {},
  };

  scenario.summary = buildScenarioSummary(scenario, rawScenario.summary ?? {});
  scenario.allocationIndex = new Map(scenario.allocation.map((row) => [row.iso3, row]));
  return scenario;
}

function normalizeScenarioAllocation(rows) {
  return (rows ?? [])
    .map((row) => ({
      iso3: row.iso3,
      country_name: row.country_name ?? row.country ?? row.name ?? row.iso3,
      current: normalizeNumber(row.current),
      optimal: normalizeNumber(row.optimal),
      change: normalizeNumber(row.change),
      change_pct: normalizeNumber(row.change_pct),
      projected_output: normalizeNumber(row.projected_output),
      projected_output_change: normalizeNumber(row.projected_output_change),
      projected_output_change_pct: normalizeNumber(row.projected_output_change_pct),
    }))
    .filter((row) => row.iso3);
}

function buildFallbackScenario() {
  const allocation = (store.overview.countries ?? [])
    .filter((country) => country.current != null || country.optimal != null || country.change_pct != null)
    .map((country) => ({
      iso3: country.iso3,
      country_name: country.country_name,
      current: normalizeNumber(country.current),
      optimal: normalizeNumber(country.optimal),
      change: normalizeNumber(country.change),
      change_pct: normalizeNumber(country.change_pct),
    }));

  if (!allocation.length) {
    return null;
  }

  const scenario = {
    scenario_id: "fallback_max_output_1p0",
    objective: "max_output",
    budget_multiplier: 1.0,
    objective_value: null,
    status: "fallback_from_overview",
    label: "Need-weighted baseline | Current budget",
    allocation,
    summary: {},
  };
  scenario.summary = buildScenarioSummary(scenario, {
    note: "Fallback scenario derived from the latest overview artifact.",
  });
  scenario.allocationIndex = new Map(scenario.allocation.map((row) => [row.iso3, row]));
  return scenario;
}

function buildScenarioSummary(scenario, rawSummary = {}) {
  const allocation = scenario.allocation ?? [];
  const totalCurrent = sumValues(allocation.map((row) => row.current));
  const totalOptimal = sumValues(allocation.map((row) => row.optimal));
  const recipients = allocation
    .filter((row) => (row.change ?? 0) > 0)
    .sort((left, right) => (right.change_pct ?? -Infinity) - (left.change_pct ?? -Infinity));
  const donors = allocation
    .filter((row) => (row.change ?? 0) < 0)
    .sort((left, right) => (left.change_pct ?? Infinity) - (right.change_pct ?? Infinity));
  const movedBudget = sumValues(allocation.map((row) => Math.abs(row.change ?? 0))) / 2;
  const merged = {
    label: rawSummary.label ?? scenario.label,
    note: rawSummary.note ?? OBJECTIVE_META[scenario.objective]?.note ?? "",
    recipient_count: rawSummary.recipient_count ?? recipients.length,
    donor_count: rawSummary.donor_count ?? donors.length,
    total_current: rawSummary.total_current ?? totalCurrent,
    total_optimal: rawSummary.total_optimal ?? totalOptimal,
    moved_budget: rawSummary.moved_budget ?? movedBudget,
    projected_output_change_pct:
      rawSummary.projected_output_change_pct ?? normalizeNumber(rawSummary.projected_output_change_pct),
    top_recipient: rawSummary.top_recipient ?? recipients[0]?.country_name ?? "N/A",
    top_donor: rawSummary.top_donor ?? donors[0]?.country_name ?? "N/A",
    objective_label: rawSummary.objective_label ?? objectiveLabel(scenario.objective),
    budget_label: rawSummary.budget_label ?? budgetLabel(scenario.budget_multiplier),
  };

  return merged;
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

  document.getElementById("objective-select").addEventListener("change", (event) => {
    state.objective = normalizeObjective(event.target.value);
    syncScenarioSelection();
    renderAll();
  });

  document.getElementById("budget-select").addEventListener("change", (event) => {
    state.budgetMultiplier = normalizeBudget(event.target.value);
    syncScenarioSelection();
    renderAll();
  });

  document.getElementById("country-jump").addEventListener("click", handleCountryJump);
  document.getElementById("country-search").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleCountryJump();
    }
  });

  document.getElementById("spotlight-close").addEventListener("click", closeSpotlightModal);
  document.getElementById("spotlight-backdrop").addEventListener("click", closeSpotlightModal);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && state.dialogOpen) {
      closeSpotlightModal();
      return;
    }
    if (event.key === "Tab" && state.dialogOpen) {
      trapDialogFocus(event);
    }
  });

  window.addEventListener(
    "resize",
    debounce(() => {
      ["map-chart", "detail-chart", "companion-chart", "spotlight-chart"].forEach((id) => {
        const node = document.getElementById(id);
        if (node) {
          Plotly.Plots.resize(node);
        }
      });
    }, 120),
  );
}

function syncScenarioSelection() {
  const scenarios = store.optimizationScenarios;
  if (!scenarios.length) {
    state.scenarioId = "";
    return;
  }

  const exact = scenarios.find(
    (scenario) =>
      scenario.objective === normalizeObjective(state.objective) &&
      Math.abs(scenario.budget_multiplier - normalizeBudget(state.budgetMultiplier)) < 1e-9,
  );

  const sameObjective = scenarios.filter((scenario) => scenario.objective === normalizeObjective(state.objective));
  const pool = sameObjective.length ? sameObjective : scenarios;
  const chosen = exact ?? nearestScenario(pool, normalizeBudget(state.budgetMultiplier));

  state.scenarioId = chosen.scenario_id;
  state.objective = chosen.objective;
  state.budgetMultiplier = chosen.budget_multiplier;
}

function nearestScenario(scenarios, budgetMultiplier) {
  return [...scenarios].sort(
    (left, right) =>
      Math.abs(left.budget_multiplier - budgetMultiplier) -
      Math.abs(right.budget_multiplier - budgetMultiplier),
  )[0];
}

function populateCountryDatalist() {
  const datalist = document.getElementById("country-list");
  datalist.innerHTML = (store.overview.countries ?? [])
    .map((country) => `<option value="${escapeHtml(countryLabel(country))} (${country.iso3})"></option>`)
    .join("");
}

function handleCountryJump() {
  const input = safeLower(document.getElementById("country-search").value.trim());
  if (!input) {
    return;
  }

  const iso3 = resolveCountryInput(input);
  if (!iso3) {
    return;
  }

  state.country = iso3;
  renderPanels();
  updateMapHighlight(iso3);
  openSpotlightModal(iso3);
}

function resolveCountryInput(input) {
  if (store.countryLookup.has(input)) {
    return store.countryLookup.get(input);
  }

  const partial = (store.overview.countries ?? []).find((country) =>
    safeLower(country.country_name).includes(input),
  );
  return partial?.iso3 ?? null;
}

function renderAll() {
  syncControls();
  renderSummaryStrip();
  renderMap();
  renderPanels();
}

function syncControls() {
  document.querySelectorAll("[data-dimension]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.dimension === state.dimension);
  });

  const metricSelect = document.getElementById("metric-select");
  metricSelect.innerHTML = DIMENSIONS[state.dimension].metrics
    .map((metric) => `<option value="${metric}">${escapeHtml(METRIC_META[metric].label)}</option>`)
    .join("");
  metricSelect.value = state.metric;

  const riskField = document.getElementById("risk-field");
  riskField.style.display = state.dimension === "dim2" ? "grid" : "none";
  if (state.dimension === "dim2") {
    const riskSelect = document.getElementById("risk-select");
    riskSelect.innerHTML = (store.riskLatest.available_risks ?? [])
      .map(
        (risk) =>
          `<option value="${escapeHtml(risk.risk_code)}">${escapeHtml(risk.risk_name)}</option>`,
      )
      .join("");
    riskSelect.value = state.risk;
  }

  const objectiveField = document.getElementById("objective-field");
  const budgetField = document.getElementById("budget-field");
  objectiveField.style.display = state.dimension === "dim3" ? "grid" : "none";
  budgetField.style.display = state.dimension === "dim3" ? "grid" : "none";

  if (state.dimension === "dim3") {
    const objectiveSelect = document.getElementById("objective-select");
    const budgetSelect = document.getElementById("budget-select");
    const objectives = uniqueValues(store.optimizationScenarios.map((scenario) => scenario.objective));
    const budgets = uniqueValues(
      store.optimizationScenarios.map((scenario) => scenario.budget_multiplier.toFixed(1)),
    ).map((value) => Number(value));

    objectiveSelect.innerHTML = objectives
      .map((objective) => `<option value="${objective}">${escapeHtml(objectiveLabel(objective))}</option>`)
      .join("");
    objectiveSelect.value = state.objective;

    budgetSelect.innerHTML = budgets
      .map(
        (budget) =>
          `<option value="${budget.toFixed(1)}">${escapeHtml(budgetLabel(budget))}</option>`,
      )
      .join("");
    budgetSelect.value = normalizeBudget(state.budgetMultiplier).toFixed(1);
  }

  document.getElementById("map-title").textContent = DIMENSIONS[state.dimension].mapTitle;
  document.getElementById("map-note").textContent = DIMENSIONS[state.dimension].note;
  document.getElementById("context-pill").textContent =
    state.dimension === "dim3" ? "Scenario Engine" : "Static Build";

  const currentScenario = getCurrentScenario();
  const controlNote =
    state.dimension === "dim3"
      ? `${currentScenario?.summary?.label ?? "Optimization scenario"}: ${
          OBJECTIVE_META[state.objective]?.note ?? ""
        }`
      : "Static dashboard built from competition analysis artifacts.";
  document.getElementById("control-note").textContent = controlNote;

  syncSearchField();
}

function syncSearchField() {
  const country = store.overviewIndex.get(state.country);
  if (country) {
    document.getElementById("country-search").value = `${countryLabel(country)} (${country.iso3})`;
  }
}

function renderSummaryStrip() {
  const summary = store.overview.summary ?? {};
  const scenario = getCurrentScenario();
  const tiles = [
    {
      value: formatShare(summary.dimension1?.global_ncd_share),
      label: "2023 Global NCD Share",
    },
    {
      value: escapeHtml(summary.dimension1?.top_life_expectancy_country ?? "N/A"),
      label: "Highest Life Expectancy",
    },
    {
      value: escapeHtml(summary.dimension2?.top_global_risk ?? "N/A"),
      label: "Top Global Risk Factor",
    },
    state.dimension === "dim3"
      ? {
          value: budgetLabel(scenario?.budget_multiplier ?? 1),
          label: objectiveLabel(scenario?.objective ?? "max_output"),
        }
      : {
          value: escapeHtml(summary.dimension3?.largest_shortage_country ?? "N/A"),
          label: "Largest Resource Gap",
        },
  ];

  document.getElementById("summary-strip").innerHTML = tiles
    .map(
      (tile) =>
        `<article class="summary-tile"><strong>${tile.value}</strong><span>${escapeHtml(tile.label)}</span></article>`,
    )
    .join("");
}

function renderPanels() {
  const grid = document.querySelector(".dashboard-grid");
  grid?.classList.add("dim-fading");
  window.clearTimeout(renderPanels._timer);
  renderPanels._timer = window.setTimeout(() => {
    renderCountryPanel();
    renderRankingList();
    renderDetailChart();
    renderCompanionChart();
    renderContextPanel();
    if (state.dialogOpen) {
      renderSpotlightContent(state.dialogCountry || state.country);
    }
    grid?.classList.remove("dim-fading");
  }, 120);
}

function getCurrentScenario() {
  return store.scenarioIndex.get(state.scenarioId) ?? store.optimizationScenarios[0] ?? null;
}

function getScenarioRow(iso3) {
  const scenario = getCurrentScenario();
  return scenario?.allocationIndex?.get(iso3) ?? null;
}

function getMapRecords() {
  if (state.dimension === "dim2") {
    return (store.riskLatest.risks ?? []).filter(
      (row) => row.risk_code === state.risk && METRIC_META[state.metric].accessor(row) != null,
    );
  }

  if (state.dimension === "dim3") {
    const scenarioIndex = getCurrentScenario()?.allocationIndex ?? new Map();
    return (store.overview.countries ?? [])
      .map((country) => ({ ...country, ...(scenarioIndex.get(country.iso3) ?? {}) }))
      .filter((row) => METRIC_META[state.metric].accessor(row) != null);
  }

  return (store.overview.countries ?? []).filter(
    (row) => METRIC_META[state.metric].accessor(row) != null,
  );
}

function renderMap() {
  const metric = METRIC_META[state.metric];
  const records = getMapRecords();
  const values = records.map((row) => metric.accessor(row));
  const bounds = getScaleBounds(values, metric.diverging);
  const selected = records.find((row) => row.iso3 === state.country);

  Plotly.react(
    "map-chart",
    [
      {
        type: "choropleth",
        locationmode: "ISO-3",
        locations: records.map((row) => row.iso3),
        z: values,
        text: records.map((row) => countryLabel(row)),
        hovertext: records.map((row) => buildHoverText(row)),
        hovertemplate: "%{hovertext}<extra></extra>",
        colorscale: metric.colorscale,
        zmin: bounds.zmin,
        zmax: bounds.zmax,
        zmid: bounds.zmid,
        marker: {
          line: {
            color: records.map((row) =>
              row.iso3 === state.country ? "rgba(34,211,238,0.72)" : "rgba(148,163,184,0.18)",
            ),
            width: records.map((row) => (row.iso3 === state.country ? 2 : 0.4)),
          },
        },
        colorbar: {
          title: metric.label,
          thickness: 12,
          len: 0.68,
          x: 0.02,
          xanchor: "left",
          tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.muted },
          titlefont: { family: "system-ui, sans-serif", size: 12, color: THEME.muted },
          outlinewidth: 0,
        },
      },
      {
        type: "choropleth",
        locationmode: "ISO-3",
        locations: selected ? [selected.iso3] : [],
        z: selected && metric.accessor(selected) != null ? [metric.accessor(selected)] : [],
        text: selected ? [countryLabel(selected)] : [],
        hoverinfo: "skip",
        showscale: false,
        colorscale: metric.colorscale,
        zmin: bounds.zmin,
        zmax: bounds.zmax,
        zmid: bounds.zmid,
        marker: {
          line: { color: "rgba(34,211,238,0.95)", width: 3 },
        },
      },
    ],
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 0, r: 0, t: 0, b: 0 },
      geo: {
        projection: { type: "natural earth", scale: 1.06 },
        showframe: false,
        showcountries: true,
        countrycolor: "rgba(148,163,184,0.18)",
        showcoastlines: false,
        landcolor: "rgba(30,41,59,0.92)",
        bgcolor: "rgba(0,0,0,0)",
      },
      font: { family: "system-ui, sans-serif", color: THEME.ink },
      hoverlabel: {
        bgcolor: THEME.hover,
        bordercolor: "rgba(34,211,238,0.22)",
        font: { family: "system-ui, sans-serif", color: THEME.inkBright, size: 13 },
      },
      transition: { duration: 300, easing: "cubic-in-out" },
    },
    {
      responsive: true,
      displayModeBar: false,
      scrollZoom: false,
    },
  );

  const mapNode = document.getElementById("map-chart");
  if (!mapNode.dataset.bound) {
    mapNode.on("plotly_click", (event) => {
      const iso3 = event?.points?.[0]?.location;
      if (!iso3) {
        return;
      }
      state.country = iso3;
      renderPanels();
      updateMapHighlight(iso3);
      openSpotlightModal(iso3);
    });
    mapNode.dataset.bound = "1";
  }
}

function updateMapHighlight(iso3) {
  const mapNode = document.getElementById("map-chart");
  const records = getMapRecords();
  const metric = METRIC_META[state.metric];
  const selected = records.find((row) => row.iso3 === iso3);
  if (!mapNode?.data?.length) {
    return;
  }

  Plotly.restyle(
    mapNode,
    {
      "marker.line.color": [
        records.map((row) =>
          row.iso3 === iso3 ? "rgba(34,211,238,0.72)" : "rgba(148,163,184,0.18)",
        ),
      ],
      "marker.line.width": [records.map((row) => (row.iso3 === iso3 ? 2 : 0.4))],
    },
    [0],
  );

  Plotly.restyle(
    mapNode,
    {
      locations: [selected ? [selected.iso3] : []],
      z: [selected && metric.accessor(selected) != null ? [metric.accessor(selected)] : []],
      text: [selected ? [countryLabel(selected)] : []],
    },
    [1],
  );
}

function buildHoverText(row) {
  if (state.dimension === "dim2") {
    return [
      `<b>${escapeHtml(countryLabel(row))}</b>`,
      `Region: ${escapeHtml(row.who_region ?? "N/A")} / ${escapeHtml(row.wb_income ?? "N/A")}`,
      `Risk: ${escapeHtml(row.risk_name ?? getRiskName(state.risk))}`,
      `${METRIC_META[state.metric].label}: ${escapeHtml(
        METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(row)),
      )}`,
      `Attributable deaths: ${escapeHtml(formatCompact(row.attributable_deaths))}`,
    ].join("<br>");
  }

  if (state.dimension === "dim3") {
    const scenario = getCurrentScenario();
    return [
      `<b>${escapeHtml(countryLabel(row))}</b>`,
      `Region: ${escapeHtml(row.who_region ?? "N/A")} / ${escapeHtml(row.wb_income ?? "N/A")}`,
      `${METRIC_META[state.metric].label}: ${escapeHtml(
        METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(row)),
      )}`,
      `Scenario: ${escapeHtml(scenario?.summary?.label ?? "N/A")}`,
      `Gap: ${escapeHtml(formatSigned(row.gap))}`,
      `Efficiency: ${escapeHtml(formatSigned(row.efficiency))}`,
    ].join("<br>");
  }

  return [
    `<b>${escapeHtml(countryLabel(row))}</b>`,
    `Region: ${escapeHtml(row.who_region ?? "N/A")} / ${escapeHtml(row.wb_income ?? "N/A")}`,
    `${METRIC_META[state.metric].label}: ${escapeHtml(
      METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(row)),
    )}`,
    `Top risk: ${escapeHtml(row.top_risk_name ?? "N/A")}`,
    `Top risk share: ${escapeHtml(formatShare(row.top_risk_share))}`,
  ].join("<br>");
}

function renderCountryPanel() {
  const profile = store.profiles[state.country];
  const latest = profile?.latest ?? {};
  const meta = profile?.meta ?? {};
  const scenarioRow = getScenarioRow(state.country);

  document.getElementById("country-title").textContent = countryLabel(meta) || state.country;
  document.getElementById("country-tag").textContent = `${meta.who_region ?? "N/A"} / ${
    meta.wb_income ?? "N/A"
  }`;

  const title = document.getElementById("country-title");
  title.classList.remove("flash");
  void title.offsetWidth;
  title.classList.add("flash");

  let items = [];
  if (state.dimension === "dim1") {
    items = [
      ["Life Expectancy", METRIC_META.life_expectancy.formatter(latest.life_expectancy), "cyan"],
      ["Communicable Share", formatShare(latest.communicable_share), "amber"],
      ["NCD Share", formatShare(latest.ncd_share), "violet"],
      ["GDP per Capita", formatCurrency(latest.gdp_per_capita), "teal"],
      ["Health Exp / GDP", formatPercentValue(latest.health_exp_pct_gdp), "blue"],
      ["Top Risk", latest.top_risk_name ?? "N/A", "rose"],
    ];
  } else if (state.dimension === "dim2") {
    const selectedRisk = store.riskIndex.get(`${state.country}|${state.risk}`) ?? {};
    items = [
      ["Top Risk", latest.top_risk_name ?? "N/A", "cyan"],
      ["Top Risk Share", formatShare(latest.top_risk_share), "teal"],
      ["Top Risk Deaths", formatCompact(latest.top_risk_deaths), "rose"],
      ["Selected Risk", selectedRisk.risk_name ?? getRiskName(state.risk), "violet"],
      ["Selected Share", formatShare(selectedRisk.share), "amber"],
      ["Selected Deaths", formatCompact(selectedRisk.attributable_deaths), "blue"],
    ];
  } else {
    items = [
      ["Scenario Objective", objectiveLabel(state.objective), "cyan"],
      ["Current Spend", formatCurrency(scenarioRow?.current ?? latest.current), "teal"],
      ["Scenario Optimal", formatCurrency(scenarioRow?.optimal ?? latest.optimal), "blue"],
      ["Recommended Change", formatSignedPercent(scenarioRow?.change_pct ?? latest.change_pct), "violet"],
      ["Resource Gap", formatSigned(latest.gap), "rose"],
      ["Efficiency", formatSigned(latest.efficiency), "amber"],
    ];
  }

  document.getElementById("country-metrics").innerHTML = items
    .map(
      ([label, value, accent]) =>
        `<article class="metric-tile" data-accent="${accent}"><span>${escapeHtml(
          label,
        )}</span><strong>${escapeHtml(value)}</strong></article>`,
    )
    .join("");
}

function renderRankingList() {
  const metric = METRIC_META[state.metric];
  const rows = [...getMapRecords()];
  const descending = !(state.dimension === "dim3" && state.metric === "gap");
  rows.sort((left, right) => {
    const leftValue = metric.accessor(left);
    const rightValue = metric.accessor(right);
    if (descending) {
      return (rightValue ?? -Infinity) - (leftValue ?? -Infinity);
    }
    return (leftValue ?? Infinity) - (rightValue ?? Infinity);
  });

  let caption = "Sorted by current map metric";
  if (state.dimension === "dim2") {
    caption = `${getRiskName(state.risk)} | ${metric.label}`;
  } else if (state.dimension === "dim3" && state.metric === "change_pct") {
    caption = `${objectiveLabel(state.objective)} | ${budgetLabel(state.budgetMultiplier)}`;
  } else if (state.dimension === "dim3" && state.metric === "gap") {
    caption = "Most severe shortage";
  }
  document.getElementById("ranking-caption").textContent = caption;

  const topRows = rows.slice(0, 10);
  const maxValue = Math.max(...topRows.map((row) => Math.abs(metric.accessor(row) ?? 0)), 1e-9);
  document.getElementById("ranking-list").innerHTML = topRows
    .map((row, index) => {
      const progress = Math.round((Math.abs(metric.accessor(row) ?? 0) / maxValue) * 100);
      return `
        <button
          class="ranking-row ${row.iso3 === state.country ? "is-selected" : ""}"
          data-country="${escapeHtml(row.iso3)}"
          data-rank="${index + 1}"
          style="--progress:${progress}%;animation-delay:${index * 45}ms"
          type="button"
        >
          <span class="rank-badge">${index + 1}</span>
          <span class="row-info">
            <b>${escapeHtml(countryLabel(row))}</b>
            <small>${escapeHtml(row.who_region ?? "N/A")} / ${escapeHtml(row.wb_income ?? "N/A")}</small>
          </span>
          <span class="row-value">${escapeHtml(metric.formatter(metric.accessor(row)))}</span>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll(".ranking-row").forEach((button) => {
    button.addEventListener("click", () => {
      state.country = button.dataset.country;
      renderPanels();
      updateMapHighlight(button.dataset.country);
      openSpotlightModal(button.dataset.country);
    });
  });
}

function renderDetailChart() {
  const profile = store.profiles[state.country];
  if (!profile) {
    emptyPlot("detail-chart", "No country profile is available.");
    return;
  }

  if (state.dimension === "dim1") {
    document.getElementById("detail-title").textContent = "Health Outcomes & Disease Structure";
    document.getElementById("detail-pill").textContent = "Life expectancy vs disease shares";
    renderDimension1Detail(profile);
    return;
  }

  if (state.dimension === "dim2") {
    document.getElementById("detail-title").textContent = "Latest Risk Composition";
    document.getElementById("detail-pill").textContent = "Top attributable factors";
    renderDimension2Detail(profile);
    return;
  }

  document.getElementById("detail-title").textContent = "Selected Country Scenario";
  document.getElementById("detail-pill").textContent = "Historical spend vs scenario target";
  renderDimension3Detail(profile);
}

function renderDimension1Detail(profile) {
  const trend = profile.trend ?? [];
  if (!trend.length) {
    emptyPlot("detail-chart", "No historical trend is available.");
    return;
  }

  Plotly.react(
    "detail-chart",
    [
      {
        x: trend.map((row) => row.year),
        y: trend.map((row) => row.life_expectancy),
        name: "Life Expectancy",
        mode: "lines+markers",
        line: { color: THEME.cyan, width: 3, shape: "spline" },
        marker: { size: 6, color: THEME.cyan },
        fill: "tozeroy",
        fillcolor: "rgba(34,211,238,0.08)",
      },
      {
        x: trend.map((row) => row.year),
        y: trend.map((row) => percentValue(row.communicable_share)),
        name: "Communicable",
        mode: "lines",
        yaxis: "y2",
        line: { color: THEME.amber, width: 2.5, shape: "spline" },
      },
      {
        x: trend.map((row) => row.year),
        y: trend.map((row) => percentValue(row.ncd_share)),
        name: "NCD",
        mode: "lines",
        yaxis: "y2",
        line: { color: THEME.violet, width: 2.5, shape: "spline" },
      },
    ],
    baseLayout({
      yaxis: { title: "Years" },
      yaxis2: {
        overlaying: "y",
        side: "right",
        title: "Share (%)",
        gridcolor: "rgba(0,0,0,0)",
      },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderDimension2Detail(profile) {
  const risks = [...(profile.latest_risks ?? [])].slice(0, 6).reverse();
  if (!risks.length) {
    emptyPlot("detail-chart", "No latest risk attribution records are available.");
    return;
  }

  Plotly.react(
    "detail-chart",
    [
      {
        type: "bar",
        x: risks.map((row) => percentValue(row.share)),
        y: risks.map((row) => row.risk_name),
        orientation: "h",
        marker: {
          color: risks.map((_, index) => colorFromPalette(index)),
          cornerradius: 6,
          line: { width: 0 },
        },
        customdata: risks.map((row) => row.attributable_deaths),
        hovertemplate: "<b>%{y}</b><br>Share: %{x:.2f}%<br>Attributable deaths: %{customdata:.0f}<extra></extra>",
      },
    ],
    baseLayout({
      xaxis: { title: "Share (%)" },
      yaxis: { automargin: true },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderDimension3Detail(profile) {
  const trend = profile.trend ?? [];
  const scenarioRow = getScenarioRow(state.country);
  const latest = profile.latest ?? {};
  const currentValue = scenarioRow?.current ?? latest.current ?? latest.health_exp_per_capita;
  const optimalValue = scenarioRow?.optimal ?? latest.optimal;

  if (!trend.length && currentValue == null && optimalValue == null) {
    emptyPlot("detail-chart", "No allocation data is available for this country.");
    return;
  }

  const traces = [];
  if (trend.length) {
    traces.push({
      x: trend.map((row) => row.year),
      y: trend.map((row) => row.health_exp_per_capita),
      name: "Historical spend per capita",
      mode: "lines+markers",
      line: { color: THEME.teal, width: 3, shape: "spline" },
      marker: { size: 5, color: THEME.teal },
    });
  }

  if (optimalValue != null && trend.length) {
    traces.push({
      x: trend.map((row) => row.year),
      y: trend.map(() => optimalValue),
      name: "Scenario target",
      mode: "lines",
      line: { color: THEME.blue, width: 2, dash: "dash" },
    });
  }

  if (currentValue != null && optimalValue != null) {
    traces.push({
      type: "bar",
      x: ["Current", "Scenario target"],
      y: [currentValue, optimalValue],
      name: "Current vs target",
      marker: {
        color: [THEME.violet, THEME.cyan],
        line: { width: 0 },
      },
      opacity: 0.34,
      yaxis: trend.length ? "y3" : "y",
      hovertemplate: "<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    });
  }

  const layout = trend.length
    ? baseLayout({
        yaxis: { title: "US$ per capita" },
        yaxis3: {
          overlaying: "y",
          side: "right",
          title: "Current vs target",
          showgrid: false,
        },
      })
    : baseLayout({
        yaxis: { title: "US$ per capita" },
      });

  Plotly.react("detail-chart", traces, layout, {
    responsive: true,
    displayModeBar: false,
    scrollZoom: false,
  });
}

function renderCompanionChart() {
  if (state.dimension === "dim1") {
    document.getElementById("companion-title").textContent = "Global Disease Transition";
    document.getElementById("companion-pill").textContent = "2000-2023";
    renderGlobalDiseaseTrend();
    return;
  }

  if (state.dimension === "dim2") {
    document.getElementById("companion-title").textContent = "Risk-to-Region Flow";
    document.getElementById("companion-pill").textContent = "Sankey overview";
    renderRiskSankey();
    return;
  }

  document.getElementById("companion-title").textContent = "Scenario Winners & Donors";
  document.getElementById("companion-pill").textContent = budgetLabel(state.budgetMultiplier);
  renderOptimizationBar();
}

function renderGlobalDiseaseTrend() {
  const trend = store.globalStory.global_disease_trends ?? [];
  if (!trend.length) {
    emptyPlot("companion-chart", "No global trend artifact is available.");
    return;
  }

  Plotly.react(
    "companion-chart",
    [
      lineTrace(trend, "year", "communicable_share", "Communicable", THEME.amber, true),
      lineTrace(trend, "year", "ncd_share", "NCD", THEME.teal, true),
      lineTrace(trend, "year", "injury_share", "Injuries", THEME.rose, true),
    ],
    baseLayout({
      yaxis: { title: "Share of global deaths", tickformat: ".0%" },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderRiskSankey() {
  const sankey = store.globalStory.sankey;
  if (!sankey?.nodes?.length) {
    emptyPlot("companion-chart", "No Sankey artifact is available.");
    return;
  }

  Plotly.react(
    "companion-chart",
    [
      {
        type: "sankey",
        arrangement: "snap",
        node: {
          label: sankey.nodes,
          pad: 16,
          thickness: 18,
          line: { color: "rgba(148,163,184,0.12)", width: 0.5 },
          color: sankey.nodes.map((node) =>
            node.includes("RO") || node.includes("PRO")
              ? "rgba(167,139,250,0.72)"
              : "rgba(34,211,238,0.72)",
          ),
        },
        link: {
          source: sankey.sources,
          target: sankey.targets,
          value: sankey.values,
          color: "rgba(148,163,184,0.10)",
        },
        hoverlabel: {
          bgcolor: THEME.hover,
          bordercolor: "rgba(34,211,238,0.18)",
          font: { family: "system-ui, sans-serif", color: THEME.inkBright },
        },
      },
    ],
    baseLayout({
      margin: { l: 12, r: 12, t: 10, b: 10 },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderOptimizationBar() {
  const scenario = getCurrentScenario();
  const rows = [...(scenario?.allocation ?? [])]
    .filter((row) => row.change_pct != null)
    .sort((left, right) => Math.abs(right.change_pct) - Math.abs(left.change_pct))
    .slice(0, 14)
    .reverse();

  if (!rows.length) {
    emptyPlot("companion-chart", "No optimization scenario rows are available.");
    return;
  }

  Plotly.react(
    "companion-chart",
    [
      {
        type: "bar",
        x: rows.map((row) => row.change_pct),
        y: rows.map((row) => countryLabel(row)),
        orientation: "h",
        marker: {
          color: rows.map((row) => (row.change_pct >= 0 ? THEME.cyan : THEME.rose)),
          cornerradius: 6,
          line: { width: 0 },
        },
        customdata: rows.map((row) => [row.current, row.optimal]),
        hovertemplate:
          "<b>%{y}</b><br>Change: %{x:.1f}%<br>Current: $%{customdata[0]:,.0f}<br>Target: $%{customdata[1]:,.0f}<extra></extra>",
      },
    ],
    baseLayout({
      xaxis: { title: "Recommended change (%)" },
      yaxis: { automargin: true },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderContextPanel() {
  if (state.dimension === "dim1") {
    document.getElementById("context-title").textContent = "Global Extremes & Structural Contrast";
    renderDim1Context();
    return;
  }

  if (state.dimension === "dim2") {
    document.getElementById("context-title").textContent = "Regional Priority Stack";
    renderDim2Context();
    return;
  }

  document.getElementById("context-title").textContent = "Optimization Lab Summary";
  renderDim3Context();
}

function renderDim1Context() {
  const countries = [...(store.overview.countries ?? [])];
  const topLife = countries
    .filter((row) => row.life_expectancy != null)
    .sort((left, right) => right.life_expectancy - left.life_expectancy)
    .slice(0, 6);
  const bottomLife = countries
    .filter((row) => row.life_expectancy != null)
    .sort((left, right) => left.life_expectancy - right.life_expectancy)
    .slice(0, 6);
  const communicable = countries
    .filter((row) => row.communicable_share != null)
    .sort((left, right) => right.communicable_share - left.communicable_share)
    .slice(0, 6);

  document.getElementById("context-panel").innerHTML = renderContextColumns([
    {
      title: "Highest life expectancy",
      items: topLife.map((row) => ({ name: countryLabel(row), value: `${formatDecimal(row.life_expectancy)} yrs` })),
    },
    {
      title: "Lowest life expectancy",
      items: bottomLife.map((row) => ({ name: countryLabel(row), value: `${formatDecimal(row.life_expectancy)} yrs` })),
    },
    {
      title: "Highest communicable burden",
      items: communicable.map((row) => ({ name: countryLabel(row), value: formatShare(row.communicable_share) })),
    },
  ]);
}

function renderDim2Context() {
  const rows = store.globalStory.region_priority ?? [];
  document.getElementById("context-panel").innerHTML = renderContextColumns(
    rows.map((row) => ({
      title: row.who_region,
      items: [
        { name: `1. ${row.primary_risk ?? "N/A"}`, value: formatShare(row.primary_share) },
        { name: `2. ${row.secondary_risk ?? "N/A"}`, value: formatShare(row.secondary_share) },
        { name: `3. ${row.tertiary_risk ?? "N/A"}`, value: formatShare(row.tertiary_share) },
      ],
    })),
  );
}

function renderDim3Context() {
  const scenario = getCurrentScenario();
  const profile = store.profiles[state.country];
  const latest = profile?.latest ?? {};
  const selected = getScenarioRow(state.country);
  const recipients = [...(scenario?.allocation ?? [])]
    .filter((row) => (row.change ?? 0) > 0)
    .sort((left, right) => (right.change_pct ?? -Infinity) - (left.change_pct ?? -Infinity))
    .slice(0, 5);
  const donors = [...(scenario?.allocation ?? [])]
    .filter((row) => (row.change ?? 0) < 0)
    .sort((left, right) => (left.change_pct ?? Infinity) - (right.change_pct ?? Infinity))
    .slice(0, 5);

  const summaryGrid = `
    <div class="lab-summary-grid">
      ${renderLabStat("Scenario", scenario?.summary?.label ?? "N/A")}
      ${renderLabStat("Budget envelope", scenario?.summary?.budget_label ?? budgetLabel(state.budgetMultiplier))}
      ${renderLabStat("Recipient countries", formatInteger(scenario?.summary?.recipient_count))}
      ${renderLabStat("Donor countries", formatInteger(scenario?.summary?.donor_count))}
      ${renderLabStat("Budget moved", formatCurrency(scenario?.summary?.moved_budget))}
      ${renderLabStat("Top recipient", scenario?.summary?.top_recipient ?? "N/A")}
    </div>
  `;

  const detailColumn = {
    title: countryLabel(profile?.meta ?? store.overviewIndex.get(state.country)),
    items: [
      { name: "Current spend", value: formatCurrency(selected?.current ?? latest.current) },
      { name: "Scenario target", value: formatCurrency(selected?.optimal ?? latest.optimal) },
      { name: "Recommended change", value: formatSignedPercent(selected?.change_pct ?? latest.change_pct) },
      { name: "Resource gap", value: formatSigned(latest.gap) },
      { name: "Efficiency", value: formatSigned(latest.efficiency) },
    ],
  };

  document.getElementById("context-panel").innerHTML = `
    <p class="context-lede">${escapeHtml(
      OBJECTIVE_META[state.objective]?.note ?? "Scenario settings are applied to the latest resource panel.",
    )}</p>
    ${summaryGrid}
    ${renderContextColumns([
      {
        title: "Top recipients",
        items: recipients.map((row) => ({ name: countryLabel(row), value: formatSignedPercent(row.change_pct) })),
      },
      {
        title: "Top donors",
        items: donors.map((row) => ({ name: countryLabel(row), value: formatSignedPercent(row.change_pct) })),
      },
      detailColumn,
    ])}
  `;
}

function renderLabStat(label, value) {
  return `<article class="lab-stat"><span>${escapeHtml(label)}</span><strong>${escapeHtml(
    value ?? "N/A",
  )}</strong></article>`;
}

function renderContextColumns(columns) {
  return `<div class="context-grid">${columns
    .map(
      (column) => `
        <section class="context-column">
          <div class="col-header"><span class="col-dot"></span><h3>${escapeHtml(column.title)}</h3></div>
          ${(column.items ?? [])
            .map(
              (item) => `
                <div class="context-item">
                  <span class="ctx-name">${escapeHtml(item.name)}</span>
                  <span class="ctx-value">${escapeHtml(item.value)}</span>
                </div>
              `,
            )
            .join("")}
        </section>
      `,
    )
    .join("")}</div>`;
}

function openSpotlightModal(iso3) {
  state.dialogOpen = true;
  state.dialogCountry = iso3;
  state.previousFocus = document.activeElement;

  const backdrop = document.getElementById("spotlight-backdrop");
  const modal = document.getElementById("spotlight-modal");
  backdrop.classList.add("is-open");
  backdrop.setAttribute("aria-hidden", "false");
  modal.classList.add("is-open");
  modal.setAttribute("aria-hidden", "false");

  document.body.style.overflow = "hidden";
  renderSpotlightContent(iso3);
  window.requestAnimationFrame(() => {
    document.getElementById("spotlight-close").focus();
  });
}

function renderSpotlightContent(iso3) {
  const profile = store.profiles[iso3];
  if (!profile) {
    return;
  }

  const meta = profile.meta ?? {};
  const latest = profile.latest ?? {};
  const risks = profile.latest_risks ?? [];
  const scenarioRow = getScenarioRow(iso3);

  document.getElementById("spotlight-name").textContent = countryLabel(meta) || iso3;
  document.getElementById("spotlight-flag-fallback").textContent = iso3;
  document.getElementById("spotlight-badges").innerHTML = [
    meta.who_region
      ? `<span class="spotlight-badge" data-type="region">${escapeHtml(meta.who_region)}</span>`
      : "",
    meta.wb_income
      ? `<span class="spotlight-badge" data-type="income">${escapeHtml(meta.wb_income)}</span>`
      : "",
  ].join("");

  const metrics = [
    ["Life Expectancy", METRIC_META.life_expectancy.formatter(latest.life_expectancy), "cyan"],
    ["NCD Share", formatShare(latest.ncd_share), "violet"],
    ["Communicable Share", formatShare(latest.communicable_share), "amber"],
    ["GDP per Capita", formatCurrency(latest.gdp_per_capita), "teal"],
    ["Health Exp / GDP", formatPercentValue(latest.health_exp_pct_gdp), "blue"],
    ["Top Risk", latest.top_risk_name ?? "N/A", "rose"],
    ["Scenario Target", formatCurrency(scenarioRow?.optimal ?? latest.optimal), "emerald"],
    ["Resource Gap", formatSigned(latest.gap), "cyan"],
  ];

  document.getElementById("spotlight-metrics").innerHTML = metrics
    .map(
      ([label, value, accent]) =>
        `<div class="spotlight-metric" data-accent="${accent}"><span class="sm-label">${escapeHtml(
          label,
        )}</span><span class="sm-value">${escapeHtml(value)}</span></div>`,
    )
    .join("");

  renderSpotlightChart(profile.trend ?? [], scenarioRow?.optimal ?? latest.optimal);
  renderSpotlightRisks(risks);
  renderSpotlightAllocation(scenarioRow, latest);
}

function renderSpotlightChart(trend, optimalValue) {
  if (!trend.length) {
    emptyPlot("spotlight-chart", "No historical trend is available.");
    return;
  }

  const traces = [
    {
      x: trend.map((row) => row.year),
      y: trend.map((row) => row.life_expectancy),
      mode: "lines",
      name: "Life Expectancy",
      line: { color: THEME.cyan, width: 2.5, shape: "spline" },
      fill: "tozeroy",
      fillcolor: "rgba(34,211,238,0.08)",
      hovertemplate: "<b>%{x}</b><br>%{y:.1f} yrs<extra></extra>",
    },
  ];

  if (optimalValue != null) {
    traces.push({
      x: trend.map((row) => row.year),
      y: trend.map(() => optimalValue),
      mode: "lines",
      name: "Scenario target",
      line: { color: THEME.blue, width: 1.8, dash: "dash" },
      hovertemplate: "<b>Scenario target</b><br>$%{y:,.0f}<extra></extra>",
      yaxis: "y2",
    });
  }

  Plotly.react(
    "spotlight-chart",
    traces,
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 36, r: 18, t: 6, b: 28 },
      font: { family: "system-ui, sans-serif", color: THEME.dim },
      xaxis: { gridcolor: THEME.grid, linecolor: THEME.grid, tickfont: { size: 10, color: THEME.dim } },
      yaxis: { gridcolor: THEME.grid, linecolor: THEME.grid, tickfont: { size: 10, color: THEME.dim } },
      yaxis2: {
        overlaying: "y",
        side: "right",
        showgrid: false,
        tickfont: { size: 10, color: THEME.dim },
      },
      hoverlabel: {
        bgcolor: THEME.hover,
        bordercolor: "rgba(34,211,238,0.20)",
        font: { family: "system-ui, sans-serif", color: THEME.inkBright, size: 12 },
      },
    },
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderSpotlightRisks(risks) {
  const container = document.getElementById("spotlight-risks");
  if (!risks.length) {
    container.innerHTML = '<span class="empty-inline">No risk attribution rows are available.</span>';
    return;
  }

  const topRows = risks.slice(0, 6);
  const maxShare = Math.max(...topRows.map((row) => row.share ?? 0), 0.01);
  container.innerHTML = topRows
    .map((row, index) => {
      const pct = (((row.share ?? 0) / maxShare) * 100).toFixed(1);
      return `
        <div class="spotlight-risk-row">
          <div class="spotlight-risk-label">
            <span class="sr-name">${escapeHtml(row.risk_name)}</span>
            <span class="sr-value">${escapeHtml(formatShare(row.share))}</span>
          </div>
          <div class="spotlight-risk-track">
            <div class="spotlight-risk-fill" style="width:${pct}%;background:${colorFromPalette(index)};"></div>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderSpotlightAllocation(scenarioRow, latest) {
  const container = document.getElementById("spotlight-allocation");
  const items = [
    ["Current spend", formatCurrency(scenarioRow?.current ?? latest.current)],
    ["Scenario target", formatCurrency(scenarioRow?.optimal ?? latest.optimal)],
    ["Recommended change", formatSignedPercent(scenarioRow?.change_pct ?? latest.change_pct)],
    ["Efficiency", formatSigned(latest.efficiency)],
  ];

  container.innerHTML = items
    .map(
      ([label, value]) =>
        `<div class="spotlight-alloc-item"><span class="sa-label">${escapeHtml(
          label,
        )}</span><span class="sa-value">${escapeHtml(value)}</span></div>`,
    )
    .join("");
}

function closeSpotlightModal() {
  if (!state.dialogOpen) {
    return;
  }

  state.dialogOpen = false;
  const backdrop = document.getElementById("spotlight-backdrop");
  const modal = document.getElementById("spotlight-modal");
  backdrop.classList.remove("is-open");
  backdrop.setAttribute("aria-hidden", "true");
  modal.classList.remove("is-open");
  modal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";

  if (state.previousFocus && typeof state.previousFocus.focus === "function") {
    state.previousFocus.focus();
  }
}

function trapDialogFocus(event) {
  const modal = document.getElementById("spotlight-modal");
  const focusable = modal.querySelectorAll(
    'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
  );

  if (!focusable.length) {
    event.preventDefault();
    modal.focus();
    return;
  }

  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function emptyPlot(targetId, message) {
  Plotly.react(
    targetId,
    [],
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 16, r: 16, t: 16, b: 16 },
      xaxis: { visible: false },
      yaxis: { visible: false },
      annotations: [
        {
          x: 0.5,
          y: 0.5,
          xref: "paper",
          yref: "paper",
          text: message,
          showarrow: false,
          font: { family: "system-ui, sans-serif", size: 13, color: THEME.muted },
        },
      ],
    },
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function lineTrace(records, xKey, yKey, name, color, percentage = false) {
  return {
    x: records.map((row) => row[xKey]),
    y: records.map((row) => row[yKey]),
    mode: "lines",
    name,
    line: { color, width: 3, shape: "spline" },
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
    font: { family: "system-ui, sans-serif", color: THEME.muted },
    xaxis: {
      gridcolor: THEME.grid,
      zerolinecolor: "rgba(148,163,184,0.12)",
      linecolor: THEME.grid,
      ticks: "",
      tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.dim },
    },
    yaxis: {
      gridcolor: THEME.grid,
      zerolinecolor: "rgba(148,163,184,0.12)",
      linecolor: THEME.grid,
      ticks: "",
      tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.dim },
    },
    legend: {
      orientation: "h",
      yanchor: "bottom",
      y: 1.02,
      xanchor: "left",
      x: 0,
      font: { color: THEME.muted, size: 12 },
    },
    hoverlabel: {
      bgcolor: THEME.hover,
      bordercolor: "rgba(34,211,238,0.20)",
      font: { family: "system-ui, sans-serif", color: THEME.inkBright, size: 13 },
    },
    transition: { duration: 300, easing: "cubic-in-out" },
    ...extra,
  };
}

function renderFailure(error) {
  document.body.innerHTML = `<pre style="padding:24px;color:#fb7185;background:#0f172a;font-family:ui-monospace,monospace;min-height:100vh;">Dashboard failed to load:\n${escapeHtml(
    String(error),
  )}</pre>`;
}

function objectiveLabel(value) {
  return OBJECTIVE_META[normalizeObjective(value)]?.label ?? "Optimization";
}

function objectiveRank(value) {
  return normalizeObjective(value) === "maximin" ? 2 : 1;
}

function normalizeObjective(value) {
  const key = safeLower(value);
  return OBJECTIVE_ALIASES[key] ?? "max_output";
}

function makeScenarioId(objective, budgetMultiplier, index) {
  return `${objective}_${budgetMultiplier.toFixed(1).replace(".", "p")}_${index + 1}`;
}

function budgetLabel(value) {
  const numeric = normalizeBudget(value);
  const delta = (numeric - 1) * 100;
  if (Math.abs(delta) < 1e-9) {
    return "Current budget";
  }
  return `${delta > 0 ? "+" : ""}${delta.toFixed(0)}% budget`;
}

function normalizeBudget(value) {
  return Number.parseFloat(value ?? 1) || 1;
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

function getRiskName(riskCode) {
  const row = (store.riskLatest.available_risks ?? []).find((risk) => risk.risk_code === riskCode);
  return row?.risk_name ?? riskCode ?? "N/A";
}

function colorFromPalette(index) {
  const palette = [THEME.cyan, THEME.blue, THEME.teal, THEME.violet, THEME.amber, THEME.rose];
  return palette[index % palette.length];
}

function countryLabel(record) {
  return record?.country_name ?? record?.name ?? record?.iso3 ?? "Unknown";
}

function normalizeNumber(value) {
  if (value == null || value === "") {
    return null;
  }
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

function percentValue(value) {
  return value == null ? null : Number(value) * 100;
}

function formatDecimal(value) {
  return value == null ? "N/A" : Number(value).toFixed(2);
}

function formatInteger(value) {
  return value == null ? "N/A" : Number(value).toLocaleString("en-US", { maximumFractionDigits: 0 });
}

function formatShare(value) {
  return value == null ? "N/A" : `${(Number(value) * 100).toFixed(1)}%`;
}

function formatPercentValue(value) {
  return value == null ? "N/A" : `${Number(value).toFixed(1)}%`;
}

function formatSigned(value) {
  return value == null ? "N/A" : `${Number(value) > 0 ? "+" : ""}${Number(value).toFixed(2)}`;
}

function formatSignedPercent(value) {
  return value == null ? "N/A" : `${Number(value) > 0 ? "+" : ""}${Number(value).toFixed(1)}%`;
}

function formatCurrency(value) {
  if (value == null) {
    return "N/A";
  }
  return `$${Number(value).toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
}

function formatCompact(value) {
  if (value == null) {
    return "N/A";
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

function uniqueValues(values) {
  return [...new Set(values)];
}

function sumValues(values) {
  return values.reduce((sum, value) => sum + (value ?? 0), 0);
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
