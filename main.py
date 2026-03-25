import argparse
import json
import os
import webbrowser

from analyzer import analyze
from graph_builder import build_graph

def main():
    parser = argparse.ArgumentParser(
        prog="devmap",
        description="DevMap — Visual Codebase Explorer"
    )
    parser.add_argument("path", help="Path to the project folder to analyze")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: '{args.path}' is not a valid directory.")
        return

    print(f"Analyzing {args.path}...")
    parsed = analyze(args.path)
    print(f"Found {len(parsed['files'])} files.")

    print("Building graph...")
    graph = build_graph(parsed)
    print(f"Graph has {len(graph['nodes'])} nodes and {len(graph['edges'])} edges.")

    # ---- ADD STEP 4 HERE ----
    template_path = os.path.join(os.path.dirname(__file__), "frontend", "template.html")
    output_path = os.path.join(os.path.dirname(__file__), "output.html")

    if not os.path.exists(template_path):
        print("Error: frontend/template.html not found. Waiting for M3.")
        return

    with open(template_path, "r") as f:
        template = f.read()

    output_html = template.replace("__GRAPH_DATA__", json.dumps(graph))

    with open(output_path, "w") as f:
        f.write(output_html)

    print(f"Output saved to {output_path}")

    webbrowser.open(f"file://{os.path.abspath(output_path)}")
    print("Opened in browser.")

if __name__ == "__main__":
    main()