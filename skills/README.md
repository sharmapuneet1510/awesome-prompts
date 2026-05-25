# 🛠️ Skills Directory

> Reusable implementation modules used by all agents

**Quick Navigation**

| Skill | Purpose | Language | Used By |
|-------|---------|----------|---------|
| [Code Documentation](code_documentation_skill.md) | JSDoc/docstrings/Javadoc | JS/Python/Java | All agents |
| [Database](database_skill.md) | SQL schema + migrations | PostgreSQL/MySQL | Autonomous Dev |
| [Backend API](backend_skill.md) | REST API generation | FastAPI/Spring | Implementation |
| [Frontend](frontend_skill.md) | React components | React/TS | Implementation |
| [Testing](test_skill.md) | Unit/integration tests | JUnit5/pytest | Test Generator |
| [Code Review](code_review_skill.md) | 6-phase analysis | Language-agnostic | Code Review |
| [Apache Camel](apache_camel_skill.md) | Integration patterns | Apache Camel | Advanced |

---

## 📚 Skills Overview

Skills are **reusable, tech-specific modules** that agents delegate to for implementation. Each skill handles language idioms, best practices, and quality standards.

### Architecture

```
Implementation Agent
    ↓
Detect tech stack (Java, Python, React, etc.)
    ↓
Select appropriate skill
    ↓
Skill executes implementation
    ├─ Code patterns
    ├─ Best practices
    ├─ Quality standards
    └─ Testing approach
    ↓
Generate complete code
```

---

## 📝 Code Documentation Skill (v1.0)

**File:** [`code_documentation_skill.md`](code_documentation_skill.md)

**Generates:**
- JSDoc (JavaScript/TypeScript)
- docstrings (Python)
- Javadoc (Java)

**Coverage:**
- ✅ All public methods documented
- ✅ Parameters with types
- ✅ Return values documented
- ✅ Exceptions documented
- ✅ Usage examples provided
- ✅ Complex logic explained

**Format Examples:**
```javascript
/**
 * Register a new user with email and password
 * @param {string} email - User email address
 * @param {string} password - Plain-text password
 * @returns {Promise<User>} Created user object
 * @throws {ValueError} If email format invalid
 * @example
 * const user = await registerUser("john@example.com", "secure");
 */
```

**When to use:** All agents use this for documentation

---

## 🗄️ Database Skill (v1.0)

**File:** [`database_skill.md`](database_skill.md)

**Supports:**
- PostgreSQL
- MySQL
- MongoDB
- SQLite

**Generates:**
- Schema design
- Migration scripts
- Query optimization
- Index strategies
- Transaction handling

**Output:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_email CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
```

**When to use:** Autonomous Dev, building APIs with databases

---

## 🔌 Backend API Skill (v1.0)

**File:** [`backend_skill.md`](backend_skill.md)

**Supports:**
- FastAPI (Python)
- Spring Boot (Java)
- Express (Node.js)

**Generates:**
- REST endpoints
- Request validation
- Error handling
- Authentication
- Rate limiting
- OpenAPI specs

**Example Output:**
```python
@app.post("/users/register")
async def register_user(
    email: EmailStr,
    password: str = Field(..., min_length=8)
) -> UserResponse:
    """
    Register a new user.
    
    - **email**: Valid email address
    - **password**: Min 8 characters, must include uppercase + number
    """
    # Validation
    if await User.get_by_email(email):
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Hash password
    hashed = hash_password(password)
    
    # Create user
    user = await User.create(email=email, password_hash=hashed)
    
    return UserResponse.from_orm(user)
```

**When to use:** Building APIs, implementing backend logic

---

## ⚛️ Frontend Skill (v1.0)

**File:** [`frontend_skill.md`](frontend_skill.md)

**Supports:**
- React 18+
- TypeScript
- Tailwind CSS
- Hooks patterns

**Generates:**
- Functional components
- Custom hooks
- State management
- Form handling
- API integration
- Testing utilities

**Example Output:**
```typescript
interface UserRegistrationProps {
  onSuccess?: (user: User) => void;
}

export const UserRegistration: React.FC<UserRegistrationProps> = ({
  onSuccess
}) => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const user = await registerUser(formData);
      onSuccess?.(user);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Form fields */}
    </form>
  );
};
```

**When to use:** Building React frontends, UI components

---

## 🧪 Testing Skill (v1.0)

**File:** [`test_skill.md`](test_skill.md)

**Supports:**
- JUnit 5 (Java)
- pytest (Python)
- Jest (TypeScript/JavaScript)

**Standards:**
- AAA Pattern (Arrange-Act-Assert)
- Comprehensive coverage
- Edge case testing
- Error scenario testing
- Integration testing

**Example Output:**
```python
class TestUserRegistration:
    """Test user registration endpoint"""
    
    @pytest.fixture
    def clean_db(self):
        """Setup and teardown database"""
        yield
        User.delete_all()
    
    def test_register_with_valid_credentials(self, clean_db):
        """Given valid email/password, when registering, then user created"""
        # Arrange
        email = "john@example.com"
        password = "SecurePass123"
        
        # Act
        user = register_user(email, password)
        
        # Assert
        assert user.email == email
        assert user.password_hash != password  # Never store plain
    
    def test_register_with_invalid_email(self, clean_db):
        """Given invalid email, when registering, then error returned"""
        # Arrange
        invalid_email = "not-an-email"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            register_user(invalid_email, "SecurePass123")
    
    def test_register_prevents_duplicate_email(self, clean_db):
        """Given existing email, when registering, then conflict error"""
        # Arrange
        email = "john@example.com"
        register_user(email, "SecurePass123")
        
        # Act & Assert
        with pytest.raises(EmailAlreadyExists):
            register_user(email, "AnotherPass123")
```

**When to use:** Test Generator agent, all code generation

---

## 🔍 Code Review Skill (v3.0) ⭐ NEW

**File:** [`code_review_skill.md`](code_review_skill.md)

**Implements 6 Phases:**
1. **Requirement Analysis** — Parse JIRA, translate to plain English
2. **Requirement Validation** — Map code to ACs, calculate coverage %
3. **Code Quality Review** — 6-category checklist (Design, SOLID, Patterns, Performance, Security, Testing/Docs)
4. **Test Coverage** — Analyze test scenarios and coverage %
5. **Documentation** — Audit docstrings, parameters, examples
6. **Scorecard** — Weighted grade (A-F)

**Output:**
```
╔════════════════════════════════════╗
║     CODE REVIEW SCORECARD          ║
╠════════════════════════════════════╣
║ Requirement Met:   95% ████████░  ║
║ Code Quality:      85% ███████░░  ║
║ Test Coverage:     72% ██████░░░  ║
║ Documentation:     68% ██████░░░░ ║
╠════════════════════════════════════╣
║ Final Grade: B (83.5/100)          ║
║ Status: ⚠️ Changes Needed           ║
╚════════════════════════════════════╝
```

**When to use:** Code Review Agent v3

---

## 🚀 Apache Camel Skill (v1.0)

**File:** [`apache_camel_skill.md`](apache_camel_skill.md)

**Supports:**
- Enterprise Integration Patterns (EIP)
- Message routing
- Transformation
- Error handling

**Generates:**
- Route definitions
- Processor implementations
- Error handlers
- Conditional logic

**When to use:** Advanced integration scenarios

---

## Skills Matrix

| Skill | Language | Agent | Use Case |
|-------|----------|-------|----------|
| Code Docs | JS/Python/Java | All | Documentation |
| Database | PostgreSQL/MySQL | Autonomous | Data layer |
| Backend | FastAPI/Spring | Implementation | API development |
| Frontend | React/TS | Implementation | UI development |
| Testing | JUnit5/pytest | Test Gen | Test generation |
| Code Review | Agnostic | Code Review | PR validation |
| Camel | Apache Camel | Advanced | Integration |

---

## How Skills Work

### For Agents
Agents **delegate** to skills for language-specific implementation:

```python
# In Implementation Agent:
tech_stack = detect_technology(project)

if tech_stack.backend == "FastAPI":
    skill = backend_skill  # Apply FastAPI skill
    code = skill.generate_endpoints(requirement)
elif tech_stack.backend == "Spring":
    skill = backend_skill  # Apply Spring skill
    code = skill.generate_endpoints(requirement)
```

### For Users
You can **import and use skills directly**:

```python
from skills.code_documentation_skill import DocumentationGenerator

generator = DocumentationGenerator()
docs = generator.generate_from_code("src/auth.py", format="docstring")
print(docs)
```

---

## Adding a New Skill

1. **Create:** `skills/my_skill.md`
2. **Structure:**
   ```markdown
   ---
   name: My Skill
   version: 1.0
   description: What it does
   ---
   
   # Skill Name
   ## Overview
   ## Process
   ## Example
   ## Best Practices
   ```
3. **Test:** Run with agents
4. **Submit:** PR with examples

---

## 🔗 Links

- **[Agents Directory](../agents/README.md)** — Agent catalog
- **[Tools Documentation](./README.md)** — Utility scripts  
- **[Master Rules](../instructions/master_instruction_set.md)** — Standards
- **[Main README](../README.md)** — Project overview

---

**Last Updated:** May 25, 2026 | **Version:** 4.2.0
