# AI Agent Collaboration Workflow

## Overview

This document records the AI collaboration workflow used throughout the Health Data Insight (HdI) project, as required by the competition guidelines.

## Phases

### Phase 1: Problem Framing (Days 1-3)
- Literature review on global disease burden analysis
- Brainstorm analytical angles for 3 competition dimensions
- Discuss data source selection and supplementary dataset strategy
- Define novel GHRI composite index methodology

### Phase 2: Methodology Selection (Days 3-7)
- Evaluate panel regression approaches (FE vs RE vs GMM)
- Discuss causal inference strategy (DoWhy DAGs, IV instruments)
- Select PAF/Shapley decomposition for risk attribution
- Design DEA efficiency framework and optimization models
- Review system dynamics modeling for scenario simulation

### Phase 3: Code Development (Days 7-18)
- Develop data cleaning pipeline with country code harmonization
- Implement panel regression with Driscoll-Kraay SEs
- Build LISA spatial autocorrelation analysis
- Debug DEA linear programming formulation
- Implement Monte Carlo scenario simulation
- Code review for optimization models

### Phase 4: Interpretation & Report Writing (Days 18-25)
- Interpret regression coefficients and causal estimates
- Draft report sections for each dimension
- Generate publication-quality figures
- Review and refine conclusions

## Interaction Log Format

Each interaction is saved as JSON in `interaction_logs/` with the following schema:

```json
{
  "id": "001",
  "timestamp": "2025-03-05T10:00:00Z",
  "phase": "methodology_selection",
  "topic": "Panel regression approach",
  "user_query": "...",
  "ai_response_summary": "...",
  "outcome": "Selected FE with Driscoll-Kraay SEs",
  "tools_used": ["literature_review", "code_generation"]
}
```

## Key AI Contributions

1. **Methodology guidance**: Recommended Driscoll-Kraay SEs over clustered SEs for panels with cross-sectional dependence
2. **Code architecture**: Designed modular package structure with clear separation of concerns
3. **Debugging**: Helped resolve DEA LP formulation issues with VRS constraints
4. **Interpretation**: Assisted with E-value sensitivity analysis for unmeasured confounding
5. **Visualization**: Suggested bivariate choropleth as novel visualization technique
