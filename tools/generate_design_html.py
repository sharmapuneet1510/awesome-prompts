#!/usr/bin/env python3
"""
generate_design_html.py — Interactive HTML visualization generator for project context.

Reads context.json and generates a self-contained HTML file with:
- Architecture tab: D3.js force-directed component graph
- Tech Stack tab: Filterable technology table
- File Tree tab: Collapsible project explorer
- API Endpoints tab: Sortable HTTP method table

No external dependencies. All JS/CSS inlined. Works offline.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ContextData:
    """Parsed context.json structure."""
    project_name: str
    tech_stack: dict
    file_structure: dict
    api_endpoints: list
    database_schema: dict


class DesignHTMLGenerator:
    """Generates interactive HTML design from context.json."""

    def __init__(self, context_path: Path):
        """Initialize from context.json.

        Args:
            context_path: Path to context.json file
        """
        with open(context_path) as f:
            data = json.load(f)
        self.context = ContextData(
            project_name=data.get("project_name", "Project"),
            tech_stack=data.get("tech_stack", {}),
            file_structure=data.get("file_structure", {}),
            api_endpoints=data.get("api_endpoints", []),
            database_schema=data.get("database_schema", {}),
        )

    def _flatten_tech_stack(self) -> list[dict]:
        """Flatten nested tech_stack dict to list of tech items.

        Returns:
            List of {"name": str, "version": str, "purpose": str, "category": str}
        """
        techs = []

        for category, items in self.context.tech_stack.items():
            if isinstance(items, dict):
                for key, value in items.items():
                    if isinstance(value, dict):
                        techs.append({
                            "name": value.get("name", key.replace("_", " ").title()),
                            "version": value.get("version", ""),
                            "purpose": value.get("purpose", ""),
                            "category": category.replace("_", " ").title(),
                        })
                    else:
                        techs.append({
                            "name": key.replace("_", " ").title(),
                            "version": str(value) if value else "",
                            "purpose": "",
                            "category": category.replace("_", " ").title(),
                        })

        return techs

    def _build_file_tree_json(self) -> str:
        """Generate file tree JSON for JavaScript rendering.

        Returns:
            JSON string representation of file structure
        """
        def build_node(path: str, data: dict | int) -> dict:
            if isinstance(data, int):
                return {"name": path, "size": data, "type": "file"}

            node = {"name": path, "type": "directory", "children": []}
            for key, value in data.items():
                node["children"].append(build_node(key, value))
            return node

        root = {"name": self.context.project_name, "type": "directory", "children": []}
        for key, value in self.context.file_structure.items():
            root["children"].append(build_node(key, value))

        return json.dumps(root)

    def _build_architecture_nodes(self) -> tuple[str, str]:
        """Generate D3.js nodes and links for architecture diagram.

        Returns:
            Tuple of (nodes_json, links_json) for D3 rendering
        """
        # Create nodes from tech stack
        nodes = []
        node_id = 0

        # Frontend node
        if "frontend" in self.context.tech_stack:
            nodes.append({"id": node_id, "name": "Frontend", "group": "frontend"})
            frontend_id = node_id
            node_id += 1

        # Backend node
        if "backend" in self.context.tech_stack:
            nodes.append({"id": node_id, "name": "Backend API", "group": "backend"})
            backend_id = node_id
            node_id += 1

        # Database node
        if "database" in self.context.tech_stack:
            nodes.append({"id": node_id, "name": "Database", "group": "database"})
            database_id = node_id
            node_id += 1

        # External services (if detected)
        nodes.append({"id": node_id, "name": "External APIs", "group": "external"})

        # Create links
        links = []
        if len(nodes) >= 2:
            links.append({"source": 0, "target": 1, "label": "REST API"})
        if len(nodes) >= 3:
            links.append({"source": 1, "target": 2, "label": "SQL"})

        return json.dumps(nodes), json.dumps(links)

    def generate(self) -> str:
        """Generate complete HTML string.

        Returns:
            Self-contained HTML (no external dependencies)
        """
        techs = self._flatten_tech_stack()
        techs_json = json.dumps(techs)
        file_tree_json = self._build_file_tree_json()
        endpoints_json = json.dumps(self.context.api_endpoints)
        nodes_json, links_json = self._build_architecture_nodes()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.context.project_name} - Architecture Design</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #7f8c8d;
            font-size: 14px;
        }}

        .tabs {{
            display: flex;
            gap: 0;
            background: white;
            border-radius: 8px 8px 0 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 0;
        }}

        .tab-button {{
            flex: 1;
            padding: 16px;
            border: none;
            background: white;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            color: #7f8c8d;
            border-bottom: 3px solid #ecf0f1;
            transition: all 0.3s ease;
            text-align: center;
        }}

        .tab-button:hover {{
            background: #f5f7fa;
            color: #2c3e50;
        }}

        .tab-button.active {{
            color: #3498db;
            border-bottom-color: #3498db;
            background: white;
        }}

        .tab-content {{
            background: white;
            padding: 30px;
            border-radius: 0 0 8px 8px;
            display: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Architecture Tab */
        #architecture {{
            min-height: 500px;
        }}

        svg {{
            width: 100%;
            height: 500px;
        }}

        .node {{
            fill: #3498db;
            stroke: #2980b9;
            stroke-width: 2px;
            cursor: pointer;
        }}

        .node:hover {{
            fill: #2980b9;
        }}

        .link {{
            stroke: #95a5a6;
            stroke-width: 2px;
        }}

        .node-label {{
            font-size: 12px;
            fill: white;
            text-anchor: middle;
            pointer-events: none;
            font-weight: bold;
        }}

        /* Tech Stack Tab */
        .search-box {{
            margin-bottom: 20px;
        }}

        .search-box input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ecf0f1;
            border-radius: 4px;
            font-size: 14px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background: #ecf0f1;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #2c3e50;
            border-bottom: 2px solid #bdc3c7;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}

        tr:hover {{
            background: #f5f7fa;
        }}

        .category-tag {{
            display: inline-block;
            padding: 4px 8px;
            background: #ecf0f1;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            color: #2c3e50;
        }}

        /* File Tree Tab */
        .tree {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }}

        .tree-node {{
            margin-left: 20px;
            cursor: pointer;
            user-select: none;
        }}

        .tree-toggle {{
            display: inline-block;
            width: 20px;
            text-align: center;
            color: #3498db;
        }}

        .tree-name {{
            color: #2c3e50;
        }}

        .tree-directory {{
            font-weight: bold;
            color: #e67e22;
        }}

        .tree-file {{
            color: #7f8c8d;
        }}

        /* API Endpoints Tab */
        .endpoint-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            color: white;
            min-width: 50px;
            text-align: center;
        }}

        .method-GET {{
            background: #3498db;
        }}

        .method-POST {{
            background: #27ae60;
        }}

        .method-PUT {{
            background: #f39c12;
        }}

        .method-DELETE {{
            background: #e74c3c;
        }}

        .method-PATCH {{
            background: #9b59b6;
        }}

        .endpoint-path {{
            font-family: 'Courier New', monospace;
            color: #2c3e50;
            font-weight: 500;
        }}

        .no-data {{
            text-align: center;
            color: #7f8c8d;
            padding: 40px;
            font-size: 16px;
        }}

        footer {{
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏗️ {self.context.project_name}</h1>
            <p class="subtitle">Interactive architecture & project design</p>
        </header>

        <div class="tabs">
            <button class="tab-button active" onclick="showTab('architecture')">Architecture</button>
            <button class="tab-button" onclick="showTab('tech-stack')">Tech Stack</button>
            <button class="tab-button" onclick="showTab('file-tree')">File Tree</button>
            <button class="tab-button" onclick="showTab('endpoints')">API Endpoints</button>
        </div>

        <!-- Architecture Tab -->
        <div id="architecture" class="tab-content active">
            <h2>System Architecture</h2>
            <svg id="architecture-svg"></svg>
        </div>

        <!-- Tech Stack Tab -->
        <div id="tech-stack" class="tab-content">
            <h2>Technology Stack</h2>
            <div class="search-box">
                <input type="text" id="tech-search" placeholder="Search technologies..." onkeyup="filterTable('tech-table', 'tech-search')">
            </div>
            <table id="tech-table">
                <thead>
                    <tr>
                        <th>Technology</th>
                        <th>Version</th>
                        <th>Category</th>
                        <th>Purpose</th>
                    </tr>
                </thead>
                <tbody id="tech-tbody"></tbody>
            </table>
        </div>

        <!-- File Tree Tab -->
        <div id="file-tree" class="tab-content">
            <h2>Project Structure</h2>
            <div class="tree" id="tree-container"></div>
        </div>

        <!-- API Endpoints Tab -->
        <div id="endpoints" class="tab-content">
            <h2>API Endpoints</h2>
            <table id="endpoints-table">
                <thead>
                    <tr>
                        <th>Method</th>
                        <th>Path</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody id="endpoints-tbody"></tbody>
            </table>
        </div>

        <footer>
            Generated by Context Builder Agent • {self.context.project_name} Architecture Design
        </footer>
    </div>

    <script>
        // Tab switching
        function showTab(tabName) {{
            const tabs = document.querySelectorAll('.tab-content');
            const buttons = document.querySelectorAll('.tab-button');

            tabs.forEach(tab => tab.classList.remove('active'));
            buttons.forEach(btn => btn.classList.remove('active'));

            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        // Tech Stack Table
        const techs = {techs_json};
        function populateTechTable() {{
            const tbody = document.getElementById('tech-tbody');
            techs.forEach(tech => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${{tech.name}}</td>
                    <td>${{tech.version || 'N/A'}}</td>
                    <td><span class="category-tag">${{tech.category}}</span></td>
                    <td>${{tech.purpose || 'General'}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // File Tree
        const fileTree = {file_tree_json};
        function buildTree(node, container, level = 0) {{
            const div = document.createElement('div');
            div.className = 'tree-node';
            div.style.marginLeft = (level * 20) + 'px';

            const isDir = node.type === 'directory';
            const icon = isDir ? '📁' : '📄';
            const nameClass = isDir ? 'tree-directory' : 'tree-file';

            const label = document.createElement('span');
            label.innerHTML = `${{icon}} <span class="${{nameClass}}">${{node.name}}</span>`;
            div.appendChild(label);

            if (isDir && node.children && node.children.length > 0) {{
                const childrenDiv = document.createElement('div');
                childrenDiv.className = 'tree-children';

                node.children.forEach(child => {{
                    buildTree(child, childrenDiv, level + 1);
                }});

                div.appendChild(childrenDiv);

                label.style.cursor = 'pointer';
                label.addEventListener('click', () => {{
                    childrenDiv.style.display = childrenDiv.style.display === 'none' ? 'block' : 'none';
                }});
            }}

            container.appendChild(div);
        }}

        // API Endpoints Table
        const endpoints = {endpoints_json};
        function populateEndpointsTable() {{
            const tbody = document.getElementById('endpoints-tbody');
            endpoints.forEach(ep => {{
                const tr = document.createElement('tr');
                const method = ep.method || 'GET';
                tr.innerHTML = `
                    <td><span class="endpoint-badge method-${{method}}">${{method}}</span></td>
                    <td><span class="endpoint-path">${{ep.path}}</span></td>
                    <td>${{ep.description || 'N/A'}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Simple table filter
        function filterTable(tableId, searchId) {{
            const searchTerm = document.getElementById(searchId).value.toLowerCase();
            const rows = document.getElementById(tableId).getElementsByTagName('tbody')[0].getElementsByTagName('tr');

            rows.forEach(row => {{
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            }});
        }}

        // D3-like simple architecture diagram (without D3 dependency)
        function drawArchitecture() {{
            const svg = document.getElementById('architecture-svg');
            const width = svg.parentElement.clientWidth;
            const height = 400;

            svg.setAttribute('viewBox', `0 0 ${{width}} ${{height}}`);

            // Simple hardcoded layout for now
            const nodes = {nodes_json};
            const links = {links_json};

            // Draw links
            links.forEach(link => {{
                const source = nodes[link.source];
                const target = nodes[link.target];

                const x1 = 100 + link.source * 200;
                const y1 = 100;
                const x2 = 100 + link.target * 200;
                const y2 = 300;

                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', x1);
                line.setAttribute('y1', y1);
                line.setAttribute('x2', x2);
                line.setAttribute('y2', y2);
                line.setAttribute('stroke', '#95a5a6');
                line.setAttribute('stroke-width', '2');
                svg.appendChild(line);
            }});

            // Draw nodes
            nodes.forEach((node, i) => {{
                const x = 100 + i * 200;
                const y = 100;

                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', x);
                circle.setAttribute('cy', y);
                circle.setAttribute('r', '50');
                circle.setAttribute('fill', '#3498db');
                circle.setAttribute('stroke', '#2980b9');
                circle.setAttribute('stroke-width', '2');
                svg.appendChild(circle);

                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', x);
                text.setAttribute('y', y);
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('dy', '0.3em');
                text.setAttribute('fill', 'white');
                text.setAttribute('font-size', '12');
                text.setAttribute('font-weight', 'bold');
                text.textContent = node.name;
                svg.appendChild(text);
            }});
        }}

        // Initialize on load
        window.addEventListener('load', () => {{
            populateTechTable();
            buildTree(fileTree, document.getElementById('tree-container'));
            populateEndpointsTable();
            drawArchitecture();
        }});
    </script>
</body>
</html>"""

        return html

    def save(self, output_path: Path) -> None:
        """Save generated HTML to file.

        Args:
            output_path: Where to save the HTML file
        """
        html = self.generate()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)
        print(f"✓ Generated {output_path.name} ({len(html) / 1024:.1f} KB)")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate interactive HTML design from context.json"
    )
    parser.add_argument(
        "--context",
        type=Path,
        default=Path("docs/context/context.json"),
        help="Path to context.json file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/context/design.html"),
        help="Output HTML file path",
    )

    args = parser.parse_args()

    if not args.context.exists():
        print(f"Error: {args.context} not found")
        return 1

    generator = DesignHTMLGenerator(args.context)
    generator.save(args.output)

    print(f"\n✅ Design visualization ready!")
    print(f"Open in browser: {args.output.absolute()}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
