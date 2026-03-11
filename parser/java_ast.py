import javalang
from typing import List, Dict

class JavaExtractor:
    def extract(self, file_path: str, field_name: str) -> List[Dict]:
        findings = []
        with open(file_path, 'r') as f:
            try:
                tree = javalang.parse.parse(f.read())
                for path, node in tree:
                    # Detect Assignments (Enrichment)
                    if isinstance(node, javalang.tree.VariableDeclarator) and node.name == field_name:
                        findings.append({
                            "type": "Enrichment",
                            "detail": f"Field declared/assigned: {node.name}",
                            "line": node.position.line if node.position else 0,
                            "file": file_path
                        })
                    # Detect Method Invocations (Propagation) [cite: 7]
                    elif isinstance(node, javalang.tree.MethodInvocation) and node.member == field_name:
                        findings.append({
                            "type": "Propagation",
                            "detail": f"Method call chain involving: {node.member}",
                            "line": node.position.line if node.position else 0,
                            "file": file_path
                        })
            except: pass
        return findings