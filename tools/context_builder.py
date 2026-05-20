from datetime import datetime
from typing import Dict, List, Any, Tuple
import json
from pathlib import Path


class ContextBuilder:
    """Build context.json from project structure and requirements."""

    def __init__(self, requirement_data: Dict[str, Any]):
        """Initialize with parsed requirement data."""
        self.requirement_data = requirement_data
        self.context: Dict[str, Any] = {}

    def build(self) -> Dict[str, Any]:
        """Build complete context dictionary."""
        # Build tech_stack first since other methods depend on it
        self.context = {
            'project_name': self.requirement_data.get('project_name', 'Unnamed Project'),
            'created_at': datetime.now().isoformat(),
            'tech_stack': self._build_tech_stack(),
        }
        # Now add dependent structures
        self.context.update({
            'file_structure': self._build_file_structure(),
            'api_endpoints': self._build_api_endpoints(),
            'database': self._build_database_schema(),
            'dependencies': self._build_dependencies(),
            'test_coverage': self._build_test_coverage(),
        })
        return self.context

    def _build_tech_stack(self) -> Dict[str, str]:
        """Extract and return tech stack from requirement data."""
        tech_stack = self.requirement_data.get('tech_stack', {})
        return {
            'frontend': tech_stack.get('frontend', 'React 18+'),
            'backend': tech_stack.get('backend', 'Python/FastAPI'),
            'database': tech_stack.get('database', 'PostgreSQL'),
            'auth': tech_stack.get('auth', 'JWT'),
        }

    def _build_file_structure(self) -> Dict[str, Any]:
        """Create expected folder structure based on tech stack."""
        backend = self.context['tech_stack']['backend'].lower()

        if 'fastapi' in backend or 'python' in backend:
            return self._build_python_structure()
        elif 'spring' in backend or 'java' in backend:
            return self._build_java_structure()
        else:
            return self._build_python_structure()  # Default to Python

    def _build_python_structure(self) -> Dict[str, Any]:
        """Build Python/FastAPI project structure."""
        return {
            'backend': {
                'app': {
                    'main.py': 'FastAPI application entry point',
                    'config.py': 'Configuration management',
                    'dependencies.py': 'Dependency injection setup',
                    'models': {
                        '__init__.py': '',
                        'user.py': 'User data models',
                        'base.py': 'Base model definitions',
                    },
                    'schemas': {
                        '__init__.py': '',
                        'user.py': 'Pydantic schemas for validation',
                        'responses.py': 'Response schemas',
                    },
                    'routes': {
                        '__init__.py': '',
                        'auth.py': 'Authentication endpoints',
                        'users.py': 'User management endpoints',
                        'health.py': 'Health check endpoint',
                    },
                    'services': {
                        '__init__.py': '',
                        'auth_service.py': 'Authentication logic',
                        'user_service.py': 'User management logic',
                    },
                    'utils': {
                        '__init__.py': '',
                        'security.py': 'Security utilities (hashing, tokens)',
                        'validators.py': 'Input validation utilities',
                    },
                    'middleware': {
                        '__init__.py': '',
                        'error_handler.py': 'Global error handling',
                        'auth_middleware.py': 'Authentication middleware',
                    },
                },
                'tests': {
                    '__init__.py': '',
                    'test_auth.py': 'Authentication tests',
                    'test_users.py': 'User endpoint tests',
                    'conftest.py': 'Pytest fixtures and configuration',
                },
                'requirements.txt': 'Python dependencies',
                '.env.example': 'Environment variables template',
            },
            'frontend': {
                'src': {
                    'components': {
                        'Auth': 'Authentication components',
                        'UserProfile': 'User profile components',
                        'Common': 'Reusable components',
                    },
                    'pages': {
                        'LoginPage.tsx': 'Login page',
                        'RegisterPage.tsx': 'Registration page',
                        'DashboardPage.tsx': 'Dashboard page',
                    },
                    'services': 'API client and services',
                    'hooks': 'Custom React hooks',
                    'context': 'React context for state management',
                    'utils': 'Utility functions',
                    'App.tsx': 'Root component',
                    'index.css': 'Global styles',
                },
                'public': 'Static assets',
                'package.json': 'Node dependencies',
                'tsconfig.json': 'TypeScript configuration',
            },
        }

    def _build_java_structure(self) -> Dict[str, Any]:
        """Build Java/Spring Boot project structure."""
        return {
            'backend': {
                'src': {
                    'main': {
                        'java': {
                            'com/project/app': {
                                'Application.java': 'Spring Boot main class',
                                'config': 'Configuration classes',
                                'controller': 'REST controllers',
                                'service': 'Business logic services',
                                'repository': 'Data access objects',
                                'entity': 'JPA entities',
                                'dto': 'Data transfer objects',
                                'security': 'Security configuration',
                                'util': 'Utility classes',
                            }
                        },
                        'resources': {
                            'application.properties': 'Application configuration',
                            'application-dev.properties': 'Development configuration',
                        }
                    },
                    'test': {
                        'java': {
                            'com/project/app': 'Test classes',
                        }
                    }
                },
                'pom.xml': 'Maven configuration',
            }
        }

    def _build_api_endpoints(self) -> List[Dict[str, Any]]:
        """Infer API endpoints from features."""
        features = self.requirement_data.get('features', [])
        endpoints = []

        # Feature to endpoint mapping
        feature_endpoint_map = {
            'login': [('POST', '/api/auth/login', 'User login')],
            'registration': [('POST', '/api/auth/register', 'User registration')],
            'register': [('POST', '/api/auth/register', 'User registration')],
            'logout': [('POST', '/api/auth/logout', 'User logout')],
            'authentication': [('POST', '/api/auth/login', 'User authentication')],
            'auth': [
                ('POST', '/api/auth/login', 'User login'),
                ('POST', '/api/auth/register', 'User registration'),
            ],
            'profile': [
                ('GET', '/api/users/profile', 'Get user profile'),
                ('PUT', '/api/users/profile', 'Update user profile'),
            ],
            'user': [
                ('GET', '/api/users', 'List all users'),
                ('GET', '/api/users/{id}', 'Get user by ID'),
                ('PUT', '/api/users/{id}', 'Update user'),
                ('DELETE', '/api/users/{id}', 'Delete user'),
            ],
            'product': [
                ('GET', '/api/products', 'List all products'),
                ('GET', '/api/products/{id}', 'Get product by ID'),
                ('POST', '/api/products', 'Create product'),
                ('PUT', '/api/products/{id}', 'Update product'),
                ('DELETE', '/api/products/{id}', 'Delete product'),
            ],
            'cart': [
                ('GET', '/api/cart', 'Get shopping cart'),
                ('POST', '/api/cart/items', 'Add item to cart'),
                ('DELETE', '/api/cart/items/{id}', 'Remove item from cart'),
                ('PUT', '/api/cart/items/{id}', 'Update cart item'),
            ],
            'order': [
                ('POST', '/api/orders', 'Create order'),
                ('GET', '/api/orders', 'List user orders'),
                ('GET', '/api/orders/{id}', 'Get order details'),
            ],
            'checkout': [
                ('POST', '/api/checkout', 'Initiate checkout'),
                ('GET', '/api/checkout/status/{id}', 'Get checkout status'),
            ],
            'activity': [
                ('GET', '/api/activities', 'List activities'),
                ('POST', '/api/activities', 'Log activity'),
                ('GET', '/api/activities/{id}', 'Get activity details'),
            ],
            'report': [
                ('GET', '/api/reports', 'List reports'),
                ('GET', '/api/reports/{id}', 'Get report'),
                ('POST', '/api/reports', 'Generate report'),
            ],
            'logging': [
                ('POST', '/api/logs', 'Submit log entry'),
                ('GET', '/api/logs', 'Get logs'),
            ],
            'email': [
                ('POST', '/api/email/send', 'Send email'),
                ('POST', '/api/email/verify', 'Verify email'),
            ],
            'verification': [
                ('POST', '/api/auth/verify-email', 'Verify email address'),
                ('POST', '/api/auth/resend-verification', 'Resend verification email'),
            ],
        }

        # Build endpoints from features
        seen_endpoints = set()
        for feature in features:
            feature_lower = feature.lower()
            for keyword, endpoint_list in feature_endpoint_map.items():
                if keyword in feature_lower:
                    for method, path, description in endpoint_list:
                        endpoint_key = (method, path)
                        if endpoint_key not in seen_endpoints:
                            endpoints.append({
                                'path': path,
                                'method': method,
                                'description': description,
                                'request_body': method in ['POST', 'PUT', 'PATCH'],
                                'response_code': 200,
                            })
                            seen_endpoints.add(endpoint_key)

        # Always include health check
        if ('GET', '/api/health') not in seen_endpoints:
            endpoints.append({
                'path': '/api/health',
                'method': 'GET',
                'description': 'Health check endpoint',
                'request_body': False,
                'response_code': 200,
            })

        return endpoints

    def _build_database_schema(self) -> Dict[str, Any]:
        """Infer database tables from features."""
        features = self.requirement_data.get('features', [])
        tables = []

        # Feature to table mapping
        feature_table_map = {
            'login': 'users',
            'registration': 'users',
            'register': 'users',
            'authentication': 'users',
            'auth': 'users',
            'profile': 'users',
            'user': 'users',
            'activity': 'activity_logs',
            'logging': 'activity_logs',
            'order': 'orders',
            'checkout': 'orders',
            'product': 'products',
            'cart': 'shopping_carts',
            'report': 'reports',
            'email': 'emails',
            'verification': 'email_verifications',
        }

        # Collect required tables
        required_tables = set()
        for feature in features:
            feature_lower = feature.lower()
            for keyword, table_name in feature_table_map.items():
                if keyword in feature_lower:
                    required_tables.add(table_name)

        # Define table schemas
        table_definitions = {
            'users': {
                'name': 'users',
                'columns': [
                    {'name': 'id', 'type': 'UUID PRIMARY KEY'},
                    {'name': 'email', 'type': 'VARCHAR(255) UNIQUE NOT NULL'},
                    {'name': 'username', 'type': 'VARCHAR(100) UNIQUE NOT NULL'},
                    {'name': 'password_hash', 'type': 'VARCHAR(255) NOT NULL'},
                    {'name': 'first_name', 'type': 'VARCHAR(100)'},
                    {'name': 'last_name', 'type': 'VARCHAR(100)'},
                    {'name': 'is_active', 'type': 'BOOLEAN DEFAULT TRUE'},
                    {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                    {'name': 'updated_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                ],
            },
            'activity_logs': {
                'name': 'activity_logs',
                'columns': [
                    {'name': 'id', 'type': 'UUID PRIMARY KEY'},
                    {'name': 'user_id', 'type': 'UUID NOT NULL'},
                    {'name': 'action', 'type': 'VARCHAR(255) NOT NULL'},
                    {'name': 'description', 'type': 'TEXT'},
                    {'name': 'ip_address', 'type': 'VARCHAR(45)'},
                    {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                ],
            },
            'orders': {
                'name': 'orders',
                'columns': [
                    {'name': 'id', 'type': 'UUID PRIMARY KEY'},
                    {'name': 'user_id', 'type': 'UUID NOT NULL'},
                    {'name': 'status', 'type': 'VARCHAR(50) DEFAULT \'pending\''},
                    {'name': 'total_amount', 'type': 'DECIMAL(10, 2)'},
                    {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                    {'name': 'updated_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                ],
            },
            'products': {
                'name': 'products',
                'columns': [
                    {'name': 'id', 'type': 'UUID PRIMARY KEY'},
                    {'name': 'name', 'type': 'VARCHAR(255) NOT NULL'},
                    {'name': 'description', 'type': 'TEXT'},
                    {'name': 'price', 'type': 'DECIMAL(10, 2) NOT NULL'},
                    {'name': 'stock_quantity', 'type': 'INTEGER DEFAULT 0'},
                    {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                    {'name': 'updated_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                ],
            },
            'shopping_carts': {
                'name': 'shopping_carts',
                'columns': [
                    {'name': 'id', 'type': 'UUID PRIMARY KEY'},
                    {'name': 'user_id', 'type': 'UUID NOT NULL'},
                    {'name': 'product_id', 'type': 'UUID NOT NULL'},
                    {'name': 'quantity', 'type': 'INTEGER NOT NULL'},
                    {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                    {'name': 'updated_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                ],
            },
            'reports': {
                'name': 'reports',
                'columns': [
                    {'name': 'id', 'type': 'UUID PRIMARY KEY'},
                    {'name': 'user_id', 'type': 'UUID NOT NULL'},
                    {'name': 'title', 'type': 'VARCHAR(255) NOT NULL'},
                    {'name': 'content', 'type': 'TEXT'},
                    {'name': 'generated_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                ],
            },
            'emails': {
                'name': 'emails',
                'columns': [
                    {'name': 'id', 'type': 'UUID PRIMARY KEY'},
                    {'name': 'recipient', 'type': 'VARCHAR(255) NOT NULL'},
                    {'name': 'subject', 'type': 'VARCHAR(255) NOT NULL'},
                    {'name': 'body', 'type': 'TEXT'},
                    {'name': 'sent_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                ],
            },
            'email_verifications': {
                'name': 'email_verifications',
                'columns': [
                    {'name': 'id', 'type': 'UUID PRIMARY KEY'},
                    {'name': 'user_id', 'type': 'UUID NOT NULL'},
                    {'name': 'email', 'type': 'VARCHAR(255) NOT NULL'},
                    {'name': 'token', 'type': 'VARCHAR(255) UNIQUE NOT NULL'},
                    {'name': 'is_verified', 'type': 'BOOLEAN DEFAULT FALSE'},
                    {'name': 'created_at', 'type': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'},
                    {'name': 'expires_at', 'type': 'TIMESTAMP'},
                ],
            },
        }

        # Always include users table
        required_tables.add('users')

        # Build table list
        for table_name in sorted(required_tables):
            if table_name in table_definitions:
                tables.append(table_definitions[table_name])

        return {
            'type': self.requirement_data.get('tech_stack', {}).get('database', 'PostgreSQL'),
            'tables': tables,
        }

    def _build_dependencies(self) -> Dict[str, List[str]]:
        """Build placeholder dependencies structure."""
        backend = self.context['tech_stack']['backend'].lower()
        frontend = self.context['tech_stack']['frontend'].lower()

        dependencies = {'backend': [], 'frontend': []}

        # Backend dependencies
        if 'fastapi' in backend or 'python' in backend:
            dependencies['backend'] = [
                'fastapi>=0.104.0',
                'uvicorn>=0.24.0',
                'sqlalchemy>=2.0.0',
                'pydantic>=2.0.0',
                'python-dotenv>=1.0.0',
                'pytest>=7.4.0',
                'pytest-asyncio>=0.21.0',
            ]
        elif 'spring' in backend or 'java' in backend:
            dependencies['backend'] = [
                'spring-boot-starter-web',
                'spring-boot-starter-data-jpa',
                'spring-boot-starter-security',
                'spring-boot-starter-validation',
                'postgresql',
                'junit-jupiter-api',
                'junit-jupiter-engine',
            ]

        # Frontend dependencies
        if 'react' in frontend:
            dependencies['frontend'] = [
                'react@18.x',
                'react-dom@18.x',
                'react-router-dom@6.x',
                'axios@latest',
                '@tanstack/react-query@latest',
                'zustand@latest',
                'typescript@latest',
            ]

        return dependencies

    def _build_test_coverage(self) -> Dict[str, Any]:
        """Build test coverage structure."""
        return {
            'unit_tests': {
                'target_coverage': 80,
                'directories': ['services', 'utils', 'models'],
            },
            'integration_tests': {
                'target_coverage': 70,
                'directories': ['routes', 'api_endpoints'],
            },
            'e2e_tests': {
                'target_coverage': 60,
                'framework': 'pytest' if 'python' in self.context['tech_stack']['backend'].lower() else 'junit',
            },
        }

    def save(self, output_path: str = 'context.json') -> str:
        """Save context to JSON file."""
        if not self.context:
            self.build()

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.context, f, indent=2, default=str)

        return str(output_file.resolve())

    def save_full_context(self, output_dir: str = 'docs/context') -> Dict[str, str]:
        """Save complete context to docs/context/ with all files.

        Generates:
        - context.json — machine-readable
        - architecture.md — Mermaid diagram + narrative
        - tech-stack.md — tech reference table
        - design.html — interactive visualization

        Args:
            output_dir: Where to save all context files

        Returns:
            Dict mapping file names to their paths
        """
        if not self.context:
            self.build()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        files = {}

        # 1. Save context.json
        context_json = output_path / 'context.json'
        with open(context_json, 'w') as f:
            json.dump(self.context, f, indent=2, default=str)
        files['context.json'] = str(context_json.resolve())

        # 2. Save architecture.md
        architecture_md = output_path / 'architecture.md'
        arch_content = self._generate_architecture_md()
        with open(architecture_md, 'w') as f:
            f.write(arch_content)
        files['architecture.md'] = str(architecture_md.resolve())

        # 3. Save tech-stack.md
        tech_md = output_path / 'tech-stack.md'
        tech_content = self._generate_tech_stack_md()
        with open(tech_md, 'w') as f:
            f.write(tech_content)
        files['tech-stack.md'] = str(tech_md.resolve())

        # 4. Generate and save design.html
        try:
            from generate_design_html import DesignHTMLGenerator
            generator = DesignHTMLGenerator(context_json)
            design_html = output_path / 'design.html'
            generator.save(design_html)
            files['design.html'] = str(design_html.resolve())
        except ImportError:
            print("Warning: generate_design_html.py not found. Skipping HTML generation.")

        return files

    def _generate_architecture_md(self) -> str:
        """Generate architecture.md with Mermaid diagram."""
        tech_stack = self.context.get('tech_stack', {})
        project = self.context.get('project_name', 'Project')

        markdown = f"""# Architecture — {project}

## System Overview

This document describes the architecture of {project}, including tech stack, components, and data flow.

## Tech Stack

- **Frontend:** {tech_stack.get('frontend', 'React 18+')}
- **Backend:** {tech_stack.get('backend', 'Python FastAPI')}
- **Database:** {tech_stack.get('database', 'PostgreSQL')}
- **Authentication:** {tech_stack.get('auth', 'JWT')}

## Component Diagram

```mermaid
graph TB
    Client["Frontend<br/>{tech_stack.get('frontend', 'React')}"]
    API["Backend API<br/>{tech_stack.get('backend', 'FastAPI')}"]
    DB["Database<br/>{tech_stack.get('database', 'PostgreSQL')}"]

    Client -->|REST API| API
    API -->|SQL Queries| DB
    Client -->|Authentication| API
```

## Data Flow

1. **User Interaction** → Frontend captures user input
2. **API Request** → Frontend sends REST request to Backend
3. **Validation** → Backend validates request data
4. **Database Query** → Backend queries PostgreSQL
5. **Response** → Backend returns data to Frontend
6. **Rendering** → Frontend updates UI with response data

## File Structure

Generated automatically based on tech stack:

```
{project}/
├── backend/                 ← Backend application
│   ├── app/                 ← FastAPI app
│   │   ├── main.py         ← Entry point
│   │   ├── routes/         ← API endpoints
│   │   ├── models/         ← Data models
│   │   └── services/       ← Business logic
│   └── tests/              ← Test suite
│
├── frontend/                ← Frontend application
│   ├── src/
│   │   ├── components/     ← React components
│   │   ├── pages/          ← Page components
│   │   └── hooks/          ← Custom hooks
│   └── public/             ← Static assets
│
└── docs/context/           ← Architecture documentation
    ├── architecture.md     ← This file
    ├── tech-stack.md       ← Technology reference
    ├── context.json        ← Machine-readable context
    └── design.html         ← Interactive visualization
```

## Key Decisions

### Why {tech_stack.get('backend', 'FastAPI')}?
- Async/await support for I/O-bound operations
- Automatic API documentation (Swagger UI)
- Modern Python features (type hints, dataclasses)
- Easy testing with pytest

### Why {tech_stack.get('frontend', 'React')}?
- Component-based architecture
- Rich ecosystem (React Router, TanStack Query, etc.)
- Virtual DOM for efficient rendering
- Strong TypeScript support

### Why {tech_stack.get('database', 'PostgreSQL')}?
- ACID compliance for data integrity
- Relational schema for complex queries
- Advanced features (JSON, full-text search)
- Excellent performance for moderate scale

## Dependencies

Key packages installed in requirements.txt and package.json:

### Backend
{self._generate_backend_dependencies()}

### Frontend
{self._generate_frontend_dependencies()}

## Testing Strategy

- **Unit Tests:** Test individual functions and methods
- **Integration Tests:** Test API endpoints with real database
- **E2E Tests:** Test user workflows end-to-end

Target coverage: ≥ 80% for critical paths

## Deployment

- **Frontend:** Built with npm run build, served by Nginx
- **Backend:** Docker container, deployed to AWS ECS
- **Database:** Managed PostgreSQL instance (AWS RDS)
- **CI/CD:** GitHub Actions pipeline

## Performance Considerations

- Frontend bundling with Webpack
- API caching with Redis (optional)
- Database indexing on frequently queried columns
- Connection pooling for database connections

## Security

- JWT tokens for stateless authentication
- HTTPS for all communications
- Environment variables for secrets
- Input validation on all endpoints
- CORS configuration for cross-origin requests

## Monitoring & Logging

- Application logs to stdout (container-friendly)
- Metrics collection with Prometheus (optional)
- Error tracking with Sentry (optional)
- Health check endpoint at /api/health
"""

        return markdown

    def _generate_backend_dependencies(self) -> str:
        """Generate list of backend dependencies."""
        backend = self.context.get('tech_stack', {}).get('backend', '').lower()
        if 'fastapi' in backend or 'python' in backend:
            return """- fastapi — Web framework
- sqlalchemy — SQL ORM
- pydantic — Data validation
- pytest — Testing framework
- python-dotenv — Environment variables
- passlib — Password hashing
- pyjwt — JWT token handling
- cors — Cross-origin resource sharing"""
        else:
            return """- spring-boot — Application framework
- spring-data-jpa — JPA repository abstraction
- spring-security — Authentication/authorization
- junit5 — Testing framework
- lombok — Boilerplate reduction
- jackson — JSON processing"""

    def _generate_frontend_dependencies(self) -> str:
        """Generate list of frontend dependencies."""
        return """- react — UI framework
- react-router-dom — Client-side routing
- typescript — Type safety
- tailwindcss — Utility-first CSS
- @tanstack/react-query — Data fetching
- zustand — State management
- axios — HTTP client
- jest — Testing framework"""

    def _generate_tech_stack_md(self) -> str:
        """Generate tech-stack.md reference table."""
        tech_stack = self.context.get('tech_stack', {})

        markdown = """# Tech Stack Reference

This table maps technologies to their purposes and corresponding skill files.

| Technology | Purpose | Category | Skill File | Notes |
|-----------|---------|----------|-----------|-------|
"""

        # Frontend
        markdown += """| React | Frontend UI framework | Frontend | react_advanced_skill.md | Component-based, virtual DOM |
| TypeScript | Type safety for JavaScript | Frontend | react_advanced_skill.md | Prevents common runtime errors |
| TailwindCSS | Utility-first CSS framework | Frontend | react_advanced_skill.md | Fast styling, responsive design |
| TanStack Query | Server state management | Frontend | react_advanced_skill.md | Caching, synchronization, mutations |
| Zustand | Client state management | Frontend | react_advanced_skill.md | Lightweight, performant |

"""

        # Backend
        if 'fastapi' in tech_stack.get('backend', '').lower() or 'python' in tech_stack.get('backend', '').lower():
            markdown += """| FastAPI | Web framework | Backend | python_advanced_skill.md | Async, auto-docs, fast |
| SQLAlchemy | ORM for database access | Backend | python_advanced_skill.md | Query builder, relationships |
| Pydantic | Data validation | Backend | python_advanced_skill.md | Type hints, automatic validation |
| pytest | Unit & integration testing | Backend | testing_pytest_skill.md | Fixtures, parametrization |
| python-jose | JWT token handling | Backend | python_advanced_skill.md | Secure token management |

"""
        else:
            markdown += """| Spring Boot | Web framework | Backend | spring_advanced_skill.md | Convention over configuration |
| Spring Data JPA | ORM for database access | Backend | spring_advanced_skill.md | Automatic query generation |
| Spring Security | Authentication/authorization | Backend | spring_advanced_skill.md | Token, session management |
| JUnit5 | Unit & integration testing | Backend | testing_junit5_skill.md | Parametrized tests, extensions |

"""

        # Database
        markdown += f"""| {tech_stack.get('database', 'PostgreSQL')} | Relational database | Database | mssql_advanced_skill.md | ACID, JSON support |
| Docker | Containerization | DevOps | integration_agent.md | Consistent environment |
| Docker Compose | Multi-container orchestration | DevOps | integration_agent.md | Local development |

---

## Skill Files Reference

- **react_advanced_skill.md** — React 18+, hooks, testing, best practices
- **python_advanced_skill.md** — Python 3.11+, FastAPI, async/await, testing
- **spring_advanced_skill.md** — Spring Boot 3.x, dependency injection, patterns
- **testing_pytest_skill.md** — pytest framework, fixtures, mocking
- **testing_junit5_skill.md** — JUnit5 testing, Mockito, parametrization
- **mssql_advanced_skill.md** — SQL Server, T-SQL, optimization
- **integration_agent.md** — CI/CD pipelines, Docker, Kubernetes

See `agents/developer_agent.md` for how these skills are applied during development.
"""

        return markdown
