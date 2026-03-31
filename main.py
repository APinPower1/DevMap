import argparse
import json
import os
import shutil
import subprocess
import tempfile
import webbrowser

from analyzer import analyze
from graph_builder import build_graph


def is_github_url(path: str) -> bool:
    return path.startswith("https://github.com") or path.startswith("git@github.com")


def clone_repo(url: str) -> str:
    """Shallow-clone a GitHub repo into a temp folder and return its path."""
    # Check git is available
    if shutil.which("git") is None:
        print("Error: 'git' is not installed or not on PATH.")
        print("Install git from https://git-scm.com and try again.")
        raise SystemExit(1)

    tmp = tempfile.mkdtemp(prefix="devmap_")
    print(f"Cloning {url} ...")
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", url, tmp],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"Error: git clone failed.\n{e.stderr.decode().strip()}")
        raise SystemExit(1)

    print("Clone complete.")
    return tmp


def main():
    parser = argparse.ArgumentParser(
        prog="devmap",
        description="DevMap — Visual Codebase Explorer"
    )
    parser.add_argument(
        "path",
        help="Path to a local project folder OR a GitHub URL (e.g. https://github.com/user/repo)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path for the output HTML file (default: output.html next to main.py)"
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't automatically open the output in the browser"
    )
    args = parser.parse_args()

    # ---- Resolve folder (local or GitHub) -----------------------------------
    tmp_dir = None
    if is_github_url(args.path):
        tmp_dir = clone_repo(args.path)
        folder = tmp_dir
    else:
        folder = args.path
        if not os.path.isdir(folder):
            print(f"Error: '{folder}' is not a valid directory.")
            raise SystemExit(1)

    try:
        # ---- Analyze --------------------------------------------------------
        print(f"Analyzing {folder} ...")
        parsed = analyze(folder)
        print(f"Found {len(parsed['files'])} files.")

        # ---- Build graph ----------------------------------------------------
        print("Building graph...")
        graph = build_graph(parsed)
        print(f"Graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges.")

        # ---- Inject into template -------------------------------------------
        template_path = os.path.join(os.path.dirname(__file__), "frontend", "template.html")
        if not os.path.exists(template_path):
            print("Error: frontend/template.html not found.")
            raise SystemExit(1)

        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        output_html = template.replace("__GRAPH_DATA__", json.dumps(graph))

        # ---- Save output ----------------------------------------------------
        if args.output:
            output_path = os.path.abspath(args.output)
        else:
            output_path = os.path.join(os.path.dirname(__file__), "output.html")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_html)

        print(f"Output saved to {output_path}")

        # ---- Open in browser ------------------------------------------------
        if not args.no_open:
            webbrowser.open(f"file://{output_path}")
            print("Opened in browser.")

    finally:
        # Always clean up the temp clone, even if something went wrong
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            print("Cleaned up temp clone.")


if __name__ == "__main__":
    main()