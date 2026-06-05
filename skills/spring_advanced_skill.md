---
name: Spring Framework Advanced Skill
version: 1.0
description: >
  Deep Spring Framework knowledge beyond Spring Boot basics. Covers IoC container
  internals, AOP, WebFlux/reactive, Spring Batch, Spring Cloud, Security, Events,
  custom auto-configuration, and debugging. Used by coding and health inspection agents.
applies_to: [java, spring, spring-boot, spring-webflux, spring-batch, spring-cloud, spring-security]
tags: [spring, aop, webflux, reactive, batch, cloud, security, ioc]
---

# Spring Framework Advanced Skill — v1.0

---

## 1. IoC Container — How It Really Works

Understanding the container lifecycle helps debug startup failures and bean wiring issues.

```java
Application starts
  → Reads @ComponentScan / @Bean / XML config
  → Creates BeanDefinition for each bean (metadata — not the instance yet)
  → Resolves dependencies between BeanDefinitions
  → Instantiates beans in dependency order
  → Injects dependencies (constructor → setter → field in that order)
  → Calls @PostConstruct methods
  → Application is ready

Application shuts down
  → Calls @PreDestroy methods
  → Destroys singletons in reverse creation order
```java

### Bean Scopes

```java
@Component
@Scope("singleton")    // default — one instance per application context
public class OrderService { }

@Component
@Scope("prototype")    // new instance every time it is requested from the context
public class OrderProcessor { }

// Web scopes — only valid in a web application context
@Component
@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestContext { }   // new instance per HTTP request

@Component
@Scope(value = WebApplicationContext.SCOPE_SESSION, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class UserSession { }      // one instance per HTTP session
```java

### Conditional Beans

```java
/**
 * Creates the notification sender appropriate for the current environment.
 *
 * <p>In production: real email sender.
 * In test/dev: a stub that just logs — no real emails sent.</p>
 */
@Configuration
public class NotificationConfig {

    /**
     * Real email sender — only active when spring.mail.host is configured.
     * This means it won't try to connect to an SMTP server in dev/test.
     */
    @Bean
    @ConditionalOnProperty(name = "spring.mail.host")
    public NotificationSender emailNotificationSender(JavaMailSender mailSender) {
        return new EmailNotificationSender(mailSender);
    }

    /**
     * Stub sender — used when no mail host is configured.
     * Logs the notification instead of sending it.
     */
    @Bean
    @ConditionalOnMissingBean(NotificationSender.class)
    public NotificationSender stubNotificationSender() {
        return (recipient, subject, message) -> {
            log.info("[STUB] Notification to {}: {}", recipient, subject);
            return true;
        };
    }
}
```java

---

## 2. Aspect-Oriented Programming (AOP)

AOP lets you add cross-cutting concerns (logging, timing, security checks, retry) to
methods without modifying those methods.

### Concepts

```java
@Aspect     — marks a class as containing advice
@Pointcut   — defines WHICH methods to intercept (the "where")
@Around     — runs before AND after the method (most powerful)
@Before     — runs before the method
@After      — runs after the method (whether it succeeds or fails)
@AfterReturning — runs after the method returns successfully
@AfterThrowing  — runs when the method throws an exception
```java

### Execution Timing Aspect (Practical Example)

```java
/**
 * Logs the execution time of any method annotated with {@code @Timed}.
 *
 * <p>Place {@code @Timed} on any service method to automatically log
 * how long it takes. Useful for identifying slow methods in production.</p>
 *
 * <p>Example usage:</p>
 * <pre>
 *   {@literal @}Timed
 *   public OrderResponse createOrder(CreateOrderRequest request) { ... }
 * </pre>
 */
@Aspect
@Component
@Slf4j
public class ExecutionTimingAspect {

    /**
     * Intercepts any method annotated with @Timed in any class.
     */
    @Around("@annotation(com.acme.annotation.Timed)")
    public Object measureExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().toShortString();
        long startTime    = System.currentTimeMillis();

        try {
            // Proceed runs the actual method
            Object result = joinPoint.proceed();
            long duration = System.currentTimeMillis() - startTime;
            log.info("[TIMING] {} completed in {}ms", methodName, duration);
            return result;

        } catch (Exception ex) {
            long duration = System.currentTimeMillis() - startTime;
            log.warn("[TIMING] {} failed after {}ms — {}", methodName, duration, ex.getMessage());
            throw ex;  // re-throw so normal exception handling still works
        }
    }
}
```java

### Retry Aspect

```java
/**
 * Automatically retries methods annotated with {@code @Retryable} on transient failures.
 *
 * <p>Uses exponential backoff: first retry after 1s, second after 2s, third after 4s.</p>
 */
@Aspect
@Component
@Slf4j
public class RetryAspect {

    @Around("@annotation(retryable)")
    public Object retryOnFailure(ProceedingJoinPoint joinPoint, Retryable retryable) throws Throwable {
        int maxAttempts    = retryable.maxAttempts();
        long delayMs       = retryable.initialDelayMs();
        String methodName  = joinPoint.getSignature().toShortString();

        Exception lastException = null;

        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                return joinPoint.proceed();

            } catch (Exception ex) {
                lastException = ex;
                log.warn("[RETRY] {} failed on attempt {}/{}: {}",
                         methodName, attempt, maxAttempts, ex.getMessage());

                if (attempt < maxAttempts) {
                    Thread.sleep(delayMs);
                    delayMs *= 2;  // exponential backoff
                }
            }
        }

        log.error("[RETRY] {} exhausted all {} attempts", methodName, maxAttempts);
        throw lastException;
    }
}
```java

---

## 3. Spring WebFlux — Reactive Programming

Use WebFlux when you need to handle thousands of concurrent connections with minimal threads.
Key types: `Mono<T>` (0 or 1 item) and `Flux<T>` (0 to N items).

### When to Use WebFlux vs MVC

```json
Spring MVC (servlet, blocking)  → Use when:
  - Team is comfortable with blocking/imperative code
  - Simpler CRUD app, low-to-medium concurrency
  - Using JDBC (blocking by nature)

Spring WebFlux (reactive, non-blocking)  → Use when:
  - High concurrency (thousands of simultaneous requests)
  - Composing multiple async I/O calls (microservice fan-out)
  - Using reactive DB drivers (R2DBC, MongoDB reactive)
  - Streaming responses (SSE, websockets)
```java

### Reactive REST Controller

```java
/**
 * Reactive REST controller for order operations.
 *
 * <p>Returns Mono/Flux instead of plain objects. Spring WebFlux subscribes
 * to these and writes the result to the HTTP response when it arrives —
 * without blocking a thread while waiting.</p>
 */
@RestController
@RequestMapping("/api/v1/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    /**
     * Returns a single order by ID.
     * Mono = 0 or 1 result. Returns 404 if empty.
     */
    @GetMapping("/{id}")
    public Mono<ResponseEntity<OrderResponse>> getOrder(@PathVariable Long id) {
        return orderService.findById(id)
            .map(order -> ResponseEntity.ok(order))
            .defaultIfEmpty(ResponseEntity.notFound().build());
    }

    /**
     * Returns all orders for a customer as a stream.
     * Flux = 0 to N results. Streams items as they are produced.
     */
    @GetMapping("/stream")
    @Produces(MediaType.TEXT_EVENT_STREAM_VALUE)   // Server-Sent Events
    public Flux<OrderResponse> streamOrders(@RequestParam Long customerId) {
        return orderService.streamOrdersForCustomer(customerId);
    }
}
```java

### Composing Multiple Async Calls

```java
/**
 * Fetches a full order summary by combining data from three services in parallel.
 *
 * <p>Uses Mono.zip() to run all three calls concurrently and combine the results.
 * Total time ≈ max(orderTime, customerTime, inventoryTime) instead of sum.</p>
 */
public Mono<OrderSummary> getOrderSummary(Long orderId) {
    Mono<Order>     orderMono     = orderRepository.findById(orderId);
    Mono<Customer>  customerMono  = customerService.findById(orderId);
    Mono<Inventory> inventoryMono = inventoryService.checkAvailability(orderId);

    // Zip runs all three in parallel and combines results when all arrive
    return Mono.zip(orderMono, customerMono, inventoryMono)
               .map(tuple -> OrderSummary.builder()
                   .order(tuple.getT1())
                   .customer(tuple.getT2())
                   .inventory(tuple.getT3())
                   .build());
}
```java

### Error Handling in Reactive Chains

```java
return orderService.findById(orderId)
    // Transform NotFound into a 404 response
    .switchIfEmpty(Mono.error(new OrderNotFoundException(orderId)))
    // Catch and map specific exceptions
    .onErrorResume(OrderNotFoundException.class,
                   ex -> Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND, ex.getMessage())))
    // Log and re-throw unexpected errors
    .doOnError(ex -> log.error("Unexpected error for order {}: {}", orderId, ex.getMessage()));
```java

---

## 4. Spring Batch — Bulk Processing

### Core Concepts

```java
Job        → the whole batch process (has a name, can be restarted)
Step       → one phase of the job (read → process → write, or a tasklet)
ItemReader → reads records one at a time from a source (DB, file, queue)
ItemProcessor → transforms or filters one record (optional)
ItemWriter → writes a chunk of records to a destination
Chunk      → a batch of N records processed in a single transaction
```java

### Typical Batch Job

```java
/**
 * Batch job that reads unprocessed orders from the database,
 * calculates totals, and writes back the results.
 *
 * <p>Chunk size of 100 means: read 100 → process 100 → write 100 in one transaction.
 * If any of the 100 fail, only that chunk is rolled back — not the whole job.</p>
 */
@Configuration
@EnableBatchProcessing
@RequiredArgsConstructor
public class OrderProcessingJobConfig {

    private final JobRepository jobRepository;
    private final PlatformTransactionManager transactionManager;
    private final OrderItemReader orderItemReader;
    private final OrderProcessor   orderProcessor;
    private final OrderItemWriter  orderItemWriter;

    /**
     * Defines the full job with one step.
     */
    @Bean
    public Job processOrdersJob() {
        return new JobBuilder("processOrdersJob", jobRepository)
            .start(processOrdersStep())
            .build();
    }

    /**
     * Defines the chunk-oriented step.
     * Reads 100 orders at a time, processes each, writes in bulk.
     */
    @Bean
    public Step processOrdersStep() {
        return new StepBuilder("processOrdersStep", jobRepository)
            .<Order, ProcessedOrder>chunk(100, transactionManager)
            .reader(orderItemReader)
            .processor(orderProcessor)
            .writer(orderItemWriter)
            .faultTolerant()
            .skipLimit(10)                          // skip up to 10 bad records before failing
            .skip(MalformedOrderException.class)    // skip orders that can't be parsed
            .build();
    }
}
```java

---

## 5. Spring Cloud — Microservice Infrastructure

### Circuit Breaker (Resilience4j)

```java
/**
 * Calls the external inventory service with circuit breaker protection.
 *
 * <p>If the inventory service returns errors or times out too many times,
 * the circuit "opens" and we immediately return the fallback without
 * even trying the call — protecting both us and the failing service.</p>
 *
 * @param productId the product to check
 * @return available quantity, or 0 if the service is unavailable
 */
@CircuitBreaker(name = "inventory-service", fallbackMethod = "inventoryFallback")
@TimeLimiter(name = "inventory-service")    // timeout after configured duration
public CompletableFuture<Integer> checkInventory(Long productId) {
    return CompletableFuture.supplyAsync(() ->
        inventoryClient.getAvailableQuantity(productId)
    );
}

/**
 * Fallback used when the circuit is open or the call times out.
 * Returns 0 (assume out of stock) and logs for alerting.
 *
 * @param productId the product that was being checked
 * @param ex        the exception that triggered the fallback
 */
private CompletableFuture<Integer> inventoryFallback(Long productId, Exception ex) {
    log.warn("Inventory service unavailable for product {}. Using fallback (0). Reason: {}",
             productId, ex.getMessage());
    return CompletableFuture.completedFuture(0);
}
```java

### application.yml for Resilience4j

```yaml
resilience4j:
  circuitbreaker:
    instances:
      inventory-service:
        sliding-window-size: 10          # evaluate last 10 calls
        failure-rate-threshold: 50       # open circuit if 50%+ fail
        wait-duration-in-open-state: 30s # wait 30s before trying again (HALF_OPEN)
        permitted-number-of-calls-in-half-open-state: 3

  timelimiter:
    instances:
      inventory-service:
        timeout-duration: 2s             # fail fast after 2 seconds
```java

---

## 6. Application Events — Decoupled Communication

```java
// ── Event class (just a data carrier) ─────────────────────────────────────
/**
 * Published when an order is created successfully.
 * Listeners can react to this without the OrderService knowing about them.
 */
public record OrderCreatedEvent(Long orderId, Long customerId, BigDecimal totalAmount) {}


// ── Publisher (the service that creates orders) ────────────────────────────
@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {

    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public OrderResponse createOrder(CreateOrderRequest request) {
        Order saved = orderRepository.save(buildOrder(request));

        // Publish the event AFTER commit — listeners see committed data
        eventPublisher.publishEvent(new OrderCreatedEvent(
            saved.getId(), saved.getCustomerId(), saved.getTotalAmount()
        ));

        return OrderResponse.from(saved);
    }
}


// ── Listener (email service — completely independent of OrderService) ──────
@Component
@Slf4j
public class OrderConfirmationEmailListener {

    /**
     * Sends a confirmation email after an order is created.
     *
     * <p>Uses AFTER_COMMIT to guarantee the order is in the DB before sending
     * the email. If we sent during the transaction and it rolled back,
     * the customer would get an email for an order that doesn't exist.</p>
     */
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    @Async   // run in a separate thread so it doesn't slow down the HTTP response
    public void onOrderCreated(OrderCreatedEvent event) {
        log.info("Sending confirmation email for order {}", event.orderId());
        emailService.sendOrderConfirmation(event.customerId(), event.orderId());
    }
}
```java

---

## 7. Debugging Spring Applications

### Bean Wiring Issues

```java
// Problem: "No qualifying bean of type X found"
// Fix: check that the bean is in a @ComponentScan-covered package
// Debug: enable bean definition logging
logging.level.org.springframework.beans=DEBUG

// Problem: Circular dependency
// Spring Boot 2.6+ disallows circular deps by default.
// Fix: extract the shared logic into a third bean, or use @Lazy on one injection point.
@Lazy  // Spring will inject a proxy and only create the bean when first used
private final ServiceB serviceB;
```java

### Transaction Debugging

```java
// See every transaction begin/commit/rollback
logging.level.org.springframework.transaction=TRACE
logging.level.org.springframework.orm.jpa=DEBUG

// Common problem: @Transactional doesn't work
// Cause 1: Method is called from within the same class (Spring AOP can't intercept it)
// Fix: Call via the injected Spring bean, not via 'this.methodName()'
// Cause 2: @Transactional on a private method (AOP can't proxy private methods)
// Fix: Make the method protected or public
```java

### Startup Performance

```java
// Slow startup? Enable startup timing:
logging.level.org.springframework.boot=DEBUG

// Or add to main class:
SpringApplication app = new SpringApplication(MyApp.class);
app.setLazyInitialization(true);  // beans created on first use, not at startup
```java

---

## 8. Key Debugging Quick Reference

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `@Transactional` silently ignored | Self-invocation (calling `this.method()`) | Inject `self` reference or refactor to separate class |
| Bean not found at startup | Outside component scan package | Move to correct package or add `@ComponentScan(basePackages=...)` |
| `LazyInitializationException` | Accessing lazy collection outside transaction | Use `@Transactional(readOnly=true)` on the calling method |
| AOP advice not applied | Method is `private` or `final` | Make `protected` or `public`; remove `final` |
| `@Async` not working | Missing `@EnableAsync` | Add `@EnableAsync` to a `@Configuration` class |
| `@Scheduled` not running | Missing `@EnableScheduling` | Add `@EnableScheduling` to a `@Configuration` class |
| Application context fails to load in tests | Bean dependency issue | Use `@MockBean` for external dependencies |
