---
name: Error Handling & Resilience Skill
version: 1.0
description: >
  Comprehensive error handling patterns across Java, Python, and JavaScript/React.
  Covers custom exceptions, try-catch patterns, logging, error recovery, and resilience.
applies_to: [java, python, javascript, react, error-handling, exceptions]
tags: [error-handling, exceptions, logging, resilience, patterns]
---

# Error Handling & Resilience Skill — v1.0

---

## 1. Exception Design Principles

### 1.1 Custom Exception Hierarchy

```java
// Java: Create custom exceptions with clear semantics

/**
 * Base exception for all domain errors in the order system.
 *
 * <p>All domain-specific exceptions inherit from this, making it easy to catch
 * all business errors while letting system errors propagate.</p>
 */
public abstract class DomainException extends RuntimeException {

    private final String errorCode;

    public DomainException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public DomainException(String errorCode, String message, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }

    public String getErrorCode() {
        return errorCode;
    }
}

/**
 * Thrown when a required entity is not found.
 */
public class EntityNotFoundException extends DomainException {
    public EntityNotFoundException(String entityType, Object id) {
        super("ENTITY_NOT_FOUND",
              String.format("%s not found: %s", entityType, id));
    }
}

/**
 * Thrown when business rule validation fails.
 */
public class ValidationException extends DomainException {
    public ValidationException(String message) {
        super("VALIDATION_ERROR", message);
    }
}

/**
 * Thrown when operation cannot proceed due to resource constraints.
 */
public class InsufficientResourcesException extends DomainException {
    public InsufficientResourcesException(String resource) {
        super("INSUFFICIENT_RESOURCES",
              String.format("Insufficient %s available", resource));
    }
}

/**
 * Thrown when operation conflicts with existing state.
 */
public class ConflictException extends DomainException {
    public ConflictException(String message) {
        super("CONFLICT", message);
    }
}
```plaintext

```python
# Python: Create custom exception hierarchy

class DomainException(Exception):
    """
    Base exception for all domain errors.

    All business logic exceptions inherit from this.
    """

    def __init__(self, error_code: str, message: str, details: dict | None = None):
        """
        Initialize domain exception.

        Args:
            error_code: Machine-readable error code (e.g., "ENTITY_NOT_FOUND")
            message: Human-readable error message
            details: Optional additional error details (dict)
        """
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class EntityNotFoundException(DomainException):
    """Raised when a required entity is not found."""

    def __init__(self, entity_type: str, entity_id):
        super().__init__(
            error_code="ENTITY_NOT_FOUND",
            message=f"{entity_type} not found: {entity_id}"
        )


class ValidationException(DomainException):
    """Raised when business rule validation fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            error_code="VALIDATION_ERROR",
            message=message,
            details=details
        )


class InsufficientResourcesException(DomainException):
    """Raised when operation cannot proceed due to resource constraints."""

    def __init__(self, resource: str):
        super().__init__(
            error_code="INSUFFICIENT_RESOURCES",
            message=f"Insufficient {resource} available"
        )
```plaintext

---

## 2. Try-Catch Patterns

### 2.1 Java — Specific Exceptions First

```java
/**
 * Process an order with comprehensive error handling.
 *
 * @param orderId the order ID to process
 * @return processing result
 * @throws DomainException if business validation fails
 */
public OrderProcessResult processOrder(Long orderId) {
    try {
        // 1. Try specific, recoverable exceptions first
        Order order = findOrderById(orderId);  // throws EntityNotFoundException

        if (order.getStatus() == OrderStatus.CANCELLED) {
            throw new ValidationException("Cannot process cancelled order");
        }

        // 2. Perform business operation
        BigDecimal totalAmount = calculateTotal(order);

        if (totalAmount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new ValidationException("Order total must be positive");
        }

        // 3. External service call with retry
        PaymentResult paymentResult = retryPaymentService(() ->
                paymentGateway.processPayment(order.getPaymentToken(), totalAmount)
        );

        if (!paymentResult.isSuccessful()) {
            throw new ConflictException("Payment processing failed: " +
                    paymentResult.getErrorMessage());
        }

        // 4. Persist changes
        order.setStatus(OrderStatus.CONFIRMED);
        orderRepository.save(order);

        return OrderProcessResult.success(order);

    } catch (EntityNotFoundException e) {
        // Handle not found — client error
        log.warn("Order not found: {}", orderId);
        return OrderProcessResult.notFound(orderId);

    } catch (ValidationException e) {
        // Handle validation errors — client error
        log.warn("Validation failed: {}", e.getMessage());
        return OrderProcessResult.validationFailed(e.getMessage());

    } catch (ConflictException e) {
        // Handle conflict — retry-able error
        log.warn("Conflict detected: {}", e.getMessage());
        return OrderProcessResult.conflict(e.getMessage());

    } catch (IOException e) {
        // Handle I/O errors — infrastructure issue
        log.error("I/O error during order processing", e);
        return OrderProcessResult.systemError("Communication error occurred");

    } catch (Exception e) {
        // Catch-all for unexpected errors
        log.error("Unexpected error processing order {}", orderId, e);
        return OrderProcessResult.systemError("Unexpected error occurred");

    } finally {
        // Cleanup resources (connections, file handles, etc.)
        closeAnyOpenResources();
    }
}
```plaintext

### 2.2 Python — Try-Except-Else Pattern

```python
async def process_order(order_id: int) -> OrderProcessResult:
    """
    Process an order with comprehensive error handling.

    Args:
        order_id: The order ID to process.

    Returns:
        OrderProcessResult indicating success or failure.
    """
    try:
        # Try to retrieve and validate order
        order = await order_service.get_order_by_id(order_id)

        if not order:
            raise EntityNotFoundException("Order", order_id)

        if order.status == OrderStatus.CANCELLED:
            raise ValidationException(
                "Cannot process cancelled order",
                details={"order_id": order_id, "status": order.status}
            )

        # Validate order total
        total_amount = calculate_total(order)

        if total_amount <= 0:
            raise ValidationException(
                "Order total must be positive",
                details={"total": total_amount}
            )

        # Process payment with retries
        payment_result = await retry_operation(
            operation=lambda: payment_gateway.process_payment(
                order.payment_token,
                total_amount
            ),
            max_retries=3,
            backoff_factor=2
        )

        if not payment_result.is_successful:
            raise ConflictException(
                f"Payment processing failed: {payment_result.error_message}"
            )

    except EntityNotFoundException as e:
        logger.warning("Order not found: %s", e.message)
        return OrderProcessResult.not_found(order_id)

    except ValidationException as e:
        logger.warning("Validation failed: %s", e.message)
        return OrderProcessResult.validation_failed(
            message=e.message,
            details=e.details
        )

    except ConflictException as e:
        logger.warning("Conflict detected: %s", e.message)
        return OrderProcessResult.conflict(e.message)

    except (IOError, ConnectionError) as e:
        logger.error("I/O error during order processing", exc_info=True)
        return OrderProcessResult.system_error("Communication error occurred")

    except Exception as e:
        logger.error("Unexpected error processing order %s", order_id, exc_info=True)
        return OrderProcessResult.system_error("Unexpected error occurred")

    else:
        # Executes only if no exception was raised
        order.status = OrderStatus.CONFIRMED
        await order_service.save_order(order)
        return OrderProcessResult.success(order)

    finally:
        # Cleanup: always executes
        await cleanup_resources()
```plaintext

---

## 3. Logging Best Practices

### 3.1 Log Levels and What to Log

```java
@Slf4j
public class OrderProcessor {

    public void processOrder(Long orderId) {
        // DEBUG: Detailed diagnostic info (heavy, disabled in prod)
        log.debug("Starting order processing for orderId={}, timestamp={}",
                  orderId, Instant.now());

        try {
            Order order = orderRepository.findById(orderId)
                    .orElseThrow(() -> new EntityNotFoundException("Order", orderId));

            // INFO: Significant business events
            log.info("Retrieved order: orderId={}, customerId={}, status={}",
                    orderId, order.getCustomerId(), order.getStatus());

            // Process order
            PaymentResult result = paymentGateway.processPayment(order);

            if (result.isSuccessful()) {
                log.info("Payment processed successfully: orderId={}, amount={}",
                        orderId, result.getAmount());
            }

        } catch (EntityNotFoundException e) {
            // WARN: Recoverable problems (expected error conditions)
            log.warn("Order not found: orderId={}, cause={}", orderId, e.getMessage());

        } catch (PaymentGatewayException e) {
            // ERROR: Unexpected failures that need attention
            log.error("Payment gateway error: orderId={}, retryable={}, details={}",
                    orderId, e.isRetryable(), e.getDetails(), e);

        } catch (Exception e) {
            // ERROR + stack trace: Unexpected errors
            log.error("Unexpected error processing order: orderId={}", orderId, e);
        }
    }
}
```plaintext

```python
import logging

logger = logging.getLogger(__name__)


async def process_order(order_id: int) -> None:
    """
    Process an order with appropriate logging at each step.

    Args:
        order_id: The order ID to process.
    """
    try:
        # DEBUG: Detailed diagnostic info
        logger.debug("Starting order processing for order_id=%s, timestamp=%s",
                     order_id, datetime.utcnow().isoformat())

        order = await order_service.get_order_by_id(order_id)

        if not order:
            raise EntityNotFoundException("Order", order_id)

        # INFO: Significant business events
        logger.info("Retrieved order: order_id=%s, customer_id=%s, status=%s",
                   order_id, order.customer_id, order.status.value)

        # Process payment
        payment_result = await payment_gateway.process_payment(order)

        if payment_result.is_successful:
            logger.info("Payment processed successfully: order_id=%s, amount=%.2f",
                       order_id, payment_result.amount)

    except EntityNotFoundException as e:
        # WARN: Expected, recoverable errors
        logger.warning("Order not found: order_id=%s, error=%s",
                      order_id, e.message)

    except PaymentGatewayException as e:
        # ERROR: Unexpected failures requiring attention
        logger.error("Payment gateway error: order_id=%s, retryable=%s",
                    order_id, e.is_retryable, exc_info=e.is_critical)

    except Exception as e:
        # ERROR: Unexpected errors with full stack trace
        logger.error("Unexpected error processing order: order_id=%s",
                    order_id, exc_info=True)
```plaintext

---

## 4. Retry Logic with Exponential Backoff

```java
/**
 * Retry helper for resilient operations.
 */
public class RetryPolicy<T> {

    private final int maxAttempts;
    private final long initialBackoffMs;
    private final double backoffMultiplier;

    public RetryPolicy(int maxAttempts, long initialBackoffMs, double backoffMultiplier) {
        this.maxAttempts = maxAttempts;
        this.initialBackoffMs = initialBackoffMs;
        this.backoffMultiplier = backoffMultiplier;
    }

    /**
     * Execute operation with retry logic.
     *
     * @param operation the operation to retry
     * @return the operation result
     * @throws Exception if all retries are exhausted
     */
    public <T> T execute(Callable<T> operation) throws Exception {
        long backoffMs = initialBackoffMs;

        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                return operation.call();

            } catch (TransientException e) {
                if (attempt >= maxAttempts) {
                    throw e;  // Last attempt failed, give up
                }

                log.warn("Transient error on attempt {}/{}: {}. Retrying in {}ms",
                        attempt, maxAttempts, e.getMessage(), backoffMs);

                Thread.sleep(backoffMs);
                backoffMs = (long) (backoffMs * backoffMultiplier);

            } catch (Exception e) {
                throw e;  // Non-transient error, fail immediately
            }
        }

        throw new IllegalStateException("Unreachable code");
    }
}

// Usage
RetryPolicy<PaymentResult> policy = new RetryPolicy<>(3, 100, 2.0);
PaymentResult result = policy.execute(() ->
        paymentGateway.processPayment(order)
);
```plaintext

```python
import asyncio
from typing import Callable, TypeVar, Any

T = TypeVar('T')


async def retry_operation(
    operation: Callable,
    max_retries: int = 3,
    initial_backoff_ms: int = 100,
    backoff_multiplier: float = 2.0,
    retryable_exceptions: tuple = (ConnectionError, TimeoutError),
) -> Any:
    """
    Execute operation with exponential backoff retry logic.

    Args:
        operation: Async function to execute.
        max_retries: Maximum number of retry attempts.
        initial_backoff_ms: Initial backoff in milliseconds.
        backoff_multiplier: Multiplier for exponential backoff.
        retryable_exceptions: Tuple of exceptions that trigger retry.

    Returns:
        Operation result.

    Raises:
        The last exception if all retries are exhausted.
    """
    backoff_ms = initial_backoff_ms

    for attempt in range(1, max_retries + 1):
        try:
            return await operation()

        except retryable_exceptions as e:
            if attempt >= max_retries:
                raise  # Last attempt failed

            logger.warning(
                "Transient error on attempt %d/%d: %s. Retrying in %dms",
                attempt, max_retries, str(e), backoff_ms
            )

            await asyncio.sleep(backoff_ms / 1000)
            backoff_ms = int(backoff_ms * backoff_multiplier)

        except Exception as e:
            raise  # Non-retryable error, fail immediately

    raise RuntimeError("Unreachable code")


# Usage
result = await retry_operation(
    operation=lambda: payment_gateway.process_payment(order),
    max_retries=3,
    initial_backoff_ms=100,
    backoff_multiplier=2.0
)
```plaintext

---

## 5. Error Recovery Strategies

### 5.1 Graceful Degradation

```java
/**
 * Fetch order details with graceful degradation.
 *
 * If caching service fails, fall back to primary database.
 */
public Order getOrderWithFallback(Long orderId) {
    try {
        // Try cache first (fast but unreliable)
        return cacheService.getOrder(orderId);

    } catch (CacheException e) {
        log.warn("Cache service failed, falling back to database: {}", e.getMessage());
        try {
            return orderRepository.findById(orderId)
                    .orElseThrow(() -> new EntityNotFoundException("Order", orderId));

        } catch (DatabaseException e2) {
            log.error("Database error, cannot retrieve order", e2);
            throw new SystemUnavailableException("Order service unavailable");
        }
    }
}
```plaintext

### 5.2 Circuit Breaker Pattern

```java
/**
 * Circuit breaker for external service calls.
 *
 * Fails fast when service is down instead of retrying endlessly.
 */
public class CircuitBreaker<T> {

    enum State { CLOSED, OPEN, HALF_OPEN }

    private State state = State.CLOSED;
    private int failureCount = 0;
    private long lastFailureTime = 0;
    private final int failureThreshold = 5;
    private final long timeout = 60_000;  // 1 minute

    public synchronized T execute(Callable<T> operation) throws Exception {
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - lastFailureTime > timeout) {
                state = State.HALF_OPEN;
            } else {
                throw new CircuitBreakerOpenException("Circuit breaker is OPEN");
            }
        }

        try {
            T result = operation.call();
            onSuccess();
            return result;

        } catch (Exception e) {
            onFailure();
            throw e;
        }
    }

    private void onSuccess() {
        failureCount = 0;
        state = State.CLOSED;
    }

    private void onFailure() {
        failureCount++;
        lastFailureTime = System.currentTimeMillis();

        if (failureCount >= failureThreshold) {
            state = State.OPEN;
        }
    }
}
```plaintext

---

## 6. Error Handling Checklist

✅ Create custom exception hierarchy (extends common base)
✅ Catch specific exceptions before general ones
✅ Log at appropriate levels (DEBUG, INFO, WARN, ERROR)
✅ Include context in log messages (IDs, status, amounts)
✅ Implement retry logic for transient errors
✅ Use exponential backoff to avoid thundering herd
✅ Fail fast for non-retryable errors
✅ Implement graceful degradation (fallbacks)
✅ Use circuit breaker for external service calls
✅ Clean up resources in finally blocks
✅ Return consistent error responses to clients
✅ Never swallow exceptions silently
