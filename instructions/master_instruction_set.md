---
name: Master Instruction Set
version: 2.0
description: >
  Universal rules that ALL coding agents must follow. Covers version checking,
  project intake, OOP principles, documentation standards, simplicity rules,
  and mandatory test generation.
applies_to: [java, python, react, mssql, all-agents]
---

# Master Instruction Set — All Coding Agents

> These rules are NON-NEGOTIABLE. Every agent must follow them on every task.

---

## RULE 0 — Check Before You Code

**Never assume the environment. Always verify first.**

### 0.1 — Version Check Protocol

When the user starts a new task, ask them to run the relevant version commands
and share the output. Use the result to decide which language features are safe to use.

| Platform | Command to Run | What to Look For |
|----------|---------------|------------------|
| Java | `java -version` | 11, 17, 21 (LTS), or 23+ |
| Maven | `mvn -version` | 3.8+, 3.9+ |
| Gradle | `gradle -version` | 7.x, 8.x |
| Spring Boot | Check `pom.xml` / `build.gradle` | 2.7.x vs 3.x |
| Python | `python --version` or `python3 --version` | 3.10, 3.11, 3.12 |
| Node | `node -v` | 18 LTS, 20 LTS, 22 LTS |
| npm/pnpm | `npm -v` / `pnpm -v` | latest stable |
| SQL Server | `SELECT @@VERSION` | 2016, 2019, 2022, Azure SQL |

**Rule:** Only use features available in the detected version. If uncertain, pick the
lowest safe common version and note it.

---

## RULE 1 — Ask Before You Build (New Projects)

**If the user says "create from scratch", "new project", "start a new app" — STOP and run the intake questionnaire.**

Never generate a project skeleton without answers to the intake questions.
Use the language-specific intake template:
- Java: `instructions/java_project_intake.md`
- Python: `instructions/python_project_intake.md`

For React and MSSQL, ask the inline questions defined in each agent.

---

## RULE 2 — Always Generate Tests

**Code is not complete without tests. Tests are not optional.**

Every time you write a new class, function, method, stored procedure, or component — you MUST generate the corresponding tests in the same response.

### Test Structure (All Languages)

Follow the **AAA pattern** without exception:

```
// Arrange — set up the data and objects needed
// Act     — call the method / function being tested
// Assert  — verify the outcome
```

### Test Naming

Use the `given_when_then` or `should_action_condition` pattern:

```
// Java / Python examples:
givenValidOrder_whenCreate_thenReturnsSavedOrder()
should_return_not_found_when_order_does_not_exist()

// React examples:
it('shows loading spinner while fetching user')
it('displays error message when API returns 500')

// MSSQL examples:
-- Test_usp_ProcessOrder_WhenPending_ShouldSucceed
-- Test_usp_ProcessOrder_WhenAlreadyProcessed_ShouldFail
```

### Minimum Coverage Per Task

| Scenario | Must Be Tested |
|----------|---------------|
| Happy path | Yes — the normal, successful flow |
| Edge case | Yes — empty input, boundary values, null |
| Error / exception | Yes — what happens when things go wrong |
| Boundary values | Yes — zero, negative, max, min |

---

## RULE 3 — OOP Principles in Every Codebase

Apply these four principles naturally — never force them, but never skip them either.

### 3.1 — Encapsulation: Hide What Doesn't Need to Be Seen

Keep data private. Control access through methods.

```java
// BAD — data is exposed and anyone can change it
public class BankAccount {
    public double balance;  // anyone can set this to anything!
}

// GOOD — balance is private, only changed through controlled methods
public class BankAccount {

    private double balance;  // only this class can touch balance directly

    /**
     * Deposits the given amount into this account.
     * @param amount must be positive
     * @throws IllegalArgumentException if amount is zero or negative
     */
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Deposit amount must be positive. Got: " + amount);
        }
        this.balance += amount;
    }

    /**
     * Returns the current balance. Read-only.
     */
    public double getBalance() {
        return this.balance;
    }
}
```

### 3.2 — Abstraction: Define What, Not How

Use interfaces to define what a component does. Keep the how in the implementation.

```java
// The interface says WHAT — like a menu in a restaurant
public interface NotificationSender {
    void send(String recipient, String message);
}

// The implementation says HOW — like the kitchen
public class EmailNotificationSender implements NotificationSender {
    @Override
    public void send(String recipient, String message) {
        // ... email sending logic here
    }
}

public class SmsNotificationSender implements NotificationSender {
    @Override
    public void send(String recipient, String message) {
        // ... SMS sending logic here
    }
}
```

### 3.3 — Inheritance: Share Common Behaviour

Use inheritance for "is-a" relationships. Prefer composition when in doubt.

```java
// Base class holds common fields and behaviour
public abstract class Animal {
    private final String name;

    public Animal(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    /** Each animal makes its own sound — subclasses must implement this */
    public abstract String makeSound();
}

// Subclass only adds or overrides what is different
public class Dog extends Animal {
    public Dog(String name) {
        super(name);
    }

    @Override
    public String makeSound() {
        return "Woof!";
    }
}
```

### 3.4 — Polymorphism: One Interface, Many Shapes

Write code that works with the interface, not the specific class.

```java
// This method works with ANY NotificationSender — email, SMS, push, etc.
public void notifyUser(NotificationSender sender, String user, String message) {
    sender.send(user, message);
}

// At runtime, you can swap the sender without changing this method
notifyUser(new EmailNotificationSender(), "alice@example.com", "Your order is ready!");
notifyUser(new SmsNotificationSender(), "+447700900000",     "Your order is ready!");
```

---

## RULE 4 — Documentation: Write for the Next Developer

Every public class, method, and non-obvious field must be documented.
Write for someone who has never seen this code before.

### What to Document

| Element | Document It If... |
|---------|-----------------|
| Public class | Always |
| Public method | Always |
| Public field / constant | Always |
| Private method | Only if the logic is non-obvious |
| Private field | Only if the name doesn't explain itself |
| Complex loop / algorithm | Always — explain WHY, not WHAT |

### Java — Javadoc Format

```java
/**
 * Manages customer orders throughout their lifecycle from creation to delivery.
 *
 * <p>This service is the single point of entry for all order operations.
 * It validates input, persists to the database, and publishes domain events.</p>
 *
 * @author Team Name
 * @since 1.0
 */
@Service
public class OrderService {

    /**
     * Creates a new order for the given customer.
     *
     * <p>Validates the request, saves the order with PENDING status,
     * and publishes an {@code OrderCreatedEvent}.</p>
     *
     * @param request the order creation request — must not be null, customer ID must exist
     * @return the saved order with generated ID and PENDING status
     * @throws CustomerNotFoundException if the customer ID does not exist
     * @throws InvalidOrderException     if the order items list is empty
     */
    public OrderResponse createOrder(CreateOrderRequest request) { ... }
}
```

### Python — Docstring Format (Google Style)

```python
class OrderService:
    """Manages customer orders throughout their lifecycle.

    This service is the single point of entry for all order operations.
    It validates input, persists to the database, and publishes domain events.
    """

    def create_order(self, request: CreateOrderRequest) -> OrderResponse:
        """Creates a new order for the given customer.

        Validates the request, saves the order with PENDING status,
        and publishes an OrderCreatedEvent.

        Args:
            request: The order creation request. Customer ID must exist.

        Returns:
            The saved order with a generated ID and PENDING status.

        Raises:
            CustomerNotFoundError: If the customer ID does not exist.
            InvalidOrderError: If the order items list is empty.
        """
```

---

## RULE 5 — Simple Code. No Cleverness.

> "Simple code is not dumb code. Simple code is code that any developer on the team
> can read, understand, and change safely."

### Simplicity Rules

| Rule | Bad | Good |
|------|-----|------|
| Variable names | `d`, `tmp`, `x` | `dueDate`, `tempOrder`, `customerId` |
| Method length | > 30 lines | ≤ 20 lines — extract if longer |
| Class length | > 400 lines | ≤ 300 lines — split by responsibility |
| Nesting depth | 4+ levels of if/for | Max 2–3 — extract to methods |
| Clever one-liners | Chained lambdas that take 5 mins to decode | Break into named variables |
| Magic numbers | `if (status == 3)` | `if (status == OrderStatus.SHIPPED)` |
| Comments | `// increment i by 1` | `// Skip archived records — they're read-only` |

### One Class = One Job (Single Responsibility)

```
// BAD — this class does everything
public class UserManager {
    public void createUser(...) { }
    public void sendWelcomeEmail(...) { }
    public void saveToDatabase(...) { }
    public void logAuditEvent(...) { }
}

// GOOD — each class has one clear job
UserService        → creates / updates / deletes users (business logic)
UserRepository     → saves / reads users from the database (data access)
EmailService       → sends emails (communication)
AuditLogger        → records audit events (observability)
```

---

## RULE 6 — Code Output Format

Every code response must follow this structure:

```
1. [INTENT]        — One sentence: what this code does and why.

2. [STRUCTURE]     — Bullet list of files/classes being created or changed.

3. [CODE]          — The implementation, with documentation and comments.

4. [TESTS]         — The tests for the above code. Always in the same response.

5. [NOTES]         — Any follow-up steps, limitations, or version-specific caveats.
```

Never skip [TESTS]. If the user says "just the code", remind them that tests
are part of the deliverable and generate them anyway.

---

## RULE 7 — Project Structure Conventions

### Java (Spring Boot)
```
src/
  main/
    java/
      com.{company}.{project}/
        controller/     ← REST layer — receives requests, returns responses
        service/        ← Business logic — the "brain" of the app
        repository/     ← Database access — talks to the DB
        model/
          entity/       ← JPA entities — mirrors the DB tables
          dto/          ← Request / response objects — what the API sees
          enums/        ← Status codes, types, categories
        exception/      ← Custom exception classes
        config/         ← Spring configuration beans
        util/           ← Shared helper utilities
    resources/
      application.yml
      application-dev.yml
      application-prod.yml
  test/
    java/
      com.{company}.{project}/
        controller/     ← Integration tests for REST endpoints
        service/        ← Unit tests for business logic
        repository/     ← Repository / DB integration tests
```

### Python (FastAPI)
```
src/
  app/
    api/            ← FastAPI routers
    services/       ← Business logic
    repositories/   ← Database access
    models/         ← Pydantic schemas (request/response)
    orm/            ← SQLAlchemy ORM models
    core/           ← Config, lifespan, middleware
    exceptions/     ← Custom exception classes
tests/
  unit/
  integration/
```

### React
```
src/
  components/         ← Shared UI building blocks (Button, Input, Card)
  features/
    {feature-name}/
      components/     ← Feature-specific components
      hooks/          ← Custom hooks for this feature
      types/          ← TypeScript types for this feature
      index.ts        ← Public API of the feature
  pages/              ← Route-level page components
  lib/                ← API client, utilities
  types/              ← Global shared TypeScript types
```

---

## RULE 8 — Security is Non-Negotiable

| Threat | Prevention |
|--------|-----------|
| SQL Injection | Parameterised queries ONLY — never string-concatenate SQL |
| XSS | Escape all user content before rendering in HTML |
| Hardcoded secrets | Use environment variables or secret managers |
| Insecure deserialization | Never deserialise untrusted data with `ObjectInputStream` or `pickle` |
| Broken auth | Never roll your own auth — use Spring Security / OAuth2 / JWT |

If you spot a security risk in code you are reviewing or extending, flag it immediately before proceeding.

---

## RULE 9 — When You Are Unsure, Ask

Never guess and generate 100 lines of code in the wrong direction.

Ask when:
- The task is ambiguous ("add functionality" — which functionality?)
- There are multiple valid approaches with different trade-offs
- The target version or tech stack is unknown
- The business logic is unclear (do zero-value orders succeed or fail?)

Maximum 3 questions at a time. Be specific. Offer options where possible.
