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

                # FIX 1: use relative path as the canonical key to avoid
                # collisions between same-named files in different folders
                rel_path = os.path.relpath(file_path, folder_path)
                result["files"].append(rel_path)

                functions = []
                imports   = []

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
                            functions.extend(re.findall(pattern, content))

                        functions.extend(re.findall(r'class\s+(\w+)', content))

                        import_patterns = [
                            r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]',
                            r'require\([\'"](.+?)[\'"]\)'
                        ]
                        for pattern in import_patterns:
                            for m in re.findall(pattern, content):
                                # FIX 2: strip ./ and ../ so relative imports
                                # like "./utils" become "utils" (resolvable)
                                cleaned = re.sub(r'^\.{1,2}/', '', m)
                                imports.append(cleaned.split('/')[0])

                # FIX 3: preserve source order while deduplicating
                    result["functions"][rel_path] = list(dict.fromkeys(functions))
                    result["imports"][rel_path]   = list(dict.fromkeys(imports))

                except Exception:
                    result["functions"][rel_path] = []
                    result["imports"][rel_path]   = []

    return result