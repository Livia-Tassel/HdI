"""Minimal pandera compatibility layer used when pandera is unavailable."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from typing import Any

import pandas as pd


def _load_real_pandera():
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


_REAL_PANDERA = _load_real_pandera()

if _REAL_PANDERA is not None:
    globals().update(_REAL_PANDERA.__dict__)
else:
    class errors:
        class SchemaErrors(Exception):
            """Compatibility error raised for schema validation failures."""


    class Check:
        """Small subset of the pandera Check API used by this project."""

        def __init__(self, validator, description: str):
            self._validator = validator
            self.description = description

        def __call__(self, series: pd.Series) -> pd.Series:
            result = self._validator(series)
            if isinstance(result, pd.Series):
                return result.fillna(False)
            return pd.Series(bool(result), index=series.index)

        @staticmethod
        def str_length(min_value: int, max_value: int) -> "Check":
            return Check(
                lambda series: series.astype("string").str.len().between(min_value, max_value),
                f"string length between {min_value} and {max_value}",
            )

        @staticmethod
        def in_range(min_value: float, max_value: float) -> "Check":
            def _validator(series: pd.Series) -> pd.Series:
                numeric = pd.to_numeric(series, errors="coerce")
                return numeric.between(min_value, max_value)

            return Check(_validator, f"value between {min_value} and {max_value}")

        @staticmethod
        def greater_than_or_equal_to(min_value: float) -> "Check":
            def _validator(series: pd.Series) -> pd.Series:
                numeric = pd.to_numeric(series, errors="coerce")
                return numeric >= min_value

            return Check(_validator, f"value >= {min_value}")


    class Column:
        def __init__(
            self,
            dtype: Any,
            checks: Check | list[Check] | tuple[Check, ...] | None = None,
            nullable: bool = False,
            description: str | None = None,
        ) -> None:
            self.dtype = dtype
            if checks is None:
                self.checks = []
            elif isinstance(checks, (list, tuple)):
                self.checks = list(checks)
            else:
                self.checks = [checks]
            self.nullable = nullable
            self.description = description


    class Index:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs


    class DataFrameSchema:
        def __init__(
            self,
            columns: dict[str, Column],
            strict: bool = False,
            description: str | None = None,
        ) -> None:
            self.columns = columns
            self.strict = strict
            self.description = description

        def add_columns(self, columns: dict[str, Column]) -> "DataFrameSchema":
            merged = dict(self.columns)
            merged.update(columns)
            return DataFrameSchema(
                columns=merged,
                strict=self.strict,
                description=self.description,
            )

        def _dtype_valid(self, series: pd.Series, dtype: Any) -> bool:
            non_null = series.dropna()
            if non_null.empty:
                return True

            if dtype is str:
                return non_null.map(lambda value: isinstance(value, str)).all()

            if dtype is int:
                numeric = pd.to_numeric(non_null, errors="coerce")
                return numeric.notna().all() and (numeric % 1 == 0).all()

            if dtype is float:
                numeric = pd.to_numeric(non_null, errors="coerce")
                return numeric.notna().all()

            return True

        def validate(self, df: pd.DataFrame, lazy: bool = False) -> pd.DataFrame:
            violations: list[str] = []

            missing = [column for column in self.columns if column not in df.columns]
            if missing:
                violations.append(f"Missing required columns: {missing}")

            if self.strict:
                extras = [column for column in df.columns if column not in self.columns]
                if extras:
                    violations.append(f"Unexpected columns: {extras}")

            for column_name, column_schema in self.columns.items():
                if column_name not in df.columns:
                    continue

                series = df[column_name]
                if not column_schema.nullable and series.isna().any():
                    violations.append(f"{column_name} contains null values")

                if not self._dtype_valid(series, column_schema.dtype):
                    violations.append(f"{column_name} has invalid dtype")

                for check in column_schema.checks:
                    mask = check(series)
                    effective_mask = mask | series.isna()
                    if not effective_mask.all():
                        violations.append(
                            f"{column_name} failed check: {check.description}"
                        )

            if violations:
                raise errors.SchemaErrors("; ".join(violations))
            return df


    __all__ = [
        "Check",
        "Column",
        "DataFrameSchema",
        "Index",
        "errors",
    ]
