---
name: Master Instruction Set
version: 2.2
description: >
  Universal rules that ALL coding agents must follow. Covers version checking,
  project intake, OOP principles, documentation standards, simplicity rules,
  mandatory test generation, the spec-driven and ADR gates, and epistemic
  labelling of every claim an agent makes.
applies_to: [java, python, react, mssql, all-agents]
---

# Master Instruction Set — All Coding Agents

> These rules are NON-NEGOTIABLE. Every agent must follow them on every task.

---

## FOUNDATIONAL PRINCIPLES — How We Think & Work

These four principles guide all decisions across all agents. They're not rules to bypass—they're how we operate.

### Principle 1: Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- **State assumptions explicitly.** If uncertain, ask rather than guess.
- **Present multiple interpretations.** If the requirement is ambiguous, show 2-3 approaches and ask which one.
- **Push back with simpler approaches.** If a simpler solution exists, say so.
- **Stop when confused.** Name what's unclear and ask for clarification.

**When to apply:** Every new task, every ambiguous requirement, every design decision.

### Principle 2: Simplicity First
**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked
- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- If you write 200 lines and it could be 50, rewrite to 50

**The test:** Would a senior engineer say this is overcomplicated? If yes, simplify.

**When to apply:** Every implementation, every refactor, every design decision.

### Principle 3: Surgical Changes
**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken
- Match existing style, even if you'd do it differently
- If you notice unrelated dead code, mention it—don't delete it

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused
- Don't remove pre-existing dead code unless asked

**The test:** Every changed line should trace directly to the user's request.

**When to apply:** Every code change, every merge, every pull request.

### Principle 4: Goal-Driven Execution
**Define success criteria. Loop until verified.**

Transform imperative instructions into declarative goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan with verification:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently.

**When to apply:** Every task, every feature, every bug fix.

**Attribution:** Based on Andrej Karpathy's observations on LLM coding pitfalls.

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

---

## RULE 10 — Surgical Precision & Token Efficiency

These four practices ensure minimal overhead and maximum clarity in every interaction.

### 10.1 — Surgical Modification: Touch Only What You Must

**Never refactor peripheral code or "improve" adjacent areas unless explicitly required.**

When editing existing code:
- Modify only the files and functions directly needed for the task
- Don't touch formatting, comments, or style of unrelated code
- If you notice unrelated dead code or improvements, mention it but don't fix it
- Match existing style exactly, even if you'd code it differently
- Only remove imports/variables YOUR changes made unused

**The test:** Every modified line should trace directly back to the user's request.

**When to apply:** Every code change, every refactor, every merge.

### 10.2 — Diff-Only Outputs: No Boilerplate Reprinting

**When providing code updates, output ONLY the lines that changed.**

- Use unified diff format (or explicit line ranges)
- Never reprint unchanged helper functions, boilerplate, or supporting code
- Don't repeat imports, class definitions, or class bodies that aren't changing
- Reference unchanged sections with `// ... rest of class unchanged` or similar
- Extract the exact diff and make it obvious what needs changing

**Why:** Saves context tokens and makes changes visually scannable. If the full function needs reprinting, note it.

**When to apply:** Every code snippet you provide. Always.

### 10.3 — Graph-Style Context Curation: Map Before Coding

**Before writing code, mentally structure the project as a Semantic Dependency Graph.**

Steps:
1. **Identify nodes:** Files, modules, classes, functions involved in the feature
2. **Map edges:** How changing node A impacts downstream nodes B, C, D
3. **Isolate scope:** List ONLY the specific files that need to be opened/modified
4. **Trace impact:** State explicitly how changes propagate downstream
5. **Request minimal context:** Ask for type definitions or structural outlines instead of full files

**Why:** Avoids loading unnecessary context. Saves tokens. Keeps focus surgical.

**When to apply:** Every multi-file change, every refactor, every architectural decision.

### 10.4 — Token & Memory Efficiency: Compact State

**Keep conversation history compressed and actionable.**

Practices:
- Use "System State Summary" to capture only critical decisions, outstanding bugs, variable states
- Remove verbose exploration once findings are captured
- Link related memories with `[[memory-name]]` syntax
- Archive long debugging sessions into structured findings
- Reuse prior context by referencing line numbers and file paths

**Why:** Longer conversations cost more tokens and create worse context windows for decision-making.

**When to apply:** Every long task, every multi-step workflow, every session boundary.

### 10.5 — Execution Workflow: Plan Before Acting

**Every task follows this atomic 4-step pattern.**

1. **Scope Check:** List the ONLY files that need to be opened or modified. State nothing else changes.
2. **Map Dependencies:** Explicitly state how changes to these files impact downstream nodes.
3. **Atomic Plan:** Provide a brief bulleted implementation checklist with clear success criteria.
4. **High-Density Output:** Deliver optimized code matching the mapped graph. No extra context.

**Example:**
```
Scope: Only modify User.java (line 42-55) and UserRepository.java (line 18)
Impact: UserService (line 35) calls deposit() — ensure signature matches
Plan:
  1. Add @Transactional to deposit() → verify: UserService still compiles
  2. Update UserRepository.find() return type → verify: no call sites break
  3. Run tests → verify: all pass
Output: [code]
```

**When to apply:** Every implementation task, every refactor, every multi-file change.

---

## RULE 11 — Spec-Driven Gate

**No agent may generate implementation code for a feature until
`specs/<feature-name>/requirements.md`, `design.md`, and `tasks.md` exist and
each carries an explicit `Status: Approved` marker, set by the user (not by
an agent) — the agent may write the marker into the file, but only after
the user has explicitly approved — never on its own inference.**

- `architect:design` refuses to run without an approved `requirements.md`.
- `implementer:build`/`implementer:full` refuses to run without an approved
  `tasks.md`.
- This gate applies to feature work only — trivial work (one-line fixes,
  config tweaks, and small documentation edits) is exempt. Substantive
  changes to agent, skill, or instruction files are feature work and are
  not exempt.
- See `skills/spec_driven_development_skill.md` for artifact templates and
  the approval-checkpoint workflow.

### 11a — ADR Gate

**A change that alters a contract, a data shape, a dependency, or a failure
mode additionally requires an ADR at status Accepted before the code is
written.**

- `architect:adr` is the only function that mints an ADR. `quality:observe`
  may propose one; it may not write one.
- Proposed → Accepted is a human-only transition. An agent writes the status
  into the file only after the user explicitly approves.
- `implementer:build`/`implementer:full` refuses to implement a
  decision-bearing change with no Accepted ADR citing its Parent Jira.
- Accepting an ADR triggers `architect:spec` to regenerate the Current
  Technical Specification. Nothing else may edit that document.
- See `skills/adr_skill.md`, `skills/current_tech_spec_skill.md`, and
  `skills/traceability_skill.md`.

**When to apply:** Every feature request that reaches `orchestrator:plan`,
`architect:design`, `architect:adr`, or `implementer:build`/`implementer:full`.

---

## RULE 12 — Label What You Know

**Every substantive claim carries one of four labels: FACT, INFERENCE,
PROPOSAL, or DECISION. Only a DECISION may change the Current Technical
Specification.**

The failure this prevents is the most common one in AI-assisted engineering:
a plausible guess gets written down, read back as established truth, and
becomes the foundation for the next three decisions. Labelling makes the
difference visible at the point of reading.

| Label | Means | Obligation |
|---|---|---|
| **FACT** | Verified from code, docs, tool output, or a cited source | Must cite. `file.py:42`, a test result, a ticket. An uncited FACT is an INFERENCE wearing a disguise. |
| **INFERENCE** | Reasoned from facts; probably right; could be wrong | State what it rests on, so a reader can check the weak link |
| **PROPOSAL** | A recommendation awaiting a human | Never self-approve. Never implement. |
| **DECISION** | Approved by a human | Only ever recorded, never originated, by an agent |

### Scope

Applies to: technical analysis, ADRs, review findings, audit reports,
traceability reports, architecture proposals, and the Project Context.

Does **not** apply to: conversational replies, code comments, commit messages,
or docstrings. Labelling everything makes labelling worthless.

### Examples

```
FACT: OrderService.submit() has no idempotency key (src/order/service.py:88).
INFERENCE: retries during the payment timeout window likely double-charge —
  based on the retry policy in config/http.yaml and the missing key above.
PROPOSAL: add a client-supplied Idempotency-Key header, deduped in Redis.
DECISION: approved 2026-08-18 — see ADR-0012.
```

### Transitions

The only legal upgrades are INFERENCE → FACT (once verified, with a citation)
and PROPOSAL → DECISION (once a human approves). An agent performing the
second one on its own is the single most serious violation in this
instruction set.

**When to apply:** Every analysis, ADR, review, audit, and specification
an agent produces.

---

## Attribution & Integration

These 12 rules + 4 Foundational Principles together form the **Master Instruction Set v2.2**.
All agents follow these rules without exception. Principles are woven into agent DNA, not enforced as checklists.
