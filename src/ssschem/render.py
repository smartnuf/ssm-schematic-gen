from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

import networkx as nx
import sympy as sp

from .formats import OutputFormat

ONE = sp.Integer(1)

NODE_STYLES = {
    "input": {"shape": "circle", "style": "filled", "fillcolor": "#dbeafe"},
    "output": {"shape": "doublecircle", "style": "filled", "fillcolor": "#dcfce7"},
    "state": {"shape": "circle"},
    "xdot": {"shape": "circle", "style": "dashed"},
    "sum": {"shape": "circle", "style": "filled", "fillcolor": "#fef3c7"},
    "int": {"shape": "box"},
}


def graph_to_dot(
    graph: nx.DiGraph,
    *,
    rankdir: str = "LR",
    simplify: bool = False,
    float_precision: Optional[int] = None,
) -> str:
    styled = graph.copy()
    for node_id, data in styled.nodes(data=True):
        node_type = data.get("type")
        for key, value in NODE_STYLES.get(node_type, {}).items():
            data.setdefault(key, value)
        data.setdefault("label", node_id)
    for _, _, data in styled.edges(data=True):
        gain = data.get("gain", ONE)
        data["label"] = format_gain(gain, simplify=simplify, float_precision=float_precision)
    dot = nx.drawing.nx_pydot.to_pydot(styled)
    dot.set_rankdir(rankdir)
    return dot.to_string()


def write_output(
    graph: nx.DiGraph,
    *,
    output_path: Path,
    fmt: OutputFormat = OutputFormat.DOT,
    rankdir: str = "LR",
    simplify: bool = False,
    float_precision: Optional[int] = None,
) -> None:
    dot_source = graph_to_dot(
        graph, rankdir=rankdir, simplify=simplify, float_precision=float_precision
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt is OutputFormat.DOT:
        output_path.write_text(dot_source, encoding="utf-8")
        return
    _render_with_graphviz(dot_source, output_path, fmt)


def format_gain(
    gain: sp.Expr,
    *,
    simplify: bool = False,
    float_precision: Optional[int] = None,
) -> str:
    expr = sp.simplify(gain) if simplify else gain
    if float_precision is not None and expr.is_number:
        try:
            numeric = float(expr.evalf(float_precision))
        except (TypeError, ValueError):
            return str(expr)
        return f"{numeric:.{float_precision}g}"
    label = str(expr)
    if label == "1" and gain is ONE:
        return "1"
    return label


def _render_with_graphviz(source: str, output_path: Path, fmt: OutputFormat) -> None:
    executable = shutil.which("dot")
    if executable is None:
        msg = (
            "Graphviz 'dot' executable not found. Install graphviz or output DOT instead."
        )
        raise RuntimeError(msg)
    command = [executable, f"-T{fmt.value}", "-o", str(output_path)]
    try:
        subprocess.run(command, input=source.encode("utf-8"), check=True)
    except subprocess.CalledProcessError as exc:
        msg = f"Graphviz failed with exit code {exc.returncode}"
        raise RuntimeError(msg) from exc
