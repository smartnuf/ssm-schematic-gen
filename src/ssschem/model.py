from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import sympy as sp


@dataclass(frozen=True)
class StateSpaceModel:
    """Container for a linear state-space realisation."""

    name: str
    A: sp.Matrix
    b: sp.Matrix
    c: sp.Matrix
    d: sp.Expr
    variables: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        n = self.A.rows
        if self.A.cols != n:
            msg = "Matrix A must be square"
            raise ValueError(msg)
        if self.b.shape != (n, 1):
            msg = f"Vector b must have shape ({n}, 1)"
            raise ValueError(msg)
        if self.c.shape != (1, n):
            msg = f"Vector c must have shape (1, {n})"
            raise ValueError(msg)

    @property
    def order(self) -> int:
        return self.A.rows

    def state_name(self, index: int) -> str:
        """Return the display name for the given zero-based state index."""
        return f"x{index + 1}"
