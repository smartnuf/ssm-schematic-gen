# State-Space Schematic Generator

`ssschem` converts linear state-space realisations into direct-integrator and signal-flow Graphviz schematics. It accepts YAML/JSON models and emits DOT, SVG, or PDF, making it easy to visualise controller structures in notebooks, VS Code, or documentation.

## Features
- Parse numeric or symbolic matrices using SymPy with optional variable declarations.
- Validate inputs with JSON Schema to catch dimension issues early.
- Build either a textbook integrator diagram or a compact signal-flow graph.
- Export DOT via `pydot`/`networkx` and optionally call Graphviz `dot` to render SVG/PDF.
- Python API plus Typer-powered CLI (`ssschem build ...`).

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
```

Ubuntu users should install Graphviz for SVG/PDF rendering:
```bash
sudo apt install graphviz
```

Alternatively, install from requirements:
```bash
pip install -r requirements.txt
```

## Usage
Example model (`examples/biquad_symbolic.yaml`):
```yaml
name: "biquad"
A:
  - [0, 1]
  - [-a0, -a1]
b: [0, 1]
c: [b0, b1]
variables: [a0, a1, b0, b1]
```

Build DOT:
```bash
ssschem build examples/biquad_symbolic.yaml \
  --style sfg --format dot --out examples/out/biquad.dot
```

Render SVG (requires Graphviz `dot`):
```bash
ssschem build examples/biquad_symbolic.yaml \
  --style integrator --format svg --out examples/out/biquad.svg
```

Key options:
- `--style {sfg,integrator}` select topology.
- `--rankdir {LR,TB}` orient graph.
- `--simplify` reduce symbolic labels.
- `--prune-zeros` omit zero-weight edges.
- `--float N` format numeric gains to `N` significant figures.
- `--unicode` enable unicode labels for derivative/sum symbols.

## Python API
```python
from pathlib import Path
from ssschem import load_model, build_graph, OutputFormat
from ssschem.render import graph_to_dot
model = load_model(Path("examples/biquad_symbolic.yaml"))
graph = build_graph(model, style="sfg")
dot = graph_to_dot(graph)
```

## Development
- Ensure Python 3.11+.
- Run `scripts/dev_setup.sh` for a fresh virtualenv and editable install.
- Execute tests via `pytest`.
- Lint using `ruff check .` (configured via `pyproject.toml`).

## Examples and Outputs
- `examples/biquad_symbolic.yaml`: symbolic biquad.
- `examples/numeric_3rd_order.json`: numeric third-order example.
- Generated files live in `examples/out/`.

## License
This project is distributed under the MIT License (see `LICENSE`).
