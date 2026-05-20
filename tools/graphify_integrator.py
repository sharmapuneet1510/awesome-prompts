"""GraphifyIntegrator for knowledge graph generation and token caching."""

import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List


class GraphifyIntegrator:
    """Integrator for graphify knowledge graph generation and caching."""

    def __init__(self, codebase_path: Path, cache_dir: Optional[Path] = None):
        """
        Initialize GraphifyIntegrator.

        Args:
            codebase_path: Path to the codebase to analyze
            cache_dir: Optional directory for caching embeddings (default: .graphify_cache)
        """
        self.codebase_path = Path(codebase_path)
        self.cache_dir = Path(cache_dir) if cache_dir else self.codebase_path / '.graphify_cache'
        self.graph: Dict[str, Any] = {'nodes': [], 'edges': [], 'clusters': []}

    def generate(self) -> Dict[str, Any]:
        """
        Generate knowledge graph from codebase.

        Returns:
            dict: Graph with keys 'nodes', 'edges', 'clusters'
        """
        self.graph = {
            'nodes': self._extract_nodes(),
            'edges': self._extract_edges(),
            'clusters': []
        }
        return self.graph

    def _extract_nodes(self) -> List[Dict[str, Any]]:
        """
        Extract nodes from Python classes using regex.

        Returns:
            list: List of node dictionaries with id, type, and file metadata
        """
        nodes = []
        class_pattern = re.compile(r'^class\s+(\w+)')

        # Find all Python files in codebase
        py_files = list(self.codebase_path.glob('**/*.py'))

        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract all class definitions
                for line in content.split('\n'):
                    match = class_pattern.match(line.strip())
                    if match:
                        class_name = match.group(1)
                        nodes.append({
                            'id': class_name,
                            'type': 'class',
                            'file': str(py_file.relative_to(self.codebase_path))
                        })
            except (IOError, UnicodeDecodeError):
                continue

        return nodes

    def _extract_edges(self) -> List[Dict[str, Any]]:
        """
        Extract edges from dependency relationships.

        Placeholder for future implementation of dependency extraction.

        Returns:
            list: List of edge dictionaries with source and target
        """
        # Placeholder for future dependency extraction
        return []

    def cache(self) -> None:
        """Save graph to embeddings.json in cache directory."""
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Write embeddings to JSON file
        embeddings_file = self.cache_dir / 'embeddings.json'
        with open(embeddings_file, 'w', encoding='utf-8') as f:
            json.dump(self.graph, f, indent=2)

    def load_cache(self) -> Optional[Dict[str, Any]]:
        """
        Load cached embeddings if available.

        Returns:
            dict: Cached graph data, or None if not found
        """
        embeddings_file = self.cache_dir / 'embeddings.json'

        if not embeddings_file.exists():
            return None

        try:
            with open(embeddings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            return None
