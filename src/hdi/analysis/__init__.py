"""Analysis pipelines for competition deliverables."""

__all__ = ["run_competition_pipeline", "build_dashboard_assets"]


def run_competition_pipeline(*args, **kwargs):
    from hdi.analysis.competition import run_competition_pipeline as _run_competition_pipeline

    return _run_competition_pipeline(*args, **kwargs)


def build_dashboard_assets(*args, **kwargs):
    from hdi.analysis.dashboard import build_dashboard_assets as _build_dashboard_assets

    return _build_dashboard_assets(*args, **kwargs)
