import os
import ast
import re

def analyze(folder_path: str) -> dict:
    result = {
        "files": [],
        "functions": {},
        "imports": {}
    }

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".py", ".js", ".ts")):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, folder_path)  # FIX: use relative path as key
                result["files"].append(rel_path)
                functions = []
                imports = []

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # ---- PYTHON FILES ----
                    if file.endswith(".py"):
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                functions.append(node.name)
                            elif isinstance(node, ast.ClassDef):
                                functions.append(node.name)
                            elif isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports.append(alias.name.split('.')[0])
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    imports.append(node.module.split('.')[0])

                    # ---- JS / TS FILES ----
                    else:
                        func_patterns = [
                            r'function\s+(\w+)',
                            r'(\w+)\s*=\s*\(.*?\)\s*=>',
                            r'(\w+)\s*=\s*function'
                        ]
                        for pattern in func_patterns:
                            matches = re.findall(pattern, content)
                            functions.extend(matches)

                        class_matches = re.findall(r'class\s+(\w+)', content)
                        functions.extend(class_matches)

                        import_patterns = [
                            r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]',
                            r'require\([\'"](.+?)[\'"]\)'
                        ]
                        for pattern in import_patterns:
                            matches = re.findall(pattern, content)
                            for m in matches:
                                imports.append(m.split('/')[0])

                    result["functions"][rel_path] = list(set(functions))  # FIX
                    result["imports"][rel_path] = list(set(imports))      # FIX

                except Exception:
                    result["functions"][rel_path] = []  # FIX
                    result["imports"][rel_path] = []    # FIX

    return result


if __name__ == "__main__":
    import json
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "."
    result = analyze(path)
    print(json.dumps(result, indent=2))