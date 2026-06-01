# RAG Agent

## Role
RAG Agent (Retrieval-Augmented Generation) builds searchable indices of source code and documentation for integration with AI systems, enabling code search and semantic queries.

## Responsibilities

### Index Creation
- Chunk source code into semantic units (classes, functions, files)
- Generate vector embeddings (via Claude API or local models)
- Index with metadata (file, line, repository, language)
- Create full-text search indices

### Code Indexing
- Extract docstrings and comments
- Index public APIs
- Catalog framework-specific features
- Preserve source references (file:line)
- Compute relevance scores

### Documentation Indexing
- Index markdown files from context.generated/
- Index inline code documentation
- Create cross-references (code ↔ docs)
- Build FAQ/knowledge base from analysis

### Search Capabilities
- **Code Search**: Find implementations, usages
- **Semantic Search**: Find similar patterns
- **Full-Text**: Find files by keyword
- **Faceted Search**: Filter by language, repository, framework

## Input
- **context.graph**: Technical graph with source references
- **context.generated/**: All generated documentation
- Local repositories: Source code files
- Codebase: Comments and docstrings

## Output
- **context.generated/rag-index.json**: Index metadata
- **context.generated/embeddings/**: Embedding vectors (optional)
- **context.rag_index**: In-memory search index

## AgentOutput Metrics
- `documents_indexed`: Count of indexed units (files, classes, etc.)
- `embeddings_generated`: Count of vectors (if using embeddings)
- `index_size_mb`: Total index size
- `query_performance_ms`: Average search time
- `elapsed_seconds`: Execution time

## Integration with Claude API
```python
# Pseudocode for RAG lookup
def answer_code_question(query: str):
    results = rag_index.search(query, top_k=5)
    context = "\n".join([r.content for r in results])
    prompt = f"Based on this codebase:\n{context}\n\nAnswer: {query}"
    return claude_api.call(prompt)
```

## Search Index Structure
```json
{
  "id": "class:reporting:TradeReportService",
  "type": "class",
  "repository": "reporting-core",
  "language": "java",
  "file": "src/main/java/reporting/TradeReportService.java",
  "line": 42,
  "content": "public class TradeReportService { ... }",
  "keywords": ["trade", "report", "service", "reporting"],
  "embedding": [0.1, -0.2, ...],
  "metadata": {"framework": "spring", "role": "service"}
}
```

## Success Criteria
- [ ] All code files indexed
- [ ] All documentation indexed
- [ ] Search queries return relevant results
- [ ] Index is persistent and loadable
- [ ] Performance acceptable (< 100ms per query)
- [ ] Metadata enrichment complete
- [ ] Cross-references valid

## Next Step
→ TestIntelligenceAgent (Step 8): Analyze test coverage and quality
