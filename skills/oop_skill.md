---
name: Object-Oriented Programming (OOP) Skill
version: 1.0
description: >
  Deep dive into all four OOP pillars: Encapsulation, Abstraction, Inheritance,
  and Polymorphism. Covers design patterns, SOLID principles, real-world examples
  in Java, Python, and JavaScript, and anti-patterns to avoid.
applies_to: [java, python, javascript, oop, design-patterns, solid]
tags: [oop, encapsulation, abstraction, inheritance, polymorphism, design-patterns]
---

# Object-Oriented Programming (OOP) Skill — v1.0

---

## 1. Encapsulation — Data Hiding & Control

**Goal:** Hide internal details, expose only what's necessary.

### 1.1 Encapsulation in Java

```java
/**
 * ✗ WRONG: Public fields expose internal state
 */
public class BadBankAccount {
    public String accountNumber;
    public BigDecimal balance;
    public List<Transaction> transactions;

    // Anyone can directly modify these, breaking invariants
}

/**
 * ✓ CORRECT: Private fields + controlled access
 */
public class BankAccount {
    // Private: Only this class can access
    private final String accountNumber;
    private BigDecimal balance;
    private final List<Transaction> transactions = new ArrayList<>();

    public BankAccount(String accountNumber, BigDecimal initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
    }

    // Public API: Controlled access
    public String getAccountNumber() {
        return accountNumber;  // Read-only
    }

    public BigDecimal getBalance() {
        return balance;  // Current state
    }

    public void deposit(BigDecimal amount) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Deposit must be positive");
        }
        balance = balance.add(amount);
        transactions.add(new Transaction("DEPOSIT", amount));
    }

    public void withdraw(BigDecimal amount) {
        if (amount.compareTo(balance) > 0) {
            throw new InsufficientFundsException("Not enough balance");
        }
        balance = balance.subtract(amount);
        transactions.add(new Transaction("WITHDRAW", amount));
    }

    public List<Transaction> getTransactionHistory() {
        // Return unmodifiable copy, not the original list
        return Collections.unmodifiableList(transactions);
    }
}
```

### 1.2 Encapsulation in Python

```python
class BankAccount:
    """
    Encapsulation example in Python.

    Private attributes use name mangling (_BankAccount__balance).
    Properties provide controlled access.
    """

    def __init__(self, account_number: str, initial_balance: Decimal):
        self.__account_number = account_number  # Private (name-mangled)
        self.__balance = initial_balance
        self.__transactions = []

    @property
    def account_number(self) -> str:
        """Get account number (read-only)."""
        return self.__account_number

    @property
    def balance(self) -> Decimal:
        """Get current balance (read-only)."""
        return self.__balance

    def deposit(self, amount: Decimal) -> None:
        """Deposit money with validation."""
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.__balance += amount
        self.__transactions.append({"type": "DEPOSIT", "amount": amount})

    def withdraw(self, amount: Decimal) -> None:
        """Withdraw money with validation."""
        if amount > self.__balance:
            raise ValueError("Insufficient funds")
        self.__balance -= amount
        self.__transactions.append({"type": "WITHDRAW", "amount": amount})

    def get_transaction_history(self) -> list:
        """Get transaction history (read-only copy)."""
        return self.__transactions.copy()
```

---

## 2. Abstraction — Hide Complexity

**Goal:** Simplify interface, hide implementation details.

### 2.1 Abstraction in Java

```java
/**
 * Abstraction: Database interface hides implementation.
 */
public interface OrderRepository {
    /**
     * Save an order (implementation details hidden).
     */
    Order save(Order order);

    /**
     * Find order by ID.
     */
    Optional<Order> findById(Long id);

    /**
     * Delete order.
     */
    void delete(Long id);
}

/**
 * PostgreSQL implementation of interface.
 */
public class PostgreSqlOrderRepository implements OrderRepository {
    private final DataSource dataSource;

    @Override
    public Order save(Order order) {
        // Implementation: JDBC queries, transactions, etc.
        String sql = "INSERT INTO orders (...) VALUES (...)";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            // ... execution details hidden
            return order;
        } catch (SQLException e) {
            throw new PersistenceException("Failed to save order", e);
        }
    }

    @Override
    public Optional<Order> findById(Long id) {
        // Implementation hidden
        // ... database query
        return Optional.of(order);
    }

    @Override
    public void delete(Long id) {
        // Implementation hidden
    }
}

/**
 * MongoDB implementation of same interface.
 */
public class MongoOrderRepository implements OrderRepository {
    private final MongoCollection<Document> collection;

    @Override
    public Order save(Order order) {
        // Implementation: MongoDB queries, etc.
        // BUT: Same interface, different implementation
        Document doc = new Document("_id", order.getId());
        collection.insertOne(doc);
        return order;
    }

    // ... other methods
}

/**
 * Service uses abstraction, not concrete implementation.
 */
@Service
public class OrderService {
    private final OrderRepository repository;  // Depends on abstraction, not concrete class

    public OrderService(OrderRepository repository) {
        this.repository = repository;  // Works with ANY implementation
    }

    public Order createOrder(CreateOrderRequest request) {
        Order order = new Order();
        // ... populate order

        return repository.save(order);  // Calls abstract method
        // Works same whether using PostgreSQL, MongoDB, or in-memory
    }
}
```

### 2.2 Abstraction in Python

```python
from abc import ABC, abstractmethod
from typing import Optional


class OrderRepository(ABC):
    """Abstract base class defines interface."""

    @abstractmethod
    def save(self, order: Order) -> Order:
        """Save an order (implementation hidden)."""
        pass

    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[Order]:
        """Find order by ID (implementation hidden)."""
        pass

    @abstractmethod
    def delete(self, order_id: int) -> None:
        """Delete an order (implementation hidden)."""
        pass


class PostgreSqlOrderRepository(OrderRepository):
    """PostgreSQL implementation."""

    def save(self, order: Order) -> Order:
        # Implementation details hidden
        sql = "INSERT INTO orders (...) VALUES (...)"
        # ... execute with psycopg2
        return order

    def find_by_id(self, order_id: int) -> Optional[Order]:
        # ... fetch from PostgreSQL
        return order

    def delete(self, order_id: int) -> None:
        # ... delete from PostgreSQL
        pass


class OrderService:
    """Service depends on abstraction."""

    def __init__(self, repository: OrderRepository):
        self.repository = repository  # Any implementation

    def create_order(self, request: CreateOrderRequest) -> Order:
        order = Order(**request.dict())
        return self.repository.save(order)  # Works with any implementation
```

---

## 3. Inheritance — Hierarchy & Reuse

**Goal:** Create hierarchy, reuse code through parent classes.

### 3.1 Inheritance in Java

```java
/**
 * Base class: Common payment behavior.
 */
public abstract class Payment {
    protected final String transactionId;
    protected final BigDecimal amount;
    protected final String currency;
    protected PaymentStatus status;

    protected Payment(String transactionId, BigDecimal amount, String currency) {
        this.transactionId = transactionId;
        this.amount = amount;
        this.currency = currency;
        this.status = PaymentStatus.PENDING;
    }

    /**
     * Common behavior: Log transaction.
     */
    protected final void logTransaction() {
        System.out.printf("Transaction %s: %s %s (status: %s)%n",
                transactionId, amount, currency, status);
    }

    /**
     * Abstract method: Subclasses must implement.
     */
    public abstract PaymentResult process();

    /**
     * Hook method: Subclasses can override.
     */
    protected void onPaymentSuccess() {
        // Default implementation: subclasses can override
        sendNotification("Payment successful");
    }

    protected void sendNotification(String message) {
        System.out.println("Notification: " + message);
    }
}

/**
 * Credit card payment: Specialized payment.
 */
public class CreditCardPayment extends Payment {
    private final String cardNumber;
    private final String cvv;

    public CreditCardPayment(String transactionId, BigDecimal amount,
                             String currency, String cardNumber, String cvv) {
        super(transactionId, amount, currency);
        this.cardNumber = maskCardNumber(cardNumber);
        this.cvv = cvv;
    }

    @Override
    public PaymentResult process() {
        logTransaction();  // Inherited common behavior

        try {
            // Credit card specific logic
            validateCard();
            chargeCard();
            status = PaymentStatus.SUCCESS;
            onPaymentSuccess();  // Call hook method
            return PaymentResult.success(transactionId);

        } catch (CardException e) {
            status = PaymentStatus.FAILED;
            return PaymentResult.failure(e.getMessage());
        }
    }

    private void validateCard() throws CardException {
        if (cardNumber.isEmpty() || cvv.isEmpty()) {
            throw new CardException("Invalid card");
        }
    }

    private void chargeCard() {
        // Credit card charging logic
    }

    private String maskCardNumber(String cardNumber) {
        return cardNumber.substring(0, 4) + "****" + cardNumber.substring(12);
    }
}

/**
 * Bank transfer: Different specialization.
 */
public class BankTransferPayment extends Payment {
    private final String bankAccount;
    private final String routingNumber;

    public BankTransferPayment(String transactionId, BigDecimal amount,
                               String currency, String bankAccount, String routingNumber) {
        super(transactionId, amount, currency);
        this.bankAccount = bankAccount;
        this.routingNumber = routingNumber;
    }

    @Override
    public PaymentResult process() {
        logTransaction();  // Inherited

        try {
            validateBankAccount();
            transferFunds();
            status = PaymentStatus.SUCCESS;
            return PaymentResult.success(transactionId);

        } catch (BankException e) {
            status = PaymentStatus.FAILED;
            return PaymentResult.failure(e.getMessage());
        }
    }

    // Bank transfer specific methods
}
```

### 3.2 Multi-Level Inheritance

```java
/**
 * Hierarchy: Animal -> Mammal -> Dog
 *
 * ✓ Keep hierarchies shallow (max 2-3 levels)
 */
public abstract class Animal {
    protected String name;

    public abstract void makeSound();

    public void move() {
        System.out.println(name + " is moving");
    }
}

public abstract class Mammal extends Animal {
    public void nurse() {
        System.out.println(name + " is nursing");
    }
}

public class Dog extends Mammal {
    @Override
    public void makeSound() {
        System.out.println(name + " barks");
    }
}
```

---

## 4. Polymorphism — Many Forms

**Goal:** Same interface, different implementations.

### 4.1 Method Overriding (Runtime Polymorphism)

```java
/**
 * Polymorphism: Same method, different behaviors.
 */
public class PaymentProcessor {
    public void processPayment(Payment payment) {
        // Compiler: Knows it's a Payment
        // Runtime: Knows actual type (CreditCardPayment, BankTransferPayment, etc.)
        PaymentResult result = payment.process();  // Calls actual subclass method
        System.out.println("Payment result: " + result);
    }
}

// Usage:
Payment creditCard = new CreditCardPayment(...);
Payment bankTransfer = new BankTransferPayment(...);
Payment wallet = new DigitalWalletPayment(...);

PaymentProcessor processor = new PaymentProcessor();
processor.processPayment(creditCard);     // Calls CreditCardPayment.process()
processor.processPayment(bankTransfer);   // Calls BankTransferPayment.process()
processor.processPayment(wallet);         // Calls DigitalWalletPayment.process()

// Output:
// Payment result: SUCCESS (credit card processed)
// Payment result: PENDING (bank transfer initiated)
// Payment result: SUCCESS (wallet charged)
```

### 4.2 Interface Polymorphism

```java
/**
 * Multiple implementations of same interface.
 */
public interface Logger {
    void log(String message);
}

public class ConsoleLogger implements Logger {
    @Override
    public void log(String message) {
        System.out.println(message);
    }
}

public class FileLogger implements Logger {
    @Override
    public void log(String message) {
        // Write to file
    }
}

public class DatabaseLogger implements Logger {
    @Override
    public void log(String message) {
        // Write to database
    }
}

/**
 * Service uses Logger interface, not specific implementation.
 */
public class OrderService {
    private final Logger logger;

    public OrderService(Logger logger) {
        this.logger = logger;  // Any logger works
    }

    public void createOrder(OrderRequest request) {
        logger.log("Creating order...");  // Works with any Logger implementation
        // ... create order
        logger.log("Order created");
    }
}

// Usage:
OrderService service1 = new OrderService(new ConsoleLogger());       // Logs to console
OrderService service2 = new OrderService(new FileLogger());          // Logs to file
OrderService service3 = new OrderService(new DatabaseLogger());      // Logs to DB
// Same service, different behaviors
```

---

## 5. SOLID Principles

| Principle | Meaning | Example |
|-----------|---------|---------|
| **S** | Single Responsibility | Class has one reason to change |
| **O** | Open/Closed | Open for extension, closed for modification |
| **L** | Liskov Substitution | Subtypes replaceable for supertypes |
| **I** | Interface Segregation | Small focused interfaces |
| **D** | Dependency Inversion | Depend on abstractions, not concretions |

### 5.1 Single Responsibility Principle

```java
/**
 * ✗ WRONG: User class does too much
 */
public class User {
    private String username;
    private String password;

    // ✗ Validation logic (SRP violation)
    public boolean isValidPassword() {
        return password.length() >= 8;
    }

    // ✗ Database logic (SRP violation)
    public void saveToDatabase() {
        // Save user to DB
    }

    // ✗ Email logic (SRP violation)
    public void sendWelcomeEmail() {
        // Send email
    }
}

/**
 * ✓ CORRECT: Separate concerns
 */
public class User {
    private String username;
    private String password;
}

public class PasswordValidator {
    public boolean isValid(String password) {
        return password.length() >= 8;
    }
}

public class UserRepository {
    public void save(User user) {
        // Database logic
    }
}

public class EmailService {
    public void sendWelcomeEmail(User user) {
        // Email logic
    }
}
```

---

## 6. Design Patterns

### 6.1 Factory Pattern

```java
/**
 * Factory: Create objects without specifying concrete classes.
 */
public class PaymentFactory {
    public static Payment createPayment(PaymentType type, PaymentData data) {
        return switch (type) {
            case CREDIT_CARD -> new CreditCardPayment(
                    data.getTransactionId(),
                    data.getAmount(),
                    data.getCurrency(),
                    data.getCardNumber(),
                    data.getCvv()
            );

            case BANK_TRANSFER -> new BankTransferPayment(
                    data.getTransactionId(),
                    data.getAmount(),
                    data.getCurrency(),
                    data.getBankAccount(),
                    data.getRoutingNumber()
            );

            case WALLET -> new DigitalWalletPayment(
                    data.getTransactionId(),
                    data.getAmount(),
                    data.getCurrency(),
                    data.getWalletId()
            );

            default -> throw new IllegalArgumentException("Unknown payment type");
        };
    }
}

// Usage:
Payment payment = PaymentFactory.createPayment(
        PaymentType.CREDIT_CARD,
        new PaymentData(...)
);
```

### 6.2 Strategy Pattern

```java
/**
 * Strategy: Different algorithms, same interface.
 */
public interface DiscountStrategy {
    BigDecimal calculateDiscount(Order order);
}

public class VolumeDiscount implements DiscountStrategy {
    @Override
    public BigDecimal calculateDiscount(Order order) {
        if (order.getItems().size() > 10) {
            return order.getTotalAmount().multiply(BigDecimal.valueOf(0.10));  // 10%
        }
        return BigDecimal.ZERO;
    }
}

public class LoyaltyDiscount implements DiscountStrategy {
    @Override
    public BigDecimal calculateDiscount(Order order) {
        if (order.getCustomer().isLoyaltyMember()) {
            return order.getTotalAmount().multiply(BigDecimal.valueOf(0.15));  // 15%
        }
        return BigDecimal.ZERO;
    }
}

public class Order {
    private DiscountStrategy discountStrategy;

    public Order(DiscountStrategy discountStrategy) {
        this.discountStrategy = discountStrategy;
    }

    public BigDecimal getFinalAmount() {
        BigDecimal total = getTotalAmount();
        BigDecimal discount = discountStrategy.calculateDiscount(this);
        return total.subtract(discount);
    }
}
```

---

## 7. OOP Checklist

✅ Hide implementation, expose interface (Encapsulation)
✅ Create abstractions for complex logic (Abstraction)
✅ Reuse code through inheritance (Inheritance)
✅ Design for substitutability (Polymorphism)
✅ Follow SOLID principles
✅ Use composition over inheritance when suitable
✅ Keep inheritance hierarchies shallow
✅ Implement interfaces for contracts
✅ Use abstract classes for shared behavior
✅ Avoid deep coupling
✅ Name classes by responsibility, not implementation
✅ Keep classes focused and cohesive
✅ Design for extensibility, not modification
✅ Test behavior, not implementation
✅ Document contracts (Javadoc, docstrings)
