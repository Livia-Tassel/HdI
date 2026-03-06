"""Compatibility shim for fastapi.testclient."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path


def _load_real_testclient():
    current_file = Path(__file__).resolve()
    current_src = current_file.parents[1]
    search_paths = [
        path
        for path in sys.path
        if Path(path or ".").resolve() != current_src
    ]
    spec = importlib.machinery.PathFinder.find_spec(__name__, search_paths)
    if spec and spec.origin and Path(spec.origin).resolve() != current_file:
        module = importlib.util.module_from_spec(spec)
        sys.modules[__name__] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    return None


_REAL_TESTCLIENT = _load_real_testclient()

if _REAL_TESTCLIENT is not None:
    globals().update(_REAL_TESTCLIENT.__dict__)
else:
    from fastapi import TestClient

    __all__ = ["TestClient"]
