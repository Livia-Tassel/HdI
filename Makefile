.PHONY: data clean report api test setup

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

clean:
	rm -rf data/interim/*.parquet data/interim/*.csv
	rm -rf data/processed/*.parquet data/processed/spatial/*.geojson
	rm -rf api_output/dim1/*.json api_output/dim2/*.json api_output/dim3/*.json api_output/metadata/*.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

report:
	cd reports && pdflatex report.tex && pdflatex report.tex

api:
	$(RUN) -m uvicorn hdi.api.app:app --reload --port 8000

api-export:
	$(RUN) -m hdi.api.serializers

test:
	$(RUN) -m pytest tests/ -v

lint:
	$(RUN) -m ruff check src/ tests/
