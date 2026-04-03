---
name: OpenTelemetry Observability & Distributed Tracing
version: 1.0
description: >
  Complete guide to OpenTelemetry for observability in distributed systems. Covers
  tracing, metrics, logs, instrumentation, Spring Boot integration, Jaeger/Prometheus
  exporters, context propagation, and production patterns.
applies_to: [java, observability, tracing, metrics, opentelemetry, spring-boot]
tags: [opentelemetry, tracing, metrics, observability, jaeger, prometheus]
---

# OpenTelemetry Observability & Distributed Tracing — v1.0

---

## 1. OpenTelemetry Overview

### 1.1 Three Pillars of Observability

```
┌─────────────────────────────────────────────────────────┐
│  OBSERVABILITY = Traces + Metrics + Logs                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  TRACES: Request flow through distributed system       │
│  ├─ Span: Single operation (HTTP request, DB query)    │
│  ├─ Trace ID: Correlate spans across services          │
│  └─ Baggage: Context passed between services           │
│                                                          │
│  METRICS: Numerical measurements (counters, gauges)    │
│  ├─ Request count, latency, error rate                │
│  ├─ JVM memory, CPU, thread count                      │
│  └─ Business metrics (orders/sec, revenue)             │
│                                                          │
│  LOGS: Structured text events                          │
│  ├─ Application logs                                   │
│  ├─ Correlation with traces via trace IDs              │
│  └─ Machine-readable JSON format                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 1.2 OpenTelemetry Architecture

```
Application Code
        ↓
   OpenTelemetry API (Facade)
        ↓
   OpenTelemetry SDK (Implementation)
        ↓
   Exporters (Jaeger, Prometheus, OTLP)
        ↓
   Backend (Jaeger, Prometheus, ELK, DataDog, etc.)
```

---

## 2. Maven Setup & Dependencies

### 2.1 OpenTelemetry Dependencies

```xml
<!-- OpenTelemetry BOM: Manage all versions consistently -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>io.opentelemetry</groupId>
            <artifactId>opentelemetry-bom</artifactId>
            <version>1.35.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- Core OpenTelemetry API -->
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-api</artifactId>
</dependency>

<!-- OpenTelemetry SDK -->
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-sdk</artifactId>
</dependency>

<!-- Auto-instrumentation (Spring Boot starter) -->
<dependency>
    <groupId>io.opentelemetry.instrumentation</groupId>
    <artifactId>opentelemetry-spring-boot-starter</artifactId>
    <version>1.35.0-alpha</version>
</dependency>

<!-- Jaeger exporter for tracing -->
<dependency>
    <groupId>io.opentelemetry.exporter</groupId>
    <artifactId>opentelemetry-exporter-jaeger-thrift</artifactId>
</dependency>

<!-- Prometheus exporter for metrics -->
<dependency>
    <groupId>io.opentelemetry.exporter</groupId>
    <artifactId>opentelemetry-exporter-prometheus</artifactId>
</dependency>

<!-- OTLP exporter (gRPC protocol) -->
<dependency>
    <groupId>io.opentelemetry.exporter</groupId>
    <artifactId>opentelemetry-exporter-otlp</artifactId>
</dependency>
```

### 2.2 Spring Boot Auto-Configuration

```yaml
# application.yml
otel:
  # Service identification
  service:
    name: order-service
    version: 1.0.0

  # Tracing configuration
  exporter:
    otlp:
      endpoint: http://localhost:4317  # Jaeger/OTLP collector

  # Sampling: What percentage of traces to collect
  traces:
    sampler: always_on  # or: always_off, parentbased_always_on, parentbased_always_off

  # Metrics configuration
  metrics:
    export:
      interval: 60000  # Export metrics every 60 seconds

logging:
  pattern:
    level: "%5p"
```

---

## 3. Distributed Tracing with Spans

### 3.1 Basic Span Creation

```java
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.Span;

@Service
public class OrderService {

    private static final Tracer tracer = GlobalOpenTelemetry.getTracer(
            "com.example.orders",
            "1.0.0"
    );

    /**
     * Manual span creation.
     */
    public Order createOrder(CreateOrderRequest request) {
        Span span = tracer.spanBuilder("createOrder")
                .setAttribute("customerId", request.getCustomerId())
                .setAttribute("amount", request.getAmount().doubleValue())
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            logger.info("Creating order");

            // Validate
            var order = new Order(request);

            // Add event to span
            span.addEvent("order_validated");

            // Save
            orderRepository.save(order);
            span.addEvent("order_saved", Attributes.of(
                    AttributeKey.stringKey("orderId"), order.getId().toString()
            ));

            return order;

        } catch (Exception e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR, e.getMessage());
            throw e;

        } finally {
            span.end();
        }
    }
}
```

### 3.2 Automatic HTTP Instrumentation

```java
/**
 * Spring Boot with OpenTelemetry starter: Automatic instrumentation.
 * No manual span creation needed for HTTP requests.
 */
@SpringBootApplication
public class OrderApplication {

    public static void main(String[] args) {
        SpringApplication.run(OrderApplication.class, args);
    }
}

/**
 * HTTP requests automatically instrumented:
 * - Incoming HTTP requests create spans
 * - Outgoing HTTP calls add child spans
 * - Database queries create spans
 */
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @PostMapping
    public ResponseEntity<Order> createOrder(
            @RequestBody CreateOrderRequest request) {
        // Automatically traced
        var order = orderService.createOrder(request);
        return ResponseEntity.ok(order);
    }
}
```

### 3.3 Span Attributes & Events

```java
/**
 * Add rich context to spans.
 */
public void processOrderWithDetails(Order order) {
    Span span = tracer.spanBuilder("processOrder")
            .setAttribute("orderId", order.getId())
            .setAttribute("customerId", order.getCustomerId())
            .setAttribute("amount", order.getAmount().doubleValue())
            .setAttribute("status", order.getStatus())
            .startSpan();

    try (Scope scope = span.makeCurrent()) {
        // Add events as operations complete
        span.addEvent("validation_started");
        validateOrder(order);
        span.addEvent("validation_completed");

        span.addEvent("payment_processing_started");
        processPayment(order);
        span.addEvent("payment_completed", Attributes.of(
                AttributeKey.stringKey("paymentId"), "PAY-123",
                AttributeKey.stringKey("method"), "CREDIT_CARD"
        ));

        span.addEvent("order_confirmed");

    } finally {
        span.end();
    }
}
```

---

## 4. Context Propagation in Distributed Systems

### 4.1 Trace ID & Baggage

```java
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.baggage.Baggage;

/**
 * Context flows automatically across:
 * - HTTP headers (traceparent, tracestate)
 * - Message queues (Kafka, RabbitMQ)
 * - Async calls
 */
@Service
public class OrderService {

    /**
     * Access current span and trace ID.
     */
    public void logTraceContext() {
        Span span = Span.current();
        var spanContext = span.getSpanContext();

        logger.info("Trace ID: {}", spanContext.getTraceId());
        logger.info("Span ID: {}", spanContext.getSpanId());
    }

    /**
     * Add baggage: Context passed to downstream services.
     */
    public void setUserContext(String userId) {
        // Baggage is automatically propagated
        Baggage baggage = Baggage.builder()
                .put("userId", userId)
                .put("tenantId", "acme-corp")
                .build();

        try (Scope scope = baggage.makeCurrent()) {
            // userId and tenantId available in downstream services
            orderService.createOrder(request);
        }
    }

    /**
     * Read baggage in downstream service.
     */
    public void processWithBaggage() {
        var userId = Baggage.current().getEntryValue("userId");
        var tenantId = Baggage.current().getEntryValue("tenantId");

        logger.info("Processing for user {} in tenant {}", userId, tenantId);
    }
}
```

### 4.2 Kafka Message Instrumentation

```java
/**
 * OpenTelemetry automatically propagates context through Kafka messages.
 */
@Component
public class OrderEventProducer {

    private final KafkaTemplate<String, OrderEvent> kafkaTemplate;

    public void publishOrderEvent(Order order) {
        var event = new OrderEvent(order.getId(), order.getCustomerId());

        // Trace context automatically added to message headers
        kafkaTemplate.send("orders-topic", event);
        // Downstream consumer will receive the same trace ID
    }
}

@Component
public class OrderEventConsumer {

    @KafkaListener(topics = "orders-topic")
    public void handleOrderEvent(OrderEvent event) {
        // Automatic span created for this message
        // Trace ID from producer available here
        logger.info("Order event received: {}", event.getOrderId());

        Span span = Span.current();
        logger.info("Parent span: {}", span.getSpanContext().getTraceId());
    }
}
```

---

## 5. Metrics with OpenTelemetry

### 5.1 Meter Provider & Instruments

```java
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.metrics.MeterProvider;

@Service
public class OrderMetrics {

    private final Meter meter;
    private final LongCounter orderCounter;
    private final LongHistogram orderAmountHistogram;
    private final AtomicReference<Integer> activeOrders;

    public OrderMetrics(MeterProvider meterProvider) {
        this.meter = meterProvider.get("com.example.orders");

        // Counter: Increments (never decreases)
        this.orderCounter = meter.counterBuilder("orders.created")
                .setDescription("Number of orders created")
                .setUnit("1")
                .build();

        // Histogram: Distribution of values
        this.orderAmountHistogram = meter.histogramBuilder("orders.amount")
                .setDescription("Order amount in USD")
                .setUnit("USD")
                .ofLongs()
                .build();

        // Gauge: Current value (e.g., active connections)
        this.activeOrders = new AtomicReference<>(0);
        meter.gaugeBuilder("orders.active")
                .setDescription("Number of active orders")
                .buildWithCallback(result -> result.observe(activeOrders.get()));
    }

    public void createOrder(Order order) {
        // Increment counter
        orderCounter.add(1, Attributes.of(
                AttributeKey.stringKey("status"), "new"
        ));

        // Record histogram
        orderAmountHistogram.record(order.getAmount().longValue());

        // Update gauge
        activeOrders.set(activeOrders.get() + 1);
        // ... process order ...
        activeOrders.set(activeOrders.get() - 1);
    }
}
```

### 5.2 Prometheus Metrics Export

```java
/**
 * Spring Boot configuration for Prometheus metrics.
 */
@Configuration
public class PrometheusConfig {

    @Bean
    public MeterRegistry meterRegistry() {
        return new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
    }
}

// application.yml
management:
  endpoints:
    web:
      exposure:
        include: prometheus,health,metrics
  endpoint:
    metrics:
      enabled: true
    prometheus:
      enabled: true

// Access metrics at:
// http://localhost:8080/actuator/prometheus
```

### 5.3 Prometheus Query Examples

```prometheus
# Counter: Total orders created
rate(orders_created_total[5m])

# Histogram: P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Gauge: Active orders
orders_active

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

---

## 6. Spring Boot OpenTelemetry Integration

### 6.1 Spring Boot Starter Configuration

```yaml
# application.yml
spring:
  application:
    name: order-service

otel:
  # Service metadata
  resource:
    attributes:
      service.name: order-service
      service.version: 1.0.0
      deployment.environment: production

  # Tracing
  traces:
    exporter: jaeger
    sampler: parentbased_always_on

  exporter:
    jaeger:
      endpoint: http://localhost:14250  # Jaeger gRPC endpoint

  # Metrics
  metrics:
    exporter: prometheus
    interval: 60000

  # Logs correlation with traces
  logs:
    exporter: otlp
    context:
      api:
        enabled: true
```

### 6.2 Auto-Instrumented HTTP Requests

```java
/**
 * No code changes needed: HTTP requests automatically traced.
 */
@RestController
public class OrderController {

    private static final Logger logger = LoggerFactory.getLogger(OrderController.class);

    @PostMapping("/api/orders")
    public ResponseEntity<Order> createOrder(
            @RequestBody CreateOrderRequest request,
            HttpServletRequest httpRequest) {

        // Trace ID automatically injected
        var traceId = httpRequest.getHeader("X-Trace-Id");
        logger.info("Creating order with trace ID: {}", traceId);

        var order = orderService.createOrder(request);
        return ResponseEntity.ok(order);
    }
}
```

### 6.3 Manual Instrumentation When Needed

```java
/**
 * For custom logic not auto-instrumented.
 */
@Service
public class ComplexOrderService {

    private final Tracer tracer;

    public ComplexOrderService(Tracer tracer) {
        this.tracer = tracer;
    }

    public Order processComplexOrder(Order order) {
        Span span = tracer.spanBuilder("processComplexOrder")
                .setAttribute("orderId", order.getId())
                .startSpan();

        try (Scope scope = span.makeCurrent()) {
            // Business logic with automatic child spans
            validateOrder(order);           // Auto-instrumented by HTTP client
            processPayment(order);          // Auto-instrumented by HTTP client
            updateInventory(order);         // Auto-instrumented by HTTP client

            span.setStatus(StatusCode.OK);
            return order;

        } catch (Exception e) {
            span.recordException(e);
            span.setStatus(StatusCode.ERROR);
            throw e;

        } finally {
            span.end();
        }
    }
}
```

---

## 7. Database Query Instrumentation

### 7.1 JDBC Instrumentation

```java
/**
 * OpenTelemetry auto-instrumentation covers JDBC queries.
 * No manual span creation for database access.
 */
@Repository
public class OrderRepository {

    private final JdbcTemplate jdbcTemplate;

    public Optional<Order> findById(Long id) {
        // Automatically traced as child span
        var order = jdbcTemplate.queryForObject(
                "SELECT * FROM orders WHERE id = ?",
                new OrderRowMapper(),
                id
        );
        // Span includes: query text, duration, result count
        return Optional.ofNullable(order);
    }
}
```

### 7.2 JPA/Hibernate Instrumentation

```java
/**
 * JPA queries automatically instrumented via Hibernate bytecode enhancement.
 */
@Service
public class OrderService {

    private final OrderRepository orderRepository;

    public List<Order> getRecentOrders() {
        // Automatically traced with span name:
        // "SELECT Order FROM Order WHERE createdAt > ?"
        return orderRepository.findRecentOrders();
    }

    public void saveOrder(Order order) {
        // Automatically traced:
        // "INSERT INTO orders ..."
        // "UPDATE orders ..."
        orderRepository.save(order);
    }
}
```

---

## 8. Jaeger Backend Setup

### 8.1 Docker Compose: Jaeger Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      # OTLP gRPC receiver
      - "4317:4317"
      # OTLP HTTP receiver
      - "4318:4318"
      # Jaeger agent (legacy)
      - "6831:6831/udp"
      # Jaeger compact protocol
      - "6832:6832/udp"
      # Jaeger binary protocol
      - "5775:5775/udp"
      # UI
      - "16686:16686"
    environment:
      COLLECTOR_OTLP_ENABLED: "true"

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
```

### 8.2 Jaeger Query & Analysis

```bash
# Access Jaeger UI
open http://localhost:16686

# Search traces by service name
- Select "order-service" from dropdown
- View all traces for that service

# Filter by tag
- Select service, add filters:
  - http.status_code = 500
  - error = true
  - customerId = 123

# View trace details
- Click trace to see span waterfall
- Inspect attributes, events, exceptions
- Correlate with other services' spans
```

---

## 9. Production Observability Patterns

### 9.1 Sampling Strategies

```java
/**
 * Production requires sampling to reduce overhead.
 */
@Configuration
public class TracingSamplerConfig {

    @Bean
    public Sampler sampler() {
        // Sample 10% of traces
        return Sampler.traceIdRatioBased(0.1);

        // OR: Always sample traces with errors
        // return new ErrorAwareSampler();

        // OR: Sample based on trace ID
        // return Sampler.parentBased(Sampler.traceIdRatioBased(0.1));
    }
}

/**
 * Custom sampler: Always sample error responses.
 */
public class ErrorAwareSampler implements Sampler {

    @Override
    public SamplingResult shouldSample(Context parentContext, String traceId,
                                      String name, SpanKind spanKind,
                                      Attributes attributes, List<LinkData> parentLinks) {

        // Check if response has error attribute
        if (attributes.get(AttributeKey.stringKey("http.status_code"))
                .equals("500")) {
            return SamplingResult.recordAndSample();  // Always sample errors
        }

        // Otherwise sample 1% of requests
        return Sampler.traceIdRatioBased(0.01).shouldSample(
                parentContext, traceId, name, spanKind, attributes, parentLinks
        );
    }
}
```

### 9.2 Correlation ID Flow

```java
/**
 * Correlate logs, metrics, and traces with correlation ID.
 */
@Component
public class CorrelationIdFilter extends OncePerRequestFilter {

    private static final Logger logger = LoggerFactory.getLogger(CorrelationIdFilter.class);

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                   HttpServletResponse response,
                                   FilterChain filterChain) throws ServletException, IOException {

        // Get or create correlation ID
        String correlationId = request.getHeader("X-Correlation-Id");
        if (correlationId == null) {
            correlationId = UUID.randomUUID().toString();
        }

        // Add to MDC for logging
        MDC.put("correlationId", correlationId);

        // Add to baggage for tracing
        Baggage baggage = Baggage.builder()
                .put("correlationId", correlationId)
                .build();

        try (Scope scope = baggage.makeCurrent()) {
            response.addHeader("X-Correlation-Id", correlationId);
            filterChain.doFilter(request, response);

        } finally {
            MDC.remove("correlationId");
        }
    }
}
```

---

## 10. OpenTelemetry Checklist

✅ Add OpenTelemetry BOM and dependencies
✅ Configure Spring Boot starter auto-instrumentation
✅ Set service name and version in configuration
✅ Configure trace exporter (Jaeger or OTLP)
✅ Configure metrics exporter (Prometheus)
✅ Set sampling strategy appropriate for production
✅ Implement correlation ID flow
✅ Use baggage for context propagation
✅ Instrument message queue producers/consumers
✅ Add custom spans for business logic
✅ Set up Jaeger backend with Docker
✅ Configure Prometheus scrape targets
✅ Create Grafana dashboards
✅ Monitor error rates and latencies
✅ Document tracing strategy for team
✅ Train team on reading trace waterfall
✅ Set alerts on SLO violations
✅ Regularly review and optimize sampling
✅ Test context propagation across services
✅ Validate trace quality in staging before production
