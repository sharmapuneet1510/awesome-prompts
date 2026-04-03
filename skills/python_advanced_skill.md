---
name: Python Advanced Coding Skill
version: 2.0
description: >
  Reusable skill module for Python coding. Covers Python 3.11/3.12 features,
  OOP principles with ABC and dataclasses, Google-style docstrings, type hints,
  async patterns, and pytest test generation.
applies_to: [python, fastapi, sqlalchemy, pydantic, asyncio]
---

# Python Advanced Coding Skill — v2.0

---

## 1. Version Detection First

Before writing any Python code, check what is installed:

```bash
python --version   # or: python3 --version
pip --version
```python

| Python Version | Features Available |
|---------------|--------------------|
| 3.10 | `match` statement, `X \| Y` union types (in annotations only) |
| 3.11 | ~60% faster, `tomllib`, `ExceptionGroup`, `Self` type |
| 3.12 | `@override` decorator, `type` alias statement, better f-strings |
| 3.13 | Free-threaded mode (experimental), improved REPL |

**Default target:** Python 3.11 features unless a higher version is confirmed.

---

## 2. Four OOP Pillars — Applied in Python

### 2.1 Encapsulation — Properties and Private Attributes

Python uses naming convention (`_name`) and `@property` for encapsulation.

```python
class BankAccount:
    """Represents a customer bank account.

    The balance is private — it can only be changed through
    deposit() and withdraw() methods, not set directly from outside.

    Attributes:
        owner_name: The name of the account holder.
    """

    def __init__(self, owner_name: str, initial_balance: float = 0.0) -> None:
        """Creates a new bank account.

        Args:
            owner_name: Full name of the account holder.
            initial_balance: Starting balance. Must be zero or positive.

        Raises:
            ValueError: If initial_balance is negative.
        """
        if initial_balance < 0:
            raise ValueError(
                f"Initial balance cannot be negative. Got: {initial_balance}"
            )
        self._owner_name = owner_name          # _name = private by convention
        self._balance    = initial_balance

    @property
    def balance(self) -> float:
        """The current account balance. Can be read but not set directly."""
        return self._balance

    @property
    def owner_name(self) -> str:
        """The account holder's name. Read-only."""
        return self._owner_name

    def deposit(self, amount: float) -> None:
        """Adds the given amount to the account balance.

        Args:
            amount: The amount to deposit. Must be positive.

        Raises:
            ValueError: If amount is zero or negative.
        """
        if amount <= 0:
            raise ValueError(f"Deposit amount must be positive. Got: {amount}")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        """Removes the given amount from the account balance.

        Args:
            amount: The amount to withdraw. Must not exceed current balance.

        Raises:
            ValueError: If amount is zero or negative.
            InsufficientFundsError: If the account does not have enough balance.
        """
        if amount <= 0:
            raise ValueError(f"Withdrawal amount must be positive. Got: {amount}")
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Cannot withdraw {amount:.2f}. Available balance: {self._balance:.2f}"
            )
        self._balance -= amount

    def __repr__(self) -> str:
        """Returns a developer-friendly string for debugging."""
        return f"BankAccount(owner='{self._owner_name}', balance={self._balance:.2f})"
```python

### 2.2 Abstraction — ABC for Interfaces

Use `abc.ABC` and `@abstractmethod` to define contracts.

```python
from abc import ABC, abstractmethod


class NotificationSender(ABC):
    """Defines the contract for sending notifications.

    Any class that wants to send notifications should inherit from this
    and implement the send() method. This means callers can work with
    any sender (email, SMS, push) without knowing the details.
    """

    @abstractmethod
    def send(self, recipient: str, subject: str, message: str) -> bool:
        """Sends a notification to the recipient.

        Args:
            recipient: The address or identifier (email, phone, device token).
            subject: A short title for the notification.
            message: The full notification body.

        Returns:
            True if the notification was delivered successfully.

        Raises:
            NotificationError: If delivery fails after all retries.
        """


class EmailNotificationSender(NotificationSender):
    """Sends notifications via email using SMTP.

    Attributes:
        smtp_host: The SMTP server hostname.
        smtp_port: The SMTP server port number.
    """

    def __init__(self, smtp_host: str, smtp_port: int = 587) -> None:
        """Initialises the email sender.

        Args:
            smtp_host: SMTP server hostname (e.g. 'smtp.gmail.com').
            smtp_port: SMTP port. Defaults to 587 (TLS).
        """
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port

    def send(self, recipient: str, subject: str, message: str) -> bool:
        """Sends an email to the recipient.

        Args:
            recipient: The destination email address.
            subject: Email subject line.
            message: Email body text.

        Returns:
            True when the email is accepted by the SMTP server.
        """
        # SMTP sending logic here
        return True
```python

### 2.3 Inheritance — Shared Base, Specialised Subclasses

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Payment(ABC):
    """Base class for all payment types.

    Holds common payment fields and defines the process() method
    that each payment type must implement.

    Attributes:
        amount: The payment amount. Must be positive.
        currency: ISO 4217 currency code (e.g. 'GBP').
        reference_id: Unique identifier for this payment.
    """
    amount: float
    currency: str
    reference_id: str

    def __post_init__(self) -> None:
        """Validates common fields after dataclass initialisation."""
        if self.amount <= 0:
            raise ValueError(f"Payment amount must be positive. Got: {self.amount}")

    @abstractmethod
    def process(self) -> "PaymentResult":
        """Processes this payment through its specific channel.

        Returns:
            A PaymentResult indicating success or failure.
        """


@dataclass
class CardPayment(Payment):
    """A payment made with a credit or debit card.

    Extends Payment with card-specific fields.

    Attributes:
        masked_card_number: Last 4 digits only (e.g. '****1234').
        card_holder_name: Name as it appears on the card.
    """
    masked_card_number: str
    card_holder_name: str

    def process(self) -> "PaymentResult":
        """Processes the card payment via the card gateway.

        Returns:
            PaymentResult with the transaction ID on success.
        """
        # Card gateway integration logic here
        return PaymentResult(success=True, transaction_id=self.reference_id)
```python

### 2.4 Polymorphism — Write Code to the Interface

```python
def send_payment_confirmation(
    sender: NotificationSender,   # works with ANY NotificationSender
    recipient: str,
    payment: Payment,
) -> None:
    """Sends a payment confirmation to the customer.

    Works with any notification channel — email, SMS, push.
    The caller decides which sender to use.

    Args:
        sender: The notification channel to use.
        recipient: The customer's contact address.
        payment: The payment that was just processed.
    """
    subject = f"Payment confirmed — {payment.reference_id}"
    message = f"Your payment of {payment.amount:.2f} {payment.currency} was received."
    sender.send(recipient, subject, message)

# This works with any sender — no code change needed in send_payment_confirmation
send_payment_confirmation(EmailNotificationSender("smtp.example.com"), "alice@example.com", payment)
send_payment_confirmation(SmsNotificationSender("+447700900000"), "+447700900000", payment)
```python

---

## 3. Dataclasses and Pydantic Models

### Dataclass — Internal Data Carriers

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class OrderItem:
    """A single line item within a customer order.

    Attributes:
        product_id: Unique ID of the product.
        product_name: Human-readable product name.
        quantity: Number of units ordered. Must be positive.
        unit_price: Price per unit in the order currency.
    """
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

    @property
    def line_total(self) -> float:
        """The total cost for this line: quantity × unit price."""
        return self.quantity * self.unit_price
```python

### Pydantic v2 — API Request / Response Models

```python
from pydantic import BaseModel, Field, field_validator


class CreateOrderRequest(BaseModel):
    """Request body for creating a new customer order.

    All fields are validated automatically by Pydantic before
    the API handler is called.
    """

    customer_id: int = Field(gt=0, description="The customer placing the order")
    items: list[str] = Field(min_length=1, description="List of product IDs")
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("items")
    @classmethod
    def items_must_not_contain_duplicates(cls, items: list[str]) -> list[str]:
        """Ensures no duplicate product IDs in the same order."""
        if len(items) != len(set(items)):
            raise ValueError("Order items must not contain duplicate product IDs.")
        return items


class OrderResponse(BaseModel):
    """Response returned after creating or retrieving an order."""

    order_id: int
    customer_id: int
    status: str
    total_amount: float
    created_at: datetime

    model_config = {"from_attributes": True}  # allows creating from ORM objects
```python

---

## 4. Async Patterns (FastAPI / asyncio)

### Async Service with Dependency Injection

```python
from typing import Protocol


class OrderRepository(Protocol):
    """Defines the data access contract for orders.

    Using Protocol means any class with these methods is compatible —
    no explicit inheritance required. Great for mocking in tests.
    """

    async def find_by_id(self, order_id: int) -> "Order | None":
        """Finds an order by ID. Returns None if not found."""
        ...

    async def save(self, order: "Order") -> "Order":
        """Saves an order and returns the persisted version."""
        ...


class OrderService:
    """Business logic for managing customer orders.

    This service validates input, coordinates with the repository,
    and applies business rules. It knows nothing about HTTP or SQL.
    """

    def __init__(self, repository: OrderRepository) -> None:
        """Initialises the service.

        Args:
            repository: The data access object to use. Injected for testability.
        """
        self._repository = repository

    async def get_order(self, order_id: int) -> OrderResponse:
        """Retrieves an order by its ID.

        Args:
            order_id: The unique order identifier.

        Returns:
            The order data.

        Raises:
            OrderNotFoundError: If no order with this ID exists.
        """
        order = await self._repository.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return OrderResponse.model_validate(order)
```python

---

## 5. Custom Exceptions

```python
class AppError(Exception):
    """Base exception for all application-specific errors.

    Catch this to handle any error raised by application code.
    Use specific subclasses to handle individual error types.
    """


class OrderNotFoundError(AppError):
    """Raised when an order with the given ID does not exist.

    Maps to HTTP 404 in the API exception handler.
    """

    def __init__(self, order_id: int) -> None:
        """
        Args:
            order_id: The ID that was not found.
        """
        super().__init__(f"Order with ID {order_id} was not found.")
        self.order_id = order_id


class InvalidOrderError(AppError):
    """Raised when order data fails business validation.

    Maps to HTTP 422 in the API exception handler.
    """
```python

---

## 6. Docstring Standard (Google Style)

Every public class, method, and function must have a docstring.

```python
def calculate_discount(original_price: float, discount_percent: float) -> float:
    """Calculates the discounted price after applying a percentage discount.

    Args:
        original_price: The price before discount. Must be positive.
        discount_percent: The discount as a percentage (0–100). E.g. 20 means 20% off.

    Returns:
        The price after the discount is applied.

    Raises:
        ValueError: If original_price is negative.
        ValueError: If discount_percent is not between 0 and 100.

    Example:
        >>> calculate_discount(100.0, 20.0)
        80.0
    """
    if original_price < 0:
        raise ValueError(f"Price cannot be negative. Got: {original_price}")
    if not 0 <= discount_percent <= 100:
        raise ValueError(f"Discount must be 0–100. Got: {discount_percent}")
    return original_price * (1 - discount_percent / 100)
```python

---

## 7. Testing Standards — pytest

### Unit Tests

```python
import pytest


class TestBankAccount:
    """Unit tests for BankAccount.

    Each test is independent — no shared state between tests.
    Uses the AAA pattern: Arrange / Act / Assert.
    """

    def test_given_positive_amount_when_deposit_then_balance_increases(self) -> None:
        """Happy path: depositing money should increase the balance."""
        # Arrange
        account = BankAccount(owner_name="Alice", initial_balance=100.0)

        # Act
        account.deposit(50.0)

        # Assert
        assert account.balance == 150.0

    def test_given_negative_amount_when_deposit_then_raises_value_error(self) -> None:
        """Error case: negative deposit should raise ValueError with clear message."""
        # Arrange
        account = BankAccount(owner_name="Alice", initial_balance=100.0)

        # Act & Assert
        with pytest.raises(ValueError, match="must be positive"):
            account.deposit(-10.0)

    @pytest.mark.parametrize("amount", [0.0, -1.0, -100.0])
    def test_given_zero_or_negative_deposit_when_deposit_then_raises(
        self, amount: float
    ) -> None:
        """Edge cases: zero and negative amounts are all invalid."""
        account = BankAccount(owner_name="Alice", initial_balance=100.0)
        with pytest.raises(ValueError):
            account.deposit(amount)

    def test_given_insufficient_balance_when_withdraw_then_raises(self) -> None:
        """Error case: withdrawing more than available should raise InsufficientFundsError."""
        account = BankAccount(owner_name="Alice", initial_balance=50.0)
        with pytest.raises(InsufficientFundsError):
            account.withdraw(100.0)
```python

### Async Tests (FastAPI / asyncio)

```python
import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_given_valid_id_when_get_order_then_returns_order() -> None:
    """Happy path: valid order ID should return the order."""
    # Arrange
    mock_repo = AsyncMock(spec=OrderRepository)
    mock_repo.find_by_id.return_value = Order(order_id=1, customer_id=2, status="PENDING")
    service = OrderService(repository=mock_repo)

    # Act
    result = await service.get_order(order_id=1)

    # Assert
    assert result.order_id == 1
    assert result.status == "PENDING"


@pytest.mark.asyncio
async def test_given_non_existent_id_when_get_order_then_raises_not_found() -> None:
    """Error case: unknown order ID should raise OrderNotFoundError."""
    # Arrange
    mock_repo = AsyncMock(spec=OrderRepository)
    mock_repo.find_by_id.return_value = None
    service = OrderService(repository=mock_repo)

    # Act & Assert
    with pytest.raises(OrderNotFoundError):
        await service.get_order(order_id=999)
```python

---

## 8. Code Quality Rules (Quick Reference)

| Rule | Detail |
|------|--------|
| Type hints | Every function parameter and return type must be annotated |
| Docstrings | Every public class and function — Google style |
| `Any` type | Avoid — use `unknown` patterns or `TypeVar` instead |
| Bare `except` | Never — always `except SpecificError` |
| Secrets | Never in code — use `pydantic-settings` / `.env` |
| Blocking in async | Never — use `asyncio.to_thread()` for blocking calls |
| `print()` | Use `logging` module instead |
| Magic numbers | Use named constants or Enum values |
