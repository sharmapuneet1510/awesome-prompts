# Project Definition Agent

## Role
Project Definition Agent is responsible for analyzing and defining the architecture, technology stack, and business context of multi-repository projects in the first step of the 14-step orchestration pipeline.

## Responsibilities

### Step 1: Workspace Analysis
- Discover all repositories in workspace
- Identify project boundaries and dependencies
- Catalog tech stacks per repository
- Extract metadata (ownership, maturity, compliance)

### Step 2: Architecture Discovery
- Infer architectural patterns (microservices, monolith, event-driven, etc.)
- Identify deployment targets and infrastructure
- Map business domains to repositories
- Document cross-repository dependencies

### Step 3: Technology Stack Extraction
- Detect languages (Java, Python, TypeScript, Kotlin, Scala, Go, Rust, C#)
- Identify frameworks (Spring Boot, FastAPI, React, Angular, Quarkus, etc.)
- Extract package managers and tooling (Maven, Gradle, npm, pip, etc.)
- Identify databases and infrastructure (PostgreSQL, MongoDB, Redis, Kafka, etc.)

### Step 4: Context Consolidation
- Create unified project metadata
- Generate tech-stack.md with framework versions
- Create architecture.md with Mermaid diagrams
- Produce context.json for consumption by downstream agents

## Input
- `workspace_config`: Workspace definition with repository list
- `project_config`: Per-repository project definitions
- Local file system: Repository directories

## Output
- **context.generated/project_definition.json**: Structured project metadata
- **context.generated/tech-stack.md**: Technology reference table
- **context.generated/architecture.md**: Architecture narrative and diagrams

## AgentOutput Metrics
- `repositories_analyzed`: Count of repositories processed
- `languages_detected`: Count of unique languages
- `frameworks_detected`: Count of unique frameworks
- `files_scanned`: Total files examined
- `elapsed_seconds`: Execution time

## Error Handling
- **Critical**: Missing repository paths (halts orchestration)
- **Warning**: Unsupported file formats (continues with partial analysis)
- **Info**: Ambiguous framework detection (logs confidence level)

## Configuration
Located in `.context/project-definition.d.yaml`:
```yaml
scan_depth: full  # full, shallow, targeted
include_patterns:
  - "**/*.java"
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
exclude_patterns:
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/dist/**"
  - "**/build/**"
```

## Success Criteria
- [ ] All repositories successfully analyzed
- [ ] Tech stack accurately identified (>90% confidence)
- [ ] Cross-repo dependencies discovered
- [ ] Architecture pattern inferred
- [ ] Output files generated in context.generated/
- [ ] No critical errors

## Next Step
→ RepoScannerAgent (Step 2): Detailed file and code analysis
