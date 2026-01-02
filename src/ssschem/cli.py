from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .formats import OutputFormat
from .graph import GraphStyle, build_graph
from .parse import load_model
from .render import write_output

app = typer.Typer(
    help="State-space schematic generator.",
    invoke_without_command=False,
)


@app.callback(invoke_without_command=False)
def main() -> None:
    """State-space schematic generator CLI."""


@app.command()
def build(  # noqa: D401 - handled by Typer
    model_path: Path = typer.Argument(..., help="Path to YAML or JSON model file."),
    *,
    fmt: OutputFormat = typer.Option(
        OutputFormat.DOT,
        "--format",
        "-f",
        case_sensitive=False,
        help="Output format (dot/svg/pdf).",
    ),
    style: GraphStyle = typer.Option(
        GraphStyle.SFG,
        "--style",
        "-s",
        help="Graph style: sfg or integrator.",
    ),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Output file path."),
    rankdir: str = typer.Option(
        "LR",
        "--rankdir",
        help="Graphviz rank direction (LR or TB).",
    ),
    simplify: bool = typer.Option(False, "--simplify", help="Simplify symbolic gains."),
    prune_zeros: bool = typer.Option(False, "--prune-zeros", help="Drop zero-value edges."),
    float_digits: Optional[int] = typer.Option(
        None,
        "--float",
        min=1,
        help="Format numeric gains to N significant figures.",
    ),
    unicode_labels: bool = typer.Option(
        False, "--unicode", help="Use Unicode labels for sums and derivatives."
    ),
) -> None:
    """Build a schematic from a state-space definition."""
    try:
        rank = _normalize_rankdir(rankdir)
        model = load_model(model_path)
        graph = build_graph(
            model, style=style, unicode_labels=unicode_labels, prune_zeros=prune_zeros
        )
        output_path = out or Path(f"{model.name}.{fmt.value}")
        write_output(
            graph,
            output_path=output_path,
            fmt=fmt,
            rankdir=rank,
            simplify=simplify,
            float_precision=float_digits,
        )
        typer.secho(f"Wrote {fmt.value} to {output_path}", fg=typer.colors.GREEN)
    except Exception as exc:  # pragma: no cover - error path
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


def _normalize_rankdir(value: str) -> str:
    rank = value.upper()
    if rank not in {"LR", "TB"}:
        msg = "rankdir must be either LR or TB"
        raise typer.BadParameter(msg)
    return rank
