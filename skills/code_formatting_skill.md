---
name: Code Formatting & Style Skill
version: 1.0
description: >
  Universal code formatting standards across Java, Python, and JavaScript/TypeScript.
  Covers indentation, line length, whitespace, naming conventions, alignment, and tooling.
applies_to: [java, python, javascript, typescript, code-quality, formatting]
tags: [formatting, style, conventions, tools, linting, prettier, black, google-style]
---

# Code Formatting & Style Skill — v1.0

---

## 1. Universal Formatting Rules

### 1.1 Indentation & Spacing

| Rule | Standard | Example |
|------|----------|---------|
| **Indentation** | 4 spaces (never tabs) | `    public void method() {}` |
| **Line length** | Max 100-120 chars | Break long lines at operators |
| **Blank lines** | 1 between methods | `method1()\n\nmethod2()` |
| **No trailing spaces** | Remove all | End of line must be clean |
| **File ending** | Single newline | `code...\n` (one at end) |

### 1.2 Spacing Rules

```java
// ✓ GOOD: Spaces around operators
int result = a + b * c;
if (x == 5) { }

// ✗ AVOID: No spaces around operators
int result = a+b*c;
if (x==5) { }

// ✓ GOOD: Space after comma
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// ✗ AVOID: No space after comma
List<String> names = Arrays.asList("Alice","Bob","Charlie");

// ✓ GOOD: Space after keywords
if (condition) { }
for (int i = 0; i < 10; i++) { }

// ✗ AVOID: No space after keywords
if(condition) { }
for(int i=0; i<10; i++) { }

// ✓ GOOD: No space before parentheses in method calls
method(arg1, arg2);

// ✗ AVOID: Space before parentheses
method (arg1, arg2);
```plaintext

---

## 2. Language-Specific Formatting

### 2.1 Java Formatting

**Use Google Java Style Guide:**

```java
// Package declaration (no blank lines)
package com.example.orders;

// Imports (alphabetically sorted)
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import com.example.models.Order;
import com.example.services.OrderService;

/**
 * Javadoc comment for class.
 * - Use /** */ for public class/method documentation
 * - Use // for inline comments
 * - Use /* */ for block comments
 */
public class OrderProcessor {

    // Constants: UPPER_SNAKE_CASE
    private static final int MAX_RETRIES = 3;
    private static final String DEFAULT_CURRENCY = "USD";

    // Instance fields: lowerCamelCase
    private final OrderService orderService;
    private final PaymentGateway paymentGateway;

    /**
     * Constructor with proper indentation.
     *
     * @param orderService the order service
     * @param paymentGateway the payment gateway
     */
    public OrderProcessor(OrderService orderService, PaymentGateway paymentGateway) {
        this.orderService = orderService;
        this.paymentGateway = paymentGateway;
    }

    /**
     * Method with proper formatting:
     * - 4 space indentation
     * - Max 20 lines per method
     * - Clear variable names
     *
     * @param orderId the order ID
     * @return processing result
     */
    public Result processOrder(Long orderId) {
        // Variable declaration: lowerCamelCase
        Optional<Order> orderOptional = orderService.findById(orderId);

        if (orderOptional.isEmpty()) {
            return Result.notFound();
        }

        Order order = orderOptional.get();

        // Multi-line method call: indent continuation
        PaymentResult paymentResult = paymentGateway.processPayment(
                order.getId(),
                order.getTotalAmount(),
                order.getCurrency()
        );

        return paymentResult.isSuccessful()
                ? Result.success(order)
                : Result.failure("Payment declined");
    }

    // Closing brace on own line for class
}
```plaintext

**Java Formatter Tools:**
- **Spotless** (Gradle/Maven plugin)
- **google-java-format** (CLI tool)

```xml
<!-- pom.xml -->
<plugin>
    <groupId>com.diffplug.spotless</groupId>
    <artifactId>spotless-maven-plugin</artifactId>
    <version>2.43.0</version>
    <configuration>
        <java>
            <googleJavaFormat>
                <version>1.19.2</version>
            </googleJavaFormat>
        </java>
    </configuration>
</plugin>
```plaintext

### 2.2 Python Formatting

**Use PEP 8 + Black:**

```python
"""Module docstring.

Multi-line docstring with description of module purpose.
"""

from typing import Optional, List
from datetime import datetime

import requests

from app.models import Order
from app.services import OrderService

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_CURRENCY = "USD"


class OrderProcessor:
    """Process orders with payment and fulfillment.

    Args:
        order_service: The order service.
        payment_gateway: The payment gateway.
    """

    def __init__(
        self,
        order_service: OrderService,
        payment_gateway,
    ) -> None:
        """Initialize OrderProcessor."""
        self.order_service = order_service
        self.payment_gateway = payment_gateway

    def process_order(self, order_id: int) -> dict:
        """
        Process an order with payment and fulfillment.

        Formatted with Black (line length 88 chars).

        Args:
            order_id: The order ID to process.

        Returns:
            Processing result dict.
        """
        # Variable declaration: snake_case
        order = self.order_service.find_by_id(order_id)

        if not order:
            return {"status": "NOT_FOUND"}

        # Multi-line method call: align continuation
        payment_result = self.payment_gateway.process_payment(
            order_id=order.id,
            amount=order.total_amount,
            currency=order.currency,
        )

        # Use f-strings for string formatting
        if payment_result["success"]:
            message = f"Order {order.id} processed successfully"
        else:
            message = f"Payment failed: {payment_result['error']}"

        return {"status": "SUCCESS", "message": message}
```plaintext

**Python Formatter Tools:**
- **Black** (opinionated code formatter)
- **isort** (import sorting)
- **pylint** / **flake8** (linting)

```bash
# Install tools
pip install black isort pylint flake8

# Format with Black (line length 88)
black --line-length 88 app/

# Sort imports
isort app/

# Lint code
pylint app/
flake8 app/
```plaintext

**pyproject.toml:**
```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 88

[tool.pylint."messages control"]
disable = ["C0330", "C0326"]  # Formatting handled by Black
```plaintext

### 2.3 JavaScript/TypeScript Formatting

**Use Prettier + ESLint:**

```typescript
/**
 * Order processor module.
 *
 * Handles order processing with payment and fulfillment.
 */

import { OrderService } from './services/OrderService';
import { PaymentGateway } from './gateways/PaymentGateway';
import type { Order, ProcessResult } from './types';

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;
const DEFAULT_CURRENCY = 'USD';

/**
 * Process orders with payment and fulfillment.
 */
export class OrderProcessor {
  private orderService: OrderService;

  private paymentGateway: PaymentGateway;

  constructor(orderService: OrderService, paymentGateway: PaymentGateway) {
    this.orderService = orderService;
    this.paymentGateway = paymentGateway;
  }

  /**
   * Process an order.
   *
   * Formatted with Prettier (line length 100).
   *
   * @param orderId - The order ID to process
   * @returns Processing result
   */
  async processOrder(orderId: number): Promise<ProcessResult> {
    // Variable declaration: lowerCamelCase
    const order = await this.orderService.findById(orderId);

    if (!order) {
      return { status: 'NOT_FOUND' };
    }

    // Multi-line method call: Prettier handles indentation
    const paymentResult = await this.paymentGateway.processPayment({
      orderId: order.id,
      amount: order.totalAmount,
      currency: order.currency,
    });

    // Template literals for string interpolation
    const message = paymentResult.success
      ? `Order ${order.id} processed successfully`
      : `Payment failed: ${paymentResult.error}`;

    return { status: 'SUCCESS', message };
  }
}
```plaintext

**Prettier Configuration (.prettierrc):**
```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always"
}
```plaintext

**ESLint Configuration (.eslintrc.json):**
```json
{
  "extends": ["eslint:recommended", "prettier"],
  "rules": {
    "indent": ["error", 2],
    "linebreak-style": ["error", "unix"],
    "quotes": ["error", "single"],
    "semi": ["error", "always"],
    "no-trailing-spaces": "error",
    "eol-last": ["error", "always"]
  }
}
```plaintext

---

## 3. Alignment & Readability

### 3.1 Method Signatures

```java
// ✓ GOOD: Break at logical points
public OrderProcessResult processOrder(
        Long orderId,
        PaymentRequest paymentRequest,
        DeliveryAddress deliveryAddress) {
    // method body
}

// ✗ AVOID: Keep parameters on same line if fits
public OrderProcessResult processOrder(Long orderId, PaymentRequest paymentRequest, DeliveryAddress deliveryAddress) {
    // method body
}
```plaintext

### 3.2 Long Expressions

```java
// ✓ GOOD: Break at operators, indent continuation
boolean isEligibleForDiscount =
        customer.isActive()
        && customer.getTotalSpent() > 1000
        && order.getOrderDate().isAfter(cutoffDate)
        && !customer.hasRecentRefund();

// ✓ GOOD: Chain method calls vertically
List<Order> recentOrders = orderRepository.findAll()
        .stream()
        .filter(o -> o.getStatus() == OrderStatus.COMPLETED)
        .filter(o -> o.getCreatedAt().isAfter(cutoffDate))
        .map(this::enrichOrderData)
        .collect(Collectors.toList());
```plaintext

---

## 4. Naming Conventions Summary

| Type | Convention | Example |
|------|-----------|---------|
| **Class** | PascalCase | `OrderProcessor`, `PaymentGateway` |
| **Method/Function** | lowerCamelCase | `processOrder()`, `validatePayment()` |
| **Variable** | lowerCamelCase | `totalAmount`, `customerName` |
| **Constant** | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_CURRENCY` |
| **Package/Module** | lowercase (no caps) | `com.example.orders` |
| **Private method** | lowerCamelCase with prefix | `_validateInput()` (Python) |

---

## 5. Auto-Formatting Setup

### 5.1 Pre-commit Hook Example

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Format Java files
./mvnw spotless:apply

# Format Python files
black app/ && isort app/

# Format JS/TS files
npx prettier --write src/

# Stage formatted files
git add -A

exit 0
```plaintext

### 5.2 GitHub Actions Workflow

```yaml
# .github/workflows/format-check.yml
name: Code Format Check

on: [push, pull_request]

jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check Java formatting
        run: ./mvnw spotless:check

      - name: Check Python formatting
        run: |
          pip install black isort
          black --check app/
          isort --check-only app/

      - name: Check JS/TS formatting
        run: |
          npm install
          npx prettier --check src/
```plaintext

---

## 6. Code Formatting Checklist

✅ Use 4 spaces for indentation (never tabs)
✅ Max 100-120 characters per line
✅ Add spaces around operators (a + b, not a+b)
✅ Add spaces after commas
✅ Single newline at end of file
✅ No trailing whitespace
✅ Use meaningful variable/method names (lowerCamelCase)
✅ Use UPPER_SNAKE_CASE for constants
✅ Use PascalCase for classes
✅ Follow language-specific style guide (Google, PEP 8, Prettier)
✅ Automate formatting with tools (Spotless, Black, Prettier)
✅ Run formatter in pre-commit hooks
✅ Enforce formatting in CI/CD
✅ Never manually override auto-formatter decisions
