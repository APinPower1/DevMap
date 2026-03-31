"""
graph_builder.py — DevMap Visual Codebase Explorer
Member 2: Graph Builder

Takes parsed data from the code analyzer (Member 1) and builds a
NetworkX directed graph, then converts it to the node/edge dict
format expected by the frontend visualizer.
"""

import json
import os
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
    #
    # FIX 1: use os.path.basename() instead of split("/")[-1] so that
    #         Windows backslash paths are handled correctly.
    #
    # FIX 2: register __init__.py files under their parent package name
    #         so that `import vibevoice` resolves to vibevoice/__init__.py
    # ------------------------------------------------------------------
    stem_to_file: dict[str, str] = {}
    for f in files:
        stem = f.rsplit(".", 1)[0]               # "src/utils.py" -> "src/utils"
        bare = os.path.basename(stem)            # FIX 1: handles \ and / correctly
        stem_to_file[stem] = f
        stem_to_file[bare] = f                   # register bare name too

        # FIX 2: map the package folder name -> __init__.py
        # so `import vibevoice` resolves to vibevoice/__init__.py
        if bare == "__init__":
            pkg_name = os.path.basename(os.path.dirname(f))
            if pkg_name:
                stem_to_file[pkg_name] = f

    # ------------------------------------------------------------------
    # Construct the NetworkX directed graph
    # ------------------------------------------------------------------
    G = nx.DiGraph()

    # Add one node per file, storing its function list as an attribute
    for f in files:
        funcs = functions.get(f, [])
        size  = max(len(funcs), 1)               # minimum size of 1
        G.add_node(f, functions=funcs, size=size)

    # Add edges: file A -> file B when A imports B (and B is in the project)
    for source_file, raw_imports in imports.items():
        if source_file not in G:
            continue                             # skip files not listed in "files"

        seen_targets: set[str] = set()           # deduplicate within this source

        for imp in raw_imports:
            target_file = stem_to_file.get(imp)

            if target_file is None:
                continue                         # stdlib / external -- skip silently

            if target_file == source_file:
                continue                         # no self-loops

            if target_file in seen_targets:
                continue                         # no duplicate edges

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
# Quick smoke-test -- run with:  python graph_builder.py
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
            "main.py":   ["utils", "config", "os"],   # os -> ignored (stdlib)
            "utils.py":  ["os", "json"],               # both stdlib -> no edges
            "config.py": [],                           # no imports
        },
    }

    result = build_graph(sample_data)
    print(json.dumps(result, indent=2))

    print("\n--- Edge case: empty parsed_data ---")
    print(json.dumps(build_graph({}), indent=2))

    print("\n--- Edge case: file with no functions (size should be 1) ---")
    no_funcs = {
        "files": ["lonely.py"],
        "functions": {},
        "imports": {"lonely.py": []},
    }
    print(json.dumps(build_graph(no_funcs), indent=2))

    print("\n--- Edge case: Windows-style backslash paths ---")
    win_paths = {
        "files": ["demo\\app.py", "demo\\utils.py"],
        "functions": {
            "demo\\app.py":   ["main"],
            "demo\\utils.py": ["helper"],
        },
        "imports": {
            "demo\\app.py":   ["utils"],
            "demo\\utils.py": [],
        },
    }
    print(json.dumps(build_graph(win_paths), indent=2))

    print("\n--- Edge case: package __init__.py resolution ---")
    pkg = {
        "files": ["main.py", "vibevoice\\__init__.py"],
        "functions": {
            "main.py":                ["run"],
            "vibevoice\\__init__.py": [],
        },
        "imports": {
            "main.py":                ["vibevoice"],   # should resolve to __init__.py
            "vibevoice\\__init__.py": [],
        },
    }
    print(json.dumps(build_graph(pkg), indent=2))