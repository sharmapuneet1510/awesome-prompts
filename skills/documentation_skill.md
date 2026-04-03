---
name: Code Documentation & Comments Skill
version: 1.0
description: >
  Comprehensive documentation standards across Java, Python, and JavaScript.
  Covers Javadoc, docstrings, inline comments, method descriptions, author/date headers.
applies_to: [java, python, javascript, typescript, documentation, code-quality]
tags: [documentation, comments, javadoc, docstrings, jsdoc, author-date, method-docs]
---

# Code Documentation & Comments Skill — v1.0

---

## 1. File Headers with Author & Date

### 1.1 Java File Header

```java
/**
 * Order processing service for managing order lifecycle.
 *
 * <p>Handles order creation, validation, payment processing, and fulfillment.
 * This service is the main entry point for order operations.</p>
 *
 * <p><b>Author:</b> John Doe</p>
 * <p><b>Date:</b> 2026-04-03</p>
 * <p><b>Version:</b> 2.0</p>
 * <p><b>Last Modified:</b> 2026-04-03 by John Doe</p>
 *
 * @author John Doe (john@example.com)
 * @version 2.0
 * @since 1.0
 */
package com.example.orders.services;

import java.time.LocalDateTime;
import java.util.List;

public class OrderService {
    // Class content
}
```plaintext

### 1.2 Python File Header

```python
"""
Order processing service for managing order lifecycle.

Handles order creation, validation, payment processing, and fulfillment.
This service is the main entry point for order operations.

Author: John Doe (john@example.com)
Date: 2026-04-03
Version: 2.0
Last Modified: 2026-04-03 by John Doe

Attributes:
    logger: Configured logger instance for this module.
"""

__author__ = "John Doe"
__email__ = "john@example.com"
__date__ = "2026-04-03"
__version__ = "2.0"

import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class OrderService:
    """Order processing service."""
```plaintext

### 1.3 JavaScript/TypeScript File Header

```typescript
/**
 * Order processing service for managing order lifecycle.
 *
 * Handles order creation, validation, payment processing, and fulfillment.
 * This service is the main entry point for order operations.
 *
 * @author John Doe <john@example.com>
 * @version 2.0
 * @since 1.0
 * @date 2026-04-03
 * @lastModified 2026-04-03 by John Doe
 */

import { OrderRepository } from './repositories/OrderRepository';
import { PaymentGateway } from './gateways/PaymentGateway';

export class OrderService {
  // Class content
}
```plaintext

---

## 2. Javadoc Standard (Java)

### 2.1 Class Documentation

```java
/**
 * Manages the complete lifecycle of customer orders.
 *
 * <p>This service provides methods to create, retrieve, update, and cancel orders.
 * It coordinates with multiple dependent services including {@link PaymentGateway},
 * {@link InventoryService}, and {@link EmailService}.</p>
 *
 * <p><b>Thread Safety:</b> This class is thread-safe due to immutable dependencies.</p>
 *
 * <p><b>Usage Example:</b></p>
 * <pre><code>
 * OrderService service = new OrderService(repository, gateway, inventory);
 * Order order = service.createOrder(request);
 * </code></pre>
 *
 * @author John Doe (john@example.com)
 * @version 2.0
 * @since 1.0
 * @see PaymentGateway
 * @see OrderRepository
 */
public class OrderService {
    // Class content
}
```plaintext

### 2.2 Method Documentation

```java
/**
 * Processes an order by validating, reserving inventory, and charging payment.
 *
 * <p>This method performs the following steps:</p>
 * <ol>
 *   <li>Validates the order against business rules</li>
 *   <li>Reserves inventory for all items</li>
 *   <li>Processes payment through the gateway</li>
 *   <li>Confirms the order in the database</li>
 * </ol>
 *
 * <p>If any step fails, previously completed steps are compensated (rolled back).</p>
 *
 * @param orderId the ID of the order to process
 * @return the processing result with status and transaction ID
 *
 * @throws EntityNotFoundException if the order does not exist
 * @throws ValidationException if the order fails validation
 * @throws PaymentGatewayException if payment processing fails
 * @throws InventoryException if inventory reservation fails
 *
 * @see #validateOrder(Long)
 * @see #reserveInventory(Order)
 * @see PaymentGateway#processPayment(Order)
 */
public ProcessResult processOrder(Long orderId)
        throws EntityNotFoundException, ValidationException {
    // Implementation
}

/**
 * Retrieves an order by its unique identifier.
 *
 * @param orderId the order ID (must be positive)
 * @return an Optional containing the order, or empty if not found
 *
 * @throws IllegalArgumentException if orderId is null or non-positive
 *
 * @since 1.0
 */
public Optional<Order> getOrderById(Long orderId) {
    // Implementation
}
```plaintext

### 2.3 Field Documentation

```java
/**
 * The customer who placed this order.
 *
 * <p>Must not be null. Set during order creation and immutable thereafter.</p>
 */
@NotNull(message = "customerId is required")
private final Long customerId;

/**
 * Total order amount including taxes and shipping.
 *
 * <p>Calculated field: sum of all item subtotals + shipping + taxes - discounts.</p>
 */
@DecimalMin(value = "0.01")
private final BigDecimal totalAmount;

/**
 * Current status of the order.
 *
 * <p>Valid transitions: PENDING → CONFIRMED → SHIPPED → DELIVERED or CANCELLED.</p>
 *
 * @see OrderStatus
 */
@Enumerated(EnumType.STRING)
private OrderStatus status;
```plaintext

---

## 3. Docstrings Standard (Python)

### 3.1 Google Style Docstrings

```python
def process_order(order_id: int) -> ProcessResult:
    """
    Process an order by validating, reserving inventory, and charging payment.

    This function performs the following steps:
        1. Validates the order against business rules
        2. Reserves inventory for all items
        3. Processes payment through the gateway
        4. Confirms the order in the database

    If any step fails, previously completed steps are compensated (rolled back).

    Args:
        order_id: The ID of the order to process (must be positive).

    Returns:
        ProcessResult: A result object containing:
            - status: 'SUCCESS', 'FAILURE', or 'PENDING'
            - transaction_id: The payment transaction ID (if successful)
            - error_message: Error description (if failed)

    Raises:
        EntityNotFoundException: If the order does not exist.
        ValidationException: If the order fails validation.
        PaymentGatewayException: If payment processing fails.
        InventoryException: If inventory reservation fails.

    Example:
        >>> service = OrderService(repo, gateway, inventory)
        >>> result = service.process_order(123)
        >>> if result.status == 'SUCCESS':
        ...     print(f"Order processed: {result.transaction_id}")

    Note:
        This is an async-friendly operation. Use await for async calls.

    See Also:
        validate_order: Performs order validation
        reserve_inventory: Reserves stock
    """
    # Implementation
```plaintext

### 3.2 Attribute Documentation

```python
class Order:
    """
    Represents a customer order.

    Attributes:
        id: The unique order identifier (assigned by database).
        customer_id: The ID of the customer who placed this order (positive int).
        status: Current order status (see OrderStatus enum).
            Valid transitions: PENDING → CONFIRMED → SHIPPED → DELIVERED
        total_amount: Total order amount including taxes and shipping (Decimal).
            Calculated as: sum(item.subtotal) + shipping + taxes - discounts
        items: List of OrderItem objects representing ordered products.
        created_at: ISO 8601 timestamp when order was created (read-only).
        updated_at: ISO 8601 timestamp of last modification.
    """

    def __init__(
        self,
        customer_id: int,
        status: str = "PENDING",
        total_amount: Decimal = Decimal("0.00"),
    ) -> None:
        """
        Initialize an Order.

        Args:
            customer_id: The customer ID (must be positive).
            status: Initial order status. Defaults to "PENDING".
            total_amount: Initial order amount. Defaults to 0.00.

        Raises:
            ValueError: If customer_id is not positive.
            ValueError: If total_amount is negative.
        """
        if customer_id <= 0:
            raise ValueError("customer_id must be positive")

        self.customer_id = customer_id
        self.status = status
        self.total_amount = total_amount
```plaintext

---

## 4. JSDoc Standard (JavaScript/TypeScript)

### 4.1 Function Documentation

```typescript
/**
 * Process an order by validating, reserving inventory, and charging payment.
 *
 * This function performs the following steps:
 * 1. Validates the order against business rules
 * 2. Reserves inventory for all items
 * 3. Processes payment through the gateway
 * 4. Confirms the order in the database
 *
 * If any step fails, previously completed steps are compensated (rolled back).
 *
 * @async
 * @param {number} orderId - The ID of the order to process (must be positive)
 * @returns {Promise<ProcessResult>} A promise resolving to:
 *   - status: 'SUCCESS', 'FAILURE', or 'PENDING'
 *   - transactionId: The payment transaction ID (if successful)
 *   - errorMessage: Error description (if failed)
 *
 * @throws {EntityNotFoundException} If the order does not exist
 * @throws {ValidationException} If the order fails validation
 * @throws {PaymentGatewayException} If payment processing fails
 * @throws {InventoryException} If inventory reservation fails
 *
 * @example
 * const service = new OrderService(repo, gateway, inventory);
 * const result = await service.processOrder(123);
 * if (result.status === 'SUCCESS') {
 *   console.log(`Order processed: ${result.transactionId}`);
 * }
 *
 * @see {@link validateOrder}
 * @see {@link reserveInventory}
 * @author John Doe <john@example.com>
 * @since 1.0
 */
async function processOrder(orderId: number): Promise<ProcessResult> {
    // Implementation
}
```plaintext

### 4.2 Class & Property Documentation

```typescript
/**
 * Manages the complete lifecycle of customer orders.
 *
 * This class provides methods to create, retrieve, update, and cancel orders.
 * It coordinates with multiple dependent services.
 *
 * @class
 * @example
 * const service = new OrderService(repo, gateway, inventory);
 * const order = await service.createOrder(request);
 *
 * @author John Doe <john@example.com>
 * @version 2.0
 */
export class OrderService {
    /**
     * The order repository for database operations.
     *
     * @type {OrderRepository}
     * @readonly
     */
    private readonly repository: OrderRepository;

    /**
     * External payment gateway for processing payments.
     *
     * @type {PaymentGateway}
     * @readonly
     */
    private readonly gateway: PaymentGateway;

    /**
     * Get an order by its ID.
     *
     * @param {number} orderId - The order ID (positive integer)
     * @returns {Promise<Order | null>} The order, or null if not found
     * @throws {IllegalArgumentException} If orderId is not positive
     *
     * @example
     * const order = await service.getOrderById(123);
     */
    async getOrderById(orderId: number): Promise<Order | null> {
        // Implementation
    }
}
```plaintext

---

## 5. Inline Comments

### 5.1 When to Use Comments

```java
// ✓ GOOD: Explain WHY, not WHAT

/**
 * Sort by creation date descending.
 * Customers prefer to see newest orders first, not oldest.
 */
List<Order> orders = repository.findAll().stream()
        .sorted(Comparator.comparing(Order::getCreatedAt).reversed())
        .collect(Collectors.toList());

// ✗ AVOID: Comment states obvious fact

// Loop through all orders
for (Order order : orders) {
    processOrder(order);  // Process the order
}

// ✓ GOOD: Document non-obvious algorithm

// Fisher-Yates shuffle: randomize order in O(n) time
// See: https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle
for (int i = items.size() - 1; i > 0; i--) {
    int j = random.nextInt(i + 1);
    Collections.swap(items, i, j);
}

// ✓ GOOD: Explain workarounds and gotchas

// NOTE: This must be a separate query because loading related orders
// in the main query triggers N+1 problem with Hibernate lazy loading.
// We use selectinload to fetch eagerly.
Order order = orderRepository.findByIdWithItems(orderId);

// HACK: PaymentGateway sometimes returns 500 even on success.
// Retry once after 500ms to work around their rate limiting.
// TODO: Contact PaymentGateway team to fix this behavior.
```plaintext

### 5.2 Comment Format

```java
// Single-line comment should start with space
// This is a single-line comment explaining the next line

/*
 * Multi-line comment format.
 * Each line starts with * aligned.
 * Ends with closing on separate line.
 */

/**
 * Javadoc comment.
 * Must be used for public class/method/field.
 * Includes @param, @return, @throws tags.
 */
```plaintext

---

## 6. Documentation in IDEs

### 6.1 IDE Shortcuts

| IDE | Generate Javadoc | Keyboard |
|-----|------------------|----------|
| **IntelliJ IDEA** | Place cursor on class/method | Alt+Cmd+J (Mac) / Alt+Ctrl+J (Win) |
| **VS Code** | Install "Better Comments" | Type `/**` + Enter |
| **Eclipse** | Generate Javadoc | Alt+Shift+J |

---

## 7. Documentation Checklist

✅ Add file header with author, date, version
✅ Document all public classes with purpose and usage
✅ Document all public methods with @param, @return, @throws
✅ Document all public fields with their purpose
✅ Include code examples in documentation
✅ Explain WHY, not WHAT (comments should add value)
✅ Use Javadoc/docstrings/JSDoc consistently
✅ Keep documentation up-to-date with code changes
✅ Use meaningful variable names (reduces need for comments)
✅ Document non-obvious algorithms with references
✅ Include @author tags with contact info
✅ Include @since and @version tags for tracking
✅ Document exceptions that methods throw
✅ Add @deprecated tags for obsolete code
✅ Cross-reference related methods with @see tags
