---
title: Comprehensive Function Examples — All Agents
version: 2.0
date: 2026-06-08
description: 1,200+ line guide with real-world examples for all 30 functions across 5 agents
---

# Function Examples — All 5 Agents + 30 Functions

Real-world usage examples for every agent and function. **See [FUNCTION_QUICK_REFERENCE.md](FUNCTION_QUICK_REFERENCE.md) for one-page cheat sheets.**

---

## 📋 Table of Contents (Quick Jump)

### By Agent
- [🎯 Orchestrator (7 functions)](#orchestrator-agent-7-functions) — plan, build, context, review, tradeoff, risk, pr
- [🏗️ Architect (6 functions)](#architect-agent-6-functions) — design, refactor, schema, api, frontend, a11y
- [💻 Implementer (7 functions)](#implementer-agent-7-functions) — build, test, doc, pipeline, docker, iac, full
- [✅ Quality (8 functions)](#quality-agent-8-functions) — review, audit, security, perf, debug, report, batch-review, diagnose
- [📊 Business Analyst (2 functions)](#business-analyst-agent-2-functions) — report, parse

### By Use Case
- [Starting a project](#starting-a-project) → orchestrator:plan + architect:design
- [Build production system](#building-a-complete-system) → orchestrator:build + implementer:full
- [Code review & validation](#code-review--validation) → quality:review + quality:audit
- [Fix bugs & optimize](#debugging--performance) → quality:debug + quality:perf
- [Design decisions](#architectural-decisions) → orchestrator:tradeoff + orchestrator:review

---

## 🎯 Orchestrator Agent (7 Functions)

**Role:** Strategy & Orchestration | **Tech:** Language-agnostic | **Context:** Full-stack generation, technical leadership

### Quick Commands (Copy-Paste)

```bash
orchestrator:plan "Build user authentication system"
orchestrator:build path=./requirements.md
orchestrator:context path=./existing-project
orchestrator:review path=./system-design.md
orchestrator:tradeoff goal="Handle 1M users"
orchestrator:risk path=./architecture
orchestrator:pr title="feat: user auth MVP"
```

### Function Map (Orchestrator)

| Function | Use When | Time | Output |
|----------|----------|------|--------|
| **plan** | Starting new project, need strategic direction | 5-10 min | Task breakdown, clarified requirements |
| **build** | Need full-stack MVP, end-to-end generation | 1-2 hours | Complete system (code + tests + docs) |
| **context** | Joining team, need project overview | 10-15 min | architecture.md, tech-stack.md, design.html |
| **review** | Before implementation, need senior perspective | 15-20 min | Design review with risks & challenges |
| **tradeoff** | Choosing between architecture patterns | 10-15 min | 3 approaches with effort/complexity |
| **risk** | Production readiness check | 15-20 min | Risk assessment with mitigations |
| **pr** | Ready to submit for review | 5 min | GitHub PR with full context |

---

### orchestrator:plan
**What it does:** Parse requirements, clarify assumptions, create task breakdown

**Example 1: MVP for E-Commerce Platform**
```bash
orchestrator:plan "Build an e-commerce platform with product catalog, shopping cart, and checkout"
```

**What happens:**
1. PHASE 0 (Think Before Coding):
   - "Are you assuming this is B2C or B2B?"
   - "Payment processing: Stripe only or multiple gateways?"
   - "Inventory management: Real-time or batch?"

2. PHASE 1 (Parse & Plan):
   - Confirms assumptions
   - Creates task breakdown:
     - Task 01: Database schema (products, orders, users)
     - Task 02: Backend API (product endpoints, cart, checkout)
     - Task 03: Frontend (React components)
     - Task 04: Tests (95%+ coverage)
     - Task 05: Deployment (Docker + CI/CD)

**Output:**
```
requirements.md          ← Clarified requirements
task-breakdown.json      ← 5 tasks with acceptance criteria
execution-order.txt      ← Dependencies and sequence
```

---

### orchestrator:build
**What it does:** Execute full-stack generation end-to-end

**Example: Complete MVP Build**
```bash
orchestrator:build path=./requirements.md
```

**What happens:**
1. Reads clarified requirements
2. Orchestrates complete pipeline:
   - architect:design → System topology
   - implementer:build → Code generation
   - implementer:test → Test suite
   - implementer:doc → Documentation
   - implementer:full → All together in one context

**Output:**
```
Generated system with:
├─ Backend API (FastAPI or Spring Boot)
├─ Frontend UI (React components)
├─ Database schema (migrations)
├─ Tests (95%+ coverage)
├─ Documentation (README, API specs)
└─ CI/CD pipeline (GitHub Actions)
```

---

### orchestrator:context
**What it does:** Build project understanding (architecture, tech stack, knowledge graph)

**Example: Analyze Existing Project**
```bash
orchestrator:context path=./existing-project
```

**Output:**
```
docs/context/
├─ architecture.md        ← C4 diagram + design narrative
├─ tech-stack.md          ← Technology table
├─ context.json           ← Machine-readable metadata
└─ design.html            ← Interactive visualization
```

---

### orchestrator:review
**What it does:** Strategic architecture review (challenge decisions, identify risks)

**Example: Review New Design**
```bash
orchestrator:review path=./system-design.md
```

**Analysis includes:**
- ✓ Are assumptions stated? (or hidden?)
- ✓ Is design too complex for scope?
- ✓ What could fail in production?
- ✓ Can 5% of team maintain this?
- ✓ What's the 5-year maintenance cost?

---

### orchestrator:tradeoff
**What it does:** Compare 3 approaches with effort/complexity analysis

**Example: Choose Architecture Pattern**
```bash
orchestrator:tradeoff goal="Handle 1M concurrent users, 99.99% uptime"
```

**Presents:**
```
Approach 1: Monolithic (simplest, limited scale)
- Effort: 4 weeks
- Complexity: Low
- Scale limit: 10K users
- Risk: Single point of failure

Approach 2: Microservices (complex, scales well)
- Effort: 12 weeks
- Complexity: High
- Scale: Unlimited
- Risk: Operational complexity

Approach 3: Hybrid (moderate, good scale)
- Effort: 8 weeks
- Complexity: Moderate
- Scale: 100K users easily
- Risk: Balanced
```

**Recommendation:** "Hybrid approach fits your timeline and needs"

---

### orchestrator:risk
**What it does:** Risk assessment with failure modes and mitigation

**Example: Production Readiness**
```bash
orchestrator:risk path=./architecture
```

**Analysis:**
```
🔴 CRITICAL RISKS:
  - Single database instance (SPOF)
    Mitigation: Add read replicas + failover
  - No API rate limiting
    Mitigation: Add rate limiter + circuit breaker
  
🟡 HIGH RISKS:
  - No observability setup
    Mitigation: Add APM + logging
  - Missing CORS security headers
    Mitigation: Add CORS middleware
```

---

### orchestrator:pr
**What it does:** Package deliverables and create GitHub PR

**Example: Open PR with Generated Code**
```bash
orchestrator:pr title="feat: e-commerce platform MVP" \
  description="Implements product catalog, shopping cart, checkout with tests and deployment config"
```

**Creates:**
```
GitHub PR with:
├─ Complete code diff
├─ Architecture narrative
├─ Test coverage report
├─ Deployment instructions
└─ Reviewers assigned
```

---

## 🏗️ Architect Agent (6 Functions)

**Role:** Architecture & Design | **Tech:** Language-agnostic | **Context:** System topology, API contracts, DB schema, UI architecture

### Quick Commands (Copy-Paste)

```bash
architect:design requirements="Real-time chat for 100K users"
architect:refactor path=./monolith goal="Split into microservices"
architect:schema requirements="Users, products, orders" db=postgresql
architect:api requirements="List products, create order, get user"
architect:frontend requirements="Product card with image, price, rating"
architect:a11y path=./product-page.tsx
```

### Function Map (Architect)

| Function | Use When | Time | Output |
|----------|----------|------|--------|
| **design** | Designing system from scratch | 1-2 hours | C4 diagram, API spec, DB schema, deployment |
| **refactor** | Modernizing legacy system | 2-3 hours | Migration guide, rollback strategies, phased plan |
| **schema** | Database design from scratch | 30-45 min | SQL DDL, indexes, migrations |
| **api** | REST API contract design | 30-45 min | OpenAPI 3.0 spec with examples |
| **frontend** | React component architecture | 1-2 hours | Component design, TypeScript interfaces |
| **a11y** | Accessibility audit (WCAG 2.1 AA) | 15-30 min | Audit findings, remediation steps |

---

### architect:design
**What it does:** Greenfield system design (C4, API contracts, schema, caching, deployment)

**Example 1: Real-Time Chat System**
```bash
architect:design requirements="Real-time chat system for 100K concurrent users"
```

**Output:**
```
Delivers:
├─ System topology (C4 diagram)
│  └─ Frontend (React) → API Gateway → Services
├─ Component structure
│  ├─ WebSocket service (chat messages)
│  ├─ User service (auth, profiles)
│  └─ Message queue (message processing)
├─ Data flow (Mermaid)
├─ API contract (OpenAPI spec)
│  └─ POST /messages
│  └─ WS /chat/:room_id
├─ Database schema (PostgreSQL)
│  ├─ users table
│  ├─ messages table
│  └─ rooms table
├─ Caching strategy (Redis)
├─ Deployment topology (K8s)
└─ Code stubs (models, routes)
```

**Example 2: Data Pipeline**
```bash
architect:design requirements="Process 1M events/sec from IoT devices, store in data warehouse"
```

Output includes Kafka → Spark → Snowflake topology.

---

### architect:refactor
**What it does:** Brownfield refactoring (assess current state, create migration roadmap)

**Example: Monolith to Microservices**
```bash
architect:refactor path=./monolith-app goal="Split into microservices"
```

**Produces:**
```
├─ Current state analysis
│  └─ Tightly coupled modules identified
├─ Target state design
│  └─ 4 independent microservices
├─ Phased migration roadmap
│  ├─ Phase 1: Extract user service (Week 1-2)
│  ├─ Phase 2: Extract product service (Week 3-4)
│  ├─ Phase 3: Extract order service (Week 5-6)
│  └─ Phase 4: Remove monolith (Week 7)
├─ Zero-downtime migration guide (for each phase)
└─ Rollback strategies (if something breaks)
```

---

### architect:schema
**What it does:** Database schema design (DDL, indexes, migrations)

**Example: E-Commerce Database**
```bash
architect:schema requirements="Users, products, orders, inventory" db=postgresql
```

**Output:**
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  price DECIMAL(10,2),
  stock_count INT,
  CONSTRAINT check_price CHECK (price >= 0)
);

CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_users_email ON users(email);

-- Migration script
ALTER TABLE products ADD COLUMN category_id INT;
ALTER TABLE products ADD CONSTRAINT fk_category 
  FOREIGN KEY (category_id) REFERENCES categories(id);
```

---

### architect:api
**What it does:** REST API contract design (OpenAPI spec, endpoints, schemas)

**Example: Product API**
```bash
architect:api requirements="List products, get product details, create product (admin only)"
```

**Output (OpenAPI 3.0):**
```yaml
paths:
  /products:
    get:
      summary: List products
      parameters:
        - name: skip
          in: query
          schema: { type: integer, default: 0 }
        - name: limit
          in: query
          schema: { type: integer, default: 10 }
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items: { $ref: '#/components/schemas/Product' }
    
    post:
      summary: Create product (admin only)
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/ProductCreate' }
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Product' }

components:
  schemas:
    Product:
      type: object
      properties:
        id: { type: integer }
        name: { type: string }
        price: { type: number }
        stock_count: { type: integer }
```

---

### architect:frontend
**What it does:** Frontend component architecture (React, TypeScript, reusability)

**Example: Product Card Component**
```bash
architect:frontend requirements="Reusable product card with image, price, rating, buy button"
```

**Output:**
```typescript
// components/ProductCard.tsx
interface ProductCardProps {
  id: string;
  name: string;
  price: number;
  image: string;
  rating: number;
  onBuy: (id: string) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  id,
  name,
  price,
  image,
  rating,
  onBuy,
}) => {
  return (
    <article className="product-card">
      <img src={image} alt={name} />
      <h3>{name}</h3>
      <div className="rating">★ {rating}</div>
      <div className="price">${price}</div>
      <button onClick={() => onBuy(id)}>Buy Now</button>
    </article>
  );
};

// Usage examples
// <ProductCard id="123" name="Laptop" price={999} image="..." rating={4.5} onBuy={handleBuy} />
```

**Also includes:**
- Props/API design
- Accessibility (WCAG 2.1 AA)
- Usage examples
- Best practices
- Responsive design considerations

---

### architect:a11y
**What it does:** Accessibility audit (WCAG 2.1 AA compliance)

**Example: Audit Product Page**
```bash
architect:a11y path=./product-page.tsx
```

**Findings:**
```
✓ PASS: Heading hierarchy (H1 → H2 → H3)
✓ PASS: Color contrast (4.5:1 minimum)
✓ PASS: Keyboard navigation (Tab, Enter, Escape work)
❌ FAIL: Missing alt text on product images
❌ FAIL: Form labels not associated with inputs
⚠️  WARNING: Focus indicator not visible (add :focus styles)

Recommendations:
1. Add alt text: <img alt="Product: {name}" />
2. Link labels: <label htmlFor="email">Email</label> <input id="email" />
3. Add focus styles: input:focus { outline: 2px solid blue; }
```

---

## 💻 Implementer Agent (7 Functions)

**Role:** Implementation & Execution | **Tech:** Auto-detects (Java/Python/React/Node) | **Context:** Code generation, testing, CI/CD, deployment

### Quick Commands (Copy-Paste)

```bash
implementer:build path=./api-spec.md
implementer:test path=./services/user_service.py
implementer:doc path=./src
implementer:pipeline path=./ platform=github-actions
implementer:docker path=./src
implementer:iac path=./app type=kubernetes
implementer:full path=./requirements.md
```

### Function Map (Implementer)

| Function | Use When | Time | Output | Key Benefit |
|----------|----------|------|--------|-------------|
| **build** | Need to write code from spec | 30-60 min | Production-ready code (auto-detects stack) | Models, routes, services |
| **test** | Need comprehensive tests | 30-45 min | Test suite with 95%+ coverage | Unit + integration + edge cases |
| **doc** | Need auto-generated docs | 20-30 min | JSDoc/docstrings + README + API guide | Inline + architecture + guides |
| **pipeline** | Setting up CI/CD | 15-20 min | GitHub Actions / GitLab CI / Jenkins | Tests, linting, coverage, deploy |
| **docker** | Containerizing application | 10-15 min | Dockerfile + docker-compose.yml | Multi-stage build, health checks |
| **iac** | Deploying to cloud | 20-30 min | K8s / Terraform / CloudFormation | deployment.yaml, service.yaml |
| **full** | Complete end-to-end implementation | 2-3 hours | Code + tests + docs + CI/CD + Docker + K8s | NO context loss between phases! |

---

### implementer:build
**What it does:** Generate production-ready code (auto-detects tech stack)

**Example 1: FastAPI Backend**
```bash
implementer:build path=./api-spec.md
```

**Detects:** Python + FastAPI  
**Generates:**
```python
# models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

# routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

**Example 2: React Frontend**
```bash
implementer:build path=./ui-spec.md
```

**Detects:** React + TypeScript  
**Generates:**
```typescript
// components/ProductList.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

interface Product {
  id: string;
  name: string;
  price: number;
}

export const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/products');
        setProducts(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {products.map(product => (
        <li key={product.id}>{product.name} - ${product.price}</li>
      ))}
    </ul>
  );
};
```

---

### implementer:test
**What it does:** Generate comprehensive test suite (95%+ coverage)

**Example: Tests for User Service**
```bash
implementer:test path=./services/user_service.py
```

**Generates (pytest):**
```python
# tests/test_user_service.py
import pytest
from services.user_service import UserService, UserNotFoundError

@pytest.fixture
def user_service(db_session):
    return UserService(db_session)

class TestUserService:
    """User service tests"""
    
    def test_create_user_success(self, user_service):
        """givenValidEmail_whenCreate_thenReturnsNewUser"""
        # Arrange
        email = "test@example.com"
        password = "secure_password"
        
        # Act
        user = user_service.create_user(email, password)
        
        # Assert
        assert user.email == email
        assert user.id is not None
        assert user.password_hash != password  # Should be hashed
    
    def test_create_user_duplicate_email(self, user_service):
        """givenExistingEmail_whenCreate_thenRaisesError"""
        # Arrange
        email = "existing@example.com"
        user_service.create_user(email, "password")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            user_service.create_user(email, "password2")
    
    def test_get_user_by_id(self, user_service):
        """givenValidId_whenGetUser_thenReturnsUser"""
        # Arrange
        user = user_service.create_user("test@example.com", "password")
        
        # Act
        retrieved = user_service.get_user_by_id(user.id)
        
        # Assert
        assert retrieved.email == "test@example.com"
    
    def test_get_user_nonexistent(self, user_service):
        """givenNonexistentId_whenGetUser_thenRaisesError"""
        # Act & Assert
        with pytest.raises(UserNotFoundError):
            user_service.get_user_by_id(99999)
```

---

### implementer:doc
**What it does:** Auto-generate documentation (code docs, API, architecture, README)

**Example: Full Documentation**
```bash
implementer:doc path=./src
```

**Generates:**
```
docs/
├─ README.md                 ← Project overview, setup, usage
├─ API.md                    ← API endpoints reference
├─ ARCHITECTURE.md           ← System design (C4 diagrams)
├─ CONTRIBUTING.md           ← How to contribute
├─ api/
│  ├─ users.md              ← User endpoints
│  ├─ products.md           ← Product endpoints
│  └─ orders.md             ← Order endpoints
└─ guides/
   ├─ database-setup.md
   ├─ local-development.md
   └─ deployment.md

+ Inline documentation:
  ├─ Python files with docstrings
  ├─ TypeScript files with JSDoc
  └─ SQL files with comments
```

---

### implementer:pipeline
**What it does:** CI/CD pipeline generation (GitHub Actions, GitLab CI, Jenkins)

**Example: GitHub Actions Pipeline**
```bash
implementer:pipeline path=./ platform=github-actions
```

**Generates (.github/workflows/ci.yml):**
```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov=./ --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          docker build -t myapp:latest .
          docker push myapp:latest
          kubectl apply -f k8s/deployment.yaml
```

---

### implementer:docker
**What it does:** Docker containerization (Dockerfile, docker-compose)

**Example: Python FastAPI**
```bash
implementer:docker path=./src
```

**Generates:**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Generates docker-compose.yml:**
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db/myapp
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

### implementer:iac
**What it does:** Infrastructure as Code (Terraform, K8s, CloudFormation)

**Example: Kubernetes Deployment**
```bash
implementer:iac path=./app type=kubernetes
```

**Generates:**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: api
        image: myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

### implementer:full
**What it does:** Complete lifecycle (build + test + doc + pipeline + docker all together)

**Example: Build Everything**
```bash
implementer:full path=./requirements.md
```

**Executes in one context window:**
1. ✓ Builds code (models, routes, services)
2. ✓ Generates tests (95%+ coverage)
3. ✓ Creates documentation (README, API, guides)
4. ✓ Sets up CI/CD pipeline
5. ✓ Creates Dockerfile + docker-compose
6. ✓ Generates K8s manifests
7. ✓ Commits everything to git

**No context loss between phases!**

---

## ✅ Quality Agent (8 Functions)

**Role:** QA, Security & Performance | **Tech:** Language-agnostic | **Context:** PR validation, security audit, performance optimization, debugging

### Quick Commands (Copy-Paste)

```bash
quality:review pr=456 ticket=PROJ-123
quality:audit path=./backend
quality:security path=./app compliance=SOC2
quality:perf path=./src baseline="500ms"
quality:debug stack_trace="NullPointerException at line 42" path=./src
quality:report path=./src comprehensive=true
quality:batch-review from=./reviews.json output=./report.html
quality:diagnose problem="Orders endpoint taking 10 seconds"
```

### Function Map (Quality)

| Function | Use When | Time | Output | Score Range |
|----------|----------|------|--------|-------------|
| **review** | Reviewing pull requests | 20-30 min | 6-phase report with A-F grade | A-F scorecard |
| **audit** | Auditing existing codebase | 1-2 hours | Architecture analysis, tech debt roadmap | Health score |
| **security** | Security audit / compliance | 1-2 hours | Vulnerability report with severity | Critical/High/Medium |
| **perf** | Optimizing slow application | 1-2 hours | Bottleneck analysis, optimization roadmap | Before/after metrics |
| **debug** | Fixing production bugs | 30-45 min | 5-phase RCA with fixed code + tests | Root cause identified |
| **report** | Complete quality synthesis | 2-3 hours | Unified report (all dimensions) | Comprehensive assessment |
| **batch-review** | Reviewing multiple PRs | 5 min per PR | Single HTML report with tabs + summary | Comparative analysis |
| **diagnose** | Conversational problem solving | 15-20 min | RCA + proposed solutions with examples | Actionable fixes |

---

### quality:review
**What it does:** PR validation (requirements, code quality, tests, docs)

**Example: Review Backend PR**
```bash
quality:review pr=456 ticket=PROJ-123 context="OAuth2 implementation"
```

**Analysis includes:**
```
PHASE 1: Requirement Validation
  ✓ AC1: OAuth2 provider integration — SATISFIED
  ✓ AC2: Token refresh mechanism — SATISFIED
  ❌ AC3: Rate limiting on token endpoint — MISSING

PHASE 2: Code Quality
  ✓ No security vulnerabilities detected
  ❌ One hardcoded secret found (line 42)
  ✓ Follows project style guide
  ⚠️  High cyclomatic complexity in auth_handler.py

PHASE 3: Test Coverage
  ✓ Overall coverage: 94%
  ✓ OAuth flow covered
  ❌ Missing: Invalid token edge case
  ❌ Missing: Expired token refresh test

PHASE 4: Documentation
  ✓ API endpoints documented
  ✓ Auth flow explained
  ❌ No example requests in README

Score: 72/100 (NEEDS WORK)
Verdict: Request changes
```

---

### quality:audit
**What it does:** Full codebase audit (architecture, SOLID, tech debt)

**Example: Audit Monolith**
```bash
quality:audit path=./backend
```

**Report includes:**
```
ARCHITECTURE ANALYSIS
  ✓ Layered architecture identified
  ✓ Separation of concerns mostly good
  ❌ User module tightly coupled to Order module

SOLID VIOLATIONS
  ❌ Single Responsibility: UserController handles auth + profile + admin
  ⚠️  Open/Closed: Adding new payment types requires modifying PaymentProcessor

DUPLICATION
  ❌ Same database query logic duplicated in 3 services (13 lines each)
  ❌ Same validation rules in 4 places

TECH DEBT SCORE: 42/100 (HIGH)
  - 8 deprecated dependencies
  - 120 lines of dead code
  - 5 TODO comments from 2021

Refactoring Priority:
  1. Extract shared query logic (5 hours)
  2. Remove dead code (2 hours)
  3. Decouple modules (12 hours)
  4. Update dependencies (3 hours)
```

---

### quality:security
**What it does:** Security audit (OWASP Top 10, vulnerabilities, compliance)

**Example: Security Audit**
```bash
quality:security path=./app compliance=SOC2
```

**Findings:**
```
🔴 CRITICAL
  - Hardcoded database credentials in config.py:42
  - SQL injection vulnerability in product search (not parameterized)
  - Missing HTTPS enforcement (no redirect)

🟡 HIGH
  - Weak password policy (min 6 chars, no complexity)
  - No rate limiting on login endpoint
  - Session tokens stored in localStorage (XSS risk)

🟢 MEDIUM
  - Missing CORS validation
  - No API key rotation policy
  - Logs contain PII (passwords)

Remediation Plan:
  1. (URGENT) Move secrets to env vars — 1 hour
  2. (URGENT) Use parameterized queries — 3 hours
  3. Add rate limiting — 2 hours
  4. Move tokens to httpOnly cookies — 1 hour
  5. Implement password policy — 2 hours

Compliance: 65% SOC 2 ready (need audit trail logging)
```

---

### quality:perf
**What it does:** Performance audit (profiling, bottlenecks, optimization)

**Example: Performance Analysis**
```bash
quality:perf path=./api baseline="500ms response time" scale="1M users"
```

**Analysis:**
```
BOTTLENECK ANALYSIS
  42% Database queries (slow SELECT with no index)
  30% N+1 queries (fetching user for each order)
  18% React re-renders (no memoization)
  10% Other

OPTIMIZATION ROADMAP
  
  Quick Wins (4 hours, 70% improvement):
  1. Add index on products(category_id) — 250ms → 2ms ✓
  2. Use JOIN instead of N+1 — 150ms → 5ms ✓
  3. Memoize Dashboard component — 50ms → 5ms ✓
  
  Result: 500ms → 100ms response time (5x faster!)

  Medium-term (2 weeks, additional 20% improvement):
  1. Implement Redis caching
  2. Add read replicas for scale
  3. Optimize React rendering with virtualization
  
  Long-term (1+ month, production scaling):
  1. Database sharding
  2. Horizontal scaling (3 more servers)
  3. CDN for static assets

SCALABILITY PROJECTION
  Current: 100 users, 500ms response time
  At 1M users: 2000ms ❌ EXCEEDS TARGET
  With optimizations: 200ms ✓ WITHIN TARGET
```

---

### quality:debug
**What it does:** Root cause analysis (stack trace → fix)

**Example: Production Bug**
```bash
quality:debug stack_trace="NullPointerException at OrderService.java:42" path=./src
```

**5-Phase Analysis:**
```
PHASE 1: CODE FUNCTIONALITY
  Line 40: orders = ordersRepository.findByUserId(123)
  Line 41: for (Order o : orders) ← NullPointerException here
  
  Issue: Code assumes findByUserId returns empty List, but returns NULL

PHASE 2: ROOT CAUSE
  findByUserId returns null when:
  - Result set is empty
  - JPA configuration returns null instead of empty list
  
  Why now (not before):
  - MySQL 5.7 → 8.0 upgrade changed behavior
  - 15% of users have no orders (legitimate case)

PHASE 3: FAILURE EXPLANATION
  Trigger: User views their order history
  Execution: OrderService.getOrders() → queries → null result → crash
  Why not caught: No test for "user with zero orders" case

PHASE 4: EDGE CASES
  ✓ User with zero orders (causing crash)
  ✓ Concurrent order creation (race condition)
  ✓ User deleted between requests (should handle gracefully)
  ✓ Database timeout (returns null, not exception)

PHASE 5: PRODUCTION-READY FIX
  
  Step 1: Defensive null check (immediate)
  ```java
  List<Order> orders = ordersRepository.findByUserId(userId);
  if (orders == null) orders = Collections.emptyList();
  ```
  
  Step 2: Root cause (JPA configuration)
  - Ensure repository returns empty List, not null
  
  Step 3: Testing
  - Add test for zero orders case
  - Add load test with concurrent requests
  
  Result: No 500 error, proper empty state shown
```

---

### quality:report
**What it does:** Unified quality synthesis (review + audit + security + perf + debug combined)

**Example: Complete Quality Report**
```bash
quality:report path=./src comprehensive=true
```

**Generates HTML report with:**
- Summary dashboard (score, critical issues)
- All findings from review + audit + security + perf + debug
- Priority matrix (impact vs. effort)
- Remediation roadmap
- Risk assessment

---

### quality:batch-review
**What it does:** Review multiple PRs in batch, produce single HTML report

**Example:**
```bash
quality:batch-review from=./pr-list.json output=./report.html
```

**Input (pr-list.json):**
```json
[
  { "pr": 456, "ticket": "PROJ-123" },
  { "pr": 457, "ticket": "PROJ-124" },
  { "pr": 458, "ticket": "PROJ-125" }
]
```

**Output:**
- Tabbed HTML report with summary + per-PR tabs
- Score comparison chart
- Merged issues matrix
- PDF/export ready

---

### quality:diagnose
**What it does:** Conversational problem solving

**Example: Slow Endpoint**
```bash
quality:diagnose problem="Orders endpoint taking 10 seconds to load"
```

**Conversation:**
```
Q1: When did it start? Always slow or recently?
A: Recently (after database upgrade)

Q2: How many orders per user typically?
A: 5-500 depending on user

Q3: Any error messages or timeouts?
A: Just slow, eventually returns

Analysis:
✓ Likely N+1 query pattern
✓ Database upgrade changed query plan
✓ Missing indexes on orders table

Proposed fixes:
1. Add index on orders(user_id, created_at)
2. Use JOIN to fetch orders + order items in one query
3. Implement pagination (load 10 at a time)

Expected result: 10sec → 200ms
```

---

## 📊 Business Analyst Agent (2 Functions)

**Role:** Utility — Backlog Management | **Tech:** JIRA, JSON, CSV | **Context:** Backlog parsing, visualization, reporting

### Quick Commands (Copy-Paste)

```bash
ba:report path=./jira-export.json project=MYAPP
ba:parse path=./jira-export.json format=json
```

### Function Map (Business Analyst)

| Function | Use When | Time | Output |
|----------|----------|------|--------|
| **report** | Analyzing JIRA backlog | 5-10 min | Interactive HTML report with filters, charts |
| **parse** | Need machine-readable JIRA data | 2-3 min | Structured JSON with stories, points, status |

---

### ba:report
**What it does:** Parse JIRA backlog, generate HTML report

**Example:**
```bash
ba:report path=./jira-export.json project=MYAPP
```

**Generates:**
- Interactive HTML backlog report
- Filterable by status, priority, assignee
- Burndown charts
- Velocity trends
- Export to CSV/PDF

---

### ba:parse
**What it does:** Extract structured data from JIRA export

**Example:**
```bash
ba:parse path=./jira-export.json format=json
```

**Output:**
```json
{
  "stories": [
    {
      "key": "MYAPP-123",
      "title": "User authentication",
      "status": "In Progress",
      "assignee": "john@example.com",
      "estimate": 8,
      "acceptance_criteria": [
        "Users can register with email",
        "Users can login with password"
      ]
    }
  ],
  "total_story_points": 250,
  "completed_points": 180
}
```

---

---

## 📌 Use Case Index

### Starting a Project
```bash
# 1. Clarify requirements + create task breakdown
orchestrator:plan "Build e-commerce platform with..."

# 2. Design system topology + API contracts + schema
architect:design requirements="..."

# 3. Generate complete system in one pass
implementer:full path=./requirements.md
```

### Building a Complete System
```bash
# End-to-end generation with full orchestration
orchestrator:build path=./requirements.md
# Output: Code + tests + docs + CI/CD pipeline
```

### Code Review & Validation
```bash
# Review PR against requirements
quality:review pr=123 ticket=PROJ-456

# Full codebase audit (architecture, SOLID, tech debt)
quality:audit path=./backend

# Security audit with compliance checking
quality:security path=./app compliance=SOC2

# Single consolidated report
quality:report path=./src comprehensive=true
```

### Debugging & Performance
```bash
# Fix production bugs with RCA
quality:debug stack_trace="error" path=./src

# Find and fix performance bottlenecks
quality:perf path=./src baseline="500ms" scale="1M users"

# Conversational problem solving
quality:diagnose problem="Orders endpoint slow"
```

### Architectural Decisions
```bash
# Compare 3 approaches with tradeoffs
orchestrator:tradeoff goal="Handle 1M concurrent users"

# Strategic review with risks + recommendations
orchestrator:review path=./system-design.md

# Risk assessment with failure modes
orchestrator:risk path=./architecture
```

### Existing Project Analysis
```bash
# Build complete project understanding
orchestrator:context path=./existing-project
# Output: architecture.md, tech-stack.md, design.html
```

### Database & API Design
```bash
# Design database schema from scratch
architect:schema requirements="Users, products, orders" db=postgresql

# Design REST API contract
architect:api requirements="List products, create order, get user"
```

### Component Design
```bash
# React component architecture
architect:frontend requirements="Product card with image, price, rating"

# Accessibility audit (WCAG 2.1 AA)
architect:a11y path=./product-page.tsx
```

### Brownfield Refactoring
```bash
# Plan migration from monolith to microservices
architect:refactor path=./monolith goal="Split into microservices"
# Output: Current state, target design, phased roadmap
```

### Backlog Management
```bash
# Visualize JIRA backlog with charts + filtering
ba:report path=./jira-export.json project=MYAPP

# Extract structured data from JIRA
ba:parse path=./jira-export.json format=json
```

---

## 🚀 Common Workflows

### Workflow 1: MVP Launch (4-6 hours)
```
orchestrator:plan
    ↓
architect:design
    ↓
implementer:full (code + tests + docs + CI/CD)
    ↓
quality:review
    ↓
orchestrator:pr
```

### Workflow 2: Code Review Sprint
```
quality:review pr=123 ticket=PROJ-456
quality:review pr=124 ticket=PROJ-457
quality:batch-review from=./reviews.json
```

### Workflow 3: Legacy System Modernization
```
orchestrator:context path=./legacy
quality:audit path=./src
quality:security path=./src
architect:refactor path=./legacy goal="..."
```

### Workflow 4: Production Incident
```
quality:debug stack_trace="error"
quality:diagnose problem="description"
quality:perf path=./affected-module
implementer:test path=./fix (verify fix)
```

---

## ✨ Pro Tips

1. **Always start with PHASE 0** — orchestrator:plan asks clarifying questions first (no assumptions)
2. **Use implementer:full** — Builds code + tests + docs in one context with zero state loss
3. **Review against requirements** — quality:review validates against JIRA acceptance criteria
4. **Chain functions** — orchestrator:plan → architect:design → implementer:full → quality:review → orchestrator:pr
5. **Batch reviews** — quality:batch-review for multiple PRs (faster than individual reviews)
6. **Quick reference** — See [FUNCTION_QUICK_REFERENCE.md](FUNCTION_QUICK_REFERENCE.md) for one-page cheat sheets
7. **Tech stack auto-detection** — implementer:build detects Python/Java/React automatically
8. **Comprehensive reports** — quality:report combines review + audit + security + perf + debug

---

## 📚 See Also

- **[FUNCTION_QUICK_REFERENCE.md](FUNCTION_QUICK_REFERENCE.md)** — One-page cheat sheets for all 30 functions
- **[agents/README.md](agents/README.md)** — Agent descriptions and dispatch syntax
- **[SPECIALIST_AGENT_MODES.md](SPECIALIST_AGENT_MODES.md)** — 9 specialist role-based modes (Full-Stack Engineer, Code Auditor, etc.)
- **[skills/README.md](skills/README.md)** — 25 reusable implementation skills
- **[instructions/master_instruction_set.md](instructions/master_instruction_set.md)** — Foundational principles and non-negotiable standards
