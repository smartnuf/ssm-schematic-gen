from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import jsonschema
import sympy as sp

from .formats import InputFormat, load_input_data
from .model import StateSpaceModel

_SCALAR_SCHEMA = {"type": ["number", "string", "integer"]}
MODEL_SCHEMA: Mapping[str, Any] = {
    "type": "object",
    "required": ["A", "b", "c"],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "A": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "array", "minItems": 1, "items": _SCALAR_SCHEMA},
        },
        "b": {
            "type": "array",
            "minItems": 1,
            "items": {"anyOf": [_SCALAR_SCHEMA, {"type": "array", "minItems": 1, "items": _SCALAR_SCHEMA}]},
        },
        "c": {
            "type": "array",
            "minItems": 1,
            "items": {"anyOf": [_SCALAR_SCHEMA, {"type": "array", "minItems": 1, "items": _SCALAR_SCHEMA}]},
        },
        "d": _SCALAR_SCHEMA,
        "variables": {"type": "array", "items": {"type": "string"}},
    },
}

_VALIDATOR = jsonschema.Draft202012Validator(MODEL_SCHEMA)


def load_model(path: Path) -> StateSpaceModel:
    fmt, data = load_input_data(path)
    source = f"{fmt.value}:{path}"
    return parse_model_dict(data, source=source)


def parse_model_dict(data: Mapping[str, Any], *, source: str = "input") -> StateSpaceModel:
    _validate_schema(data, source)
    name = str(data.get("name") or "state-space-model")
    variables = tuple(str(v) for v in data.get("variables", []))
    locals_map = {var: sp.symbols(var) for var in variables}

    def parse_expr(value: Any) -> sp.Expr:
        try:
            return sp.sympify(value, locals=locals_map)
        except sp.SympifyError as exc:
            msg = f"Failed to parse expression '{value}' in {source}"
            raise ValueError(msg) from exc

    A = _parse_matrix(data["A"], parse_expr, "A")
    if A.rows != A.cols:
        msg = "Matrix A must be square"
        raise ValueError(msg)
    n = A.rows

    b = _parse_vector(data["b"], parse_expr, n, "b", column=True)
    c = _parse_vector(data["c"], parse_expr, n, "c", column=False)
    d = parse_expr(data.get("d", 0))

    return StateSpaceModel(name=name, A=A, b=b, c=c, d=d, variables=variables)


def _validate_schema(data: Mapping[str, Any], source: str) -> None:
    errors = sorted(_VALIDATOR.iter_errors(data), key=lambda e: e.json_path)
    if not errors:
        return
    joined = "; ".join(f"{error.json_path or '$'}: {error.message}" for error in errors)
    msg = f"Input model validation failed for {source}: {joined}"
    raise ValueError(msg)


def _parse_matrix(raw: Sequence[Any], parse_expr: Any, location: str) -> sp.Matrix:
    rows: list[list[sp.Expr]] = []
    width: int | None = None
    for r_index, row in enumerate(raw):
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes)):
            msg = f"{location} row {r_index} must be a sequence"
            raise ValueError(msg)
        parsed_row = [parse_expr(value) for value in row]
        if width is None:
            width = len(parsed_row)
        elif len(parsed_row) != width:
            msg = f"{location} rows must all have {width} columns"
            raise ValueError(msg)
        rows.append(parsed_row)
    if not rows:
        msg = f"{location} must contain at least one row"
        raise ValueError(msg)
    return sp.Matrix(rows)


def _parse_vector(
    raw: Sequence[Any],
    parse_expr: Any,
    expected_len: int,
    location: str,
    *,
    column: bool,
) -> sp.Matrix:
    flattened = _flatten_vector(raw, location)
    if len(flattened) != expected_len:
        msg = f"{location} must have length {expected_len}, got {len(flattened)}"
        raise ValueError(msg)
    parsed = [parse_expr(value) for value in flattened]
    if column:
        return sp.Matrix([[value] for value in parsed])
    return sp.Matrix([parsed])


def _flatten_vector(raw: Sequence[Any], location: str) -> list[Any]:
    flattened: list[Any] = []
    for index, value in enumerate(raw):
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            if len(value) != 1:
                msg = f"{location} entry {index} must be a scalar or single-element list"
                raise ValueError(msg)
            flattened.append(value[0])
        else:
            flattened.append(value)
    return flattened
