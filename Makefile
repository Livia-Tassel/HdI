.PHONY: data analysis notebooks dashboard dashboard-serve deliverables clean report api test setup

PYTHON ?= python
PIP ?= pip
PYTHONPATH ?= $(CURDIR)/src
RUN = PYTHONPATH=$(PYTHONPATH) $(PYTHON)
DATA_STAMP = data/processed/.data_pipeline.stamp

setup:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

data: $(DATA_STAMP)

$(DATA_STAMP): src/hdi/data/integrator.py
	mkdir -p data/processed
	$(RUN) -m hdi.data.integrator
	touch $(DATA_STAMP)

analysis: $(DATA_STAMP)
	$(RUN) -m hdi.analysis.competition

notebooks: analysis
	$(PYTHON) scripts/generate_notebooks.py

dashboard: analysis
	$(RUN) -m hdi.analysis.dashboard

dashboard-serve: dashboard
	$(PYTHON) scripts/serve_dashboard.py

deliverables: notebooks dashboard

clean:
	rm -rf data/interim/*.parquet data/interim/*.csv
	rm -rf data/processed/*.parquet data/processed/spatial/*.geojson
	rm -rf api_output/dim1/*.json api_output/dim2/*.json api_output/dim3/*.json api_output/metadata/*.json
	rm -rf dashboard/data/*.json
	rm -rf reports/figures/*.png reports/tables/*.csv reports/tables/*.tex reports/analysis_summary.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

report: analysis
	@if command -v xelatex >/dev/null 2>&1; then \
		cd reports && xelatex report.tex && xelatex report.tex; \
	else \
		echo "XeLaTeX not found. Report source is ready at reports/report.tex"; \
	fi

api:
	$(RUN) -m uvicorn hdi.api.app:app --reload --port 8000

api-export:
	$(RUN) -m hdi.api.serializers

test:
	$(RUN) -m pytest tests/ -v

lint:
	$(RUN) -m ruff check src/ tests/
