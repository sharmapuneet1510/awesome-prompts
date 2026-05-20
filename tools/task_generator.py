from datetime import datetime
from typing import Dict, List, Any


class TaskGenerator:
    """Generate task specifications from requirement data."""

    TASK_TEMPLATES = [
        {
            'id': '01',
            'title': 'Database Schema & Migrations',
            'skill': 'Database Design',
            'duration': '2-3 days',
        },
        {
            'id': '02',
            'title': 'Backend API & Services',
            'skill': 'Backend Development',
            'duration': '4-5 days',
        },
        {
            'id': '03',
            'title': 'Frontend UI Components',
            'skill': 'Frontend Development',
            'duration': '4-5 days',
        },
        {
            'id': '04',
            'title': 'Integration Tests',
            'skill': 'QA & Testing',
            'duration': '2-3 days',
        },
        {
            'id': '05',
            'title': 'Deployment & CI/CD',
            'skill': 'DevOps & Infrastructure',
            'duration': '2-3 days',
        },
    ]

    def __init__(self, requirement_data: Dict[str, Any]):
        """Initialize with parsed requirement data."""
        self.requirement = requirement_data
        self.project_name = requirement_data.get('project_name', 'Unknown Project')
        self.tech_stack = requirement_data.get('tech_stack', {})
        self.features = requirement_data.get('features', [])
        self.timeline = requirement_data.get('timeline', 'Not specified')

    def generate(self) -> List[Dict[str, Any]]:
        """Generate all 5 task specifications."""
        tasks = []

        for template in self.TASK_TEMPLATES:
            task_id = template['id']

            if task_id == '01':
                spec = self._spec_database_schema()
            elif task_id == '02':
                spec = self._spec_backend_api()
            elif task_id == '03':
                spec = self._spec_frontend_ui()
            elif task_id == '04':
                spec = self._spec_integration_tests()
            elif task_id == '05':
                spec = self._spec_deployment()
            else:
                spec = self._generate_spec(template)

            task = {
                'id': task_id,
                'title': template['title'],
                'skill': template['skill'],
                'duration': template['duration'],
                'spec': spec,
            }
            tasks.append(task)

        return tasks

    def _generate_spec(self, template: Dict[str, Any]) -> str:
        """Create a generic markdown spec for a task."""
        task_id = template['id']
        title = template['title']
        skill = template['skill']
        duration = template['duration']

        spec = f"""---
id: {task_id}
title: {title}
project: {self.project_name.lower().replace(' ', '_')}
skill: {skill}
duration: {duration}
generated_at: {datetime.now().isoformat()}
---

# Task {task_id}: {title}

## Context
Project: **{self.project_name}**
Skill: {skill}
Estimated Duration: {duration}

## Requirements:
- Implement as part of {self.project_name} project
- Follow tech stack: Frontend ({self.tech_stack.get('frontend', 'React')}), Backend ({self.tech_stack.get('backend', 'Python/FastAPI')}), Database ({self.tech_stack.get('database', 'PostgreSQL')})
- Integrate with other tasks (01-05)

## Acceptance Criteria:
- [ ] Task completed and peer reviewed
- [ ] Code follows project standards
- [ ] Documentation updated
- [ ] Integrated with adjacent tasks

## Success Metrics:
- Code quality score ≥ 85%
- Test coverage ≥ 80%
- All acceptance criteria met
"""
        return spec

    def _spec_database_schema(self) -> str:
        """Generate database schema task spec."""
        spec = f"""---
id: 01
title: Database Schema & Migrations
project: {self.project_name.lower().replace(' ', '_')}
skill: Database Design
duration: 2-3 days
generated_at: {datetime.now().isoformat()}
---

# Task 01: Database Schema & Migrations

## Context
Project: **{self.project_name}**
Technology: {self.tech_stack.get('database', 'PostgreSQL')}
Timeline: {self.timeline}

## Requirements:

### Schema Design
- Design database schema for {self.project_name}
- Create tables for core entities"""

        # Add feature-based requirements
        if any(f in str(self.features).lower() for f in ['login', 'registration', 'auth', 'user']):
            spec += """
- Include users table with authentication fields (email, password_hash, salt)
- Add user_roles table for role-based access control"""

        if any(f in str(self.features).lower() for f in ['activity', 'log', 'audit', 'history']):
            spec += """
- Include activity_logs table for audit trail"""

        spec += f"""
- Add timestamps (created_at, updated_at) to all tables
- Define foreign key relationships
- Create indexes for frequently queried columns

### Migrations
- Create initial schema migration file
- Add seed data migrations if needed
- Ensure idempotent migrations

## Acceptance Criteria:

- [ ] Database schema designed and documented
- [ ] Migration scripts created and tested
- [ ] All tables include proper indexes
- [ ] Relationships and constraints defined
- [ ] Migration rollback tested
- [ ] Schema documentation in place

## Success Metrics:

- Schema normalized to 3NF
- Migration execution time < 30 seconds
- Zero referential integrity violations
- Test coverage ≥ 80%
"""
        return spec

    def _spec_backend_api(self) -> str:
        """Generate backend API task spec."""
        backend_tech = self.tech_stack.get('backend', 'Python/FastAPI')
        spec = f"""---
id: 02
title: Backend API & Services
project: {self.project_name.lower().replace(' ', '_')}
skill: Backend Development
duration: 4-5 days
generated_at: {datetime.now().isoformat()}
---

# Task 02: Backend API & Services

## Context
Project: **{self.project_name}**
Technology: {backend_tech}
API Style: RESTful

## Requirements:

### API Routes
- Create REST endpoints for core features"""

        # Add feature-based endpoints
        if any(f in str(self.features).lower() for f in ['login', 'registration', 'auth']):
            spec += """
- POST /auth/register - User registration
- POST /auth/login - User login
- POST /auth/logout - User logout
- GET /auth/me - Get current user
- POST /auth/refresh - Refresh JWT token"""

        if any(f in str(self.features).lower() for f in ['user', 'profile']):
            spec += """
- GET /users - List all users (admin only)
- GET /users/:id - Get user by ID
- PUT /users/:id - Update user profile
- DELETE /users/:id - Delete user"""

        spec += """
- Proper HTTP status codes
- JSON request/response format
- Error handling with meaningful messages

### Services & Models
- Create data models with validation
- Implement service layer for business logic
- Add dependency injection
- Proper error handling and logging

### Authentication & Authorization
- Implement JWT token generation and validation
- Add role-based access control (RBAC)
- Secure password hashing

## Acceptance Criteria:

- [ ] All API routes implemented and tested
- [ ] Data models with validation
- [ ] Service layer complete
- [ ] Authentication/authorization working
- [ ] Error handling comprehensive
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Integration tests passing

## Success Metrics:

- API response time < 200ms
- Test coverage ≥ 85%
- All endpoints documented
- Zero security vulnerabilities
"""
        return spec

    def _spec_frontend_ui(self) -> str:
        """Generate frontend UI task spec."""
        frontend_tech = self.tech_stack.get('frontend', 'React 18+')
        spec = f"""---
id: 03
title: Frontend UI Components
project: {self.project_name.lower().replace(' ', '_')}
skill: Frontend Development
duration: 4-5 days
generated_at: {datetime.now().isoformat()}
---

# Task 03: Frontend UI Components

## Context
Project: **{self.project_name}**
Technology: {frontend_tech}
Component Library: TailwindCSS

## Requirements:

### Core Components
- Create reusable UI components (Button, Input, Card, Modal)
- Implement layout components (Header, Sidebar, Footer)
- Add form components with validation"""

        # Add feature-based UI components
        if any(f in str(self.features).lower() for f in ['login', 'registration']):
            spec += """
- LoginPage - Email/password form with JWT handling
- RegisterPage - User registration form with validation
- ProfilePage - User profile view and edit"""

        spec += """
- Proper TypeScript types for all props
- Error boundary components

### Styling & Theming
- Use TailwindCSS for consistent styling
- Implement responsive design (mobile-first)
- Add dark/light theme support
- Maintain component library consistency

### State Management
- Implement global state (Zustand/Redux)
- User authentication state
- API response caching
- Loading and error states

## Acceptance Criteria:

- [ ] All UI components built and storybooked
- [ ] Responsive design verified on mobile/tablet/desktop
- [ ] Theme switching working
- [ ] Form validation complete
- [ ] Error states properly handled
- [ ] Accessibility (WCAG 2.1 AA) compliant
- [ ] Component tests passing

## Success Metrics:

- Lighthouse score ≥ 90
- Page load time < 2 seconds
- Component test coverage ≥ 85%
- Zero console errors
"""
        return spec

    def _spec_integration_tests(self) -> str:
        """Generate integration tests task spec."""
        spec = f"""---
id: 04
title: Integration Tests
project: {self.project_name.lower().replace(' ', '_')}
skill: QA & Testing
duration: 2-3 days
generated_at: {datetime.now().isoformat()}
---

# Task 04: Integration Tests

## Context
Project: **{self.project_name}**
Test Framework: Jest (frontend), pytest (backend)
Coverage Target: ≥ 80%

## Requirements:

### Backend Integration Tests
- Test API endpoints with real database
- Verify end-to-end request/response flow"""

        if any(f in str(self.features).lower() for f in ['login', 'registration', 'auth']):
            spec += """
- Test authentication flow (register → login → access protected route)
- Test JWT token generation and validation
- Test password hashing and security"""

        spec += """
- Test error scenarios and edge cases
- Verify database transactions

### Frontend Integration Tests
- Component interaction tests
- Form submission workflows"""

        if any(f in str(self.features).lower() for f in ['login', 'registration']):
            spec += """
- Authentication flow tests
- Protected route access tests"""

        spec += """
- API integration tests
- State management tests

### Test Data & Fixtures
- Create test database seeds
- Mock API responses
- Setup/teardown hooks

### Performance Tests
- Load testing with concurrent users
- Database query performance
- API response time benchmarks

## Acceptance Criteria:

- [ ] Backend integration tests written
- [ ] Frontend integration tests written
- [ ] All tests passing
- [ ] Test coverage ≥ 80%
- [ ] Performance benchmarks established
- [ ] CI/CD integration working
- [ ] Test documentation complete

## Success Metrics:

- Test execution time < 5 minutes
- All tests passing in CI/CD
- Code coverage ≥ 80%
- Zero flaky tests
"""
        return spec

    def _spec_deployment(self) -> str:
        """Generate deployment task spec."""
        spec = f"""---
id: 05
title: Deployment & CI/CD
project: {self.project_name.lower().replace(' ', '_')}
skill: DevOps & Infrastructure
duration: 2-3 days
generated_at: {datetime.now().isoformat()}
---

# Task 05: Deployment & CI/CD

## Context
Project: **{self.project_name}**
Target Platform: Docker + Kubernetes (or Cloud Platform)
Timeline: {self.timeline}

## Requirements:

### Containerization
- Create Dockerfile for backend service
- Create Dockerfile for frontend service
- Compose multi-container setup with docker-compose
- Optimize image sizes (multi-stage builds)

### CI/CD Pipeline
- GitHub Actions workflow for automated testing
- Automated linting and code quality checks
- Build and push Docker images
- Deploy to staging environment

### Deployment Configuration
- Environment variables management (.env files)
- Database migration automation on deployment
- Health checks and monitoring
- Rollback procedures

### Infrastructure Setup
- Cloud deployment (AWS, GCP, Azure, or DigitalOcean)
- Database setup and backups
- CDN configuration for static assets
- SSL/TLS certificate setup

### Monitoring & Logging
- Application logging setup
- Error tracking (Sentry, etc.)
- Performance monitoring
- Alert configuration

## Acceptance Criteria:

- [ ] Docker images build successfully
- [ ] docker-compose setup working locally
- [ ] CI/CD pipeline configured
- [ ] Automated tests run on push
- [ ] Staging deployment automated
- [ ] Production deployment documented
- [ ] Monitoring and alerts active
- [ ] Rollback procedure tested
- [ ] Security scanning enabled

## Success Metrics:

- Deployment time < 10 minutes
- Zero manual deployment steps
- 99.9% uptime target
- Sub-100ms latency from CDN
- All security scans passing
"""
        return spec
