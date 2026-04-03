---
name: SonarQube & Security Vulnerability Skill
version: 1.0
description: >
  SonarQube rules, security vulnerabilities, OWASP Top 10, secure coding patterns.
  Covers code smells, bugs, vulnerabilities, and how to write secure code across languages.
applies_to: [java, python, javascript, security, code-quality, sonarqube, owasp]
tags: [security, vulnerabilities, sonarqube, owasp, secure-coding, sqli, xss]
---

# SonarQube & Security Vulnerability Skill — v1.0

---

## 1. Common Security Vulnerabilities (OWASP Top 10)

### 1.1 SQL Injection — A03:2021

**Vulnerability:** Attacker injects SQL commands through user input.

```java
// ✗ VULNERABLE: String concatenation
String query = "SELECT * FROM orders WHERE customer_id = " + customerId;
ResultSet rs = stmt.executeQuery(query);
// Attack: customerId = "1 OR 1=1" → Returns all orders

// ✓ SECURE: Use parameterized queries
String query = "SELECT * FROM orders WHERE customer_id = ?";
PreparedStatement pstmt = connection.prepareStatement(query);
pstmt.setInt(1, customerId);
ResultSet rs = pstmt.executeQuery();
```plaintext

```python
# ✗ VULNERABLE: String formatting
query = f"SELECT * FROM orders WHERE customer_id = {customer_id}"
cursor.execute(query)
# Attack: customer_id = "1 OR 1=1" → Returns all orders

# ✓ SECURE: Use parameterized queries
query = "SELECT * FROM orders WHERE customer_id = %s"
cursor.execute(query, (customer_id,))
```plaintext

```typescript
// ✗ VULNERABLE: String concatenation in ORM
const orders = await Order.find(`WHERE customer_id = ${customerId}`);

// ✓ SECURE: Use ORM query builders
const orders = await Order.find({ where: { customerId } });
```plaintext

**SonarQube Rule:** `java:S2077` (SQL Injection), `python:S3649`, `typescript:S3649`

---

### 1.2 Cross-Site Scripting (XSS) — A03:2021

**Vulnerability:** Attacker injects malicious JavaScript that executes in users' browsers.

```javascript
// ✗ VULNERABLE: Direct innerHTML assignment
document.getElementById('output').innerHTML = userInput;
// Attack: userInput = "<img src=x onerror='steal credentials'>"

// ✓ SECURE: Use textContent for text, or sanitize HTML
document.getElementById('output').textContent = userInput;

// ✓ SECURE: If HTML is needed, use DOMPurify library
import DOMPurify from 'dompurify';
document.getElementById('output').innerHTML = DOMPurify.sanitize(userInput);
```plaintext

```typescript
// React: XSS example

// ✗ VULNERABLE: dangerouslySetInnerHTML without sanitization
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✓ SECURE: Use text content (escapes automatically)
<div>{userInput}</div>

// ✓ SECURE: Sanitize before dangerouslySetInnerHTML
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />
```plaintext

**SonarQube Rules:** `typescript:S2091` (XSS), `java:S5131`

---

### 1.3 Insecure Deserialization — A08:2021

**Vulnerability:** Deserializing untrusted data can lead to code execution.

```java
// ✗ VULNERABLE: ObjectInputStream from untrusted source
ObjectInputStream ois = new ObjectInputStream(untrustedData);
Object obj = ois.readObject();  // Can execute arbitrary code

// ✓ SECURE: Use safer alternatives (JSON with schema validation)
ObjectMapper mapper = new ObjectMapper();
mapper.readValue(jsonString, Order.class);  // Type-safe

// ✓ SECURE: Implement ObjectInputFilter
ObjectInputStream ois = new ObjectInputStream(untrustedData);
ois.setObjectInputFilter(info -> {
    Class<?> clazz = info.getClass();
    return allowedClasses.contains(clazz.getName());
});
Object obj = ois.readObject();
```plaintext

**SonarQube Rule:** `java:S2094` (Unsafe Serialization)

---

### 1.4 Authentication & Authorization Issues — A01:2021

**Vulnerability:** Weak or missing authentication/authorization checks.

```java
// ✗ VULNERABLE: No authentication check
@GetMapping("/api/orders/{id}")
public Order getOrder(@PathVariable Long id) {
    return orderRepository.findById(id).orElseThrow();
}
// Any user can access any order

// ✓ SECURE: Authenticate user and authorize access
@GetMapping("/api/orders/{id}")
public ResponseEntity<Order> getOrder(
        @PathVariable Long id,
        @AuthenticationPrincipal UserDetails user) {

    Order order = orderRepository.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("Order not found"));

    // Check authorization: User can only see their own orders
    if (!order.getCustomerId().equals(user.getId())) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
    }

    return ResponseEntity.ok(order);
}
```plaintext

```python
# ✗ VULNERABLE: No permission check
@app.route('/api/orders/<int:order_id>')
async def get_order(order_id: int):
    order = await db.orders.find_one({"id": order_id})
    return order  # Anyone can view any order

# ✓ SECURE: Authenticate and authorize
@app.route('/api/orders/<int:order_id>')
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    order = await db.orders.find_one({"id": order_id})

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Verify ownership
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return order
```plaintext

**SonarQube Rules:** `java:S3649` (Auth), `python:S5131`

---

## 2. SonarQube Rules & Code Smells

### 2.1 Code Smell: Duplicate Code

```java
// ✗ VULNERABLE: Duplicate calculation logic

public BigDecimal calculateOrderTotal(Order order) {
    BigDecimal subtotal = BigDecimal.ZERO;
    for (OrderItem item : order.getItems()) {
        subtotal = subtotal.add(
                item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity()))
        );
    }
    return subtotal.add(order.getShippingCost()).add(order.getTax());
}

public BigDecimal calculateInvoiceTotal(Invoice invoice) {
    BigDecimal subtotal = BigDecimal.ZERO;
    for (InvoiceItem item : invoice.getItems()) {
        subtotal = subtotal.add(
                item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity()))
        );
    }
    return subtotal.add(invoice.getShippingCost()).add(invoice.getTax());
}

// ✓ SECURE: Extract common logic

private BigDecimal calculateSubtotal(List<? extends LineItem> items) {
    return items.stream()
            .map(item -> item.getUnitPrice()
                    .multiply(BigDecimal.valueOf(item.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
}

public BigDecimal calculateOrderTotal(Order order) {
    return calculateSubtotal(order.getItems())
            .add(order.getShippingCost())
            .add(order.getTax());
}

public BigDecimal calculateInvoiceTotal(Invoice invoice) {
    return calculateSubtotal(invoice.getItems())
            .add(invoice.getShippingCost())
            .add(invoice.getTax());
}
```plaintext

**SonarQube Rule:** `java:S1121` (Duplicated Blocks)

### 2.2 Code Smell: Cognitive Complexity

```java
// ✗ VULNERABLE: High cognitive complexity (too many nested conditions)

public void processOrder(Order order) {
    if (order.getStatus().equals("PENDING")) {
        if (order.getItems().size() > 0) {
            if (order.getTotalAmount().compareTo(BigDecimal.ZERO) > 0) {
                if (order.getCustomer() != null) {
                    if (order.getDeliveryAddress() != null) {
                        if (paymentGateway.canProcess(order.getTotalAmount())) {
                            processPayment(order);
                            confirmOrder(order);
                        } else {
                            handleInsufficientFunds(order);
                        }
                    }
                }
            }
        }
    }
}

// ✓ SECURE: Reduce complexity by extracting validation

private void processOrder(Order order) {
    if (!isOrderValid(order)) {
        return;
    }

    if (!canProcessPayment(order)) {
        handleInsufficientFunds(order);
        return;
    }

    processPayment(order);
    confirmOrder(order);
}

private boolean isOrderValid(Order order) {
    return order.getStatus().equals("PENDING")
            && !order.getItems().isEmpty()
            && order.getTotalAmount().compareTo(BigDecimal.ZERO) > 0
            && order.getCustomer() != null
            && order.getDeliveryAddress() != null;
}

private boolean canProcessPayment(Order order) {
    return paymentGateway.canProcess(order.getTotalAmount());
}
```plaintext

**SonarQube Rule:** `java:S3776` (Cognitive Complexity)

### 2.3 Code Smell: Method Too Long

```java
// ✗ VULNERABLE: Method too long (>20 lines)

public void processOrder(Order order) {
    // 50+ lines of logic mixed together
    validate();
    reserveInventory();
    processPayment();
    updateDatabase();
    sendNotification();
}

// ✓ SECURE: Break into smaller methods (≤20 lines each)

public void processOrder(Order order) {
    Order validated = validateOrder(order);
    Order inventoryReserved = reserveInventory(validated);
    Order paid = processPayment(inventoryReserved);
    Order persisted = updateDatabase(paid);
    sendNotification(persisted);
}

private Order validateOrder(Order order) { /* 5 lines */ }
private Order reserveInventory(Order order) { /* 5 lines */ }
private Order processPayment(Order order) { /* 8 lines */ }
private Order updateDatabase(Order order) { /* 3 lines */ }
private void sendNotification(Order order) { /* 4 lines */ }
```plaintext

**SonarQube Rule:** `java:S138` (Method too long)

---

## 3. Secure Coding Patterns

### 3.1 Input Validation

```java
// ✓ SECURE: Validate all inputs

@PostMapping("/api/orders")
public ResponseEntity<Order> createOrder(@Valid @RequestBody CreateOrderRequest request) {
    // @Valid triggers validation annotations
    // Validates: @NotNull, @NotBlank, @Min, @Max, @Size, @Email, etc.

    // Additional custom validation
    if (request.getTotalAmount().compareTo(BigDecimal.ZERO) <= 0) {
        throw new ValidationException("Total amount must be positive");
    }

    if (request.getItems().isEmpty()) {
        throw new ValidationException("Order must contain at least one item");
    }

    if (!isValidEmailDomain(request.getCustomerEmail())) {
        throw new ValidationException("Invalid email domain");
    }

    return ResponseEntity.ok(orderService.create(request));
}

private boolean isValidEmailDomain(String email) {
    // Whitelist valid domains
    return email.endsWith("@company.com") || email.endsWith("@trusted-partner.com");
}
```plaintext

```python
# ✓ SECURE: Validate all inputs with Pydantic

from pydantic import BaseModel, EmailStr, validator, conint

class CreateOrderRequest(BaseModel):
    """Order creation request with validation."""

    customer_id: conint(gt=0)  # Constraint: positive integer
    total_amount: float = Field(..., gt=0, le=999999.99)  # Positive, max 999999.99
    customer_email: EmailStr  # Must be valid email format
    items: List[OrderItemRequest] = Field(..., min_items=1, max_items=100)

    @validator('customer_email')
    @classmethod
    def validate_email_domain(cls, v):
        """Validate email domain is whitelisted."""
        allowed_domains = ['company.com', 'trusted-partner.com']
        domain = v.split('@')[1]

        if domain not in allowed_domains:
            raise ValueError(f'Email domain {domain} not allowed')

        return v
```plaintext

### 3.2 Sensitive Data Protection

```java
// ✗ VULNERABLE: Logging sensitive data
log.info("Processing order: {}", orderJson);  // May contain credit card

// ✓ SECURE: Don't log sensitive data
log.info("Processing order with ID: {}", order.getId());  // Safe

// ✓ SECURE: Mask sensitive data in logs
private String maskCardNumber(String cardNumber) {
    if (cardNumber == null || cardNumber.length() < 4) {
        return "****";
    }
    return cardNumber.substring(0, 4) + "****";
}

log.info("Payment with card: {}", maskCardNumber(cardNumber));
```plaintext

```java
// ✓ SECURE: Never store passwords in plain text
@Entity
public class User {
    private String email;

    // ✗ WRONG: Store passwords in plain text
    // private String password;

    // ✓ RIGHT: Hash passwords with strong algorithm (bcrypt)
    private String passwordHash;

    public void setPassword(String plainPassword) {
        this.passwordHash = BCrypt.hashpw(plainPassword, BCrypt.gensalt());
    }

    public boolean checkPassword(String plainPassword) {
        return BCrypt.checkpw(plainPassword, this.passwordHash);
    }
}
```plaintext

### 3.3 Rate Limiting & Throttling

```java
// ✓ SECURE: Implement rate limiting

@Component
public class RateLimitInterceptor implements HandlerInterceptor {

    private final RateLimiter rateLimiter = RateLimiter.create(10);  // 10 req/sec

    @Override
    public boolean preHandle(HttpServletRequest request,
                            HttpServletResponse response,
                            Object handler) throws Exception {

        String clientId = getClientId(request);  // IP or API key

        if (!rateLimiter.tryAcquire()) {
            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            return false;
        }

        return true;
    }

    private String getClientId(HttpServletRequest request) {
        return request.getHeader("X-Client-ID") != null
                ? request.getHeader("X-Client-ID")
                : request.getRemoteAddr();
    }
}
```plaintext

---

## 4. SonarQube Configuration

### 4.1 pom.xml (Maven)

```xml
<properties>
    <sonar.projectKey>com.example:awesome-prompts</sonar.projectKey>
    <sonar.host.url>https://sonarqube.company.com</sonar.host.url>
    <sonar.login>${SONAR_TOKEN}</sonar.login>
    <sonar.coverage.exclusions>**/config/**,**/dto/**</sonar.coverage.exclusions>
    <sonar.exclusions>**/generated/**,**/target/**</sonar.exclusions>
</properties>

<plugin>
    <groupId>org.sonarsource.scanner.maven</groupId>
    <artifactId>sonar-maven-plugin</artifactId>
    <version>3.10.0.2594</version>
</plugin>
```plaintext

### 4.2 Run SonarQube Analysis

```bash
# Analyze code with SonarQube
mvn clean verify sonar:sonar \
    -Dsonar.host.url=https://sonarqube.company.com \
    -Dsonar.login=$SONAR_TOKEN \
    -Dsonar.projectVersion=2.0.0

# For Python
sonar-scanner \
    -Dsonar.projectKey=awesome-prompts \
    -Dsonar.sources=app \
    -Dsonar.host.url=https://sonarqube.company.com \
    -Dsonar.login=$SONAR_TOKEN

# For JavaScript
sonar-scanner \
    -Dsonar.projectKey=awesome-prompts-js \
    -Dsonar.sources=src \
    -Dsonar.host.url=https://sonarqube.company.com \
    -Dsonar.login=$SONAR_TOKEN
```plaintext

---

## 5. Security Checklist

✅ Never concatenate SQL queries — use parameterized queries
✅ Never embed user input in HTML — use text nodes or sanitize
✅ Validate all user inputs on the server side
✅ Authenticate every request requiring access control
✅ Authorize users to only access their own resources
✅ Don't log sensitive data (passwords, credit cards, tokens)
✅ Hash passwords with bcrypt or similar strong algorithm
✅ Use HTTPS for all communications
✅ Implement rate limiting to prevent brute force/DoS
✅ Use prepared statements for all database queries
✅ Escape output when rendering user-supplied content
✅ Implement input length limits to prevent buffer overflows
✅ Don't expose stack traces in production errors
✅ Keep dependencies updated for security patches
✅ Use SonarQube to catch code smells and vulnerabilities
✅ Review security rules regularly (OWASP, CWE)
