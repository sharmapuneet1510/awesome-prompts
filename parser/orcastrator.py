import os
import json
import hashlib
from extractors.java_ast import JavaExtractor
from extractors.xslt_parser import XSLTExtractor

class Orchestrator:
    def __init__(self, lib_path: str, juris_path: str):
        self.repos = {"library": lib_path, "jurisdiction": juris_path} # [cite: 10]
        self.java_ext = JavaExtractor()
        self.xslt_ext = XSLTExtractor()

    def run(self, field_name: str):
        all_logic = []
        for source, path in self.repos.items():
            for root, _, files in os.walk(path): # [cite: 14, 15]
                for file in files:
                    full_path = os.path.join(root, file)
                    results = []
                    if file.endswith(".java"):
                        results = self.java_ext.extract(full_path, field_name)
                    elif file.endswith(".xslt") or file.endswith(".xml"):
                        results = self.xslt_ext.extract(full_path, field_name)
                    
                    for r in results:
                        r["logic_source"] = source # [cite: 10]
                        all_logic.append(r)
        
        self._export_results(field_name, all_logic)

    def _export_results(self, field, data):
        # JSON Output
        with open(f"{field}_derivation.json", "w") as f:
            json.dump(data, f, indent=4)
        
        # MD5 Output
        md5_hash = hashlib.md5(json.dumps(data).encode()).hexdigest()
        with open(f"{field}.md5", "w") as f:
            f.write(md5_hash)
            
        print(f"Analysis complete for {field}. Files generated.")

if __name__ == "__main__":
    # Example usage
    agent = Orchestrator(lib_path="./repo1", juris_path="./repo2")
    agent.run("messageKey") # [cite: 11]