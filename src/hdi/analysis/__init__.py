"""Analysis pipelines for competition deliverables."""

__all__ = ["run_competition_pipeline"]


def run_competition_pipeline(*args, **kwargs):
    from hdi.analysis.competition import run_competition_pipeline as _run_competition_pipeline

    return _run_competition_pipeline(*args, **kwargs)
