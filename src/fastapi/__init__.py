"""Minimal FastAPI compatibility layer used when FastAPI is unavailable."""

from __future__ import annotations

import asyncio
import importlib.machinery
import importlib.util
import inspect
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, get_args, get_origin
from urllib.parse import parse_qs, urlsplit


def _load_real_fastapi():
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


_REAL_FASTAPI = _load_real_fastapi()

if _REAL_FASTAPI is not None:
    globals().update(_REAL_FASTAPI.__dict__)
else:
    @dataclass
    class _Route:
        method: str
        path: str
        handler: Any


    def Query(default: Any = None, **_: Any) -> Any:
        return default


    def _join_path(prefix: str, path: str) -> str:
        prefix = prefix.rstrip("/")
        path = path if path.startswith("/") else f"/{path}"
        return f"{prefix}{path}" if prefix else path


    def _coerce_value(value: str, annotation: Any) -> Any:
        if annotation in (inspect._empty, str, Any):
            return value
        if annotation is int:
            return int(value)
        if annotation is float:
            return float(value)
        if annotation is bool:
            return value.lower() in {"1", "true", "yes", "on"}

        origin = get_origin(annotation)
        if origin is None:
            return value

        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            return _coerce_value(value, args[0])
        return value


    class APIRouter:
        def __init__(self, tags: list[str] | None = None):
            self.tags = tags or []
            self.routes: list[_Route] = []

        def get(self, path: str, response_model: Any = None):
            def decorator(func):
                self.routes.append(_Route("GET", path, func))
                return func

            return decorator


    class FastAPI(APIRouter):
        def __init__(self, **kwargs: Any):
            super().__init__()
            self.config = kwargs
            self.middlewares: list[tuple[Any, dict[str, Any]]] = []

        def add_middleware(self, middleware_class: Any, **kwargs: Any) -> None:
            self.middlewares.append((middleware_class, kwargs))

        def include_router(self, router: APIRouter, prefix: str = "") -> None:
            for route in router.routes:
                self.routes.append(
                    _Route(route.method, _join_path(prefix, route.path), route.handler)
                )


    class _Response:
        def __init__(self, payload: Any, status_code: int = 200):
            self._payload = payload
            self.status_code = status_code

        def json(self) -> Any:
            return self._payload


    class TestClient:
        def __init__(self, app: FastAPI):
            self.app = app

        def _dispatch(self, method: str, url: str) -> _Response:
            parsed = urlsplit(url)
            route = next(
                (
                    candidate
                    for candidate in self.app.routes
                    if candidate.method == method and candidate.path == parsed.path
                ),
                None,
            )
            if route is None:
                return _Response({"detail": "Not Found"}, status_code=404)

            query = parse_qs(parsed.query, keep_blank_values=True)
            kwargs = {}
            signature = inspect.signature(route.handler)
            for name, parameter in signature.parameters.items():
                if name in query:
                    kwargs[name] = _coerce_value(
                        query[name][-1],
                        parameter.annotation,
                    )

            if inspect.iscoroutinefunction(route.handler):
                payload = asyncio.run(route.handler(**kwargs))
            else:
                payload = route.handler(**kwargs)

            return _Response(payload, status_code=200)

        def get(self, url: str) -> _Response:
            return self._dispatch("GET", url)


    TestClient.__test__ = False

    __all__ = ["APIRouter", "FastAPI", "Query", "TestClient"]
