import lxml.etree as ET

class XSLTExtractor:
    def extract(self, file_path: str, field_name: str) -> List[Dict]:
        findings = []
        try:
            tree = ET.parse(file_path)
            # Find elements where field is defined or used 
            xpath_query = f"//*[contains(@name, '{field_name}') or contains(@select, '{field_name}')]"
            for el in tree.xpath(xpath_query):
                findings.append({
                    "type": "Transformation",
                    "detail": f"XSLT Logic: <{el.tag}>",
                    "line": el.sourceline,
                    "file": file_path
                })
        except: pass
        return findings