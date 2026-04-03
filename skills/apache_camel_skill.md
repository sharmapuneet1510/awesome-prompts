---
name: Apache Camel Advanced Skill
version: 1.0
description: >
  Advanced knowledge skill for Apache Camel integration framework. Covers
  Enterprise Integration Patterns, route DSL, error handling, components,
  testing, Spring Boot integration, and debugging techniques. Used by coding
  and health inspection agents.
applies_to: [java, apache-camel, spring-boot, integration, eip]
tags: [camel, integration, eip, routing, messaging]
---

# Apache Camel Advanced Skill — v1.0

---

## 1. Core Concepts (Mental Model First)

Understanding Camel starts with four objects that flow through every route:

```java
Exchange  — the wrapper that carries a message through a route
  └── Message (IN)   — the current message being processed
        ├── Body     — the payload (String, byte[], POJO, InputStream, etc.)
        ├── Headers  — key/value metadata (like HTTP headers, file names, etc.)
        └── Properties — exchange-scoped metadata (survive routing steps)
```java

**Route** = a pipeline of steps. Data enters at a `from()`, flows through
processors and transformers, and exits at one or more `to()` endpoints.

**Component** = a connector to an external system (file, HTTP, Kafka, DB, etc.).
A component creates **Endpoints**. An endpoint creates **Producers** (send) and
**Consumers** (receive).

**Processor** = a single processing step. Receives an `Exchange`, modifies it,
passes it on.

---

## 2. Route DSL — Java (Primary)

### Basic Route Structure

```java
import org.apache.camel.builder.RouteBuilder;

/**
 * Processes incoming orders from a file drop folder.
 *
 * <p>Reads JSON files from /data/orders/incoming, validates them,
 * transforms to the internal format, and sends to the order-processing queue.
 * Failed files are moved to /data/orders/error.</p>
 */
@Component
public class OrderIngestionRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {

        // ── Global error handling for this route builder ──────────────
        // If anything throws an exception, move the file to the error folder
        // and send an alert. Do NOT retry file routes (files don't disappear).
        errorHandler(
            deadLetterChannel("file:/data/orders/error?autoCreate=true")
                .log("Order file failed: ${exception.message}")
        );

        // ── Route definition ──────────────────────────────────────────
        from("file:/data/orders/incoming?delete=true&moveFailed=../error")
            .routeId("order-ingestion")           // give every route a unique ID
            .description("Reads order files and sends to processing queue")

            .log("Processing order file: ${header.CamelFileName}")

            // Step 1: Unmarshal JSON to Java object
            .unmarshal().json(OrderFileDto.class)

            // Step 2: Validate (custom Processor — see section 4)
            .process(new OrderValidator())

            // Step 3: Transform to internal domain object
            .bean(OrderTransformer.class, "transform")

            // Step 4: Send to queue for async processing
            .to("pulsar:persistent://orders/default/order-processing")

            .log("Order ${body.orderId} sent to processing queue");
    }
}
```java

### Content-Based Router (EIP Pattern)

```java
/**
 * Routes payments to the correct processor based on payment type.
 *
 * <p>Uses Camel's Content-Based Router pattern — one of the core EIPs.
 * Each payment type has its own downstream endpoint so they can be
 * scaled and managed independently.</p>
 */
@Component
public class PaymentRoutingRoute extends RouteBuilder {

    @Override
    public void configure() {

        from("direct:route-payment")
            .routeId("payment-routing")
            .description("Routes payments to the correct processor by type")

            .choice()
                // Card payments → card gateway
                .when(header("paymentType").isEqualTo("CARD"))
                    .to("direct:process-card-payment")

                // Bank transfers → BACS processor
                .when(header("paymentType").isEqualTo("BANK_TRANSFER"))
                    .to("direct:process-bank-transfer")

                // PayPal → PayPal adapter
                .when(header("paymentType").isEqualTo("PAYPAL"))
                    .to("direct:process-paypal")

                // Unknown type — send to dead letter for manual review
                .otherwise()
                    .log(LoggingLevel.WARN, "Unknown payment type: ${header.paymentType}")
                    .to("direct:unknown-payment-type")
            .end();
    }
}
```java

### Splitter + Aggregator (Process a list, collect results)

```java
/**
 * Splits a batch order into individual items, processes each one,
 * then aggregates the results back into a single batch result.
 */
@Component
public class BatchOrderRoute extends RouteBuilder {

    @Override
    public void configure() {

        from("direct:process-batch-order")
            .routeId("batch-order-processing")

            // Split the order into individual line items
            // ${body.items} is a List<OrderItem>
            .split(simple("${body.items}"), new BatchResultAggregator())
                .parallelProcessing()         // process items in parallel
                .streaming()                  // don't load all into memory at once

                // Process each individual item
                .process(exchange -> {
                    OrderItem item = exchange.getIn().getBody(OrderItem.class);
                    // ... processing logic
                })

                .to("direct:process-single-item")

            .end()

            // After all items processed, body is the aggregated BatchResult
            .log("Batch complete: ${body.successCount} succeeded, ${body.failureCount} failed");
    }
}
```java

---

## 3. Error Handling — The Right Way

### Per-Route Exception Handling

```java
@Component
public class PaymentProcessingRoute extends RouteBuilder {

    @Override
    public void configure() {

        // ── Handle specific exceptions ────────────────────────────────

        // Retryable error: network blip — retry up to 3 times with backoff
        onException(HttpOperationFailedException.class)
            .maximumRedeliveries(3)
            .redeliveryDelay(1000)          // 1 second initial delay
            .backOffMultiplier(2.0)         // double delay each retry: 1s, 2s, 4s
            .retryAttemptedLogLevel(LoggingLevel.WARN)
            .handled(true)                  // don't propagate after retries exhausted
            .to("direct:payment-failed");   // send to failure handler

        // Non-retryable error: validation failure — don't retry, just route to error
        onException(PaymentValidationException.class)
            .handled(true)
            .log(LoggingLevel.ERROR, "Payment validation failed: ${exception.message}")
            .setHeader("failureReason", simple("${exception.message}"))
            .to("direct:invalid-payment");

        // Catch-all: unexpected errors — log full stack trace and alert
        onException(Exception.class)
            .handled(true)
            .log(LoggingLevel.ERROR, "Unexpected error in payment route: ${exception.stacktrace}")
            .to("direct:payment-system-error");

        // ── Main route ────────────────────────────────────────────────
        from("direct:process-payment")
            .routeId("payment-processing")
            .process(new PaymentValidator())
            .to("https://payment-gateway/charge")
            .to("direct:payment-success");
    }
}
```java

### Dead Letter Channel (Global Fallback)

```java
// In a base RouteBuilder that other routes extend:
errorHandler(
    deadLetterChannel("jms:queue:dead-letter")
        .maximumRedeliveries(3)
        .redeliveryDelay(2000)
        .useOriginalMessage()           // send the original message, not the modified one
        .deadLetterHandleNewException(false)
        .log("Message sent to DLQ after ${header.CamelRedeliveryCounter} retries")
);
```java

---

## 4. Processors — Custom Logic Steps

```java
/**
 * Validates that an incoming order has the required fields.
 *
 * <p>Implements {@link Processor} — the basic unit of work in a Camel route.
 * Throws {@link OrderValidationException} if validation fails, which triggers
 * the route's error handling.</p>
 */
public class OrderValidator implements Processor {

    private static final Logger log = LoggerFactory.getLogger(OrderValidator.class);

    @Override
    public void process(Exchange exchange) throws Exception {
        // Get the current message body, converted to our domain type
        OrderRequest order = exchange.getIn().getBody(OrderRequest.class);

        log.debug("Validating order from customer {}", order.getCustomerId());

        // Validate — throw a domain exception if invalid (triggers error handling)
        if (order.getCustomerId() == null || order.getCustomerId() <= 0) {
            throw new OrderValidationException("Customer ID is required and must be positive");
        }
        if (order.getItems() == null || order.getItems().isEmpty()) {
            throw new OrderValidationException("Order must contain at least one item");
        }

        // Enrich the exchange with metadata for downstream steps
        exchange.getIn().setHeader("validatedAt", System.currentTimeMillis());
        exchange.getIn().setHeader("customerId", order.getCustomerId());

        log.debug("Order validation passed for customer {}", order.getCustomerId());
    }
}
```java

---

## 5. Spring Boot Integration

### application.yml for Camel

```yaml
camel:
  springboot:
    name: OrderService              # shown in JMX, logs, and health endpoint
    main-run-controller: true       # keeps the app alive for consumer routes
  health:
    enabled: true                   # exposes /actuator/health with route statuses
  management:
    enabled: true                   # exposes Camel routes via JMX

# Component-level config (set per component)
camel:
  component:
    http:
      connection-timeout: 5000      # ms — ALWAYS set timeouts on HTTP components
      response-timeout: 10000
```java

### Inject Camel Context in Spring Beans

```java
@Service
@RequiredArgsConstructor
public class OrderDispatchService {

    private final ProducerTemplate producerTemplate;  // injected by Spring (Camel auto-configures it)

    /**
     * Sends an order synchronously to the order-processing route.
     *
     * @param order the order to process
     * @return the processed order result
     * @throws CamelExecutionException if the route throws an exception
     */
    public OrderResult dispatchOrder(OrderRequest order) {
        // Send to a direct: endpoint and wait for the result
        return producerTemplate.requestBody("direct:process-order", order, OrderResult.class);
    }

    /**
     * Sends an order asynchronously — fire and forget.
     *
     * @param order the order to process
     */
    public void dispatchOrderAsync(OrderRequest order) {
        producerTemplate.asyncSendBody("direct:process-order", order);
    }
}
```java

---

## 6. Testing Camel Routes

```java
/**
 * Unit tests for OrderIngestionRoute.
 *
 * <p>Uses CamelTestSupport — starts a lightweight Camel context with
 * the route under test. Mock endpoints replace real external systems
 * so tests run fast without network or filesystem access.</p>
 */
@CamelSpringBootTest
@SpringBootTest
class OrderIngestionRouteTest extends CamelTestSupport {

    @Autowired
    private ProducerTemplate producerTemplate;

    @EndpointInject("mock:pulsar:persistent://orders/default/order-processing")
    private MockEndpoint mockOrderQueue;

    @Test
    @DisplayName("Given valid order file, when route processes it, then sends to queue")
    void givenValidOrderFile_whenRouteProcesses_thenSendsToQueue() throws Exception {
        // Arrange — set expectation on the mock endpoint
        mockOrderQueue.expectedMessageCount(1);
        mockOrderQueue.expectedHeaderReceived("customerId", 42L);

        String orderJson = """
            {
                "customerId": 42,
                "items": [{"productId": 1, "quantity": 2}]
            }
            """;

        // Act — send directly to the route's from() endpoint
        producerTemplate.sendBodyAndHeader(
            "file:/data/orders/incoming",
            orderJson,
            Exchange.FILE_NAME,
            "order-123.json"
        );

        // Assert — verify the mock received exactly what we expected
        mockOrderQueue.assertIsSatisfied();
    }

    @Test
    @DisplayName("Given invalid order, when route processes it, then sends to error endpoint")
    void givenInvalidOrder_whenRouteProcesses_thenSendsToError() throws Exception {
        MockEndpoint mockError = getMockEndpoint("mock:direct:invalid-payment");
        mockError.expectedMessageCount(1);

        producerTemplate.sendBody("direct:process-order", "{ }");  // empty JSON = invalid

        mockError.assertIsSatisfied();
    }

    @Override
    protected RoutesBuilder createRouteBuilder() {
        return new OrderIngestionRoute();
    }
}
```java

---

## 7. Debugging Guide

### Logging the Exchange at Any Point

```java
// Add .log() anywhere in a route to inspect the message
from("direct:my-route")
    .log("Body before transform: ${body}")
    .log("Headers: ${headers}")
    .bean(MyTransformer.class)
    .log("Body after transform: ${body}")
    .to("direct:next");
```java

### Tracer (Full Exchange History)

```java
// In a @Configuration class — enables detailed tracing in dev
@Bean
public BacklogTracer backlogTracer(CamelContext context) {
    BacklogTracer tracer = BacklogTracer.createTracer(context);
    tracer.setEnabled(true);
    tracer.setBacklogSize(100);          // keep last 100 traced exchanges
    tracer.setTraceFilter("routeId == 'order-ingestion'");  // trace specific route
    return tracer;
}
```java

### Common Debugging Patterns

```java
// Pattern 1: Inspect body type at runtime
.process(exchange -> {
    Object body = exchange.getIn().getBody();
    System.out.println("Body type: " + body.getClass().getName());
    System.out.println("Body value: " + body);
})

// Pattern 2: Save body to a header before transforming (for error recovery)
.setHeader("originalBody", body())
.bean(RiskyTransformer.class)

// Pattern 3: Check exchange for errors
.process(exchange -> {
    Exception ex = exchange.getProperty(Exchange.EXCEPTION_CAUGHT, Exception.class);
    if (ex != null) {
        // handle the caught exception
    }
})
```java

### Common Issues and Fixes

| Problem | Symptom | Fix |
|---------|---------|-----|
| Body is `null` after a `.to()` | Next processor gets null body | InOut vs InOnly MEP mismatch — check `.setExchangePattern(ExchangePattern.InOut)` |
| Route never starts | No log output | Check `autoStartup`, route ID conflicts, or missing `@Component` |
| File route re-processes files | Same file processed multiple times | Use `delete=true` or `move=../done` on the file component URI |
| `TypeConversionException` | Can't convert body to target type | Register a custom `TypeConverter` or add a `.convertBodyTo(TargetClass.class)` step |
| Memory grows on Splitter | OOM on large files | Add `.streaming()` to the split — loads one item at a time |
| `HTTP 503` not retried | Camel doesn't retry | Add `onException(HttpOperationFailedException.class).maximumRedeliveries(3)` |
