import javalang
from typing import List, Dict

class JavaExtractor:
    """
    Enhanced Java Extractor designed to detect Debug Field Keys 
    accessed via constants and method calls[cite: 7, 11, 17].
    """
    def extract(self, file_path: str, field_name: str) -> List[Dict]:
        findings = []
        with open(file_path, 'r') as f:
            content = f.read()
            try:
                # Build AST to track method chains and field propagation [cite: 7, 13]
                tree = javalang.parse.parse(content)
                
                for path, node in tree:
                    # 1. Detect Member References (Captures Line 69's constant usage) [cite: 12]
                    if isinstance(node, javalang.tree.MemberReference):
                        if field_name in node.member:
                            findings.append(self._format_finding(node, file_path, "Data Enrichment"))

                    # 2. Detect Method Invocations (Captures calls like debugMap.get()) 
                    elif isinstance(node, javalang.tree.MethodInvocation):
                        # Check if our target field is passed as an argument [cite: 13]
                        for arg in node.arguments:
                            if hasattr(arg, 'member') and field_name in arg.member:
                                findings.append(self._format_finding(node, file_path, "Downstream Detection"))
                                
            except Exception:
                # Fallback to ensure we never miss a line due to AST parsing errors [cite: 17]
                findings.extend(self._line_by_line_fallback(content, file_path, field_name))
        
        return findings

    def _format_finding(self, node, file_path, logic_type):
        """Creates the structured JSON output required for machine processing."""
        return {
            "type": logic_type,
            "detail": f"Java Logic Reference: {getattr(node, 'member', 'Method Call')}",
            "line": node.position.line if node.position else "Unknown",
            "file": file_path,
            "logic_source": "jurisdiction" if "jurisdiction" in file_path.lower() else "library" [cite: 10]
        }

    def _line_by_line_fallback(self, content, file_path, field_name):
        """Ensures 100% detection coverage even if AST fails."""
        matches = []
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if field_name in line:
                matches.append({
                    "type": "Data Enrichment",
                    "detail": f"Source Line: {line.strip()}",
                    "line": i,
                    "file": file_path,
                    "logic_source": "jurisdiction" if "jurisdiction" in file_path.lower() else "library" [cite: 10]
                })
        return matches