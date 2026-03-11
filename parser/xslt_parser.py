import lxml.etree as ET

class XSLTExtractor:
    def extract(self, file_path: str, field_name: str):
        findings = []
        # Define the XSL namespace used in your files
        namespaces = {'xsl': 'http://www.w3.org/1999/XSL/Transform'}
        
        try:
            tree = ET.parse(file_path)
            # Search for the field in names, select attributes, or text content [cite: 4]
            query = f"//*[contains(@name, '{field_name}') or contains(@select, '{field_name}') or contains(text(), '{field_name}')]"
            elements = tree.xpath(query, namespaces=namespaces)
            
            for el in elements:
                # Capture the actual XML snippet for the derivation chain [cite: 3]
                logic_snippet = ET.tostring(el, encoding='unicode', method='xml').strip()
                findings.append({
                    "type": "Transformation",
                    "detail": f"XSLT Logic: {logic_snippet}",
                    "line": el.sourceline,
                    "file": file_path,
                    "logic_source": "jurisdiction" if "jurisdiction" in file_path.lower() else "library"
                })
        except Exception:
            pass
        return findings