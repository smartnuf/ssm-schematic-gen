from __future__ import annotations

from enum import Enum
from typing import Callable

import networkx as nx
import sympy as sp

from .model import StateSpaceModel

S_SYMBOL = sp.Symbol("s")
ONE = sp.Integer(1)
ZERO = sp.Integer(0)


class GraphStyle(str, Enum):
    SFG = "sfg"
    INTEGRATOR = "integrator"


def build_graph(
    model: StateSpaceModel,
    *,
    style: GraphStyle = GraphStyle.SFG,
    unicode_labels: bool = False,
    prune_zeros: bool = False,
) -> nx.DiGraph:
    if style is GraphStyle.SFG:
        return build_sfg_graph(model, unicode_labels=unicode_labels, prune_zeros=prune_zeros)
    if style is GraphStyle.INTEGRATOR:
        return build_integrator_graph(model, unicode_labels=unicode_labels, prune_zeros=prune_zeros)
    msg = f"Unsupported graph style '{style}'"
    raise ValueError(msg)


def build_sfg_graph(
    model: StateSpaceModel, *, unicode_labels: bool = False, prune_zeros: bool = False
) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("u", type="input", label="u")
    graph.add_node("y", type="output", label="y")
    for idx in range(model.order):
        state_id = _state_id(idx)
        xdot_id = _xdot_id(idx)
        graph.add_node(state_id, type="state", label=_state_label(idx, unicode_labels))
        graph.add_node(xdot_id, type="xdot", label=_xdot_label(idx, unicode_labels))
    _add_state_edges(
        graph,
        model,
        prune_zeros=prune_zeros,
        sum_node_fn=lambda idx: _xdot_id(idx),
    )
    for idx in range(model.order):
        xdot_id = _xdot_id(idx)
        state_id = _state_id(idx)
        _add_edge(graph, xdot_id, state_id, ONE / S_SYMBOL, prune_zeros=False)
        _add_edge(graph, state_id, "y", model.c[0, idx], prune_zeros=prune_zeros)
    if model.d != ZERO:
        _add_edge(graph, "u", "y", model.d, prune_zeros=prune_zeros)
    return graph


def build_integrator_graph(
    model: StateSpaceModel, *, unicode_labels: bool = False, prune_zeros: bool = False
) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("u", type="input", label="u")
    graph.add_node("y", type="output", label="y")
    graph.add_node("ysum", type="sum", label=_output_sum_label(unicode_labels))
    _add_edge(graph, "ysum", "y", ONE, prune_zeros=False)
    for idx in range(model.order):
        sum_id = _sum_id(idx)
        int_id = _integrator_id(idx)
        state_id = _state_id(idx)
        graph.add_node(sum_id, type="sum", label=_sum_label(idx, unicode_labels))
        graph.add_node(int_id, type="int", label="1/s")
        graph.add_node(state_id, type="state", label=_state_label(idx, unicode_labels))
        _add_edge(graph, sum_id, int_id, ONE, prune_zeros=False)
        _add_edge(graph, int_id, state_id, ONE, prune_zeros=False)
    _add_state_edges(
        graph,
        model,
        prune_zeros=prune_zeros,
        sum_node_fn=lambda idx: _sum_id(idx),
    )
    for idx in range(model.order):
        state_id = _state_id(idx)
        _add_edge(graph, state_id, "ysum", model.c[0, idx], prune_zeros=prune_zeros)
    if model.d != ZERO:
        _add_edge(graph, "u", "ysum", model.d, prune_zeros=prune_zeros)
    return graph


def _add_state_edges(
    graph: nx.DiGraph,
    model: StateSpaceModel,
    *,
    prune_zeros: bool,
    sum_node_fn: Callable[[int], str],
) -> None:
    for row in range(model.order):
        sum_node = sum_node_fn(row)
        for col in range(model.order):
            src = _state_id(col)
            gain = model.A[row, col]
            _add_edge(graph, src, sum_node, gain, prune_zeros=prune_zeros)
        _add_edge(graph, "u", sum_node, model.b[row, 0], prune_zeros=prune_zeros)


def _add_edge(graph: nx.DiGraph, src: str, dst: str, gain: sp.Expr, *, prune_zeros: bool) -> None:
    if prune_zeros and _is_zero(gain):
        return
    graph.add_edge(src, dst, gain=gain)


def _is_zero(expr: sp.Expr) -> bool:
    return bool(sp.simplify(expr) == 0)


def _state_id(index: int) -> str:
    return f"x{index + 1}"


def _xdot_id(index: int) -> str:
    return f"xdot{index + 1}"


def _sum_id(index: int) -> str:
    return f"sum{index + 1}"


def _integrator_id(index: int) -> str:
    return f"int{index + 1}"


def _state_label(index: int, unicode_labels: bool) -> str:
    return f"x{index + 1}"


def _xdot_label(index: int, unicode_labels: bool) -> str:
    if unicode_labels:
        return f"x\u0307{index + 1}"
    return f"x_dot{index + 1}"


def _sum_label(index: int, unicode_labels: bool) -> str:
    if unicode_labels:
        return f"\u03a3{index + 1}"
    return f"sum{index + 1}"


def _output_sum_label(unicode_labels: bool) -> str:
    if unicode_labels:
        return "\u03a3_y"
    return "sum_y"
