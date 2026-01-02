from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Tuple

import yaml


class InputFormat(str, Enum):
    YAML = "yaml"
    JSON = "json"


class OutputFormat(str, Enum):
    DOT = "dot"
    SVG = "svg"
    PDF = "pdf"


def detect_input_format(path: Path) -> InputFormat:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return InputFormat.YAML
    if suffix == ".json":
        return InputFormat.JSON
    msg = f"Unsupported input extension '{suffix}'"
    raise ValueError(msg)


def load_input_data(path: Path) -> Tuple[InputFormat, Any]:
    fmt = detect_input_format(path)
    text = path.read_text(encoding="utf-8")
    if fmt is InputFormat.YAML:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if data is None:
        msg = f"Input file '{path}' is empty"
        raise ValueError(msg)
    return fmt, data
