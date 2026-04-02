---
name: Java Advanced Coding Skill
version: 2.0
description: >
  Reusable skill module for Java coding. Covers Java 17/21 features, OOP
  principles with clear examples, Spring Boot 3.x patterns, Javadoc standards,
  and test generation with JUnit 5 + Mockito.
applies_to: [java, spring-boot, maven, gradle]
---

# Java Advanced Coding Skill — v2.0

---

## 1. Version Detection First

Before writing any Java code, check what is installed:

```bash
java -version
mvn -version
```

Then match features to what is available:

| Java Version | Use These Features |
|-------------|-------------------|
| Java 11 | `var`, HTTP Client, `Optional`, lambda, streams |
| Java 17 (LTS) | All above + **records**, **sealed classes**, **text blocks**, switch expressions |
| Java 21 (LTS) | All above + **virtual threads** (`Thread.ofVirtual()`), **pattern matching for switch**, sequenced collections |

---

## 2. Four OOP Pillars — Applied in Java

### 2.1 Encapsulation — Control What Can Change

Keep fields private. Provide controlled access through methods.

```java
/**
 * Represents a customer's bank account.
 *
 * <p>Balance can only change through deposit() and withdraw().
 * Direct field access is not allowed outside this class.</p>
 */
public class BankAccount {

    /** The account owner's full name. Immutable after creation. */
    private final String ownerName;

    /** Current balance in the account currency. Modified only via transactions. */
    private double balance;

    /**
     * Creates a new bank account.
     *
     * @param ownerName     the full name of the account holder
     * @param initialBalance starting balance — must be zero or positive
     * @throws IllegalArgumentException if initialBalance is negative
     */
    public BankAccount(String ownerName, double initialBalance) {
        if (initialBalance < 0) {
            throw new IllegalArgumentException(
                "Initial balance cannot be negative. Got: " + initialBalance
            );
        }
        this.ownerName = ownerName;
        this.balance   = initialBalance;
    }

    /**
     * Deposits money into the account.
     *
     * @param amount amount to deposit — must be positive
     * @throws IllegalArgumentException if amount is zero or negative
     */
    public void deposit(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Deposit must be positive. Got: " + amount);
        }
        this.balance += amount;
    }

    /** Returns the current balance. Callers can read it but not set it directly. */
    public double getBalance() {
        return balance;
    }

    /** Returns the account owner's name. */
    public String getOwnerName() {
        return ownerName;
    }
}
```

### 2.2 Abstraction — Define WHAT, Not HOW

Use interfaces to define the contract. Implementations provide the detail.

```java
/**
 * Defines how notifications are sent.
 *
 * <p>Any class that wants to send notifications should use this interface.
 * This means you can swap email for SMS or push without changing the callers.</p>
 */
public interface NotificationSender {

    /**
     * Sends a notification to the recipient.
     *
     * @param recipient the address to send to (email, phone number, device token)
     * @param subject   a short title for the notification
     * @param message   the full notification content
     * @return true if the notification was delivered successfully
     */
    boolean send(String recipient, String subject, String message);
}


/**
 * Sends notifications via email using JavaMail.
 *
 * <p>Implements {@link NotificationSender} for the email channel.</p>
 */
public class EmailNotificationSender implements NotificationSender {

    private final JavaMailSender mailSender;
    private final String fromAddress;

    /**
     * @param mailSender   the Spring Mail component to use for sending
     * @param fromAddress  the "From" email address for outbound messages
     */
    public EmailNotificationSender(JavaMailSender mailSender, String fromAddress) {
        this.mailSender  = mailSender;
        this.fromAddress = fromAddress;
    }

    @Override
    public boolean send(String recipient, String subject, String message) {
        SimpleMailMessage mail = new SimpleMailMessage();
        mail.setFrom(fromAddress);
        mail.setTo(recipient);
        mail.setSubject(subject);
        mail.setText(message);
        mailSender.send(mail);
        return true;
    }
}
```

### 2.3 Inheritance — Shared Behaviour, Specialised Differences

Use inheritance for true "is-a" relationships. Keep hierarchies shallow (max 2–3 levels).

```java
/**
 * Base class for all payment types processed by this system.
 *
 * <p>Holds the common fields (amount, currency, reference) and defines
 * the process() method that each payment type must implement.</p>
 */
public abstract class Payment {

    protected final double amount;
    protected final String currency;
    protected final String referenceId;

    /**
     * @param amount      the payment amount — must be positive
     * @param currency    the ISO 4217 currency code (e.g. "GBP")
     * @param referenceId a unique reference for this payment
     */
    protected Payment(double amount, String currency, String referenceId) {
        this.amount      = amount;
        this.currency    = currency;
        this.referenceId = referenceId;
    }

    /**
     * Processes this payment through its specific channel.
     *
     * @return a {@link PaymentResult} indicating success or failure with details
     */
    public abstract PaymentResult process();

    /** Returns the payment amount. */
    public double getAmount() { return amount; }

    /** Returns the ISO 4217 currency code. */
    public String getCurrency() { return currency; }
}


/**
 * Processes payments via a credit or debit card.
 *
 * <p>Extends {@link Payment} with card-specific fields and card gateway logic.</p>
 */
public class CardPayment extends Payment {

    private final String maskedCardNumber;   // e.g. "****-****-****-1234"
    private final String cardHolderName;

    /**
     * @param amount            payment amount
     * @param currency          ISO 4217 currency code
     * @param referenceId       unique payment reference
     * @param maskedCardNumber  last 4 digits shown (e.g. "****1234")
     * @param cardHolderName    name on the card
     */
    public CardPayment(double amount, String currency, String referenceId,
                       String maskedCardNumber, String cardHolderName) {
        super(amount, currency, referenceId);
        this.maskedCardNumber = maskedCardNumber;
        this.cardHolderName   = cardHolderName;
    }

    @Override
    public PaymentResult process() {
        // Card gateway integration logic goes here
        return PaymentResult.success(referenceId);
    }
}
```

### 2.4 Polymorphism — Write Code to the Interface

```java
/**
 * Sends a payment confirmation to the customer after a successful transaction.
 *
 * <p>This method works with any {@link NotificationSender} implementation.
 * You can pass an email sender, SMS sender, or push sender — this code
 * does not need to know which one.</p>
 *
 * @param sender    the notification channel to use
 * @param recipient the customer's contact address
 * @param payment   the payment that was just processed
 */
public void sendConfirmation(NotificationSender sender, String recipient, Payment payment) {
    String subject = "Payment confirmed — " + payment.getReferenceId();
    String message = String.format("Your payment of %.2f %s has been received.",
                                   payment.getAmount(), payment.getCurrency());
    sender.send(recipient, subject, message);
}
```

---

## 3. Java 17 / 21 Modern Features

### Records (Java 17+) — Immutable Data Carriers

Use records for request/response objects and value types. They are immutable by design.

```java
/**
 * Request object for creating a new customer order.
 *
 * <p>Uses a Java record — all fields are final, getters are auto-generated,
 * and equals/hashCode/toString are included for free.</p>
 *
 * @param customerId the ID of the customer placing the order — must be positive
 * @param items      list of items to include — must not be empty
 */
public record CreateOrderRequest(
    @NotNull Long customerId,
    @NotEmpty List<String> items
) {}
```

### Sealed Classes (Java 17+) — Controlled Hierarchies

Use sealed classes when you have a fixed set of subtypes:

```java
/**
 * Represents the result of a payment operation.
 *
 * <p>Can only be a {@link Success} or a {@link Failure} —
 * no other subtypes are allowed. This makes switch expressions exhaustive.</p>
 */
public sealed interface PaymentResult permits PaymentResult.Success, PaymentResult.Failure {

    /** Creates a successful result with the transaction ID. */
    static PaymentResult success(String transactionId) {
        return new Success(transactionId);
    }

    /** Creates a failure result with a human-readable reason. */
    static PaymentResult failure(String reason) {
        return new Failure(reason);
    }

    /** Returned when the payment was processed successfully. */
    record Success(String transactionId) implements PaymentResult {}

    /** Returned when the payment failed, with the reason why. */
    record Failure(String reason) implements PaymentResult {}
}

// Usage — switch is exhaustive, no default needed
String message = switch (result) {
    case PaymentResult.Success s -> "Payment " + s.transactionId() + " succeeded";
    case PaymentResult.Failure f -> "Payment failed: " + f.reason();
};
```

### Virtual Threads (Java 21+) — Simple Concurrency

```java
// Traditional thread pool — complex setup
ExecutorService executor = Executors.newFixedThreadPool(200);

// Virtual threads (Java 21) — simple, scales to millions
// In Spring Boot 3.2+, enable with: spring.threads.virtual.enabled=true
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();

// Or create a single virtual thread:
Thread.ofVirtual()
      .name("order-processor")
      .start(() -> processOrder(orderId));
```

---

## 4. Spring Boot 3.x Patterns

### Layered Architecture (Always Follow This)

```
REST Controller   → Receives HTTP requests, calls Service, returns responses
Service Interface → Defines the business operations (what)
Service Impl      → Implements the business logic (how)
Repository        → Data access (Spring Data JPA interface)
Entity            → JPA entity (maps to a DB table)
DTO               → What goes in/out of the API (not the entity)
```

### Constructor Injection (Always)

```java
// ❌ WRONG — field injection makes testing harder and hides dependencies
@Service
public class OrderService {
    @Autowired
    private OrderRepository repository;
}

// ✅ CORRECT — constructor injection is explicit and testable
@Service
@RequiredArgsConstructor   // Lombok generates the constructor
public class OrderServiceImpl implements OrderService {

    private final OrderRepository repository;  // injected via constructor
}
```

### application.yml Recommended Defaults

```yaml
spring:
  jpa:
    open-in-view: false        # Prevents lazy loading outside transactions
    show-sql: false            # Only enable during development

  mvc:
    problemdetails:
      enabled: true            # Use RFC 9457 error format in responses

# Java 21 + Spring Boot 3.2+ — enable virtual threads for better throughput
spring:
  threads:
    virtual:
      enabled: true
```

---

## 5. Javadoc Standards

Every public class and method must have Javadoc. No exceptions.

```java
/**
 * [One-sentence summary of what this class is and what it does.]
 *
 * <p>[Optional: One paragraph of context — why does this class exist?
 * What problem does it solve? What are its key responsibilities?]</p>
 *
 * @author [Team or developer name]
 * @since  [Version or sprint when this was added]
 */
public class YourClass {

    /**
     * [One-sentence summary of what this method does.]
     *
     * <p>[Optional extra context for non-obvious logic.]</p>
     *
     * @param paramName [what it is, any constraints — e.g. "must not be null", "must be positive"]
     * @return          [what is returned and when]
     * @throws SomeException [when this exception is thrown and why]
     */
    public ReturnType methodName(ParamType paramName) { }
}
```

---

## 6. Testing Standards

### Unit Tests — JUnit 5 + Mockito

```java
/**
 * Unit tests for {@link OrderServiceImpl}.
 *
 * <p>Mocks are used for all dependencies. No Spring context or database
 * is loaded — these tests run in milliseconds.</p>
 */
@ExtendWith(MockitoExtension.class)
class OrderServiceImplTest {

    // ── Test naming: givenContext_whenAction_thenExpectedOutcome ──────────

    @Test
    @DisplayName("Given valid request, when createOrder, then saves and returns order")
    void givenValidRequest_whenCreateOrder_thenSavesAndReturnsOrder() {
        // Arrange — set up the world for this test
        ...
        // Act — call the method under test
        ...
        // Assert — verify the outcome
        ...
    }

    @ParameterizedTest
    @NullSource
    @ValueSource(longs = {0L, -1L, -100L})
    @DisplayName("Given invalid customer ID, when createOrder, then throws exception")
    void givenInvalidCustomerId_whenCreateOrder_thenThrowsException(Long customerId) {
        // Tests multiple bad inputs with one test method
    }
}
```

### Integration Tests — @SpringBootTest + Testcontainers

```java
/**
 * Integration test for the orders REST endpoint.
 *
 * <p>Starts the full Spring context and a real PostgreSQL database via
 * Testcontainers. Tests the complete request → response cycle.</p>
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class OrderControllerIntegrationTest {

    @Test
    @DisplayName("POST /api/v1/orders — valid request should return HTTP 201")
    void givenValidRequest_whenPostOrder_thenReturns201() throws Exception {
        mockMvc.perform(post("/api/v1/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {
                        "customerId": 1,
                        "items": ["product-A", "product-B"]
                    }
                    """))
               .andExpect(status().isCreated())
               .andExpect(jsonPath("$.id").isNotEmpty())
               .andExpect(jsonPath("$.status").value("PENDING"));
    }
}
```

---

## 7. Code Quality Rules (Quick Reference)

| Rule | Detail |
|------|--------|
| Field injection | Never — use constructor injection |
| Magic numbers/strings | Use enums or named constants |
| Method length | ≤ 20 lines — extract to private helpers |
| Class length | ≤ 300 lines — split by responsibility |
| Exception swallowing | Never — always log or rethrow |
| Logging | SLF4J only — never `System.out.println` |
| Nulls | Use `Optional<T>` for nullable returns — never return `null` from public methods |
| SQL in strings | Use JPQL with named parameters — never concatenate |
