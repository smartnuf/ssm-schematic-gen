# AGENT.md — State-Space Realisation Schematic Generator

## Goal

Implement a Python project that converts a state-space realisation

    x_dot = A x + b u
    y     = c x (+ d u optional)

into a **direct integrator schematic** / **signal-flow graph** representation:

- State nodes `x1..xn`
- Input node `u`
- Output node `y`
- For each state, a summer computing `x_dot_i = sum_j a_ij x_j + b_i u`
- An integrator `1/s` producing `x_i` from `x_dot_i`
- Output summer `y = sum_i c_i x_i (+ d u optional)`
- Edges labelled with (possibly symbolic) gains: `a_ij`, `b_i`, `c_i`, `d`

Primary deliverables:
1. A CLI tool that accepts matrices and outputs **Graphviz DOT**, and optionally renders **SVG/PDF**.
2. A Python API usable from notebooks/scripts.
3. Unit tests.
4. Example inputs and generated outputs.
5. Repo layout suitable for GitHub, with `.venv/`, `pyproject.toml`, and `requirements.txt`.

Target platform: **WSL2 Ubuntu 24.04**. Editor/debugger: **VSCode**.

---

## Non-goals

- No Simulink integration.
- No GUI editor (CLI + files only).
- No numerical simulation required.
- Do not attempt "minimal realisation" or transformations unless explicitly asked; assume A,b,c are already the desired realisation.

---

## Repository Layout

Create:

state-space-schematic/
AGENT.md
README.md
pyproject.toml
requirements.txt
requirements-dev.txt
.gitignore
src/
ssschem/
init.py
cli.py
parse.py
model.py
graph.py
render.py
formats.py
tests/
test_parse.py
test_graph.py
test_cli.py
examples/
biquad_symbolic.yaml
numeric_3rd_order.json
out/
(generated .dot/.svg)
scripts/
dev_setup.sh

yaml
Copy code

Use a **src-layout** package (`src/ssschem`).

---

## Dependencies

Core:
- `sympy` for symbolic entries (including parsing expressions like "a12" or "k*(s+1)").
- `numpy` for numeric convenience (optional).
- `networkx` to build an internal directed graph representation.
- `pydot` (or `graphviz` Python package) to emit DOT.
- `pyyaml` and `jsonschema` to support YAML/JSON input and validate it.
- `typer` (preferred) or `argparse` for CLI.

Optional rendering:
- Use system `dot` from Graphviz if available (`graphviz` apt package).
- If not installed, still output DOT.

Dev:
- `pytest`, `ruff`, `mypy` (optional), `pre-commit` (optional).

---

## Input Formats

Support at least **YAML** and **JSON** file input.

Schema:

```yaml
name: "example"
A:
  - [0, 1]
  - [-a0, -a1]
b: [0, 1]
c: [b0, b1]
d: 0        # optional
variables:  # optional (for sympy symbols)
  - a0
  - a1
  - b0
  - b1
Rules:

A is n x n.

b is length n (allow n x 1 too).

c is length n (allow 1 x n too).

d optional scalar.

Entries may be numeric or strings that SymPy can parse.

CLI Spec
Command name: ssschem

Examples:

Generate DOT:

bash
Copy code
ssschem build examples/biquad_symbolic.yaml --format dot --out examples/out/biquad.dot
Render SVG (requires Graphviz installed):

bash
Copy code
ssschem build examples/biquad_symbolic.yaml --format svg --out examples/out/biquad.svg
Choose style:

bash
Copy code
ssschem build examples/biquad_symbolic.yaml --style sfg --format dot --out out.dot
ssschem build examples/biquad_symbolic.yaml --style integrator --format svg --out out.svg
Options:

--style {sfg,integrator}:

sfg: compact signal-flow graph with 1/s on edges from x_dot_i -> x_i.

integrator: explicit "sum" nodes and "integrator" nodes to resemble textbook block diagrams.

--rankdir {LR,TB} default LR.

--simplify: simplify symbolic labels with SymPy (e.g., simplify()).

--prune-zeros: omit edges with identically zero gains.

--float N: if numeric, format to N significant figures.

Exit codes:

0 success

non-zero for parse/validation/render errors.

Internal Data Model
Create dataclasses:

StateSpaceModel:

A: MatrixLike (sympy.Matrix)

b: sympy.Matrix (n x 1)

c: sympy.Matrix (1 x n)

d: sympy.Expr

name: str

Graph construction outputs networkx.DiGraph with:

nodes: include type attribute: {"type": "state"|"sum"|"int"|"input"|"output"|"xdot"}

edges: {"gain": sympy.Expr, "label": str}

Two graph builders:

build_sfg(model):

nodes: u, y, x1..xn, xdot1..xdotn

edges:

xj -> xdoti with gain A[i,j]

u -> xdoti with gain b[i]

xdoti -> xi with gain 1/s (or label s^-1)

xi -> y with gain c[i]

optionally u -> y with gain d

build_integrator(model):

nodes: sum_i, int_i, x_i

edges:

xj -> sum_i (gain A[i,j])

u -> sum_i (gain b[i])

sum_i -> int_i (gain 1)

int_i -> x_i (label 1/s block or edge)

x_i -> ysum (gain c[i])

output sum node ysum then to y.

For both: remove zero edges if --prune-zeros.

DOT Output and Styling
Implement a DOT exporter with consistent style:

u as a small circle or box labelled u

states x_i as circles

derivative nodes ẋ_i as circles labelled x_dot_i (ASCII fallback)

integrator edges labelled 1/s (or s^-1)

sums as small filled circles or nodes with label Σ

Avoid requiring LaTeX. Keep labels ASCII-compatible, but allow Unicode if --unicode.

Provide consistent node IDs:

u, y, x1, xdot1, etc.

Rendering
If output format is dot: write DOT file.

If svg or pdf:

Prefer calling system dot:

bash
Copy code
dot -Tsvg in.dot -o out.svg
dot -Tpdf in.dot -o out.pdf
Detect if dot exists; if not, error with actionable message and still allow .dot.

Tests
Write pytest tests for:

parsing YAML/JSON

dimension checking and helpful error messages

graph construction correctness for:

a 2-state biquad canonical example

a 3-state example with some zeros (test pruning)

CLI smoke test: write dot to temp directory

Use snapshots lightly (e.g., ensure edges count and key labels rather than full DOT string).

Documentation
README should include:

Installation using .venv

apt install graphviz for rendering (Ubuntu)

Example commands

Small worked example (biquad)

Also add examples/biquad_symbolic.yaml containing a true biquad-like 2-state A,b,c.

Dev Environment
Provide scripts/dev_setup.sh:

create .venv

pip install -r requirements-dev.txt

pip install -e .

run tests

Create .gitignore including .venv/, __pycache__/, .pytest_cache/, *.svg, *.pdf, examples/out/ (optional).

Quality Bar
Clear error messages

Pure Python 3.11+ compatible (Ubuntu 24.04 has 3.12 by default; be compatible with 3.11–3.12)

No hard-coded paths

Type hints where reasonable

Keep core functions small and testable

Suggested Implementation Order
repo scaffolding + packaging

parser + schema validation

internal model dataclass

graph builders (sfg + integrator)

DOT exporter

CLI

renderer (Graphviz dot)

examples + README

tests + lint config

Notes / Conventions
Use s as the Laplace variable symbol when needed (sympy.Symbol("s")).

Integrator gain may be represented symbolically as 1/s but should be labelled 1/s in DOT.

Prefer deterministic output ordering to keep diffs stable (sort nodes/edges).

markdown
Copy code

### Next steps (in your repo)
1. Create the repo folder and drop that in as `AGENT.md`.
2. Run Codex CLI pointed at the repo root; it should follow the build order and deliver the scaffold + code.

If you want, I can also give you:
- a ready-to-copy `pyproject.toml` + `requirements*.txt` matching this plan, and
- a concrete `examples/biquad_symbolic.yaml` that mirrors the biquadratic cases you’ve been discussing (controllable or tridiagonal/modal).
::contentReference[oaicite:0]{index=0}





