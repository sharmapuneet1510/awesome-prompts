import os
import json
import hashlib

class FieldDerivationAgent:
    def __init__(self, repo_paths: list):
        self.repo_paths = repo_paths
        self.java_ext = JavaExtractor() # Using the MemberReference update from before
        self.xslt_ext = XSLTExtractor()

    def analyze(self, field_name: str):
        all_results = []
        
        for repo in self.repo_paths:
            for root, _, files in os.walk(repo):
                for file in files:
                    full_path = os.path.join(root, file)
                    
                    # Track Java (Line 69) 
                    if file.endswith(".java"):
                        all_results.extend(self.java_ext.extract(full_path, field_name))
                    
                    # Track XSLT Transformations 
                    elif file.endswith(".xslt") or file.endswith(".xml"):
                        all_results.extend(self.xslt_ext.extract(full_path, field_name))
        
        return self._generate_outputs(field_name, all_results)

    def _generate_outputs(self, field, results):
        # 1. JSON Primary Output
        output_json = {
            "field_name": field,
            "derivation_chain": results
        }
        with open(f"{field}_derivation.json", "w") as f:
            json.dump(output_json, f, indent=4)
            
        # 2. MD5 for record keeping
        md5_hash = hashlib.md5(json.dumps(output_json).encode()).hexdigest()
        with open(f"{field}.md5", "w") as f:
            f.write(md5_hash)
            
        return output_json