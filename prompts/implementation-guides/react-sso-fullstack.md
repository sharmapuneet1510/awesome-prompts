# Build Production-Ready React App with Enterprise SSO

## Context
You have access to the awesome-prompts repository with 26 comprehensive skills covering:
- React 18+ best practices (react_advanced_skill)
- REST API design (rest_api_java_skill, rest_api_python_skill)
- Error handling & resilience (error_handling_skill)
- Testing patterns (testing_react_skill, testing_junit5_skill)
- Code health & observability (code_health_skill, logger_skill, opentelemetry_skill)
- Documentation standards (documentation_skill)

## Task
Build a **production-ready React application with enterprise SSO (OAuth2/OIDC)** following all best practices.

---

## Requirements

### 1. SSO Implementation
- [ ] OAuth2 / OpenID Connect (Okta, Auth0, Azure AD, or custom)
- [ ] JWT token handling and refresh token rotation
- [ ] Secure token storage (httpOnly cookies, not localStorage)
- [ ] PKCE flow for browser-based apps
- [ ] Role-based access control (RBAC)
- [ ] Automatic token refresh before expiry
- [ ] Logout with token revocation

### 2. React Frontend
Follow `react_advanced_skill`:
- [ ] Functional components with hooks
- [ ] TypeScript for type safety
- [ ] TanStack Query for server state
- [ ] Zustand or Context for client state
- [ ] React Router v6 with lazy loading
- [ ] Protected routes (redirect to login if unauthenticated)
- [ ] Error boundaries for error handling
- [ ] Suspense for async loading states

### 3. API Integration
Follow `rest_api_java_skill` / `rest_api_python_skill`:
- [ ] REST API backend with CORS configuration
- [ ] Bearer token authentication on all API calls
- [ ] Request/response interceptors
- [ ] Automatic retry on 401 (expired token)
- [ ] Proper error handling (4xx, 5xx responses)
- [ ] Request cancellation on component unmount
- [ ] Loading states and error states

### 4. Error Handling
Follow `error_handling_skill`:
- [ ] Try-catch in async operations
- [ ] User-friendly error messages
- [ ] Error logging to observability platform
- [ ] Graceful degradation
- [ ] Timeout handling for long requests
- [ ] Network failure retry logic

### 5. Testing
Follow `testing_react_skill`:
- [ ] Unit tests for components
- [ ] Integration tests for flows
- [ ] Mock SSO authentication
- [ ] Mock API responses
- [ ] Accessibility testing (a11y)
- [ ] E2E tests for critical paths (login, protected routes)

### 6. Observability & Logging
Follow `logger_skill` + `opentelemetry_skill`:
- [ ] Structured logging with correlation IDs
- [ ] Session tracking
- [ ] Error event logging
- [ ] Performance metrics
- [ ] Distributed tracing (trace SSO + API calls)
- [ ] User action tracking

### 7. Code Quality
Follow `code_health_skill` + `documentation_skill`:
- [ ] ESLint + Prettier configuration
- [ ] Component documentation (Storybook)
- [ ] API endpoint documentation
- [ ] README with setup instructions
- [ ] Environment configuration (.env.example)
- [ ] Security best practices documented

### 8. Security Checklist
- [ ] HTTPS only (enforce in production)
- [ ] CSRF protection on state-changing requests
- [ ] XSS prevention (sanitize user input)
- [ ] No secrets in frontend code
- [ ] Environment variables for API endpoints
- [ ] CSP headers configured
- [ ] SameSite cookie attribute
- [ ] Secure token refresh mechanism

---

## Tech Stack

```json
{
  "frontend": {
    "framework": "React 18+",
    "language": "TypeScript",
    "router": "React Router v6",
    "state": "Zustand or Context API",
    "server_state": "TanStack Query v5",
    "styling": "Tailwind CSS or Styled Components",
    "testing": "Vitest + React Testing Library",
    "e2e": "Playwright or Cypress",
    "linting": "ESLint + Prettier"
  },
  "backend": {
    "framework": "Spring Boot 3.x (Java 17+) or FastAPI (Python 3.11+)",
    "auth": "Spring Security or python-jose",
    "validation": "Lombok + Bean Validation or Pydantic"
  },
  "sso": {
    "protocol": "OAuth2 / OpenID Connect",
    "providers": "Okta, Auth0, Azure AD, or Keycloak",
    "library": "react-oauth/google or authjs"
  },
  "observability": {
    "logging": "SLF4J + Logback (backend) + Pino (frontend)",
    "tracing": "OpenTelemetry + Jaeger",
    "metrics": "Prometheus + Grafana"
  }
}
```

---

## Project Structure

```
my-app/
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable React components
│   │   ├── pages/            # Page components (route-based)
│   │   ├── hooks/            # Custom hooks (useSSOAuth, useApi)
│   │   ├── services/         # API service layer
│   │   ├── store/            # Zustand stores
│   │   ├── types/            # TypeScript interfaces
│   │   ├── utils/            # Utility functions
│   │   ├── App.tsx           # Main app with routing
│   │   └── main.tsx
│   ├── tests/                # Test files
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── src/
│   │   ├── main/java/com/example/
│   │   │   ├── config/       # Security, CORS, OAuth2 config
│   │   │   ├── controller/   # REST endpoints
│   │   │   ├── service/      # Business logic
│   │   │   ├── security/     # JWT, token validation
│   │   │   └── entity/       # JPA entities
│   │   └── resources/
│   │       └── application.yml
│   ├── tests/
│   └── pom.xml
│
└── docker-compose.yml        # Jaeger, Prometheus for local dev
```

---

## Implementation Phases

### Phase 1: Backend Setup
1. Create Spring Boot / FastAPI REST API
2. Configure OAuth2 resource server (validate JWT tokens)
3. Implement CORS (allow frontend origin)
4. Create protected endpoints (require Bearer token)
5. Add error handling and validation
6. Write API tests

### Phase 2: Frontend Setup
1. Create React + TypeScript project (Vite)
2. Install: react-router, zustand, @tanstack/react-query
3. Configure environment variables
4. Set up routing with ProtectedRoute component
5. Create layout components

### Phase 3: SSO Integration
1. Choose SSO provider (Okta, Auth0, Azure AD)
2. Register application with provider
3. Install SSO library (react-oauth/google, authjs)
4. Create useAuth hook for authentication state
5. Implement login/logout flows
6. Add token refresh logic
7. Store tokens securely (httpOnly cookie)

### Phase 4: API Integration
1. Create API service layer (fetch + TanStack Query)
2. Add request interceptor (inject Bearer token)
3. Add response interceptor (handle 401, refresh token)
4. Wire TanStack Query to backend endpoints
5. Test API calls with mock SSO

### Phase 5: Error Handling & Observability
1. Add error boundary component
2. Implement structured logging (correlation IDs)
3. Set up OpenTelemetry tracing
4. Configure Jaeger and Prometheus
5. Test observability flow

### Phase 6: Testing & QA
1. Write component unit tests
2. Write integration tests (login flow, protected routes)
3. Write API integration tests
4. Set up E2E tests (Playwright)
5. Security audit checklist

### Phase 7: Deployment
1. Build Docker images (frontend, backend)
2. Configure environment variables per environment
3. Set up CI/CD pipeline
4. Deploy to staging
5. Performance testing
6. Deploy to production

---

## Prompts to Use

After cloning the awesome-prompts repository, feed these prompts to Claude/Copilot:

### 1. Backend SSO Setup

```
Using skills from awesome-prompts repo (spring_advanced_skill,
rest_api_java_skill, error_handling_skill, logger_skill),
implement OAuth2 resource server in Spring Boot 3.x that:
- Validates JWT tokens from [SSO_PROVIDER]
- Protects REST endpoints with @PreAuthorize("isAuthenticated()")
- Implements custom exception handling
- Logs all authentication attempts
- Handles token expiry gracefully
```

### 2. React Frontend Setup

```
Using skills from awesome-prompts repo (react_advanced_skill,
testing_react_skill, error_handling_skill), create React 18+
TypeScript application with:
- Protected routes that redirect to login if unauthenticated
- useAuth hook managing JWT tokens
- TanStack Query for API calls with automatic token injection
- Error boundary catching component errors
- Tests for login flow and protected routes
```

### 3. SSO Integration

```
Integrate [SSO_PROVIDER] OAuth2 OIDC flow into React app:
- PKCE flow (no client secret in browser)
- Secure token storage (httpOnly cookies)
- Automatic token refresh before expiry
- Logout with token revocation
- Role-based route protection
```

### 4. API Integration

```
Create REST API service layer using best practices from
awesome-prompts (rest_api_java_skill, error_handling_skill):
- Request/response types with TypeScript interfaces
- TanStack Query hooks for each endpoint
- Automatic Bearer token injection
- Request cancellation on unmount
- Error retry logic with exponential backoff
```

### 5. Testing & Observability

```
Using awesome-prompts skills (testing_react_skill, logger_skill,
opentelemetry_skill), implement:
- Unit tests for authentication and API services
- Integration tests for protected routes
- Structured logging with correlation IDs
- OpenTelemetry tracing for API calls
- Error tracking and monitoring
```

---

## Success Criteria

- [ ] User can log in via SSO
- [ ] JWT token stored securely (httpOnly cookie)
- [ ] Protected routes redirect to login if not authenticated
- [ ] API calls include Bearer token in Authorization header
- [ ] Token automatically refreshes before expiry
- [ ] User can log out (token revoked)
- [ ] All requests traced (trace IDs in logs)
- [ ] Error logging captured with stack traces
- [ ] 80%+ test coverage
- [ ] No console warnings/errors in production build
- [ ] Performance: First Contentful Paint < 2s
- [ ] Security audit passing

---

## References

- **Repository**: https://github.com/[user]/awesome-prompts
- **OAuth2 Flow**: https://datatracker.ietf.org/doc/html/rfc6749
- **OIDC**: https://openid.net/specs/openid-connect-core-1_0.html
- **React Skills**: See `react_advanced_skill.md` in repository
- **API Design**: See `rest_api_java_skill.md` in repository
- **Testing**: See `testing_react_skill.md` in repository
- **Logging**: See `logger_skill.md` in repository
- **Observability**: See `opentelemetry_skill.md` in repository
- **Error Handling**: See `error_handling_skill.md` in repository

---

## Quick Start

```bash
# 1. Clone awesome-prompts repo
git clone https://github.com/[user]/awesome-prompts
cd awesome-prompts

# 2. Export skills to your AI tool
python3 tools/skill_exporter.py

# 3. Create new project
mkdir my-sso-app && cd my-sso-app

# 4. Start with backend prompt
# Copy "Backend SSO Setup" prompt above and send to Claude/Copilot
# Reference: awesome-prompts/skills/spring_advanced_skill.md

# 5. Then frontend
# Copy "React Frontend Setup" prompt
# Reference: awesome-prompts/skills/react_advanced_skill.md

# 6. Continue through phases, using prompts with skill references
```

---

## Notes

- **All skills are production-tested**: Follow recommendations from respective skill files
- **Multi-platform**: Skills exported to Copilot, Claude, Cursor, Continue.dev, OpenAI
- **Comprehensive examples**: Each skill includes 200+ code examples
- **Team ready**: Documentation for onboarding developers
- **Shareable**: No secrets, all open-source patterns
