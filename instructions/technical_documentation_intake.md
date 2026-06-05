---
name: Technical Documentation Intake Form
version: 1.0
description: Structured questions to gather project information before generating technical documentation
---

# Technical Documentation Intake Form

Answer these questions to help generate accurate, comprehensive technical documentation for your project.

---

## Section 1: Project Overview

### Q1: Project Name and Acronym
**Question:** What is your project called? (Include acronym if applicable)

**Example:** "User Management Service (UMS)", "E-commerce Platform (ECP)"

**Why:** Sets the context and helps label all generated documentation

---

### Q2: Project Purpose and Mission
**Question:** In 2-3 sentences, what is this project's main purpose?

**Example:** "The User Management Service handles authentication, authorization, and user profile management for all enterprise applications. It provides single sign-on (SSO) and role-based access control (RBAC)."

**Why:** Helps readers understand the project's scope and mission immediately

---

### Q3: Key Features
**Question:** What are the 5-7 main features or capabilities?

**Format:** Bullet list

**Example:**
- User registration and email verification
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- User profile management
- OAuth2 integration with Google/GitHub
- Password reset and recovery
- Multi-factor authentication (MFA)

**Why:** Helps readers understand what the system does

---

### Q4: Documentation Audience
**Question:** Who will read this documentation? (Select all that apply)

**Options:**
- [ ] Backend developers
- [ ] Frontend developers
- [ ] DevOps / Infrastructure engineers
- [ ] QA / Test engineers
- [ ] Product managers / Non-technical stakeholders
- [ ] New team members / Onboarding
- [ ] Architects / Technical leads
- [ ] External partners / API consumers

**Why:** Determines the depth, tone, and focus of documentation

---

## Section 2: Technology Stack

### Q5: Frontend Technology
**Question:** What frontend framework(s) are you using?

**Options:**
- [ ] React (with version: ___)
- [ ] Vue (with version: ___)
- [ ] Angular (with version: ___)
- [ ] Svelte (with version: ___)
- [ ] NextJS / Nuxt (with version: ___)
- [ ] Plain HTML/CSS/JS
- [ ] Other: ___

**Why:** Determines which frontend patterns and examples to document

---

### Q6: Backend Technology
**Question:** What backend framework(s) are you using?

**Options:**
- [ ] Node.js / Express (with version: ___)
- [ ] Python / FastAPI (with version: ___)
- [ ] Python / Django (with version: ___)
- [ ] Java / Spring Boot (with version: ___)
- [ ] Go (with version: ___)
- [ ] .NET / C# (with version: ___)
- [ ] Ruby on Rails (with version: ___)
- [ ] Other: ___

**Why:** Determines code examples, patterns, and middleware documentation

---

### Q7: Database Technology
**Question:** What database(s) are you using?

**Options for Primary Database:**
- [ ] PostgreSQL
- [ ] MySQL / MariaDB
- [ ] MongoDB
- [ ] Redis
- [ ] DynamoDB / NoSQL
- [ ] SQL Server
- [ ] SQLite
- [ ] Other: ___

**Options for Secondary/Cache:**
- [ ] Redis
- [ ] Memcached
- [ ] Elasticsearch
- [ ] None
- [ ] Other: ___

**Why:** Determines schema documentation format and relationship examples

---

### Q8: Deployment Platform
**Question:** Where is this deployed?

**Options:**
- [ ] Docker / Docker Compose
- [ ] Kubernetes (K8s)
- [ ] AWS (EC2, ECS, Lambda)
- [ ] GCP (Cloud Run, App Engine)
- [ ] Azure (App Service, Container Instances)
- [ ] Heroku
- [ ] Self-hosted / On-premises
- [ ] Multiple: ___

**Why:** Determines deployment guide content

---

### Q9: Authentication Method
**Question:** How do users/services authenticate?

**Options:**
- [ ] JWT tokens
- [ ] OAuth2 (specify provider: ___)
- [ ] Session-based (cookies)
- [ ] API keys
- [ ] mTLS / Certificates
- [ ] Mixed (specify: ___)
- [ ] None / Public API

**Why:** Determines authentication flow documentation

---

## Section 3: Project Structure

### Q10: Main Folders/Modules
**Question:** What are your main code directories?

**Format:** List paths relative to project root

**Example:**
```
src/
  components/    - React components
  services/      - Business logic
  api/           - API clients
tests/           - Test files
migrations/      - Database migrations
```

**Why:** Helps create accurate project structure documentation

---

### Q11: Entry Points
**Question:** What are the main entry points to your application?

**Format:** List files

**Example:**
- Frontend: `src/index.tsx`
- Backend: `main.py`
- Worker: `worker/index.js`

**Why:** Helps trace code workflows from user action

---

## Section 4: Architecture & Flows

### Q12: Main User Workflows
**Question:** What are 3-4 main user journeys through the system?

**Format:** Step-by-step flows

**Example:**
1. User Login Flow:
   - User enters email/password
   - Frontend calls /auth/login
   - Backend validates credentials
   - Returns JWT token
   - Frontend stores token
   - User navigates to dashboard

2. Create Resource Flow:
   - User clicks "Create New"
   - Form opens with validation
   - User submits form
   - API validates input
   - Service creates resource
   - Database stores resource
   - List view updates

**Why:** Helps generate accurate workflow diagrams

---

### Q13: Middleware & Integrations
**Question:** What middleware or external integrations exist?

**Format:** List by category

**Example:**
- Authentication: JWT middleware
- Logging: Winston logger, ELK stack
- Monitoring: Prometheus, DataDog
- Email: SendGrid
- Payment: Stripe
- Cloud: AWS S3

**Why:** Ensures complete middleware documentation

---

### Q14: Critical Data Flows
**Question:** What are the most important data flows (beyond simple CRUD)?

**Format:** Describe each flow

**Example:**
- Order to Notification Flow: Order created → Kafka message → Email service → Notification sent
- Real-time Updates: WebSocket connection → React component update
- Data Sync: Primary DB → Read replica → Cache → API response

**Why:** Helps document complex patterns

---

## Section 5: Documentation Preferences

### Q15: Output Format Preferences
**Question:** What output formats do you want?

**Options:**
- [ ] Interactive HTML file (recommended)
- [ ] Markdown files (in docs/technical/)
- [ ] Both HTML and Markdown
- [ ] Mermaid diagrams only
- [ ] ASCII diagrams only

**Why:** Determines what files are generated

---

### Q16: Diagram Preferences
**Question:** What types of diagrams are most useful?

**Options:**
- [ ] Component/Architecture diagram
- [ ] Data flow diagrams
- [ ] Sequence diagrams (user journeys)
- [ ] Entity relationship diagram (database)
- [ ] Deployment diagram
- [ ] Middleware/Request pipeline diagram
- [ ] All of the above

**Why:** Focuses documentation on most valuable visuals

---

### Q17: Code Examples
**Question:** What code examples would be most useful?

**Options:**
- [ ] API usage (curl, HTTP client)
- [ ] Frontend integration (React hooks, API calls)
- [ ] Database queries (SQL, ORM)
- [ ] Authentication flow
- [ ] Error handling
- [ ] Middleware creation
- [ ] Testing examples
- [ ] All of the above

**Why:** Ensures practical, usable examples

---

### Q18: Documentation Style
**Question:** What's your preferred documentation style?

**Options:**
- [ ] Technical and detailed (for architects)
- [ ] Practical and actionable (for developers)
- [ ] Accessible and beginner-friendly (for onboarding)
- [ ] Comprehensive (all details included)
- [ ] Concise (key points only)

**Why:** Sets the tone and depth of explanations

---

## Section 6: Special Requirements

### Q19: API Documentation Needs
**Question:** Do you need API endpoint documentation?

**If yes:**
- Number of endpoints: ___
- Are they documented in code comments? (Yes/No)
- Do you use OpenAPI/Swagger? (Yes/No)
- Need authentication/authorization examples? (Yes/No)

**Why:** Determines if API reference is generated

---

### Q20: Database-Specific Needs
**Question:** What database documentation is important?

**Options:**
- [ ] Schema diagram
- [ ] Table descriptions
- [ ] Relationship diagrams
- [ ] Migration history
- [ ] Indexing strategy
- [ ] Query optimization tips
- [ ] All of the above

**Why:** Ensures schema documentation covers what's important

---

### Q21: Deployment & DevOps Needs
**Question:** What deployment information should be included?

**Options:**
- [ ] Docker setup
- [ ] Kubernetes manifests
- [ ] Environment variables
- [ ] Prerequisites (Node.js version, etc.)
- [ ] Build steps
- [ ] CI/CD pipeline overview
- [ ] Monitoring/logging setup
- [ ] All of the above

**Why:** Determines depth of deployment guide

---

### Q22: Additional Documentation
**Question:** Are there any special topics to document?

**Format:** Free text, list as needed

**Examples:**
- Performance optimization strategy
- Security architecture and measures
- Testing strategy and test coverage
- Troubleshooting common issues
- Performance benchmarks
- Compliance requirements (GDPR, SOC2, etc.)

**Why:** Captures unique aspects of the project

---

## Summary Section

### Documentation Deliverables

Based on your answers, you will receive:

✅ **Interactive HTML Document**
- Single self-contained file
- Multiple tabs for different sections
- Search and filter capabilities
- Responsive design

✅ **Markdown Files** (10 documents)
- Project overview
- Architecture guide
- Code workflow documentation
- Database schema documentation
- API endpoint reference
- Middleware documentation
- Technology stack
- Deployment guide
- Code examples
- Troubleshooting guide

✅ **Diagrams & Visualizations**
- Component architecture diagram
- Data flow diagrams
- Database entity relationship diagram
- User journey/workflow diagrams
- Middleware chain visualization
- Technology stack visualization

✅ **Support Files**
- Manifest file (TECHNICAL_DOCUMENTATION_GENERATED.json)
- Index with links (docs/technical/README.md)
- Quick reference guide

---

## Ready?

Once you've answered all questions above, the Technical Documentation Agent will:

1. ✅ Analyze your project structure
2. ✅ Scan dependencies and configurations
3. ✅ Map code workflows and data flows
4. ✅ Generate comprehensive diagrams
5. ✅ Create HTML visualization
6. ✅ Produce markdown guides
7. ✅ Provide implementation details

**Total time:** 10-20 minutes (depending on project size)

**Output location:** `docs/technical-documentation.html` + `docs/technical/`

---

**This intake form version:** 1.0  
**Last updated:** 2026-05-20
