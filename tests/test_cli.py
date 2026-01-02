from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ssschem.cli import app


def test_cli_build_writes_dot(tmp_path: Path) -> None:
    yaml_content = """
name: cli
A:
  - [0]
b: [1]
c: [1]
"""
    model_path = tmp_path / "cli.yaml"
    out_path = tmp_path / "cli.dot"
    model_path.write_text(yaml_content, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "build",
            "--format",
            "dot",
            "--style",
            "sfg",
            "--out",
            str(out_path),
            str(model_path),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out_path.exists()
    assert "digraph" in out_path.read_text(encoding="utf-8")
