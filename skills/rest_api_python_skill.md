---
name: REST API Python Skill
version: 1.0
description: >
  Comprehensive REST API patterns for Python/FastAPI. Covers HTTP methods, status codes,
  Pydantic request/response validation, error handling, pagination, async endpoints.
applies_to: [python, fastapi, rest-api, http, async]
tags: [rest-api, http, fastapi, pydantic, async, api-design]
---

# REST API Python Skill — v1.0

---

## 1. FastAPI Project Structure

```plaintext
project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py              # Settings & environment
│   ├── dependencies.py        # Shared dependencies (DB session, auth)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── orders.py      # Order endpoints
│   │   │   ├── customers.py   # Customer endpoints
│   │   │   └── router.py      # Combine all v1 routers
│   │   │
│   │   └── v2/
│   │       ├── __init__.py
│   │       └── router.py
│   │
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── order.py
│   │   └── customer.py
│   │
│   ├── schemas/               # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── order.py
│   │   └── customer.py
│   │
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── order_service.py
│   │   └── customer_service.py
│   │
│   ├── repository/            # Data access
│   │   ├── __init__.py
│   │   ├── order_repo.py
│   │   └── customer_repo.py
│   │
│   └── exceptions/            # Custom exceptions
│       ├── __init__.py
│       └── handlers.py
│
├── tests/
│   ├── conftest.py
│   ├── test_orders.py
│   └── test_customers.py
│
├── .env
├── requirements.txt
└── pyproject.toml
```python

---

## 2. FastAPI App Initialization

```python
"""
Main FastAPI application factory.

Author: Your Name
Date: 2026-04-03
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.api.v1.router import api_router_v1
from app.exceptions.handlers import validation_exception_handler
from app.config import settings


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Order Management API",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # Middleware: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler
    )

    # Include routers
    app.include_router(api_router_v1, prefix="/api/v1")

    # Health check
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok", "version": "1.0.0"}

    return app


app = create_app()
```python

---

## 3. Pydantic Request/Response Schemas

```python
"""
Order request and response schemas.

Author: Your Name
Date: 2026-04-03
"""
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderItemRequest(BaseModel):
    """Request DTO for a single order item."""

    product_id: int = Field(..., gt=0, description="Product ID (positive integer)")
    quantity: int = Field(..., gt=0, le=1000, description="Order quantity (1-1000)")

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        """Validate quantity is reasonable."""
        if v < 1 or v > 1000:
            raise ValueError('Quantity must be between 1 and 1000')
        return v


class CreateOrderRequest(BaseModel):
    """Request DTO for creating a new order."""

    customer_id: int = Field(..., gt=0, description="Customer ID")
    items: List[OrderItemRequest] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Order items (1-100 items max)"
    )
    address: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Delivery address"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional order notes"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "customer_id": 123,
                "items": [
                    {"product_id": 456, "quantity": 2},
                    {"product_id": 789, "quantity": 1}
                ],
                "address": "123 Main St, Anytown, USA",
                "notes": "Please deliver before 5pm"
            }
        }


class UpdateOrderRequest(BaseModel):
    """Request DTO for updating an order."""

    address: Optional[str] = Field(None, min_length=5, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)


class OrderItemResponse(BaseModel):
    """Response DTO for a single order item."""

    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal  # quantity × unit_price


class OrderResponse(BaseModel):
    """Response DTO for a complete order."""

    id: int
    customer_id: int
    status: OrderStatus
    total_amount: Decimal
    items: List[OrderItemResponse]
    delivery_address: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True  # Enable ORM mode for SQLAlchemy models
```python

---

## 4. REST Endpoints with Async

```python
"""
Order REST API endpoints.

Author: Your Name
Date: 2026-04-03
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.schemas.order import (
    CreateOrderRequest,
    UpdateOrderRequest,
    OrderResponse,
)
from app.services.order_service import OrderService
from app.dependencies import get_db_session

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get(
    "",
    response_model=dict,
    summary="List all orders with pagination",
    description="Retrieve paginated list of orders. Supports sorting and filtering."
)
async def list_orders(
        page: int = Query(0, ge=0, description="Zero-indexed page number"),
        size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
        sort: str = Query("created_at,desc", description="Sort criteria"),
        db: Session = Depends(get_db_session),
) -> dict:
    """
    GET /api/v1/orders

    List all orders with pagination.

    **Query Parameters:**
    - page: Zero-indexed page number (default 0)
    - size: Items per page (default 20, max 100)
    - sort: Sort criteria, e.g. "created_at,desc"

    **Response:**
    ```json
    {
        "content": [...],
        "page_number": 0,
        "page_size": 20,
        "total_elements": 150,
        "total_pages": 8,
        "has_next": true,
        "has_previous": false
    }
    ```
    """
    service = OrderService(db)
    result = await service.get_orders_paginated(page, size)
    return result


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID"
)
async def get_order(
        order_id: int,
        db: Session = Depends(get_db_session),
) -> OrderResponse:
    """
    GET /api/v1/orders/{order_id}

    Retrieve a single order by ID.

    **Path Parameters:**
    - order_id: The order ID

    **Responses:**
    - 200 OK: Order details
    - 404 Not Found: Order does not exist
    """
    service = OrderService(db)
    order = await service.get_order_by_id(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order not found: {order_id}"
        )

    return OrderResponse.from_orm(order)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new order"
)
async def create_order(
        request: CreateOrderRequest,
        db: Session = Depends(get_db_session),
) -> OrderResponse:
    """
    POST /api/v1/orders

    Create a new order.

    **Request Body:**
    ```json
    {
        "customer_id": 123,
        "items": [
            {"product_id": 456, "quantity": 2}
        ],
        "address": "123 Main St",
        "notes": "Optional notes"
    }
    ```

    **Responses:**
    - 201 Created: Order created successfully
    - 400 Bad Request: Validation failed
    - 404 Not Found: Customer not found
    """
    try:
        service = OrderService(db)
        order = await service.create_order(request)
        return OrderResponse.from_orm(order)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update order"
)
async def update_order(
        order_id: int,
        request: UpdateOrderRequest,
        db: Session = Depends(get_db_session),
) -> OrderResponse:
    """
    PATCH /api/v1/orders/{order_id}

    Partially update an order. Only provided fields are updated.

    **Path Parameters:**
    - order_id: The order ID

    **Request Body:**
    ```json
    {
        "address": "New address",
        "notes": "Updated notes"
    }
    ```

    **Responses:**
    - 200 OK: Updated order
    - 404 Not Found: Order does not exist
    """
    service = OrderService(db)
    order = await service.update_order(order_id, request)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order not found: {order_id}"
        )

    return OrderResponse.from_orm(order)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel order"
)
async def cancel_order(
        order_id: int,
        db: Session = Depends(get_db_session),
) -> None:
    """
    DELETE /api/v1/orders/{order_id}

    Cancel an order.

    **Path Parameters:**
    - order_id: The order ID

    **Responses:**
    - 204 No Content: Order cancelled
    - 404 Not Found: Order does not exist
    """
    service = OrderService(db)
    success = await service.cancel_order(order_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order not found: {order_id}"
        )
```python

---

## 5. Error Response Handler

```python
"""
Global exception handlers.

Author: Your Name
Date: 2026-04-03
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Unified error response."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        path: str,
        field_errors: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.timestamp = datetime.utcnow().isoformat()
        self.path = path
        self.field_errors = field_errors or {}

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON response."""
        return {
            "code": self.code,
            "message": self.message,
            "status": self.status_code,
            "timestamp": self.timestamp,
            "path": self.path,
            "fieldErrors": self.field_errors,
        }


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Converts FastAPI validation errors to consistent ErrorResponse format.
    """
    field_errors = {}

    for error in exc.errors():
        field_name = ".".join(str(loc) for loc in error["loc"][1:])
        message = error["msg"]

        if field_name not in field_errors:
            field_errors[field_name] = []

        field_errors[field_name].append(message)

    error_response = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=400,
        path=str(request.url.path),
        field_errors=field_errors,
    )

    return JSONResponse(
        status_code=400,
        content=error_response.to_dict(),
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general HTTP exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    error_response = ErrorResponse(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        status_code=500,
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=500,
        content=error_response.to_dict(),
    )
```python

---

## 6. Service Layer with Dependency Injection

```python
"""
Order service with business logic.

Author: Your Name
Date: 2026-04-03
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.order import Order
from app.schemas.order import CreateOrderRequest, UpdateOrderRequest


class OrderService:
    """Order business logic."""

    def __init__(self, db: Session):
        """
        Initialize with database session.

        Args:
            db: SQLAlchemy session for database access.
        """
        self.db = db

    async def get_orders_paginated(self, page: int, size: int) -> dict:
        """
        Retrieve paginated orders.

        Args:
            page: Zero-indexed page number.
            size: Items per page.

        Returns:
            Dictionary with content, pagination metadata.
        """
        query = select(Order).offset(page * size).limit(size)
        total_count_query = select(Order)

        orders = self.db.execute(query).scalars().all()
        total_count = self.db.execute(total_count_query).scalar()

        return {
            "content": orders,
            "page_number": page,
            "page_size": size,
            "total_elements": total_count,
            "total_pages": (total_count + size - 1) // size,
            "has_next": page < (total_count // size),
            "has_previous": page > 0,
        }

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Retrieve order by ID.

        Args:
            order_id: The order ID.

        Returns:
            Order object or None if not found.
        """
        return self.db.execute(
            select(Order).where(Order.id == order_id)
        ).scalar_one_or_none()

    async def create_order(self, request: CreateOrderRequest) -> Order:
        """
        Create a new order.

        Args:
            request: Order creation request.

        Returns:
            Created Order object.

        Raises:
            ValueError: If validation fails.
        """
        # Validate customer exists
        customer = self.db.execute(
            select(Order).where(Order.customer_id == request.customer_id)
        ).scalar_one_or_none()

        if not customer:
            raise ValueError(f"Customer not found: {request.customer_id}")

        # Create order
        order = Order(
            customer_id=request.customer_id,
            delivery_address=request.address,
            notes=request.notes,
        )

        self.db.add(order)
        self.db.flush()

        # Add items (simplified)
        for item_request in request.items:
            # Add order items...
            pass

        self.db.commit()
        self.db.refresh(order)

        return order

    async def update_order(
        self,
        order_id: int,
        request: UpdateOrderRequest
    ) -> Optional[Order]:
        """
        Update an order (partial update).

        Args:
            order_id: The order ID.
            request: Update request.

        Returns:
            Updated Order or None if not found.
        """
        order = await self.get_order_by_id(order_id)

        if not order:
            return None

        if request.address:
            order.delivery_address = request.address
        if request.notes is not None:
            order.notes = request.notes

        self.db.commit()
        self.db.refresh(order)

        return order

    async def cancel_order(self, order_id: int) -> bool:
        """
        Cancel an order.

        Args:
            order_id: The order ID.

        Returns:
            True if cancelled, False if not found.
        """
        order = await self.get_order_by_id(order_id)

        if not order:
            return False

        order.status = "CANCELLED"
        self.db.commit()

        return True
```python

---

## 7. REST Checklist for Python/FastAPI

✅ Use Pydantic models for request/response validation
✅ Return appropriate HTTP status codes (200, 201, 204, 400, 404, 500)
✅ Use async/await for all endpoints (no blocking)
✅ Implement global exception handlers for consistency
✅ Add field-level validation in request schemas
✅ Document endpoints with docstrings and OpenAPI examples
✅ Use dependency injection (Depends) for services and sessions
✅ Version API paths from the start (/api/v1/...)
✅ Return consistent error responses with error codes
✅ Implement pagination for list endpoints
