from __future__ import annotations

import sympy as sp

from ssschem.graph import build_integrator_graph, build_sfg_graph
from ssschem.model import StateSpaceModel


def _demo_model(d_value: int | float = 0) -> StateSpaceModel:
    A = sp.Matrix([[0, 1], [-2, -3]])
    b = sp.Matrix([[0], [1]])
    c = sp.Matrix([[1, 0]])
    d = sp.sympify(d_value)
    return StateSpaceModel(name="demo", A=A, b=b, c=c, d=d)


def test_sfg_integrator_edge_gain_equals_inverse_s() -> None:
    model = _demo_model()
    graph = build_sfg_graph(model)
    gain = graph.edges[("xdot1", "x1")]["gain"]
    assert str(gain) == "1/s"


def test_prune_zero_edges_removes_zero_gains() -> None:
    model = _demo_model()
    graph = build_sfg_graph(model, prune_zeros=True)
    assert ("x1", "xdot1") not in graph.edges


def test_integrator_graph_includes_output_sum_and_feedthrough() -> None:
    model = _demo_model(d_value=2)
    graph = build_integrator_graph(model)
    assert "ysum" in graph.nodes
    assert ("u", "ysum") in graph.edges
    assert graph.edges[("u", "ysum")]["gain"] == 2
