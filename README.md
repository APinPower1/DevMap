# DevMap

**DevMap** is an open-source CLI tool that scans any project folder and generates an interactive, browser-based dependency graph — so you can understand an unfamiliar codebase visually in seconds.

![DevMap visualization showing a force-directed dependency graph with color-coded nodes](screenshot.png)

---

## Quick Start

```bash
# Run on a local project
devmap ./your-project

# Or point it directly at a GitHub repo
devmap https://github.com/pallets/flask
```

A browser window opens automatically with your interactive graph. That's it.

---

## Installation

**Prerequisites:** Python 3.8 or above — [Download here](https://python.org/downloads)

```bash
git clone https://github.com/APinPower1/DevMap.git
cd DevMap
pip install -r requirements.txt
pip install -e .
```

After installation, `devmap` is available as a global command from anywhere on your system.

---

## Usage

```
devmap <path_or_url> [--output PATH] [--no-open]
```

| Argument | Description |
|---|---|
| `path_or_url` | Path to a local folder **or** a GitHub URL |
| `--output PATH` | Save the output HTML to a custom path (default: `output.html`) |
| `--no-open` | Generate the file without opening it in the browser |

### Examples

```bash
# Analyze a local project
devmap ./my-project

# Analyze a GitHub repository (no manual cloning needed)
devmap https://github.com/pallets/flask

# Save the graph to a specific location
devmap ./my-project --output ~/graphs/my-project.html

# Generate without auto-opening the browser
devmap ./my-project --no-open
```

When given a GitHub URL, DevMap does a shallow clone into a temporary folder, runs the full analysis, then deletes the temp folder automatically. Git must be installed for this to work.

---

## Features

### Dependency Graph Visualization
- **Force-directed graph** powered by D3.js — nodes naturally cluster based on their relationships
- **Arrows** show the direction of imports, so you can see what depends on what at a glance
- **Node size** scales with the number of functions in that file — larger nodes are more complex
- **Color coding** by file type:
  - 🟣 Purple — Python (`.py`)
  - 🟡 Yellow — JavaScript (`.js`)
  - 🔵 Blue — TypeScript (`.ts`)

### Interaction
- **Click any node** to open the inspector panel showing its functions, outgoing imports, and incoming dependencies
- **Subgraph highlighting** — selecting a node dims everything not connected to it, so you can trace relationships instantly
- **Search** — press `/` or type in the search box to filter nodes by filename in real time
- **File type toggles** — show or hide Python, JS, and TS files independently
- **Zoom and pan** — scroll to zoom, drag the canvas to pan
- **Drag nodes** — reposition any node to untangle the graph

### Controls & Shortcuts

| Shortcut | Action |
|---|---|
| `/` | Focus the search box |
| `Esc` | Close the inspector / clear search |
| `R` | Reset zoom to default |
| Fit button | Zoom to fit all nodes on screen |

### Export
- **Export PNG** button in the sidebar saves the current graph as a high-resolution image

### GitHub URL Support
```bash
devmap https://github.com/user/repo
```
DevMap clones the repo with `--depth=1` (fast, no full history), analyzes it, and cleans up the temp folder when done. Requires `git` to be installed.

### Language Support

| Language | Import Detection | Function Extraction |
|---|---|---|
| Python | AST-based (accurate) | Functions + Classes |
| JavaScript | Regex | Functions + Arrow functions + Classes |
| TypeScript | Regex | Functions + Arrow functions + Classes |

---

## How It Works

```
devmap ./project
       │
       ├── analyzer.py      Walks the folder, extracts files / functions / imports
       │
       ├── graph_builder.py Builds a NetworkX directed graph, resolves imports to project files
       │
       ├── main.py          Injects graph JSON into frontend/template.html → output.html
       │
       └── Browser opens output.html (D3.js renders the interactive graph)
```

The output is a **fully self-contained static HTML file** — no server, no database, no framework. You can share `output.html` with anyone and it works offline.

---

## Project Structure

```
DevMap/
├── devmap/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── graph_builder.py
│   ├── main.py
│   └── frontend/
│       └── template.html
├── setup.py
├── requirements.txt
└── README.md
```

---

## Tech Stack

- **Python 3.8+** — CLI, analysis pipeline
- **NetworkX** — graph construction and traversal (only external Python dependency)
- **D3.js v7** — force-directed graph visualization (loaded from CDN, no install)
- **Pure HTML / CSS / JS** — no frontend framework

---

## Requirements

```
networkx
```

That's the only pip dependency. D3.js is loaded from a CDN at runtime.

---

## Contributing

Pull requests are welcome. If you want to add support for a new language, the right place is `analyzer.py` — add a new file extension branch and extract functions/imports into the same return shape. Everything downstream will work automatically.

Possible areas to contribute:
- Support for more languages (Go, Java, Rust, C/C++)
- `--ignore` flag to skip folders like `node_modules` or `venv`
- `--depth` flag to limit how deep the graph traverses
- Light mode toggle
- Line count / file size as an additional node metric

---

## License

MIT License

Copyright (c) 2025 APinPower1

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## AI Assistance

This project was built with significant AI assistance:

- **Claude** (Anthropic) — architecture decisions, core pipeline code, debugging, and documentation
- **ChatGPT** (OpenAI) — code generation and problem solving
- **Cursor** (AI-powered editor) — code generation and iterative development

The team designed the overall concept, defined the feature set, integrated all components, tested the tool across multiple real projects, and debugged issues throughout development.