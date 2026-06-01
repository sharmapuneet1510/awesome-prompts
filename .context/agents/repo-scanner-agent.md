# Repo Scanner Agent

## Role
Repo Scanner Agent performs deterministic fact extraction from all repositories, building detailed inventories of files, classes, methods, endpoints, and configuration without interpretation.

## Responsibilities

### Fact Extraction
- Scan all files using include/exclude patterns from config
- Parse source files using language-specific analyzers
- Extract symbols: packages, classes, interfaces, methods, endpoints
- Identify configuration files (YAML, XML, JSON, properties)
- Catalog dependencies from build files

### Language Support
- **Java**: AST parsing via javalang; Spring annotations; Maven/Gradle
- **Python**: AST parsing; decorators; requirements.txt/setup.py
- **TypeScript/JavaScript**: tree-sitter parsing; decorators; package.json
- **YAML**: Full parsing for k8s, docker-compose, helm
- **SQL**: DDL extraction; stored procedures; views

### Evidence Collection
- Source line references for all findings
- Confidence scores (high/medium/low)
- Dependency chains (who calls whom)
- Framework-specific metadata (Spring @RestController, FastAPI @app.get, etc.)

## Input
- `context.generated/project_definition.json`: Project metadata
- Local repositories: Source code files
- Config: include/exclude patterns, analysis depth

## Output
- **context.generated/inventory.json**: Complete symbol catalog
- **context.generated/dependencies.json**: Dependency graph
- **context.generated/config.json**: Configuration catalog

## AgentOutput Metrics
- `files_scanned`: Total files processed
- `symbols_extracted`: Classes, methods, functions, endpoints
- `dependencies_found`: Dependency edges in graph
- `parsing_errors`: Count of unparseable files
- `elapsed_seconds`: Execution time

## Error Handling
- **Critical**: Major language parsing errors (continues, logs)
- **Warning**: Unsupported file types (skipped)
- **Info**: Ambiguous dependency inference (logs with confidence)

## Incremental Analysis
Uses CacheService to skip unchanged repositories:
- Computes repo hash (HEAD commit + file count)
- Compares to cached hash
- Skips scanning if unchanged
- Updates cache on completion

## Success Criteria
- [ ] All files successfully scanned
- [ ] No critical parsing failures
- [ ] Inventory JSON valid and complete
- [ ] Cache updated for next run
- [ ] Dependency graph contains expected edges
- [ ] All configuration files discovered

## Next Step
→ CodeGraphAgent (Step 3): Build traversable technical graph
