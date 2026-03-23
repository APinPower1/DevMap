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
                result["files"].append(file)

                functions = []
                imports = []

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # ---- PYTHON FILES ----
                    if file.endswith(".py"):
                        tree = ast.parse(content)

                        for node in ast.walk(tree):
                            # Functions
                            if isinstance(node, ast.FunctionDef):
                                functions.append(node.name)

                            # Classes
                            elif isinstance(node, ast.ClassDef):
                                functions.append(node.name)

                            # Imports
                            elif isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports.append(alias.name.split('.')[0])

                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    imports.append(node.module.split('.')[0])

                    # ---- JS / TS FILES ----
                    else:
                        # Functions (simple regex-based detection)
                        func_patterns = [
                            r'function\s+(\w+)',
                            r'(\w+)\s*=\s*\(.*?\)\s*=>',
                            r'(\w+)\s*=\s*function'
                        ]

                        for pattern in func_patterns:
                            matches = re.findall(pattern, content)
                            functions.extend(matches)

                        # Classes
                        class_matches = re.findall(r'class\s+(\w+)', content)
                        functions.extend(class_matches)

                        # Imports
                        import_patterns = [
                            r'import\s+.*?\s+from\s+[\'"](.+?)[\'"]',
                            r'require\([\'"](.+?)[\'"]\)'
                        ]

                        for pattern in import_patterns:
                            matches = re.findall(pattern, content)
                            for m in matches:
                                imports.append(m.split('/')[0])

                    # Remove duplicates
                    result["functions"][file] = list(set(functions))
                    result["imports"][file] = list(set(imports))

                except Exception:
                    # In case of parsing errors, still include file
                    result["functions"][file] = []
                    result["imports"][file] = []

    return result