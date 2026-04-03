---
name: Spring Framework & Camel Integration Skill
version: 1.0
description: >
  Integration patterns for Apache Camel with Spring Framework and Spring Boot.
  Covers Spring beans in Camel routes, dependency injection, transactions, async
  processing, error handling, and production-ready patterns.
applies_to: [java, apache-camel, spring-boot, spring-framework, integration]
tags: [camel, spring-boot, spring, integration, beans, transactions, async]
---

# Spring Framework & Camel Integration Skill — v1.0

---

## 1. Spring Boot Camel Starter

### 1.1 Maven Setup

```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-spring-boot-starter</artifactId>
    <version>4.0.0</version>
</dependency>

<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-spring-boot</artifactId>
    <version>4.0.0</version>
</dependency>

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

### 1.2 Spring Boot Auto-Configuration

```java
/**
 * Spring Boot application with automatic Camel configuration.
 */
@SpringBootApplication
public class CamelSpringApplication {

    public static void main(String[] args) {
        SpringApplication.run(CamelSpringApplication.class, args);
    }

    /**
     * Customize Camel context.
     */
    @Bean
    public CamelContextConfiguration camelContextConfiguration() {
        return new CamelContextConfiguration() {
            @Override
            public void configureCamelContext(CamelContext camelContext) throws Exception {
                // Custom Camel configuration
                camelContext.setStreamCaching(true);
                camelContext.setTracing(false);
            }

            @Override
            public void onCamelContextStarted(CamelContext camelContext, boolean alreadyStarted) throws Exception {
                log.info("Camel context started with Spring Boot");
            }
        };
    }
}
```

---

## 2. Dependency Injection in Camel Routes

### 2.1 Using Spring Beans in Routes

```java
/**
 * Service to be injected into Camel routes.
 */
@Service
public class OrderProcessingService {

    private final OrderRepository orderRepository;
    private final PaymentService paymentService;

    public OrderProcessingService(OrderRepository orderRepository, PaymentService paymentService) {
        this.orderRepository = orderRepository;
        this.paymentService = paymentService;
    }

    /**
     * Process an order.
     */
    public OrderResult processOrder(OrderRequest request) {
        Order order = new Order();
        order.setCustomerId(request.getCustomerId());
        order.setItems(request.getItems());
        order.setTotalAmount(calculateTotal(request.getItems()));

        Order saved = orderRepository.save(order);

        PaymentResult payment = paymentService.processPayment(
                saved.getId(),
                saved.getTotalAmount()
        );

        return OrderResult.builder()
                .orderId(saved.getId())
                .paymentId(payment.getTransactionId())
                .status("PROCESSED")
                .build();
    }

    private BigDecimal calculateTotal(List<OrderItem> items) {
        return items.stream()
                .map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}

/**
 * Camel route using injected Spring bean.
 */
@Configuration
public class OrderRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        from("direct:processOrder")
                .log("Processing order: ${body}")
                .to("bean:orderProcessingService?method=processOrder")
                .log("Order processed: ${body}");
    }
}
```

### 2.2 Constructor Injection Pattern

```java
/**
 * Camel route with constructor-injected dependencies.
 */
@Component
public class PaymentRoute extends RouteBuilder {

    private final PaymentGateway paymentGateway;
    private final AuditService auditService;

    public PaymentRoute(PaymentGateway paymentGateway, AuditService auditService) {
        this.paymentGateway = paymentGateway;
        this.auditService = auditService;
    }

    @Override
    public void configure() throws Exception {
        from("direct:processPayment")
                .process(exchange -> {
                    PaymentRequest request = exchange.getIn().getBody(PaymentRequest.class);
                    PaymentResult result = paymentGateway.charge(
                            request.getAmount(),
                            request.getCardToken()
                    );
                    exchange.setProperty("paymentResult", result);
                })
                .log("Payment processed: ${property.paymentResult}")
                .process(exchange -> {
                    PaymentResult result = exchange.getProperty("paymentResult", PaymentResult.class);
                    auditService.logPayment(result);
                })
                .choice()
                    .when(simple("${property.paymentResult.success} == true"))
                        .log("Payment successful")
                    .otherwise()
                        .log("Payment failed: ${property.paymentResult.errorMessage}")
                        .to("direct:handlePaymentFailure")
                .end();
    }
}
```

---

## 3. Spring Transactions with Camel

### 3.1 Transactional Routes

```java
/**
 * Camel route with Spring transaction management.
 */
@Configuration
public class TransactionalRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Create transactional template
        SpringTransactionPolicy transactionPolicy = new SpringTransactionPolicy();

        from("direct:saveOrderTransactional")
                .log("Saving order in transaction: ${body}")
                .policy(transactionPolicy)  // Wrap in Spring transaction
                .process(exchange -> {
                    OrderRequest request = exchange.getIn().getBody(OrderRequest.class);
                    Order order = new Order();
                    order.setCustomerId(request.getCustomerId());
                    order.setItems(request.getItems());
                    exchange.setProperty("order", order);
                })
                .to("bean:orderRepository?method=save")
                .log("Order saved: ${property.order.id}")
                .to("bean:inventoryService?method=reserve(${property.order})")
                .log("Inventory reserved")
                .choice()
                    .when(simple("${property.reserveSuccess} == false"))
                        .log("Reservation failed, rolling back")
                        .throwException(new Exception("Inventory reservation failed"))
                .end()
                .to("direct:sendOrderConfirmation");
    }
}
```

### 3.2 Transaction Policy Configuration

```java
/**
 * Configure Spring transaction policy.
 */
@Configuration
public class TransactionPolicyConfig {

    @Bean
    public SpringTransactionPolicy transactionPolicy(PlatformTransactionManager transactionManager) {
        SpringTransactionPolicy policy = new SpringTransactionPolicy();
        policy.setTransactionManager(transactionManager);
        policy.setPropagate(1);  // PROPAGATION_REQUIRED
        return policy;
    }

    @Bean
    public CamelContextConfiguration camelContextConfiguration(
            SpringTransactionPolicy transactionPolicy) {

        return new CamelContextConfiguration() {
            @Override
            public void configureCamelContext(CamelContext camelContext) throws Exception {
                camelContext.getRegistry().bind("transactionPolicy", transactionPolicy);
            }

            @Override
            public void onCamelContextStarted(CamelContext camelContext, boolean alreadyStarted) throws Exception {
                log.info("Transaction policy registered");
            }
        };
    }
}
```

---

## 4. Async Processing

### 4.1 Async Method in Camel

```java
/**
 * Spring service with async methods called from Camel routes.
 */
@Service
public class EmailService {

    @Async
    public void sendOrderConfirmation(Order order) {
        log.info("Sending confirmation email for order: {}", order.getId());
        try {
            Thread.sleep(2000);  // Simulate email sending
            log.info("Email sent successfully");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    @Async
    public void sendShippingNotification(Order order) {
        log.info("Sending shipping notification for order: {}", order.getId());
        // Send notification asynchronously
    }
}

/**
 * Camel route calling async methods.
 */
@Configuration
public class AsyncRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        from("direct:orderCompleted")
                .log("Order completed: ${body}")
                // Call async method (doesn't block)
                .to("bean:emailService?method=sendOrderConfirmation")
                // Continue immediately, email is sent in background
                .log("Notification sent, continuing with next task")
                .to("direct:updateInventory");

        from("direct:updateInventory")
                .log("Updating inventory for order: ${body}");
    }
}
```

### 4.2 Enable Async Processing

```java
/**
 * Enable async processing in Spring Boot.
 */
@SpringBootApplication
@EnableAsync
public class CamelAsyncApplication {

    public static void main(String[] args) {
        SpringApplication.run(CamelAsyncApplication.class, args);
    }

    @Bean
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("camel-async-");
        executor.initialize();
        return executor;
    }
}
```

---

## 5. Error Handling in Spring Context

### 5.1 Global Error Handler with Spring

```java
/**
 * Global error handler integrated with Spring.
 */
@Configuration
public class GlobalErrorHandling extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Global exception handler
        onException(ValidationException.class)
                .handled(true)
                .maximumRedeliveries(0)
                .log("Validation error: ${exception.message}")
                .to("bean:auditService?method=logValidationError(${body}, ${exception})");

        onException(DatabaseException.class)
                .handled(true)
                .maximumRedeliveries(3)
                .redeliveryDelay(1000)
                .backOffMultiplier(2.0)
                .log("Database error, retrying...")
                .to("bean:monitoringService?method=alertDatabaseError");

        onException(Exception.class)
                .handled(true)
                .log(LoggingLevel.ERROR, "Unexpected error: ${exception.message}")
                .to("bean:alertService?method=sendCriticalAlert");
    }
}
```

---

## 6. Spring Data JPA in Camel Routes

### 6.1 Entity Operations

```java
/**
 * Spring Data repository.
 */
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerId(Long customerId);

    @Query("SELECT o FROM Order o WHERE o.status = ?1 AND o.createdAt > ?2")
    List<Order> findRecentOrdersByStatus(String status, LocalDateTime since);
}

/**
 * Camel route using Spring Data.
 */
@Configuration
public class DatabaseRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        from("direct:getAllOrders")
                .process(exchange -> {
                    List<Order> orders = orderRepository.findAll();
                    exchange.getIn().setBody(orders);
                })
                .log("Found ${body.size} orders")
                .to("bean:orderTransformer?method=toJson");

        from("direct:getOrdersByCustomer")
                .process(exchange -> {
                    Long customerId = exchange.getIn().getHeader("customerId", Long.class);
                    List<Order> orders = orderRepository.findByCustomerId(customerId);
                    exchange.getIn().setBody(orders);
                });
    }
}
```

---

## 7. Spring Security with Camel

### 7.1 Authentication in Routes

```java
/**
 * Camel route with Spring Security.
 */
@Configuration
public class SecureRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        from("direct:secureOperation")
                .process(exchange -> {
                    // Get current authentication
                    Authentication auth = SecurityContextHolder.getContext().getAuthentication();

                    if (auth == null || !auth.isAuthenticated()) {
                        throw new SecurityException("User not authenticated");
                    }

                    String username = auth.getName();
                    List<String> roles = auth.getAuthorities().stream()
                            .map(GrantedAuthority::getAuthority)
                            .collect(Collectors.toList());

                    exchange.setProperty("username", username);
                    exchange.setProperty("roles", roles);

                    log.info("User {} with roles {} is performing operation", username, roles);
                })
                .log("Performing operation for user: ${property.username}")
                .to("bean:auditService?method=logOperation");
    }
}
```

---

## 8. Spring Boot Properties for Camel

### 8.1 application.yml Configuration

```yaml
spring:
  application:
    name: camel-spring-app
  jpa:
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        format_sql: true
        dialect: org.hibernate.dialect.PostgreSQL10Dialect
  datasource:
    url: jdbc:postgresql://localhost:5432/cameldb
    username: camel
    password: password

camel:
  springboot:
    name: camel-spring-app
    main-run-controller: true
    package-scan-enabled: true
    package-scan: com.example.camel.routes

  component:
    timer:
      timer-name: default
    bean:
      cache: true

  # Tracing and debugging
  trace:
    enabled: false
    standby: false

logging:
  level:
    org.apache.camel: INFO
    org.springframework: INFO
    org.hibernate: DEBUG
```

---

## 9. Health Checks with Camel

### 9.1 Spring Boot Actuator Integration

```java
/**
 * Custom health check for Camel routes.
 */
@Component
public class CamelRouteHealth implements HealthIndicator {

    private final CamelContext camelContext;

    public CamelRouteHealth(CamelContext camelContext) {
        this.camelContext = camelContext;
    }

    @Override
    public Health health() {
        if (camelContext.getRouteController().getControlledRoutes().isEmpty()) {
            return Health.down()
                    .withDetail("routes", "No routes found")
                    .build();
        }

        camelContext.getRoutes().forEach(route -> {
            if (!route.isStarted()) {
                return Health.down()
                        .withDetail("route", route.getId() + " is not started")
                        .build();
            }
        });

        return Health.up()
                .withDetail("camelVersion", camelContext.getVersion())
                .withDetail("routeCount", camelContext.getRoutes().size())
                .withDetail("routes", camelContext.getRoutes().stream()
                        .map(Route::getId)
                        .collect(Collectors.toList()))
                .build();
    }
}
```

### 9.2 application.yml Health Config

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,routes
  endpoint:
    health:
      show-details: always
    routes:
      enabled: true
```

---

## 10. Testing Camel Routes with Spring

### 10.1 Unit Test with Spring

```java
/**
 * Test Camel route with Spring Boot Test.
 */
@SpringBootTest
class OrderRouteTest {

    @Autowired
    private CamelContext camelContext;

    @MockBean
    private OrderService orderService;

    @Test
    void givenValidOrder_whenRouteExecutes_thenProcessSuccessfully() throws Exception {
        ProducerTemplate template = camelContext.createProducerTemplate();

        // Arrange
        OrderRequest request = OrderRequest.builder()
                .customerId(1L)
                .items(List.of(new OrderItem(1L, 2)))
                .build();

        when(orderService.processOrder(any())).thenReturn(
                OrderResult.builder()
                        .orderId(100L)
                        .status("PROCESSED")
                        .build()
        );

        // Act
        OrderResult result = template.requestBody("direct:processOrder", request, OrderResult.class);

        // Assert
        assertNotNull(result);
        assertEquals("PROCESSED", result.getStatus());
        verify(orderService, times(1)).processOrder(any());
    }
}
```

---

## 11. Spring Camel Integration Checklist

✅ Add camel-spring-boot-starter dependency
✅ Enable @EnableScheduling for timers
✅ Enable @EnableAsync for async methods
✅ Use constructor injection in RouteBuilder
✅ Register Spring beans with @Bean
✅ Use SpringTransactionPolicy for transactions
✅ Implement error handling with onException()
✅ Configure application.yml for Camel
✅ Use Spring Data repositories in routes
✅ Implement Spring Security integration
✅ Add health checks with HealthIndicator
✅ Use CamelTestSupport for testing
✅ Configure logging via Spring
✅ Use @Async for non-blocking operations
✅ Monitor with Spring Boot Actuator
