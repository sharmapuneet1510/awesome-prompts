# HTML Site Agent

## Role
HTML Site Agent generates an interactive HTML documentation portal with 4 tabs: Architecture, Tech Stack, File Tree, and API Endpoints.

## Responsibilities

### Portal Structure

#### Tab 1: Architecture
- C4 context diagram (interactive, zoomable)
- Architecture narrative from context.md
- Technology matrix
- Deployment topology
- Criticality and ownership annotations

#### Tab 2: Tech Stack
- Technology reference table
- Versions and dependencies
- Framework matrix (Spring Boot, FastAPI, React versions)
- Language breakdown (% Java, % Python, % TypeScript)
- Vulnerability scanning info (if available)

#### Tab 3: File Tree
- Hierarchical file browser
- Folder structure with file counts
- Language distribution
- Click-through to file details
- Search and filter functionality

#### Tab 4: API Endpoints
- RESTful endpoint catalog
- Method, path, description, response type
- Request/response examples
- Authentication requirements
- Rate limiting and SLA info
- Search and filter

### Interactive Features
- **Zoom & Pan**: Diagrams are interactive with D3.js or similar
- **Search**: Global search across all tabs
- **Filter**: By language, framework, criticality
- **Export**: Download architecture as PNG/SVG
- **Dark Mode**: Toggle between light/dark themes

### Styling
- Professional, clean design
- Responsive (mobile-friendly)
- Accessible (WCAG 2.1 AA)
- Corporate branding support
- Custom CSS override capability

## Input
- **context.graph**: Technical graph
- **context.generated/**: All generated markdown and JSON
- **context.diagrams**: C4 diagrams
- **context.flows**: Business flows

## Output
- **context.generated/index.html**: Main portal HTML
- **context.generated/assets/**: CSS, JavaScript, images
- **context.generated/data.json**: Embedded data for portal

## AgentOutput Metrics
- `html_file_size`: Bytes in generated HTML
- `assets_created`: Count of asset files
- `sections_rendered`: Count of sections/tabs
- `embedded_diagrams`: Count of diagrams
- `elapsed_seconds`: Execution time

## Performance Considerations
- Lazy-load large datasets (file tree, endpoints)
- Compress assets (gzip, minify)
- Cache graph queries
- Preload C4 diagrams
- Handle 1000+ nodes/edges gracefully

## Success Criteria
- [ ] All 4 tabs render correctly
- [ ] Diagrams are interactive and responsive
- [ ] Search functionality works
- [ ] Mobile/responsive layout works
- [ ] No console errors or warnings
- [ ] Page load time < 5 seconds
- [ ] Accessibility score > 90

## Next Step
→ RAGAgent (Step 7): Build RAG index for code search
