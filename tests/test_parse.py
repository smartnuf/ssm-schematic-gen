from __future__ import annotations

from pathlib import Path

import pytest
import sympy as sp

from ssschem.parse import load_model, parse_model_dict


def test_parse_model_with_symbols() -> None:
    data = {
        "name": "symbolic",
        "A": [[0, 1], ["-a0", "-a1"]],
        "b": [0, 1],
        "c": [1, 0],
        "variables": ["a0", "a1"],
    }
    model = parse_model_dict(data)
    a0, a1 = sp.symbols("a0 a1")
    assert model.order == 2
    assert model.A[1, 0] == -a0
    assert model.A[1, 1] == -a1
    assert model.variables == ("a0", "a1")


def test_parse_dimension_mismatch() -> None:
    data = {
        "name": "bad",
        "A": [[1]],
        "b": [1, 2],
        "c": [1],
    }
    with pytest.raises(ValueError):
        parse_model_dict(data)


def test_load_model_yaml(tmp_path: Path) -> None:
    yaml_content = """
name: "tiny"
A:
  - [0]
b: [1]
c: [1]
"""
    path = tmp_path / "model.yaml"
    path.write_text(yaml_content, encoding="utf-8")
    model = load_model(path)
    assert model.order == 1
    assert model.b[0, 0] == 1
