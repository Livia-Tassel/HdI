# Dashboard UI Rebuild — Light Theme Design Spec

**Date:** 2026-04-21
**Scope:** `dashboard/` (static site — `index.html`, `styles.css`, `app.js`)
**Reference:** `https://data.who.int/dashboards/covid19/cases?n=c` (WHO COVID-19 dashboard)
**Authored by:** Claude (Opus 4.7), with user directive "do whatever you want, just go for it"

---

## 1. Goals

1. Convert the entire dashboard from its current **dark glass-morphism** theme to a **light, airy, data-journalism aesthetic** modelled on the WHO dashboard reference.
2. Replace the two-step search interaction (`type → click 定位`) with a **single-click combobox**: focusing the input reveals a filterable dropdown; selecting an option immediately locks the country and opens its detail view.
3. Elevate overall visual polish: refined typography scale, restrained accent palette, subtle motion, WHO-aligned data-viz colours.

### Success criteria

- No dark backgrounds anywhere in the dashboard chrome or Plotly charts.
- No `定位` button exists; selecting any option from the country / province picker instantly updates `state.country`/`state.province` and re-renders.
- All 5 dimensions (Dim1–Dim5) and the spotlight modal render without regression.
- Typography, spacing, and motion feel deliberately crafted — not templated.

---

## 2. Current State (baseline)

- `index.html` (186 lines): masthead, 5-dimension control bar, control cluster with country `<input list=country-list>` + `#country-jump` button, year slider, 5-card grid, spotlight modal.
- `styles.css` (2028 lines): dark tokens (`--bg: #060a13`), glass cards (`backdrop-filter: blur(24px)`), animated orbs, noise overlay, conic-gradient glow border on map card, text-shimmer gradients.
- `app.js` (4636 lines): `THEME` object at line 466 (dark palette), Plotly layouts use `paper_bgcolor: "rgba(0,0,0,0)"` throughout and inherit dark ink colours. Search logic at lines 943–1050 uses two-step flow.

---

## 3. Visual System

### 3.1 Palette

```
Surfaces (all near-white, not pure white to reduce eye strain)
  --bg         #F7F8FB   page background
  --surface    #FFFFFF   cards
  --surface-2  #F2F4F8   recessed zones (summary strip fill, disabled rows)
  --line       #E3E7EE   hairline borders
  --line-soft  #EEF1F6   very soft separators

Ink (typographic scale on light)
  --ink        #0F172A   headings
  --ink-body   #1F2937   body text
  --muted      #4B5563   secondary
  --dim        #6B7280   tertiary / metadata
  --placeholder #9CA3AF  input placeholders

Brand (single primary + one cool-warm complement)
  --primary    #0B6FB8   WHO-style steady blue — links, active chips, focus rings
  --primary-50 #E6F0F8   primary tint
  --primary-ink #084E82  primary hover / deep accent
  --accent-coral #E86A4F inspired by WHO Americas marker

Data-viz categorical (WHO regions, from reference image)
  AFRO  #6D5FB0   purple
  AMRO  #E86A4F   coral
  EMRO  #B87FC0   mauve (slightly shifted; reference was similar)
  EURO  #3A8CCF   azure
  SEARO #4CB58F   sea green
  WPRO  #E7A64A   amber

Data-viz sequential (maps)
  Single-hue blue scale:  #EEF5FB → #CBDEF0 → #8FB8DE → #4A8FC4 → #0B6FB8 → #084E82
Data-viz diverging (Dim3 change_pct, gap, efficiency)
  Negative #C0432C → #E86A4F → #F6C6B7 → #F7F8FB → #B3D3EC → #4A8FC4 → #0B6FB8
```

### 3.2 Typography

- Display: `"Alibaba PuHuiTi 3.0", "PingFang SC", "Hiragino Sans GB", system-ui, sans-serif` (drop the heavier "Alimama ShuHeiTi" display face — its weight fights with a light, airy surface).
- Body: same stack, regular weight.
- Mono: `"IBM Plex Mono", "SF Mono", Menlo, monospace` for numbers.
- Base size: 14px. Headings 600; body 400; numbers 500 with `font-feature-settings: "tnum" 1`.

### 3.3 Shape & elevation

- Cards: `border-radius: 14px` (down from 24px — less "balloon-y"), 1px `--line` border, **no** backdrop-filter, very subtle shadow (`0 1px 2px rgba(15,23,42,.04), 0 2px 8px rgba(15,23,42,.04)`).
- Hover lift: translate −1px, shadow deepens to `0 1px 2px rgba(15,23,42,.05), 0 6px 18px rgba(15,23,42,.06)`.
- Remove: animated orbs, noise texture overlay, physics canvas, conic-gradient rotating glow border, text-shimmer animations, ripple overlays.

### 3.4 Motion

- Ease curves retained (`ease-out-expo`, `ease-smooth`), durations shortened (250–300ms typical, 400ms maximum).
- Keep: dashboard-grid fade on dimension switch, spotlight slide-in, summary-tile hover lift.
- Drop: all infinite animations (orbs, glow rotation, brand shimmer, gradient-text shimmer).

---

## 4. Interaction Changes

### 4.1 Country / Province combobox (the main UX ask)

Replace the native `<input list>` + `#country-jump` button with a **custom combobox**:

**Markup (new)**
```html
<div class="combobox" id="country-combobox">
  <input
    id="country-search"
    class="combobox-input"
    type="text"
    role="combobox"
    aria-expanded="false"
    aria-autocomplete="list"
    aria-controls="country-listbox"
    placeholder="搜索国家或地区"
    autocomplete="off"
  />
  <button class="combobox-clear" type="button" aria-label="清除" hidden>×</button>
  <ul id="country-listbox" class="combobox-listbox" role="listbox" hidden></ul>
</div>
```

**Behaviour**
1. On **focus / click**: listbox opens showing all (up to 240) options. If a country is already selected, scroll it into view and mark `aria-selected`.
2. On **input**: filter options by substring match against both Chinese name and ISO3 code, case-insensitive. Keep the dropdown open. If empty, show "无匹配结果".
3. On **option click** or **Enter** on a highlighted row: set `state.country` (or `state.province` in Dim4), call the same downstream functions as the current `handleCountryJump` (`renderPanels`, `updateMapHighlight`, `openSpotlightModal`) — all in one user action.
4. On **ArrowDown / ArrowUp**: move highlight within the listbox.
5. On **Escape / blur outside**: close the listbox without changing state.
6. **Remove** `<button id="country-jump">` and its ripple styles.

Both Dim1–3,5 (countries) and Dim4 (provinces) use the same combobox; `syncSearchField` / `syncProvinceSearch` populate the option list for the active mode.

### 4.2 Dimension chips

Keep the 5-button switch; restyle as pill tabs with a thin underline for the active state rather than a filled cyan background. This keeps the switch visible on a light surface without looking noisy.

### 4.3 Summary strip

Retain 4 tiles but as flat rounded rectangles with a 2px left accent in the region's colour instead of the current glow bar. Drop the hover lift to just a colour shift (no transform) to feel calmer.

### 4.4 Year slider + play button

Restyle track to light gray with blue-filled progress. Play button is a 32px circular icon-only button using `--primary`.

### 4.5 Spotlight modal

Invert to light surface (`--surface` card), same structure. Metric cards go white-on-white with a coloured number. Flag block keeps rounded-corner fallback, just lightened.

---

## 5. Plotly layout overhaul

Replace every dark chart with a neutral light layout. Centralised in a new `PLOT_LAYOUT_BASE` helper:

```js
const THEME = {
  ink: "#0F172A",
  inkBody: "#1F2937",
  muted: "#4B5563",
  dim: "#6B7280",
  grid: "#E3E7EE",
  gridSoft: "#EEF1F6",
  primary: "#0B6FB8",
  coral: "#E86A4F",
  // … region colours, diverging palettes …
};

function basePlotLayout(extra = {}) {
  return {
    paper_bgcolor: "#FFFFFF",
    plot_bgcolor: "#FFFFFF",
    font: { family: "var(--font-body)", color: THEME.inkBody, size: 12 },
    margin: { l: 44, r: 20, t: 28, b: 40 },
    xaxis: { gridcolor: THEME.gridSoft, linecolor: THEME.grid, tickfont: { color: THEME.muted } },
    yaxis: { gridcolor: THEME.gridSoft, linecolor: THEME.grid, tickfont: { color: THEME.muted } },
    hoverlabel: { bgcolor: "#FFFFFF", bordercolor: THEME.grid, font: { color: THEME.ink } },
    ...extra,
  };
}
```

### 5.1 Map (Plotly `geo`)

- `geo.bgcolor: "#FFFFFF"`, `geo.landcolor: "#F4F6FA"`, `geo.lakecolor: "#FFFFFF"`, `geo.coastlinecolor: "#C6CCD4"`, `geo.showframe: false`, `geo.projection.type: "robinson"` (matches WHO reference) — fallback to `"natural earth"` if Robinson renders poorly.
- Choropleth uses the single-hue blue sequential scale (Dim1 metrics), or the diverging red-to-blue (Dim3 change_pct). Risk-factor map (Dim2) uses a warm coral-amber sequential for share.

### 5.2 Colorscales in `METRIC_META`

Each `colorscale` array is rewritten; see § 3.1 for the palettes. Diverging metrics (`change_pct`, `gap`, `efficiency`) pivot around a near-white midpoint.

---

## 6. File-level impact

| File | Change magnitude |
|------|---|
| `dashboard/styles.css` | **Major rewrite**: tokens, surface/card, control bar, dimension chips, summary tiles, combobox (new), search cluster, spotlight modal, scrollbar. ~600–900 lines changed. |
| `dashboard/index.html` | **Targeted edits**: replace search field markup with combobox, remove `#country-jump` button, remove decorative noise/orb/physics-canvas nodes if present, minor class adjustments. |
| `dashboard/app.js` | **Targeted edits**: rewrite `THEME` object; introduce `basePlotLayout` helper; update every `Plotly.react`/`newPlot` call to spread it; rewrite all `colorscale` entries in `METRIC_META`; replace `handleCountryJump` + `syncSearchField` + `syncProvinceSearch` with new combobox module (~200 LOC). |
| `dashread.md` | Update the "视觉风格" section to describe the light theme. |

No behavioural changes to data pipelines, state management, dimension logic, or the 10 JSON contracts under `dashboard/data/`.

---

## 7. Risks & tradeoffs

- **Plotly light theme is tone-sensitive.** Thin gridlines on white require careful alpha — too strong looks busy, too faint disappears. Mitigation: chosen values (#E3E7EE / #EEF1F6) are from the WHO reference and tested visually.
- **Custom combobox replaces a native control.** Loses native browser autocomplete/history but gains click-to-open and immediate-lock. The spec's keyboard handling preserves accessibility parity.
- **Removing backdrop-filter & animated orbs** may feel "flatter" to a user who expected a glossy aesthetic. This is the intended shift: WHO-style dashboards lead with data, not chrome.
- **Testing.** Unit tests are not applicable to a static site; verification is manual (open `index.html` in a browser, click through all 5 dimensions, verify the spotlight opens, verify country and province combobox behaviour).

---

## 8. Out of scope

- Re-layout of the 4-card grid (keep current areas).
- Changes to data JSON schema.
- Mobile responsive redesign beyond preserving current breakpoints.
- Any modifications to `src/hdi/` pipeline code.

---

## 9. Implementation phasing

1. **Design tokens + base chrome** (tokens, page shell, cards, masthead).
2. **Control bar + combobox** (the interaction change).
3. **Dashboard grid cards** (card-topline, insight-card, chart-card, context-card).
4. **Plotly theme centralisation** (`THEME` + `basePlotLayout` + `METRIC_META` colorscales).
5. **Spotlight modal**.
6. **Cleanup pass** (remove orbs/noise/physics, update `dashread.md`).
7. **Visual verification** in Chrome.
