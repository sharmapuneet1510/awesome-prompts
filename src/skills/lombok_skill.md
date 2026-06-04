---
name: Project Lombok Skill
version: 1.0
description: >
  Comprehensive Project Lombok annotations and patterns for reducing Java boilerplate.
  Covers @Data, @Builder, @Slf4j, @RequiredArgsConstructor, @Value, custom annotations,
  and best practices for clean, maintainable code.
applies_to: [java, lombok, spring-boot, maven, gradle, code-generation]
tags: [lombok, boilerplate, annotations, builders, logging, constructors]
---

# Project Lombok Skill — v1.0

---

## 1. Maven & Gradle Setup

### 1.1 Maven Configuration

```xml
<dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>1.18.30</version>
    <scope>provided</scope>
</dependency>

<!-- Maven compiler plugin configuration -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.10.1</version>
    <configuration>
        <source>17</source>
        <target>17</target>
        <annotationProcessorPaths>
            <path>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <version>1.18.30</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

### 1.2 Gradle Configuration

```gradle
dependencies {
    compileOnly 'org.projectlombok:lombok:1.18.30'
    annotationProcessor 'org.projectlombok:lombok:1.18.30'
}
```

### 1.3 IDE Configuration

```
IntelliJ IDEA:
  Settings → Plugins → Search "Lombok" → Install
  Settings → Build, Execution, Deployment → Compiler →
    Annotation Processors → Enable annotation processing

VS Code:
  Install "Lombok Annotations Support for VS Code"
  Install "Language Support for Java (Red Hat)"

Eclipse:
  Run: java -jar lombok.jar install eclipse.exe
```

---

## 2. Core Annotations

### 2.1 @Getter & @Setter

```java
/**
 * Generate getters and setters automatically.
 */
@Getter
@Setter
public class Order {
    private Long id;
    private Long customerId;
    private BigDecimal totalAmount;
    private String status;

    // Generates:
    // public Long getId() { return this.id; }
    // public void setId(Long id) { this.id = id; }
    // ... for all fields
}

/**
 * Selective generation: @Getter on class, @Setter on field.
 */
@Getter
public class ImmutableOrder {
    private Long id;
    private Long customerId;
    private BigDecimal totalAmount;

    @Setter
    private String status;  // Only this field has setter
}
```

### 2.2 @ToString & @EqualsAndHashCode

```java
/**
 * Generate toString, equals, and hashCode.
 */
@ToString
@EqualsAndHashCode
public class Product {
    private Long id;
    private String name;
    private BigDecimal price;

    // Generates:
    // public String toString() { return "Product(...)"; }
    // public boolean equals(Object o) { ... }
    // public int hashCode() { ... }
}

/**
 * Selective field exclusion.
 */
@ToString(exclude = {"internalId", "temp"})
@EqualsAndHashCode(exclude = {"createdAt"})
public class Order {
    private Long id;
    private String internalId;  // Won't be included in toString/equals
    private LocalDateTime createdAt;  // Won't be in equals/hashCode
    private BigDecimal totalAmount;
}
```

---

## 3. @Data & @Value

### 3.1 @Data: All-In-One Annotation

```java
/**
 * @Data = @Getter + @Setter + @ToString + @EqualsAndHashCode + @RequiredArgsConstructor
 *
 * ✓ RECOMMENDED for mutable DTOs and domain objects
 */
@Data
public class CustomerDTO {
    private Long id;
    private String name;
    private String email;
    private List<OrderDTO> orders;

    // Generates:
    // - Getters for all fields
    // - Setters for all fields
    // - toString()
    // - equals() and hashCode()
    // - Constructor with required fields (final + @NonNull)
}
```

### 3.2 @Value: Immutable Variant

```java
/**
 * @Value = immutable version of @Data
 *
 * ✓ RECOMMENDED for value objects, DTOs that should be immutable
 */
@Value
public class Money {
    BigDecimal amount;  // All fields become final
    String currency;    // All fields become private

    // Generates:
    // - Getters only (no setters)
    // - toString()
    // - equals() and hashCode()
    // - Constructor with all fields
    // - All fields are effectively immutable
}

/**
 * Mutable field in @Value using @Wither.
 */
@Value
public class OrderAmount {
    BigDecimal amount;
    String currency;

    @Wither
    LocalDateTime updatedAt;  // Has setter via .withUpdatedAt()
}
```

---

## 4. Constructors: @RequiredArgsConstructor & @AllArgsConstructor

### 4.1 Constructor Generation

```java
/**
 * @RequiredArgsConstructor: Constructor for final + @NonNull fields.
 *
 * BEST PRACTICE for dependency injection.
 */
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    private final EmailService emailService;

    // Generates:
    // public OrderService(OrderRepository orderRepository, PaymentGateway paymentGateway, EmailService emailService) {
    //     this.orderRepository = orderRepository;
    //     this.paymentGateway = paymentGateway;
    //     this.emailService = emailService;
    // }
}

/**
 * Using with @Autowired (Spring).
 */
@Service
@RequiredArgsConstructor
public class CustomerService {
    private final CustomerRepository customerRepository;
    private final CustomerMapper customerMapper;

    public CustomerDTO getCustomer(Long id) {
        Customer customer = customerRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Customer not found"));
        return customerMapper.toDTO(customer);
    }
}

/**
 * @AllArgsConstructor: Constructor for ALL fields.
 */
@AllArgsConstructor
@Data
public class Order {
    private Long id;
    private Long customerId;
    private BigDecimal totalAmount;
    private String status;

    // Generates constructor with all fields in order
}
```

---

## 5. Builder Pattern: @Builder

### 5.1 Simple Builder

```java
/**
 * @Builder: Generates Builder pattern automatically.
 */
@Builder
@Data
public class Order {
    private Long id;
    private Long customerId;
    private BigDecimal totalAmount;
    private String status;
    private LocalDateTime createdAt;
    private List<OrderItem> items;

    // Usage:
    // Order order = Order.builder()
    //     .customerId(123L)
    //     .totalAmount(BigDecimal.valueOf(99.99))
    //     .status("PENDING")
    //     .items(List.of(...))
    //     .build();
}
```

### 5.2 Builder with Defaults & Customization

```java
/**
 * Builder with custom defaults and validation.
 */
@Builder(toBuilder = true)  // Enable .toBuilder() to copy and modify
@Data
public class Order {
    private Long id;
    private Long customerId;

    @Builder.Default
    private BigDecimal totalAmount = BigDecimal.ZERO;

    @Builder.Default
    private String status = "PENDING";

    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();

    @Builder.Default
    private List<OrderItem> items = new ArrayList<>();

    // Usage:
    Order order = Order.builder()
            .customerId(123L)
            .build();  // Uses defaults

    // Copy and modify:
    Order updatedOrder = order.toBuilder()
            .status("CONFIRMED")
            .build();
}
```

### 5.3 Builder with Validation

```java
/**
 * Custom builder with validation.
 */
@Builder(toBuilder = true)
@Data
public class PaymentRequest {
    private BigDecimal amount;
    private String currency;
    private String cardToken;

    /**
     * Custom validation in builder.
     */
    public static class PaymentRequestBuilder {
        public PaymentRequest build() {
            if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
                throw new ValidationException("Amount must be positive");
            }
            if (currency == null || currency.isEmpty()) {
                throw new ValidationException("Currency is required");
            }
            if (cardToken == null || cardToken.isEmpty()) {
                throw new ValidationException("Card token is required");
            }
            return new PaymentRequest(amount, currency, cardToken);
        }
    }

    // Usage:
    try {
        PaymentRequest request = PaymentRequest.builder()
                .amount(BigDecimal.valueOf(99.99))
                .currency("USD")
                .cardToken("tok-123")
                .build();  // Validated
    } catch (ValidationException e) {
        log.error("Validation failed: {}", e.getMessage());
    }
}
```

---

## 6. Logging: @Slf4j & Variants

### 6.1 @Slf4j (SLF4J)

```java
/**
 * @Slf4j: Generates SLF4J logger named 'log'.
 *
 * RECOMMENDED: Industry standard, works with any implementation
 */
@Service
@Slf4j
public class OrderService {
    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    public Order createOrder(OrderRequest request) {
        log.debug("Creating order for customer: {}", request.getCustomerId());

        Order order = new Order();
        order.setCustomerId(request.getCustomerId());

        try {
            Order saved = orderRepository.save(order);
            log.info("Order created successfully with ID: {}", saved.getId());
            return saved;

        } catch (Exception e) {
            log.error("Failed to create order for customer: {}", request.getCustomerId(), e);
            throw e;
        }
    }
}
```

### 6.2 Other Logger Annotations

```java
/**
 * @Log (java.util.logging)
 */
@Log
public class LegacyService {
    void doSomething() {
        log.info("Using java.util.logging");
    }
}

/**
 * @Log4j2 (Apache Log4j 2)
 */
@Log4j2
public class HighPerformanceService {
    void doSomething() {
        logger.info("Using Log4j2");
    }
}

/**
 * @CommonsLog (Apache Commons Logging)
 */
@CommonsLog
public class LegacyApacheService {
    void doSomething() {
        log.info("Using Commons Logging");
    }
}
```

---

## 7. Null Checking: @NonNull

### 7.1 Parameter Validation

```java
/**
 * @NonNull on constructor parameter: generates null check.
 */
@RequiredArgsConstructor
public class PaymentProcessor {
    private final PaymentGateway paymentGateway;
    private final AuditService auditService;

    public PaymentResult processPayment(
            @NonNull BigDecimal amount,
            @NonNull String cardToken) {

        // Generates:
        // if (amount == null) throw new NullPointerException("amount is marked non-null but is null");
        // if (cardToken == null) throw new NullPointerException("cardToken is marked non-null but is null");

        return paymentGateway.charge(amount, cardToken);
    }

    /**
     * @NonNull on field: generates null check in constructor + setter.
     */
    @NonNull
    private String merchantId;

    public void setMerchantId(@NonNull String merchantId) {
        this.merchantId = merchantId;  // Null check generated
    }
}
```

---

## 8. Accessors: @Accessors

### 8.1 Fluent API

```java
/**
 * @Accessors(fluent = true): Getters/setters without get/set prefix.
 */
@Data
@Accessors(fluent = true)
public class Order {
    private Long id;
    private BigDecimal amount;
    private String status;

    // Generates:
    // public Long id() { return this.id; }
    // public Order id(Long id) { this.id = id; return this; }
    // public BigDecimal amount() { return this.amount; }
    // public Order amount(BigDecimal amount) { this.amount = amount; return this; }

    // Usage:
    Order order = new Order()
            .id(123L)
            .amount(BigDecimal.valueOf(99.99))
            .status("PENDING");
}

/**
 * @Accessors(chain = true): Setters return this for chaining.
 */
@Data
@Accessors(chain = true)
public class QueryBuilder {
    private String table;
    private String where;
    private int limit;

    // Usage:
    QueryBuilder query = new QueryBuilder()
            .setTable("orders")
            .setWhere("customer_id = 123")
            .setLimit(10);
}
```

---

## 9. Annotations with Exclusions

### 9.1 Field-Level Control

```java
/**
 * @Exclude fields from generation.
 */
@Data
@ToString(exclude = {"password", "apiKey"})
@EqualsAndHashCode(exclude = {"updatedAt"})
public class User {
    private Long id;
    private String username;

    @ToString.Exclude
    private String password;  // Won't appear in toString()

    @EqualsAndHashCode.Exclude
    private String apiKey;  // Won't affect equals/hashCode

    @EqualsAndHashCode.Exclude
    private LocalDateTime updatedAt;
}
```

---

## 10. Best Practices

### 10.1 Recommended Pattern

```java
/**
 * ✓ BEST PRACTICE: Entity with Lombok.
 */
@Entity
@Table(name = "orders")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private Long customerId;

    @Column(nullable = false)
    private BigDecimal totalAmount;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    private String status = "PENDING";

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}

/**
 * ✓ BEST PRACTICE: Service with Lombok.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    private final NotificationService notificationService;

    public Order createOrder(@NonNull CreateOrderRequest request) {
        log.info("Creating order for customer: {}", request.getCustomerId());

        Order order = Order.builder()
                .customerId(request.getCustomerId())
                .totalAmount(request.getTotalAmount())
                .status("PENDING")
                .build();

        Order saved = orderRepository.save(order);
        log.info("Order saved with ID: {}", saved.getId());

        return saved;
    }
}
```

### 10.2 Anti-Patterns to Avoid

```java
/**
 * ✗ AVOID: Lombok on interfaces or abstract classes
 * (doesn't make sense, doesn't generate anything)
 */
@Data  // ✗ Pointless
public interface OrderService {
    Order createOrder(CreateOrderRequest request);
}

/**
 * ✗ AVOID: Using @Data on classes with @Entity + bidirectional relationships
 * (generates .equals() that causes infinite recursion)
 */
@Entity
@Data  // ✗ Problematic with relationships
public class Order {
    @OneToMany(mappedBy = "order")
    private List<OrderItem> items;  // ✗ Causes recursion in equals()
}

/**
 * ✓ BETTER: Use @Data with @ToString/@EqualsAndHashCode exclusions
 */
@Entity
@Data
@ToString(exclude = "items")
@EqualsAndHashCode(exclude = "items")
public class Order {
    @OneToMany(mappedBy = "order")
    private List<OrderItem> items;  // ✓ Excluded from equals/toString
}
```

---

## 11. Lombok Checklist

✅ Add dependency to Maven/Gradle
✅ Configure IDE annotation processing
✅ Use @Data for mutable DTOs
✅ Use @Value for immutable objects
✅ Use @RequiredArgsConstructor for DI
✅ Use @Builder for complex object creation
✅ Use @Slf4j for logging
✅ Use @NonNull for parameter validation
✅ Exclude JPA relationship fields from equals/hashCode
✅ Keep using Javadoc (Lombok generates code, not docs)
✅ Be aware of @Data limitations (avoid with bidirectional relationships)
✅ Use @Accessors(fluent=true) for fluent APIs
✅ Generate boilerplate, never lose readability
✅ Don't over-engineer: simple POJOs might be clearer
✅ Test generated code like any other code
