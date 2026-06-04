---
name: Python Project Intake Template
version: 2.0
description: >
  Q&A intake form for new Python projects. The agent fills this in based on
  user responses before generating any code. Covers environment, framework,
  database, testing, and code style.
applies_to: [python, fastapi, django, flask]
---

# Python Project Intake Form

> **Agent Instructions:** Present these questions in groups of 3–4.
> Wait for answers before proceeding to the next group.
> Fill in this template as you go, then confirm the summary before coding.

---

## GROUP 1 — Environment Check

Ask the user to run these commands and share the output:

```bash
python --version         # or: python3 --version
pip --version            # or: pip3 --version
poetry --version         # if using Poetry
```

| Question | Answer |
|----------|--------|
| Q1. Python version installed? | __________ |
| Q2. Package manager? | `[ ]` pip  `[ ]` Poetry  `[ ]` PDM  `[ ]` uv |
| Q3. Virtual environment tool? | `[ ]` venv  `[ ]` conda  `[ ]` Poetry (built-in)  `[ ]` pyenv |

**Agent Decision Table — Python Version:**

| Installed | Key Features Available |
|-----------|----------------------|
| Python 3.10 | `match` statement, `X \| Y` union types |
| Python 3.11 | ~60% faster than 3.10, `tomllib`, fine-grained error locations |
| Python 3.12 | `@override` decorator, better f-strings, `pathlib` improvements |
| Python 3.13 | Free-threaded mode (no GIL, experimental), improved REPL |

> **Default target:** Use Python 3.11 features unless a higher version is confirmed.

---

## GROUP 2 — Project Identity

| Question | Answer |
|----------|--------|
| Q4. Project name? (e.g. `order-service`) | __________ |
| Q5. Top-level package name? (e.g. `order_service`) | __________ |
| Q6. Short description — what does this project do? | __________ |
| Q7. Project type? | `[ ]` REST API  `[ ]` CLI tool  `[ ]` Data pipeline  `[ ]` Library  `[ ]` Script  `[ ]` ML/Data Science |

---

## GROUP 3 — Framework

| Question | Answer |
|----------|--------|
| Q8. Web framework? | `[ ]` FastAPI  `[ ]` Django  `[ ]` Flask  `[ ]` None (plain Python) |
| Q9. If FastAPI — async or sync? | `[ ]` Async (recommended)  `[ ]` Sync |
| Q10. API versioning? | `[ ]` URL path (`/api/v1/`)  `[ ]` Header  `[ ]` None |
| Q11. WSGI/ASGI server for deployment? | `[ ]` Uvicorn  `[ ]` Gunicorn  `[ ]` Hypercorn |

**Agent Decision Table — Framework:**

| Framework | Best For | ORM | Notes |
|-----------|---------|-----|-------|
| FastAPI | APIs, microservices, async | SQLAlchemy | Modern, fast, auto-docs |
| Django | Full-stack web apps | Django ORM | Batteries included |
| Flask | Simple APIs, prototypes | SQLAlchemy / any | Minimalist, flexible |
| Plain Python | Scripts, pipelines, libraries | Any / None | No web overhead |

---

## GROUP 4 — Database

| Question | Answer |
|----------|--------|
| Q12. Database? | `[ ]` PostgreSQL  `[ ]` MySQL  `[ ]` MS SQL Server  `[ ]` SQLite  `[ ]` MongoDB  `[ ]` None |
| Q13. ORM / access? | `[ ]` SQLAlchemy 2.x (async)  `[ ]` SQLAlchemy 2.x (sync)  `[ ]` Django ORM  `[ ]` Raw SQL  `[ ]` None |
| Q14. Database migrations? | `[ ]` Alembic  `[ ]` Django migrations  `[ ]` None |
| Q15. Connection pooling? | `[ ]` SQLAlchemy pool  `[ ]` asyncpg pool  `[ ]` Default |

---

## GROUP 5 — Data Validation & Models

| Question | Answer |
|----------|--------|
| Q16. Input/output validation? | `[ ]` Pydantic v2 (recommended)  `[ ]` Pydantic v1  `[ ]` dataclasses  `[ ]` None |
| Q17. Settings / config management? | `[ ]` pydantic-settings  `[ ]` python-dotenv  `[ ]` os.environ  `[ ]` dynaconf |
| Q18. Serialisation format? | `[ ]` JSON  `[ ]` Protobuf  `[ ]` MessagePack |

---

## GROUP 6 — Testing

| Question | Answer |
|----------|--------|
| Q19. Test framework? | `[ ]` pytest (recommended)  `[ ]` unittest |
| Q20. Async test support? | `[ ]` pytest-asyncio  `[ ]` anyio  `[ ]` Not needed |
| Q21. HTTP mocking? | `[ ]` respx  `[ ]` pytest-httpx  `[ ]` responses  `[ ]` None |
| Q22. DB integration tests? | `[ ]` testcontainers-python  `[ ]` SQLite in-memory  `[ ]` None |
| Q23. Coverage tool? | `[ ]` pytest-cov  `[ ]` coverage.py |

---

## GROUP 7 — Code Quality

| Question | Answer |
|----------|--------|
| Q24. Linter? | `[ ]` ruff (recommended)  `[ ]` flake8  `[ ]` pylint |
| Q25. Formatter? | `[ ]` ruff format  `[ ]` black  `[ ]` None |
| Q26. Type checker? | `[ ]` mypy  `[ ]` pyright  `[ ]` None |
| Q27. Docstring style? | `[ ]` Google (recommended)  `[ ]` NumPy  `[ ]` reStructuredText |

---

## COMPLETED INTAKE SUMMARY

> **Agent:** Once all groups are answered, present this summary and ask for confirmation.

```
╔══════════════════════════════════════════════════════════╗
║          PYTHON PROJECT CONFIGURATION SUMMARY            ║
╠══════════════════════════════════════════════════════════╣
║  Python Version:   ______   Package Mgr:   ______        ║
║  Project Name:     ______   Package Name:  ______        ║
║  Framework:        ______   Async:         ______        ║
║  Database:         ______   ORM:           ______        ║
║  Validation:       ______   Migrations:    ______        ║
║  Test Framework:   ______   Linter:        ______        ║
╚══════════════════════════════════════════════════════════╝

Does this look right? Type YES to begin or correct any item.
```

---

## GENERATED PROJECT STRUCTURE

After confirmation, generate this structure. Replace `{package}` with the confirmed package name.

```
{project-name}/
├── src/
│   └── {package}/
│       ├── __init__.py
│       ├── main.py                   ← FastAPI app / entry point
│       ├── api/                      ← Route handlers (controllers)
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── __init__.py
│       │       └── {resource}.py
│       ├── services/                 ← Business logic
│       │   ├── __init__.py
│       │   └── {resource}_service.py
│       ├── repositories/             ← Database access layer
│       │   ├── __init__.py
│       │   └── {resource}_repository.py
│       ├── models/                   ← Pydantic request/response schemas
│       │   ├── __init__.py
│       │   └── {resource}.py
│       ├── orm/                      ← SQLAlchemy ORM models
│       │   ├── __init__.py
│       │   └── {resource}.py
│       ├── core/                     ← Config, lifespan, middleware
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── database.py
│       └── exceptions/               ← Custom exception classes
│           └── __init__.py
├── tests/
│   ├── conftest.py                   ← Shared pytest fixtures
│   ├── unit/                         ← Fast unit tests (no I/O)
│   └── integration/                  ← Tests with real DB / HTTP
├── alembic/                          ← DB migrations (if Alembic)
│   └── versions/
├── pyproject.toml                    ← Dependencies + tool config
├── .env.example                      ← Example environment variables
└── README.md
```

---

## OOP PATTERNS FOR PYTHON

When generating Python code, always apply these patterns:

### Abstract Base Class (Abstraction)
```python
from abc import ABC, abstractmethod

class NotificationSender(ABC):
    """Abstract base for all notification delivery mechanisms.

    Subclasses must implement the send method for their specific channel.
    """

    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """Sends a notification to the recipient.

        Args:
            recipient: The address or identifier to send to.
            message: The notification content.

        Returns:
            True if sent successfully, False otherwise.
        """
```

### Encapsulation with Properties
```python
class BankAccount:
    """Represents a customer bank account with controlled balance access."""

    def __init__(self, owner: str, initial_balance: float = 0.0) -> None:
        """Initialises a bank account.

        Args:
            owner: The name of the account holder.
            initial_balance: Starting balance. Must be non-negative.

        Raises:
            ValueError: If initial_balance is negative.
        """
        if initial_balance < 0:
            raise ValueError(f"Initial balance cannot be negative. Got: {initial_balance}")
        self._owner = owner        # private — use property to read
        self._balance = initial_balance  # private — only changed via deposit/withdraw

    @property
    def balance(self) -> float:
        """The current account balance. Read-only."""
        return self._balance

    def deposit(self, amount: float) -> None:
        """Deposits the given amount. Amount must be positive."""
        if amount <= 0:
            raise ValueError(f"Deposit amount must be positive. Got: {amount}")
        self._balance += amount
```

### Dataclass (Simple Data Carriers)
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Order:
    """Represents a customer order.

    Attributes:
        order_id: Unique identifier for the order.
        customer_id: ID of the customer who placed the order.
        items: List of items in the order.
        created_at: When the order was created. Defaults to now.
    """
    order_id: int
    customer_id: int
    items: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
```
