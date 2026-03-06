# Demo Video Script

## Duration: 5-8 minutes

---

### Opening (0:00 - 0:30)
- Title card: "Health Data Insight: Global Health Ecosystem Analysis"
- Team introduction
- Brief overview: "We analyze global health data across 200+ countries to uncover disease burden patterns, risk factor contributions, and resource allocation efficiency."

### Section 1: Data Pipeline (0:30 - 1:30)
- Show data sources (5 provided + external)
- Demonstrate Heywhale notebook execution
- Show master_panel.parquet assembly
- Quick EDA: panel dimensions, missing data visualization

### Section 2: Dimension 1 - Spatiotemporal Analysis (1:30 - 3:00)
- Animated choropleth: DALY rate evolution 2000-2023
- LISA cluster map: hot spots / cold spots
- Mann-Kendall trend heatmap
- Panel regression results table (Driscoll-Kraay SEs)
- SHAP beeswarm plot
- Causal DAG visualization
- Forecast fan charts for representative countries

### Section 3: Dimension 2 - Risk Attribution (3:00 - 4:30)
- PAF stacked bar chart by WHO region
- Shapley waterfall plot for China
- Sankey diagram: Risk → Disease → Outcome
- Scenario simulator: show 4 scenarios for China
- Monte Carlo fan charts with 95% CI
- Cost-effectiveness frontier

### Section 4: Dimension 3 - Resource Allocation (4:30 - 6:00)
- Diverging choropleth: resource surplus/deficit
- Four-quadrant scatter plot (interactive)
- DEA efficiency rankings
- Optimization results: current vs optimal allocation
- Reallocation Sankey
- Per-quadrant recommendation cards

### Section 5: GHRI Index (6:00 - 7:00)
- Radar chart: compare G7, BRICS countries
- GHRI world map
- Rank table with bootstrap CI
- Comparison with HDI

### Section 6: Technical Innovation (7:00 - 7:30)
- Bivariate choropleth showcase
- API architecture diagram
- Show FastAPI docs page
- Code quality: pandera validation, modular design

### Closing (7:30 - 8:00)
- Summary of key findings
- Policy implications
- Future directions
- Thank you

---

## Production Notes
- Screen recording: Heywhale notebook execution + visualization website demo
- Use OBS Studio or similar
- Export at 1080p, H.264
- Add captions for accessibility
