"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from hdi.api.app import app

client = TestClient(app)


class TestHealthCheck:
    def test_health(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestMetadataEndpoints:
    def test_countries_endpoint(self):
        response = client.get("/api/v1/metadata/countries")
        assert response.status_code == 200

    def test_indicators_endpoint(self):
        response = client.get("/api/v1/metadata/indicators")
        assert response.status_code == 200

    def test_ghri_endpoint(self):
        response = client.get("/api/v1/composite/ghri")
        assert response.status_code == 200


class TestDimension1:
    def test_trends_endpoint(self):
        response = client.get("/api/v1/dim1/trends")
        assert response.status_code == 200

    def test_forecasts_endpoint(self):
        response = client.get("/api/v1/dim1/forecasts")
        assert response.status_code == 200


class TestDimension2:
    def test_paf_endpoint(self):
        response = client.get("/api/v1/dim2/paf")
        assert response.status_code == 200

    def test_sankey_endpoint(self):
        response = client.get("/api/v1/dim2/sankey")
        assert response.status_code == 200

    def test_scenarios_endpoint(self):
        response = client.get("/api/v1/dim2/scenarios")
        assert response.status_code == 200


class TestDimension3:
    def test_resource_gap_endpoint(self):
        response = client.get("/api/v1/dim3/resource_gap")
        assert response.status_code == 200

    def test_efficiency_endpoint(self):
        response = client.get("/api/v1/dim3/efficiency")
        assert response.status_code == 200

    def test_optimization_endpoint(self):
        response = client.get("/api/v1/dim3/optimization")
        assert response.status_code == 200

    def test_optimization_endpoint_filters_scenarios(self, monkeypatch):
        from hdi.api.routers import dimension3

        payload = {
            "status": "success",
            "meta": {"query_params": {}, "record_count": 2},
            "data": {
                "default_scenario": "max_output__budget_1p0",
                "scenarios": [
                    {
                        "scenario_id": "max_output__budget_1p0",
                        "objective": "max_output",
                        "budget_multiplier": 1.0,
                        "summary": {},
                        "allocation": [],
                    },
                    {
                        "scenario_id": "maximin__budget_1p1",
                        "objective": "maximin",
                        "budget_multiplier": 1.1,
                        "summary": {},
                        "allocation": [],
                    },
                ],
            },
        }

        monkeypatch.setattr(dimension3, "_load_json", lambda _: payload)

        response = client.get("/api/v1/dim3/optimization?objective=maximin&budget_multiplier=1.1")
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["record_count"] == 1
        assert data["meta"]["query_params"] == {"objective": "maximin", "budget_multiplier": 1.1}
        assert data["data"]["scenarios"][0]["scenario_id"] == "maximin__budget_1p1"
