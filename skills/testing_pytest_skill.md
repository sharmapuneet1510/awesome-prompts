---
name: Pytest Testing Skill
version: 1.0
description: >
  Comprehensive Python testing with pytest. Covers fixtures, mocks, parameterized tests,
  test databases, async testing, naming conventions, and test organization.
applies_to: [python, pytest, fastapi, testing, async, mocking]
tags: [testing, pytest, fixtures, mocking, test-db, naming-conventions, async]
---

# Pytest Testing Skill — v1.0

---

## 1. Test File Organization & Naming

### 1.1 Project Structure

```plaintext
project/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── api/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   │
│   ├── unit/
│   │   ├── test_order_service.py
│   │   ├── test_payment_service.py
│   │   └── test_validators.py
│   │
│   ├── integration/
│   │   ├── test_order_repository.py
│   │   └── test_payment_gateway.py
│   │
│   ├── e2e/
│   │   ├── test_order_workflow.py
│   │   └── test_payment_flow.py
│   │
│   └── fixtures/
│       ├── orders.py            # Order test fixtures
│       └── payments.py          # Payment test fixtures
│
├── pytest.ini
└── requirements-dev.txt
```plaintext

### 1.2 Test Naming Convention

```python
"""
Test naming follows pattern: test_<unit>_<scenario>_<expected_result>
Also uses given_xxx_when_yyy_then_zzz pattern for clarity.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.order_service import OrderService
from app.exceptions import EntityNotFoundException, ValidationException


class TestOrderService:
    """Test cases for OrderService."""

    def test_get_order_by_id_returns_order_when_found(self):
        """
        Test: GIVEN order exists in database | WHEN getOrderById called | THEN return order.
        """
        # Arrange
        order_id = 123
        expected_order = {"id": order_id, "customer_id": 1, "status": "PENDING"}

        order_service = OrderService(mock_db={"123": expected_order})

        # Act
        result = order_service.get_order_by_id(order_id)

        # Assert
        assert result == expected_order

    def test_get_order_by_id_raises_exception_when_not_found(self):
        """
        Test: GIVEN order doesn't exist | WHEN getOrderById called | THEN raise EntityNotFoundException.
        """
        # Arrange
        order_service = OrderService(mock_db={})

        # Act & Assert
        with pytest.raises(EntityNotFoundException) as exc_info:
            order_service.get_order_by_id(999)

        assert "Order not found" in str(exc_info.value)

    def test_create_order_validates_customer_exists(self):
        """
        Test: GIVEN customer doesn't exist | WHEN createOrder called | THEN raise ValidationException.
        """
        # Arrange
        order_service = OrderService(mock_db={})
        request = {"customer_id": 999, "items": [{"product_id": 1, "qty": 2}]}

        # Act & Assert
        with pytest.raises(ValidationException):
            order_service.create_order(request)

    def test_create_order_assigns_id_and_persists(self):
        """
        Test: GIVEN valid order request | WHEN createOrder called | THEN assign ID and persist.
        """
        # Arrange
        mock_db = {}
        order_service = OrderService(mock_db=mock_db)
        request = {"customer_id": 1, "items": [{"product_id": 5, "qty": 2}]}

        # Act
        created_order = order_service.create_order(request)

        # Assert
        assert created_order["id"] is not None
        assert created_order["customer_id"] == 1
        assert len(mock_db) == 1
```plaintext

---

## 2. Fixtures — Setup & Teardown

### 2.1 Shared Fixtures in conftest.py

```python
"""
Shared fixtures for all tests.

conftest.py is automatically discovered by pytest and fixtures are available to all tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create in-memory SQLite database for entire test session.

    scope="session": Created once, reused across all tests.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """
    Create fresh database session for each test.

    scope="function": Fresh session for each test (isolation).
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def order_service(db_session):
    """Provide OrderService with mocked dependencies."""
    return OrderService(db=db_session)


@pytest.fixture
def payment_service():
    """Provide PaymentService with mocked gateway."""
    from unittest.mock import Mock
    mock_gateway = Mock()
    return PaymentService(gateway=mock_gateway)


@pytest.fixture
def sample_order():
    """Fixture: Sample order for tests."""
    return {
        "id": 1,
        "customer_id": 100,
        "status": "PENDING",
        "items": [
            {"product_id": 1, "quantity": 2, "unit_price": 25.00}
        ],
        "total_amount": 50.00
    }


@pytest.fixture
def sample_customer():
    """Fixture: Sample customer for tests."""
    return {
        "id": 100,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-555-0100"
    }


@pytest.fixture
def cleanup():
    """
    Fixture for cleanup operations.

    yield: Executes setup code before test.
    Code after yield: Executes after test (teardown).
    """
    # Setup
    print("Setting up resources...")

    yield

    # Teardown
    print("Cleaning up resources...")
```plaintext

### 2.2 Parametrized Fixtures

```python
@pytest.fixture(params=[
    {"amount": 100.00, "status": "APPROVED"},
    {"amount": 50.00, "status": "APPROVED"},
    {"amount": 999.99, "status": "PENDING_REVIEW"},
])
def payment_amounts(request):
    """
    Parametrized fixture: runs test multiple times with different values.
    """
    return request.param


def test_payment_processing_with_different_amounts(payment_amounts):
    """
    This test runs 3 times with different payment amounts.
    """
    amount = payment_amounts["amount"]
    expected_status = payment_amounts["status"]

    # Test logic
    processor = PaymentProcessor()
    result = processor.process(amount)

    assert result["status"] == expected_status
```plaintext

---

## 3. Mocking with unittest.mock

### 3.1 Mock, Patch, and Verify

```python
from unittest.mock import Mock, patch, MagicMock, call
import pytest


class TestPaymentIntegration:
    """Test payment service with mocked external gateway."""

    def test_process_payment_calls_gateway_with_correct_arguments(self):
        """
        Test: GIVEN valid payment request | WHEN processing | THEN call gateway with correct args.
        """
        # Arrange
        mock_gateway = Mock()
        mock_gateway.charge.return_value = {"transaction_id": "TXN-001"}

        payment_service = PaymentService(gateway=mock_gateway)

        # Act
        result = payment_service.process_payment(
            amount=100.00,
            card_token="tok-123"
        )

        # Assert
        assert result["transaction_id"] == "TXN-001"
        mock_gateway.charge.assert_called_once_with(amount=100.00, card_token="tok-123")

    def test_process_payment_retries_on_transient_error(self):
        """
        Test: GIVEN gateway returns transient error | WHEN retrying | THEN eventually succeed.
        """
        # Arrange
        mock_gateway = Mock()
        mock_gateway.charge.side_effect = [
            Exception("Network timeout"),
            Exception("Network timeout"),
            {"transaction_id": "TXN-002"}  # Third attempt succeeds
        ]

        payment_service = PaymentService(gateway=mock_gateway)

        # Act
        result = payment_service.process_payment_with_retry(
            amount=100.00,
            card_token="tok-123",
            max_retries=3
        )

        # Assert
        assert result["transaction_id"] == "TXN-002"
        assert mock_gateway.charge.call_count == 3

    @patch("app.services.payment_service.PaymentGateway")
    def test_payment_service_with_patched_gateway(self, mock_gateway_class):
        """
        Test: GIVEN mocked PaymentGateway class | WHEN service initializes | THEN use mock.

        @patch replaces the class in the module with a Mock.
        """
        # Arrange
        mock_instance = Mock()
        mock_instance.charge.return_value = {"transaction_id": "TXN-003"}
        mock_gateway_class.return_value = mock_instance

        # Act
        from app.services.payment_service import PaymentService
        service = PaymentService()
        result = service.charge(100.00)

        # Assert
        assert result["transaction_id"] == "TXN-003"
        mock_gateway_class.assert_called_once()
```plaintext

### 3.2 AsyncMock for Async Functions

```python
from unittest.mock import AsyncMock
import pytest


@pytest.mark.asyncio
async def test_async_payment_processing():
    """
    Test: GIVEN async payment gateway | WHEN processing | THEN return result.
    """
    # Arrange
    mock_gateway = AsyncMock()
    mock_gateway.process_async.return_value = {"status": "SUCCESS"}

    payment_service = PaymentService(gateway=mock_gateway)

    # Act
    result = await payment_service.process_payment_async(amount=100.00)

    # Assert
    assert result["status"] == "SUCCESS"
    mock_gateway.process_async.assert_called_once()
```plaintext

---

## 4. Parameterized Tests

### 4.1 @pytest.mark.parametrize

```python
import pytest


class TestOrderValidation:
    """Test order validation with multiple input combinations."""

    @pytest.mark.parametrize("total,quantity,unit_price", [
        (100.00, 1, 100.00),
        (50.00, 2, 25.00),
        (0.01, 100, 0.0001),
        (999.99, 1, 999.99),
    ])
    def test_calculate_subtotal_with_various_prices(self, total, quantity, unit_price):
        """
        Test: Calculate subtotal with multiple price combinations.

        parametrize runs this test 4 times with different values.
        """
        # Act
        result = quantity * unit_price

        # Assert
        assert abs(result - total) < 0.01  # Allow floating point rounding

    @pytest.mark.parametrize("status", [
        "PENDING",
        "CONFIRMED",
        "SHIPPED",
        "DELIVERED"
    ])
    def test_valid_order_statuses(self, status):
        """Test: Validate all valid order statuses."""
        validator = OrderValidator()
        assert validator.is_valid_status(status)

    @pytest.mark.parametrize("invalid_status", [
        "INVALID",
        "UNKNOWN",
        None,
        ""
    ])
    def test_invalid_order_statuses(self, invalid_status):
        """Test: Reject invalid order statuses."""
        validator = OrderValidator()
        with pytest.raises(ValidationException):
            validator.validate_status(invalid_status)
```plaintext

---

## 5. Testing Async Code

### 5.1 Async Test with pytest-asyncio

```python
import pytest
import asyncio


@pytest.mark.asyncio
async def test_fetch_order_async():
    """
    Test: GIVEN async order service | WHEN fetching order | THEN return order.

    @pytest.mark.asyncio marks function as async test.
    Requires pytest-asyncio plugin: pip install pytest-asyncio
    """
    # Arrange
    service = OrderService()

    # Act
    order = await service.get_order_async(order_id=123)

    # Assert
    assert order is not None
    assert order["id"] == 123


@pytest.mark.asyncio
async def test_process_multiple_orders_concurrently():
    """
    Test: GIVEN multiple orders | WHEN processing concurrently | THEN complete all.
    """
    # Arrange
    service = OrderService()
    order_ids = [1, 2, 3, 4, 5]

    # Act
    results = await asyncio.gather(
        *[service.process_order_async(oid) for oid in order_ids]
    )

    # Assert
    assert len(results) == 5
    assert all(r["status"] == "PROCESSED" for r in results)
```plaintext

---

## 6. Test Database Setup

### 6.1 PostgreSQL with pytest-postgresql

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def test_db_url():
    """
    PostgreSQL database URL for testing.

    Uses pytest-postgresql plugin: pip install pytest-postgresql
    """
    # Plugin automatically provides postgresql fixture with connection details
    return "postgresql+psycopg2://user:password@localhost/test_db"


@pytest.fixture
def db_session(test_db_url):
    """Create fresh database session for each test."""
    engine = create_engine(test_db_url, echo=False)

    # Create tables
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)


def test_order_persistence(db_session):
    """Test: GIVEN order | WHEN saving to DB | THEN retrieve from DB."""
    # Arrange
    from app.models import Order

    order = Order(
        customer_id=1,
        status="PENDING",
        total_amount=99.99
    )

    # Act
    db_session.add(order)
    db_session.commit()

    order_id = order.id
    db_session.expunge_all()

    # Assert
    retrieved = db_session.query(Order).filter_by(id=order_id).first()
    assert retrieved is not None
    assert retrieved.customer_id == 1
```plaintext

---

## 7. Pytest Configuration

### 7.1 pytest.ini

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Marker definitions
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, use external services)
    e2e: End-to-end tests (slowest)
    asyncio: Async tests
    slow: Tests that are slow to run

# Output options
addopts =
    -v                          # Verbose output
    --strict-markers            # Fail on unknown markers
    --tb=short                  # Short traceback format
    --disable-warnings          # Disable pytest warnings
    -ra                         # Report all test results

# Coverage options
testpaths = tests
norecursedirs = .git .venv build dist
asyncio_mode = auto
```plaintext

### 7.2 Run Tests with Markers

```bash
# Run only unit tests
pytest -m unit

# Run everything except slow tests
pytest -m "not slow"

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_order_service.py

# Run specific test class
pytest tests/unit/test_order_service.py::TestOrderService

# Run specific test method
pytest tests/unit/test_order_service.py::TestOrderService::test_get_order_by_id
```plaintext

---

## 8. Pytest Testing Checklist

✅ Use meaningful test function names: `test_<unit>_<scenario>_<expected>`
✅ Organize tests in unit/ and integration/ subdirectories
✅ Use conftest.py for shared fixtures
✅ Follow Arrange-Act-Assert pattern
✅ Use fixtures for database setup/teardown
✅ Mock external dependencies with unittest.mock
✅ Use AsyncMock for async function mocking
✅ Use parametrize to test multiple input combinations
✅ Mark slow/integration tests with @pytest.mark
✅ Use pytest-asyncio for async tests
✅ Use database fixtures for integration tests
✅ Keep tests independent — no shared state
✅ Use meaningful assertion messages: `assert x == y, "helpful message"`
✅ Test both happy path and error scenarios
