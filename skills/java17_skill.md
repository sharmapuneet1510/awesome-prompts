---
name: Java 17 Modern Features & Best Practices
version: 1.0
description: >
  Comprehensive guide to Java 17 features introduced since Java 11. Covers records,
  sealed classes, pattern matching, text blocks, instanceof patterns, switch expressions,
  virtual threads (preview), and modern API improvements.
applies_to: [java, java-17, spring-boot, best-practices, patterns]
tags: [java17, records, sealed-classes, pattern-matching, text-blocks, virtual-threads]
---

# Java 17 Modern Features & Best Practices — v1.0

---

## 1. Java 17 Release Overview

### 1.1 Long-Term Support (LTS)

```
Java 17 (September 2021)
├── LTS Release: Supported until September 2026
├── Next LTS: Java 21 (September 2023)
└── Recommended: Use for production systems
```

**Key Features Added:**
- Records (JEP 395)
- Sealed Classes (JEP 409)
- Pattern Matching for switch (JEP 406)
- Text Blocks (JEP 378)
- Removed legacy APIs
- Module system refinements

---

## 2. Records — Immutable Data Carriers

### 2.1 Basic Record Syntax

```java
/**
 * Record: Immutable data carrier with generated equals/hashCode/toString.
 */
public record Order(
        Long id,
        Long customerId,
        BigDecimal amount,
        String status) {
    // Compact record: 5 lines replaces 50 lines of boilerplate
}

// Usage:
Order order = new Order(1L, 100L, BigDecimal.valueOf(99.99), "PENDING");
System.out.println(order);  // Order[id=1, customerId=100, amount=99.99, status=PENDING]
System.out.println(order.id());  // 1 (accessor methods auto-generated)
```

### 2.2 Record with Validation

```java
/**
 * Record with custom validation in compact constructor.
 */
public record Money(
        BigDecimal amount,
        String currency) {

    // Compact constructor: Implicit parameters, runs before field assignment
    public Money {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount must be non-negative");
        }
        if (currency == null || currency.isEmpty()) {
            throw new IllegalArgumentException("Currency is required");
        }
        // Fields are assigned after validation
    }
}

// Usage:
Money validMoney = new Money(BigDecimal.valueOf(100), "USD");
// Money invalidMoney = new Money(BigDecimal.valueOf(-10), "USD");  // Throws exception
```

### 2.3 Record with Custom Methods

```java
/**
 * Record with additional methods and derived fields.
 */
public record OrderItem(
        Long productId,
        int quantity,
        BigDecimal unitPrice) {

    /**
     * Compact constructor with validation.
     */
    public OrderItem {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive");
        }
    }

    /**
     * Computed field: Not part of record state.
     */
    public BigDecimal totalPrice() {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }

    /**
     * Static factory method.
     */
    public static OrderItem create(Long productId, int quantity, BigDecimal unitPrice) {
        return new OrderItem(productId, quantity, unitPrice);
    }
}

// Usage:
OrderItem item = OrderItem.create(1L, 2, BigDecimal.valueOf(50));
System.out.println(item.totalPrice());  // 100
```

### 2.4 Record with Generic Types

```java
/**
 * Generic record: Reusable for any type.
 */
public record Response<T>(
        int status,
        String message,
        T data) {

    public static <T> Response<T> success(T data) {
        return new Response<>(200, "Success", data);
    }

    public static <T> Response<T> error(int status, String message) {
        return new Response<>(status, message, null);
    }
}

// Usage:
Response<OrderDTO> orderResponse = Response.success(new OrderDTO(...));
Response<UserDTO> userResponse = Response.success(new UserDTO(...));
Response<String> errorResponse = Response.error(400, "Invalid input");
```

---

## 3. Sealed Classes — Type Hierarchies

### 3.1 Sealed Class Basics

```java
/**
 * Sealed class: Restrict which classes can extend this.
 */
public sealed class Payment
        permits CreditCardPayment, BankTransferPayment, DigitalWalletPayment {

    protected final String transactionId;
    protected final BigDecimal amount;

    protected Payment(String transactionId, BigDecimal amount) {
        this.transactionId = transactionId;
        this.amount = amount;
    }

    public abstract PaymentResult process();
}

/**
 * Final subclass: Cannot be extended further.
 */
public final class CreditCardPayment extends Payment {
    private final String cardToken;

    public CreditCardPayment(String transactionId, BigDecimal amount, String cardToken) {
        super(transactionId, amount);
        this.cardToken = cardToken;
    }

    @Override
    public PaymentResult process() {
        // Credit card specific logic
        return PaymentResult.success(transactionId);
    }
}

/**
 * Non-sealed subclass: Can be extended by other classes.
 */
public non-sealed class BankTransferPayment extends Payment {
    private final String bankAccount;

    public BankTransferPayment(String transactionId, BigDecimal amount, String bankAccount) {
        super(transactionId, amount);
        this.bankAccount = bankAccount;
    }

    @Override
    public PaymentResult process() {
        // Bank transfer logic
        return PaymentResult.pending(transactionId);
    }
}

/**
 * Using sealed classes in pattern matching.
 */
public class PaymentProcessor {
    public void processPayment(Payment payment) {
        if (payment instanceof CreditCardPayment cc) {
            System.out.println("Processing credit card: " + cc.getCardToken());
        } else if (payment instanceof BankTransferPayment bt) {
            System.out.println("Processing bank transfer: " + bt.getBankAccount());
        }
    }
}
```

### 3.2 Sealed Records

```java
/**
 * Sealed interface with record implementations.
 */
public sealed interface Event
        permits OrderPlacedEvent, PaymentProcessedEvent, ShipmentStartedEvent {
    String eventType();
    LocalDateTime timestamp();
}

/**
 * Record implementing sealed interface.
 */
public record OrderPlacedEvent(
        Long orderId,
        Long customerId,
        LocalDateTime timestamp) implements Event {

    @Override
    public String eventType() {
        return "ORDER_PLACED";
    }
}

public record PaymentProcessedEvent(
        Long orderId,
        String paymentId,
        LocalDateTime timestamp) implements Event {

    @Override
    public String eventType() {
        return "PAYMENT_PROCESSED";
    }
}

/**
 * Usage: Exhaustive pattern matching on sealed types.
 */
public class EventHandler {
    public void handle(Event event) {
        switch (event) {
            case OrderPlacedEvent ope -> System.out.println("Order placed: " + ope.orderId());
            case PaymentProcessedEvent ppe -> System.out.println("Payment: " + ppe.paymentId());
            case ShipmentStartedEvent sse -> System.out.println("Shipment: " + sse.trackingId());
        }
    }
}
```

---

## 4. Pattern Matching

### 4.1 instanceof Patterns

```java
/**
 * Pattern matching with instanceof: Avoid explicit cast.
 */
public class TypeCheck {

    // ✗ OLD: Verbose explicit cast
    public void oldWay(Object obj) {
        if (obj instanceof String) {
            String str = (String) obj;  // Explicit cast
            System.out.println("String: " + str.toUpperCase());
        }
    }

    // ✓ NEW: Pattern matching (Java 16+)
    public void newWay(Object obj) {
        if (obj instanceof String str) {  // Pattern variable 'str'
            System.out.println("String: " + str.toUpperCase());  // No cast needed
        }
    }

    // ✓ Guarded pattern (Java 17+)
    public void guardedPattern(Object obj) {
        if (obj instanceof String str && str.length() > 5) {
            System.out.println("Long string: " + str);
        }
    }
}
```

### 4.2 Switch Pattern Matching

```java
/**
 * Switch expressions with pattern matching.
 */
public class ResponseHandler {

    public String handleResponse(Object response) {
        return switch (response) {
            // String pattern with guard
            case String s when s.isEmpty() -> "Empty string";
            case String s when s.length() < 10 -> "Short string: " + s;
            case String s -> "Long string: " + s;

            // Type patterns
            case Integer i -> "Integer: " + i;
            case Long l -> "Long: " + l;
            case Double d when d > 0 -> "Positive double: " + d;

            // Record patterns (Java 21+, but available as preview in 17)
            case Order(Long id, _, BigDecimal amount, _) ->
                "Order #" + id + " for $" + amount;

            // Null pattern
            case null -> "Null response";

            // Default
            default -> "Unknown type";
        };
    }
}
```

### 4.3 Record Deconstruction Patterns

```java
/**
 * Deconstruct records in pattern matching.
 */
public record Point(int x, int y) {}

public class PatternMatching {

    public void analyzePoint(Point p) {
        // Deconstruct the record
        if (p instanceof Point(int x, int y) && x == y) {
            System.out.println("Diagonal point: (" + x + ", " + y + ")");
        }
    }

    public void matchPoints(Object obj) {
        String result = switch (obj) {
            case Point(0, 0) -> "Origin";
            case Point(int x, 0) -> "On X-axis at " + x;
            case Point(0, int y) -> "On Y-axis at " + y;
            case Point(int x, int y) -> "Point at (" + x + ", " + y + ")";
            default -> "Not a point";
        };
        System.out.println(result);
    }
}
```

---

## 5. Text Blocks — Multiline Strings

### 5.1 Basic Text Blocks

```java
/**
 * Text blocks: Multiline strings without concatenation.
 */
public class TextBlocks {

    // ✗ OLD: Concatenation is verbose
    public String oldJson() {
        return "{" +
                "  \"id\": 1," +
                "  \"name\": \"John\"," +
                "  \"email\": \"john@example.com\"" +
                "}";
    }

    // ✓ NEW: Text block (Java 13+, finalized Java 15)
    public String newJson() {
        return """
                {
                  "id": 1,
                  "name": "John",
                  "email": "john@example.com"
                }
                """;
    }

    // Text block with indentation control
    public String queryWithIndent() {
        return """
                SELECT id, name, email
                FROM users
                WHERE status = 'ACTIVE'
                ORDER BY created_at DESC
                """;
    }

    // Text block with placeholders
    public String emailTemplate(String name, String orderId) {
        return """
                Dear %s,

                Your order #%s has been confirmed.
                We'll notify you when it ships.

                Thank you for your purchase!
                """.formatted(name, orderId);
    }
}
```

### 5.2 Text Blocks with Special Characters

```java
/**
 * Text blocks with special characters and escaping.
 */
public class TextBlockSpecial {

    public String xmlDocument() {
        return """
                <?xml version="1.0" encoding="UTF-8"?>
                <root>
                  <user id="1">
                    <name>John Doe</name>
                    <email>john@example.com</email>
                  </user>
                </root>
                """;
    }

    public String htmlTemplate() {
        return """
                <!DOCTYPE html>
                <html>
                <head>
                  <title>Order Confirmation</title>
                </head>
                <body>
                  <h1>Thank you for your order!</h1>
                  <p>Your order has been received.</p>
                </body>
                </html>
                """;
    }

    // Escaped text blocks
    public String jsonWithNewlines() {
        return """
                {
                  "message": "Line 1\\nLine 2\\nLine 3"
                }
                """;
    }
}
```

---

## 6. Virtual Threads (Preview in Java 17)

### 6.1 Virtual Threads Basics

```java
/**
 * Virtual threads: Lightweight threads for high-concurrency scenarios.
 * (Preview in Java 17, standard in Java 21+)
 *
 * Note: Requires --enable-preview flag in Java 17
 */
public class VirtualThreads {

    /**
     * Old way: Platform threads (expensive).
     */
    public void oldWayPlatformThreads() {
        Thread thread = new Thread(() -> {
            System.out.println("Platform thread");
        });
        thread.start();
    }

    /**
     * New way: Virtual threads (lightweight).
     * Cost: ~100 bytes vs 2 MB for platform threads
     */
    public void newWayVirtualThreads() {
        Thread thread = Thread.ofVirtual()
                .start(() -> {
                    System.out.println("Virtual thread");
                });
    }

    /**
     * Virtual thread executor: Create many lightweight tasks.
     */
    public void virtualThreadExecutor() {
        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
            // Submit 1,000,000 tasks efficiently
            for (int i = 0; i < 1_000_000; i++) {
                int taskId = i;
                executor.submit(() -> {
                    // Process task
                    processTask(taskId);
                });
            }
        }
    }

    private void processTask(int taskId) {
        // Simulate work
        try {
            Thread.sleep(100);  // Virtual thread yields, doesn't block platform thread
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

### 6.2 Virtual Threads with Spring Boot

```java
/**
 * Spring Boot with virtual threads (experimental in Spring 6.0).
 */
@SpringBootApplication
public class VirtualThreadApplication {

    public static void main(String[] args) {
        SpringApplication.run(VirtualThreadApplication.class, args);
    }

    /**
     * Virtual thread executor bean.
     */
    @Bean
    public Executor virtualThreadExecutor() {
        return Executors.newVirtualThreadPerTaskExecutor();
    }
}

@Service
public class OrderService {

    @Autowired
    private Executor virtualThreadExecutor;

    /**
     * Async method using virtual threads.
     */
    public CompletableFuture<OrderResult> processOrderAsync(Order order) {
        return CompletableFuture.supplyAsync(() -> {
            // This runs on a virtual thread
            return processOrder(order);
        }, virtualThreadExecutor);
    }

    private OrderResult processOrder(Order order) {
        // Long-running operation
        return new OrderResult(order.getId(), "PROCESSED");
    }
}
```

---

## 7. Other Java 17 Improvements

### 7.1 Module System Refinements

```java
/**
 * Module system: Encapsulation at package level (Java 9+).
 * Java 17 refines and stabilizes module APIs.
 */
module com.example.orders {
    // Require other modules
    requires com.example.payment;
    requires com.example.inventory;
    requires java.base;

    // Export specific packages
    exports com.example.orders.api;
    exports com.example.orders.service;

    // Hidden implementation
    // com.example.orders.internal is NOT exported
}
```

### 7.2 Stream API Enhancements

```java
/**
 * Stream API with pattern matching and records.
 */
public class ModernStreams {

    public void modernStreamProcessing(List<Order> orders) {
        orders.stream()
                // Filter with pattern matching
                .filter(order -> order instanceof Order o && o.getStatus().equals("PENDING"))
                // Process with records
                .map(order -> new OrderSummary(
                        order.getId(),
                        order.getCustomerId(),
                        order.getAmount()
                ))
                .forEach(System.out::println);
    }

    public record OrderSummary(Long id, Long customerId, BigDecimal amount) {}
}
```

### 7.3 New APIs

```java
/**
 * Java 17 additions to standard library.
 */
public class ModernAPIs {

    /**
     * Random number generation improvements.
     */
    public void modernRandom() {
        // Old: Random and ThreadLocalRandom mixed API
        // New: Unified RandomGenerator interface
        RandomGenerator generator = RandomGenerator.of("L64X256MixRandom");
        generator.nextLong();
    }

    /**
     * HexFormat for hex encoding/decoding (Java 17).
     */
    public void hexFormat() {
        HexFormat hex = HexFormat.of();
        String formatted = hex.formatHex(new byte[]{0x01, 0x02, 0x03});
        System.out.println(formatted);  // 010203
    }
}
```

---

## 8. Migration Guide from Java 11 to Java 17

### 8.1 Breaking Changes

```java
/**
 * Key breaking changes when upgrading to Java 17.
 */
public class MigrationGuide {

    /**
     * 1. Removed methods: SecurityManager, deprecated APIs removed.
     */
    // ✗ Java 17 removes: SecurityManager (Java 18+)
    // ✗ Java 17 removes: Various deprecated javax.* APIs
    // ✓ Use modern alternatives

    /**
     * 2. Updated default values.
     */
    // File.toString() behavior changed
    // Character encoding defaults refined

    /**
     * 3. Module system stricter.
     */
    // Add-modules and other flags may be needed for legacy code

    /**
     * Best practice: Update dependencies.
     */
    // Spring Boot 3.x (requires Java 17+)
    // Gradle 7.x+
    // Maven 3.8.1+
}
```

### 8.2 Upgrade Strategy

```
Step 1: Check Java version compatibility
  └─ Java 17 requires gradle/maven updates

Step 2: Update build tools
  ├─ Maven: 3.8.1+
  ├─ Gradle: 7.0+
  └─ IDE: Latest version with Java 17 support

Step 3: Update dependencies
  ├─ Spring Boot: 3.x
  ├─ Spring: 6.x
  └─ Libraries: Latest versions

Step 4: Migrate code to modern idioms
  ├─ Use records instead of custom POJOs
  ├─ Use sealed classes for type hierarchies
  ├─ Use pattern matching in conditionals
  └─ Use text blocks for multiline strings

Step 5: Test thoroughly
  ├─ Unit tests
  ├─ Integration tests
  └─ Performance tests
```

---

## 9. Java 17 Best Practices

✅ Use records for immutable data carriers (DTO, Value Objects)
✅ Use sealed classes to restrict inheritance hierarchies
✅ Use pattern matching in instanceof and switch
✅ Use text blocks for multiline strings and templates
✅ Avoid explicit casts with pattern variables
✅ Update Spring Boot to 3.x for full Java 17 support
✅ Use var for type inference where appropriate
✅ Leverage module system for package encapsulation
✅ Consider virtual threads for high-concurrency scenarios
✅ Use modern API versions (RandomGenerator, HexFormat)
✅ Keep dependencies up-to-date with Java 17 support
✅ Test on Java 17 before production deployment
✅ Migrate from Java 11: Gradual, test-driven approach
✅ Remove deprecated API usage (SecurityManager, etc.)
✅ Profile performance improvements from records and sealed classes

---

## 10. Java 17 Checklist

✅ Set target Java version to 17 in Maven/Gradle
✅ Update Spring Boot to 3.x
✅ Refactor DTOs to records
✅ Use sealed classes for restricted hierarchies
✅ Apply pattern matching in conditionals and switches
✅ Replace concatenation with text blocks
✅ Remove explicit casts where patterns apply
✅ Update IDE to latest version
✅ Test all legacy code on Java 17
✅ Update CI/CD to Java 17
✅ Document migration for team members
✅ Consider virtual threads for async workloads
✅ Remove SecurityManager and deprecated API usage
✅ Validate all dependencies support Java 17
✅ Benchmark performance improvements
