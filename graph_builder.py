"""
graph_builder.py — DevMap Visual Codebase Explorer
Member 2: Graph Builder

Takes parsed data from the code analyzer (Member 1) and builds a
NetworkX directed graph, then converts it to the node/edge dict
format expected by the frontend visualizer.
"""

import json
import networkx as nx


def build_graph(parsed_data: dict) -> dict:
    """
    Convert parsed project data into a graph structure for frontend visualization.

    Args:
        parsed_data: Dict with keys "files", "functions", and "imports".

    Returns:
        Dict with keys "nodes" (list of file nodes) and "edges" (list of
        directed dependency edges between project files).
    """
    # Guard: return empty graph for missing or empty input
    if not parsed_data:
        return {"nodes": [], "edges": []}

    files     = parsed_data.get("files", [])
    functions = parsed_data.get("functions", {})
    imports   = parsed_data.get("imports", {})

    if not files:
        return {"nodes": [], "edges": []}

    # ------------------------------------------------------------------
    # Build a set of "known" file stems for fast import-resolution lookup.
    # e.g. "utils.py" → "utils", "pkg/helpers.py" → "helpers"
    # We store both the stem and the full path so we can map an import
    # name back to the canonical node id used by the frontend.
    # ------------------------------------------------------------------
    stem_to_file: dict[str, str] = {}
    for f in files:
        # Use the filename without extension as the resolvable stem.
        # pathlib isn't needed; a simple rsplit is sufficient.
        stem = f.rsplit(".", 1)[0]          # "src/utils.py" → "src/utils"
        bare = stem.split("/")[-1]          # "src/utils"    → "utils"
        stem_to_file[stem] = f
        stem_to_file[bare] = f             # also register bare name

    # ------------------------------------------------------------------
    # Construct the NetworkX directed graph
    # ------------------------------------------------------------------
    G = nx.DiGraph()

    # Add one node per file, storing its function list as an attribute
    for f in files:
        funcs = functions.get(f, [])
        size  = max(len(funcs), 1)          # minimum size of 1
        G.add_node(f, functions=funcs, size=size)

    # Add edges: file A → file B when A imports B (and B is in the project)
    for source_file, raw_imports in imports.items():
        if source_file not in G:
            continue                        # skip files not listed in "files"

        seen_targets: set[str] = set()      # deduplicate within this source

        for imp in raw_imports:
            target_file = stem_to_file.get(imp)

            if target_file is None:
                continue                    # stdlib / external — skip silently

            if target_file == source_file:
                continue                    # no self-loops

            if target_file in seen_targets:
                continue                    # no duplicate edges

            G.add_edge(source_file, target_file)
            seen_targets.add(target_file)

    # ------------------------------------------------------------------
    # Serialise to the exact output shape the frontend expects
    # ------------------------------------------------------------------
    nodes = [
        {
            "id":        node,
            "functions": G.nodes[node]["functions"],
            "size":      G.nodes[node]["size"],
        }
        for node in G.nodes
    ]

    edges = [
        {"source": src, "target": tgt}
        for src, tgt in G.edges
    ]

    return {"nodes": nodes, "edges": edges}


# ----------------------------------------------------------------------
# Quick smoke-test — run with:  python graph_builder.py
# ----------------------------------------------------------------------
if __name__ == "__main__":
    sample_data = {
        "files": ["main.py", "utils.py", "config.py"],
        "functions": {
            "main.py":   ["main", "run", "helper"],
            "utils.py":  ["read_file", "write_file"],
            "config.py": ["load_config"],
        },
        "imports": {
            "main.py":   ["utils", "config", "os"],   # os → ignored (stdlib)
            "utils.py":  ["os", "json"],               # both stdlib → no edges
            "config.py": [],                           # no imports
        },
    }

    result = build_graph(sample_data)
    print(json.dumps(result, indent=2))

    # ── Additional edge-case tests ──────────────────────────────────────

    print("\n--- Edge case: empty parsed_data ---")
    print(json.dumps(build_graph({}), indent=2))

    print("\n--- Edge case: file with no functions (size should be 1) ---")
    no_funcs = {
        "files": ["lonely.py"],
        "functions": {},
        "imports": {"lonely.py": []},
    }
    print(json.dumps(build_graph(no_funcs), indent=2))

    print("\n--- Edge case: import that doesn't match any project file ---")
    phantom = {
        "files": ["app.py"],
        "functions": {"app.py": ["start"]},
        "imports": {"app.py": ["ghost_module", "sys"]},
    }
    print(json.dumps(build_graph(phantom), indent=2))

    print("\n--- Edge case: duplicate imports in the same file ---")
    dupes = {
        "files": ["a.py", "b.py"],
        "functions": {"a.py": ["foo"], "b.py": ["bar"]},
        "imports": {"a.py": ["b", "b", "b"], "b.py": []},
    }
    print(json.dumps(build_graph(dupes), indent=2))
