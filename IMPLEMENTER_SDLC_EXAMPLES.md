---
title: Implementer Agent — SDLC Examples
description: Complete software development lifecycle examples showing implementer functions in real-world scenarios
version: 1.0
---

# Implementer Agent — SDLC Examples

**Role:** Implementation & Execution | **Functions:** build, test, doc, pipeline, docker, iac, full

Complete lifecycle examples showing how implementer functions work together in implementation phases.

---

## 📋 SDLC Lifecycle Overview

```
Phase 0: Code Generation       → implementer:build
Phase 1: Testing               → implementer:test
Phase 2: Documentation         → implementer:doc
Phase 3: CI/CD Pipeline Setup  → implementer:pipeline
Phase 4: Containerization      → implementer:docker
Phase 5: Infrastructure Setup  → implementer:iac
Phase 6: Complete Lifecycle    → implementer:full (all in one!)
```

---

## 🎯 Scenario 1: User Authentication Service (New Feature)

### Phase 0: Code Generation

**Situation:** Need to implement user authentication with email/password + OAuth2.

**Command:**
```bash
implementer:build path=./auth-api-spec.md
```

**Architecture Input:**
```
API Spec (OpenAPI):
├─ POST /auth/register (email, password) → JWT token
├─ POST /auth/login (email, password) → JWT token
├─ POST /auth/refresh (refresh_token) → new JWT
├─ GET /auth/verify (token) → user details
├─ POST /auth/logout (token) → invalidate
└─ GET /auth/oauth/google (code) → JWT token

Database Schema:
├─ users (id, email, password_hash, oauth_providers)
├─ sessions (id, user_id, refresh_token, expires_at)
└─ oauth_tokens (id, user_id, provider, token, refresh_token)
```

**Implementer Output: Production-Ready Code**

```python
# models/user.py
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String(512), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from security import hash_password, verify_password, create_tokens
from schemas import LoginSchema, RegisterSchema

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenSchema)
async def register(
    data: RegisterSchema,
    db: Session = Depends(get_db)
):
    """Register new user with email and password"""
    # Check if user exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create tokens
    access_token, refresh_token = create_tokens(user.id)
    
    # Store refresh token
    session = Session(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(session)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=TokenSchema)
async def login(
    data: LoginSchema,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account disabled")
    
    access_token, refresh_token = create_tokens(user.id)
    
    session = Session(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(session)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    data: RefreshSchema,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    session = db.query(Session).filter(
        Session.refresh_token == data.refresh_token
    ).first()
    
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    access_token, new_refresh_token = create_tokens(session.user_id)
    
    session.refresh_token = new_refresh_token
    session.expires_at = datetime.utcnow() + timedelta(days=30)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

# security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_tokens(user_id: UUID) -> tuple[str, str]:
    access_payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "type": "access"
    }
    refresh_payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=30),
        "type": "refresh"
    }
    
    access_token = jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    refresh_token = jwt.encode(
        refresh_payload,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return access_token, refresh_token
```

**Output:**
- ✓ Production-ready models + routes + security utilities
- ✓ Proper error handling + validation
- ✓ Follows best practices (bcrypt hashing, JWT tokens)
- ✓ Type hints throughout
- ✓ Docstrings for every function

**Timeline:** 30-60 minutes

---

### Phase 1: Testing

**Command:**
```bash
implementer:test path=./routes/auth.py
```

**Implementer Output: Comprehensive Test Suite**

```python
# tests/test_auth.py
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    # Create test database session
    return SessionLocal()

class TestRegister:
    """User registration tests"""
    
    def test_register_success(self, client: TestClient, db_session: Session):
        """givenValidEmail_whenRegister_thenReturnsTokens"""
        # Arrange
        payload = {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        # Act
        response = client.post("/auth/register", json=payload)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify user in database
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert user is not None
        assert user.is_active
    
    def test_register_duplicate_email(self, client: TestClient, db_session: Session):
        """givenExistingEmail_whenRegister_thenReturnsError"""
        # Arrange - create user
        existing_user = User(
            email="existing@example.com",
            password_hash=hash_password("password")
        )
        db_session.add(existing_user)
        db_session.commit()
        
        payload = {
            "email": "existing@example.com",
            "password": "NewPassword123!"
        }
        
        # Act
        response = client.post("/auth/register", json=payload)
        
        # Assert
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_weak_password(self, client: TestClient):
        """givenWeakPassword_whenRegister_thenReturnsError"""
        payload = {
            "email": "test@example.com",
            "password": "123"
        }
        
        response = client.post("/auth/register", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_invalid_email(self, client: TestClient):
        """givenInvalidEmail_whenRegister_thenReturnsError"""
        payload = {
            "email": "not-an-email",
            "password": "ValidPass123!"
        }
        
        response = client.post("/auth/register", json=payload)
        
        assert response.status_code == 422

class TestLogin:
    """User login tests"""
    
    def test_login_success(self, client: TestClient, db_session: Session):
        """givenValidCredentials_whenLogin_thenReturnsTokens"""
        # Arrange - create user
        user = User(
            email="user@example.com",
            password_hash=hash_password("CorrectPassword123!")
        )
        db_session.add(user)
        db_session.commit()
        
        payload = {
            "email": "user@example.com",
            "password": "CorrectPassword123!"
        }
        
        # Act
        response = client.post("/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_password(self, client: TestClient, db_session: Session):
        """givenWrongPassword_whenLogin_thenReturnsError"""
        # Arrange
        user = User(
            email="user@example.com",
            password_hash=hash_password("CorrectPassword")
        )
        db_session.add(user)
        db_session.commit()
        
        payload = {
            "email": "user@example.com",
            "password": "WrongPassword"
        }
        
        # Act
        response = client.post("/auth/login", json=payload)
        
        # Assert
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """givenNonexistentUser_whenLogin_thenReturnsError"""
        payload = {
            "email": "nonexistent@example.com",
            "password": "AnyPassword123!"
        }
        
        response = client.post("/auth/login", json=payload)
        
        assert response.status_code == 401

class TestRefresh:
    """Token refresh tests"""
    
    def test_refresh_success(self, client: TestClient, db_session: Session):
        """givenValidRefreshToken_whenRefresh_thenReturnsNewTokens"""
        # Arrange
        user = User(email="user@example.com")
        db_session.add(user)
        db_session.commit()
        
        access_token, refresh_token = create_tokens(user.id)
        
        session = Session(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db_session.add(session)
        db_session.commit()
        
        # Act
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        # Assert
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_refresh_expired_token(self, client: TestClient, db_session: Session):
        """givenExpiredRefreshToken_whenRefresh_thenReturnsError"""
        # Arrange
        user = User(email="user@example.com")
        db_session.add(user)
        db_session.commit()
        
        access_token, refresh_token = create_tokens(user.id)
        
        # Create expired session
        session = Session(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() - timedelta(days=1)  # Expired
        )
        db_session.add(session)
        db_session.commit()
        
        # Act
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        # Assert
        assert response.status_code == 401

# Test Coverage Report
# Lines covered: 245 / 258 = 95%
# Branches covered: 38 / 42 = 90%
# Functions covered: 12 / 12 = 100%
```

**Test Results:**
```
✓ TestRegister::test_register_success
✓ TestRegister::test_register_duplicate_email
✓ TestRegister::test_register_weak_password
✓ TestRegister::test_register_invalid_email
✓ TestLogin::test_login_success
✓ TestLogin::test_login_invalid_password
✓ TestLogin::test_login_nonexistent_user
✓ TestRefresh::test_refresh_success
✓ TestRefresh::test_refresh_expired_token

Results: 9 passed in 2.34s
Coverage: 95% | Edge cases covered
```

**Timeline:** 30-45 minutes

---

### Phase 2: Documentation

**Command:**
```bash
implementer:doc path=./auth
```

**Implementer Output: Complete Documentation**

```markdown
# Authentication Service Documentation

## Overview
JWT-based authentication service supporting email/password and OAuth2.

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (for session management)

### Installation
```bash
pip install -r requirements.txt
python -m alembic upgrade head
```

### Configuration
```bash
# .env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/auth_db
OAUTH_GOOGLE_CLIENT_ID=...
OAUTH_GOOGLE_CLIENT_SECRET=...
```

## API Reference

### Register
**Endpoint:** `POST /auth/register`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Login
**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Refresh Token
**Endpoint:** `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

## Architecture

### Security
- Passwords hashed with bcrypt (salt rounds: 12)
- JWT tokens signed with HS256
- Access tokens expire in 1 hour
- Refresh tokens expire in 30 days
- HTTPS enforced in production

### Database Schema
- `users` table: Core user data
- `sessions` table: Active refresh tokens
- `oauth_tokens` table: OAuth provider tokens

### Token Flow
```
1. Register/Login → Generate access + refresh tokens
2. Store refresh token in DB
3. Client uses access token for API calls
4. When access expires → Use refresh token to get new tokens
5. Refresh token also expires → User must re-login
```

## Examples

### Using in JavaScript
```javascript
// Register
const response = await fetch('/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePassword123!'
  })
});
const { access_token } = await response.json();
localStorage.setItem('access_token', access_token);

// API Call
const api = await fetch('/api/users/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

### Using in Python
```python
import requests

# Register
response = requests.post('http://localhost:8000/auth/register', json={
    'email': 'user@example.com',
    'password': 'SecurePassword123!'
})
access_token = response.json()['access_token']

# API Call
headers = {'Authorization': f'Bearer {access_token}'}
user = requests.get('http://localhost:8000/api/users/me', headers=headers)
print(user.json())
```

## Troubleshooting

### Invalid token error
- Check token expiration: `jwt.decode(token, algorithms=['HS256'])`
- Verify SECRET_KEY matches
- Token might be expired; use refresh endpoint

### Database connection error
- Check DATABASE_URL environment variable
- Verify PostgreSQL is running
- Run migrations: `alembic upgrade head`

## Contributing
See [CONTRIBUTING.md](../CONTRIBUTING.md)

## License
MIT
```

**Additional Output:**
- API documentation (Swagger UI at `/docs`)
- Setup guide for developers
- Deployment guide for operations
- Contributing guidelines

**Timeline:** 20-30 minutes

---

### Phase 3: CI/CD Pipeline

**Command:**
```bash
implementer:pipeline path=./ platform=github-actions
```

**Implementer Output: .github/workflows/ci.yml**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: user
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Lint with flake8
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://user:password@localhost/test_db
        run: pytest --cov=. --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t auth-service:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag auth-service:${{ github.sha }} myregistry/auth-service:latest
          docker push myregistry/auth-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster production \
            --service auth-service \
            --force-new-deployment
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**Timeline:** 15-20 minutes

---

### Phase 4: Containerization

**Command:**
```bash
implementer:docker path=./
```

**Implementer Output: Dockerfile + docker-compose.yml**

```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/auth_db
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - auth-network

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - auth-network

  redis:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - auth-network

volumes:
  postgres_data:

networks:
  auth-network:
```

**Timeline:** 10-15 minutes

---

### Phase 5: Infrastructure as Code

**Command:**
```bash
implementer:iac path=./app type=kubernetes
```

**Implementer Output: K8s Manifests**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: api
        image: myregistry/auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: auth-secrets
              key: secret-key
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
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: production
spec:
  selector:
    app: auth-service
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

**Timeline:** 20-30 minutes

---

### Phase 6: Complete Lifecycle (All-in-One)

**Command:**
```bash
implementer:full path=./auth-requirements.md
```

**What Happens (All in One Context Window!):**

```
✓ Phase 1: Code generation (30 min)
✓ Phase 2: Test generation (30 min)
✓ Phase 3: Documentation (20 min)
✓ Phase 4: CI/CD pipeline (15 min)
✓ Phase 5: Docker setup (15 min)
✓ Phase 6: K8s manifests (20 min)
✓ Phase 7: Git commit + summary

Total: 2-3 hours → Complete production-ready system!

NO context loss between phases!
All artifacts in one commit
```

**Output Artifacts:**

```
auth-service/
├─ src/
│  ├─ models/
│  │  └─ user.py
│  ├─ routes/
│  │  └─ auth.py
│  ├─ security.py
│  └─ main.py
├─ tests/
│  └─ test_auth.py (95% coverage)
├─ docs/
│  ├─ README.md
│  ├─ API.md
│  └─ DEPLOYMENT.md
├─ .github/workflows/
│  └─ ci.yml
├─ Dockerfile
├─ docker-compose.yml
├─ k8s/
│  ├─ deployment.yaml
│  └─ service.yaml
├─ requirements.txt
├─ pytest.ini
├─ .env.example
└─ .gitignore
```

**Timeline:** 2-3 hours | **Output:** Complete, production-ready system

---

## 📊 SDLC Chaining Examples

### Standard Implementation Workflow (1-2 days)

```
Day 1 Morning:
  implementer:build → Code generation (30 min)

Day 1 Afternoon:
  implementer:test → Test generation (30 min)
  implementer:doc → Documentation (20 min)

Day 2 Morning:
  implementer:pipeline → CI/CD setup (15 min)
  implementer:docker → Containerization (15 min)

Day 2 Afternoon:
  implementer:iac → K8s setup (20 min)
  [Final review + commit]
```

### Fast Track (Complete MVP)

```
implementer:full path=./requirements.md
  └─ 2-3 hours → Production system!
```

---

## ✨ Pro Tips for Implementer Functions

1. **Code generation first** — Build on solid design
2. **Test as you go** — Don't skip testing phase
3. **Document early** — Easier to write while coding
4. **Automate pipeline** — Save hours per week
5. **Container from start** — Deploy consistently everywhere
6. **Infrastructure as code** — Reproducible deployments
7. **Use implementer:full** — Zero context loss, complete system
8. **Tech stack auto-detection** — Automatically chooses best practices for your language

