import pytest
import tempfile
import json
from pathlib import Path
from tools.graphify_integrator import GraphifyIntegrator


class TestGraphifyIntegrator:
    """Test suite for GraphifyIntegrator."""

    def test_generate_knowledge_graph(self):
        """Test that generate_knowledge_graph creates graph with nodes, edges, clusters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            codebase_path = Path(tmpdir)

            # Create some Python files with classes
            (codebase_path / 'models.py').write_text(
                'class User:\n'
                '    def __init__(self, name):\n'
                '        self.name = name\n'
                '\n'
                'class Repository:\n'
                '    def __init__(self, user):\n'
                '        self.user = user\n'
            )

            (codebase_path / 'services.py').write_text(
                'class UserService:\n'
                '    def create_user(self, name):\n'
                '        return User(name)\n'
                '\n'
                'class RepositoryService:\n'
                '    def __init__(self, repo):\n'
                '        self.repo = repo\n'
            )

            integrator = GraphifyIntegrator(codebase_path)
            graph = integrator.generate()

            # Verify graph structure
            assert 'nodes' in graph
            assert 'edges' in graph
            assert 'clusters' in graph

            # Verify nodes exist
            assert len(graph['nodes']) > 0
            assert any(node['id'] == 'User' for node in graph['nodes'])
            assert any(node['id'] == 'Repository' for node in graph['nodes'])
            assert any(node['id'] == 'UserService' for node in graph['nodes'])
            assert any(node['id'] == 'RepositoryService' for node in graph['nodes'])

            # Verify nodes have required metadata
            for node in graph['nodes']:
                assert 'id' in node
                assert 'type' in node
                assert 'file' in node
                assert node['type'] == 'class'

    def test_cache_graph_embeddings(self):
        """Test that cache() saves graph embeddings to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            codebase_path = Path(tmpdir)
            cache_dir = Path(tmpdir) / 'cache'

            # Create a Python file with a class
            (codebase_path / 'models.py').write_text(
                'class User:\n'
                '    def __init__(self, name):\n'
                '        self.name = name\n'
            )

            integrator = GraphifyIntegrator(codebase_path, cache_dir=cache_dir)
            graph = integrator.generate()
            integrator.cache()

            # Verify embeddings.json was created
            embeddings_file = cache_dir / 'embeddings.json'
            assert embeddings_file.exists(), "embeddings.json was not created"

            # Verify embeddings file contains valid JSON
            with open(embeddings_file, 'r') as f:
                cached_data = json.load(f)

            # Verify structure
            assert 'nodes' in cached_data
            assert 'edges' in cached_data
            assert 'clusters' in cached_data
            assert len(cached_data['nodes']) > 0
