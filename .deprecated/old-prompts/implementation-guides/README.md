# Implementation Guides

Complete, step-by-step implementation guides for building production-ready applications using skills from the awesome-prompts repository.

## Files

### react-sso-fullstack.md
**Build Production-Ready React App with Enterprise SSO**

A comprehensive guide for building a full-stack React + Spring Boot (or FastAPI) application with OAuth2/OIDC single sign-on integration.

**Covers:**
- SSO setup (Okta, Auth0, Azure AD)
- JWT token management and refresh
- Protected routes with authentication
- REST API integration with Bearer tokens
- Error handling and resilience
- Testing (unit, integration, E2E)
- Observability (logging, tracing, metrics)
- Security best practices
- Deployment strategies

**Skills Referenced:**
- react_advanced_skill
- rest_api_java_skill / rest_api_python_skill
- spring_advanced_skill
- testing_react_skill / testing_junit5_skill
- error_handling_skill
- logger_skill
- opentelemetry_skill
- code_health_skill

**Implementation Phases:**
1. Backend setup (Spring Boot OAuth2)
2. Frontend setup (React + TypeScript)
3. SSO integration (PKCE flow)
4. API integration (TanStack Query)
5. Error handling & observability
6. Testing & QA
7. Deployment

**Duration:** 4-6 weeks (single developer) or 2-3 weeks (team)

---

## How to Use

1. **Read the guide** — Understand requirements and architecture
2. **Review tech stack** — Confirm tools and versions
3. **Follow phases sequentially** — Build incrementally
4. **Use provided prompts** — Feed to Claude/Copilot with skill references
5. **Check success criteria** — Verify each phase works
6. **Reference skills** — For detailed patterns and examples

---

## Adding New Guides

To add a new implementation guide:

1. Create a new `.md` file in this directory
2. Follow the same structure:
   - Context / Overview
   - Requirements checklist
   - Tech stack
   - Project structure
   - Implementation phases
   - Prompts to use
   - Success criteria
   - References

3. Reference existing skills from `skills/` directory
4. Include code examples and architecture diagrams
5. Provide step-by-step instructions
6. Document success criteria and testing approach

---

## Quick Links

- [react-sso-fullstack.md](./react-sso-fullstack.md) — Full-stack React + SSO guide
- [../](../) — All prompts
- [../../skills/](../../skills/) — Skill modules
- [../../README.md](../../README.md) — Main repository documentation
