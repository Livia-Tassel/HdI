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
