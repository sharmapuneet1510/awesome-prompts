---
name: Logging Best Practices & Implementation
version: 1.0
description: >
  Complete logging strategy guide covering SLF4J, Log4j2, Logback, Java Util Logging,
  structured logging, log levels, appenders, configurations, performance optimization,
  and production-ready patterns.
applies_to: [java, logging, slf4j, log4j2, logback, spring-boot]
tags: [logging, slf4j, log4j2, logback, structured-logging, observability]
---

# Logging Best Practices & Implementation — v1.0

---

## 1. Logging Architecture Overview

### 1.1 Logging Stack Layers

```
┌─────────────────────────────────────────────┐
│  Application Code (Log Statements)          │
├─────────────────────────────────────────────┤
│  SLF4J / Commons Logging / JUL (Facade)    │  ← Abstraction layer
├─────────────────────────────────────────────┤
│  Logback / Log4j2 / Log4j (Implementation)  │  ← Actual logging
├─────────────────────────────────────────────┤
│  Appenders (Console, File, Network)         │  ← Output targets
├─────────────────────────────────────────────┤
│  Layouts/Patterns (Format log messages)     │  ← Message format
└─────────────────────────────────────────────┘
```

**Best Practice:** Use SLF4J as facade + Logback as implementation.

---

## 2. SLF4J — The Logging Facade

### 2.1 SLF4J with Logback (Recommended)

```xml
<!-- Maven: SLF4J with Logback -->
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <version>2.0.7</version>
</dependency>

<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.4.11</version>
</dependency>

<!-- Exclude commons-logging if present -->
<dependency>
    <groupId>commons-logging</groupId>
    <artifactId>commons-logging</artifactId>
    <scope>provided</scope>
</dependency>
```

### 2.2 Basic SLF4J Usage

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OrderService {

    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);

    public void processOrder(Order order) {
        // Log at different levels
        logger.debug("Processing order: {}", order.getId());
        logger.info("Order started for customer: {}", order.getCustomerId());

        try {
            // Process order
            saveOrder(order);
            logger.info("Order {} saved successfully", order.getId());

        } catch (Exception e) {
            logger.error("Failed to process order {}: {}", order.getId(), e.getMessage(), e);
        }
    }

    private void saveOrder(Order order) throws Exception {
        logger.trace("Entering saveOrder with id: {}", order.getId());
        // Save logic
        logger.trace("Exiting saveOrder");
    }
}
```

### 2.3 Parameterized Logging (Avoid String Concatenation)

```java
/**
 * ✗ WRONG: String concatenation causes unnecessary object creation.
 */
public void oldWayLogging(Order order, Customer customer) {
    logger.debug("Processing order " + order.getId() + " for customer " + customer.getName());
    // Even when debug is disabled, string concatenation still happens
}

/**
 * ✓ CORRECT: Parameterized logging is evaluated only if level is enabled.
 */
public void newWayLogging(Order order, Customer customer) {
    logger.debug("Processing order {} for customer {}", order.getId(), customer.getName());
    // No concatenation if debug is disabled
}

/**
 * Exception logging with parameters.
 */
public void exceptionLogging(Order order) {
    try {
        processOrder(order);
    } catch (Exception e) {
        // Include exception for stack trace
        logger.error("Error processing order {}", order.getId(), e);
        // Causes: 1) message formatted 2) stack trace logged
    }
}
```

---

## 3. Log Levels — Severity & Usage

### 3.1 Log Level Hierarchy

```
TRACE   (Level 5000) - Very detailed diagnostic information
DEBUG   (Level 10000) - Detailed information for debugging
INFO    (Level 20000) - General informational messages (default)
WARN    (Level 30000) - Warning messages, potential problems
ERROR   (Level 40000) - Error messages, failures
OFF     (Level ∞) - Logging disabled
```

### 3.2 When to Use Each Level

```java
public class LogLevelExamples {

    /**
     * TRACE: Entry/exit, variable values (only in development).
     */
    public void traceExample(Order order) {
        logger.trace("Entry: processOrder, orderId={}", order.getId());
        // Detailed trace logic
        logger.trace("Exit: processOrder");
    }

    /**
     * DEBUG: Diagnostic info (dev/staging environments).
     */
    public void debugExample(Order order) {
        logger.debug("Order deserialized: {}", order);
        logger.debug("Validation rules applied: {}", validationRules);
        logger.debug("Processing status: PENDING -> IN_PROGRESS");
    }

    /**
     * INFO: Key business events (production level).
     */
    public void infoExample(Order order) {
        logger.info("Order {} created by customer {}", order.getId(), order.getCustomerId());
        logger.info("Payment processed: amount={}, method={}", order.getAmount(), "CREDIT_CARD");
        logger.info("Order {} shipped with tracking {}", order.getId(), "TRK123456");
    }

    /**
     * WARN: Unusual conditions that don't prevent operation.
     */
    public void warnExample(Order order) {
        if (order.getAmount().compareTo(BigDecimal.valueOf(10000)) > 0) {
            logger.warn("High-value order detected: {}, amount={}", order.getId(), order.getAmount());
        }

        if (retryCount > 3) {
            logger.warn("Order {} requires {} retries, investigating...", order.getId(), retryCount);
        }
    }

    /**
     * ERROR: Failure, exception, application issues.
     */
    public void errorExample(Order order) {
        try {
            saveOrder(order);
        } catch (DatabaseException e) {
            logger.error("Failed to save order {}", order.getId(), e);
        } catch (PaymentException e) {
            logger.error("Payment processing failed for order {}: {}", order.getId(), e.getMessage(), e);
        }
    }
}
```

---

## 4. Logback Configuration

### 4.1 Basic logback.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>

    <!-- Property for log file location -->
    <property name="LOG_DIR" value="logs"/>
    <property name="LOG_PATTERN" value="%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"/>

    <!-- Console Appender -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
    </appender>

    <!-- File Appender -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_DIR}/application.log</file>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
        <!-- Roll over file every day or when it reaches 10MB -->
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>${LOG_DIR}/application-%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
            <maxFileSize>10MB</maxFileSize>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
    </appender>

    <!-- Error File Appender -->
    <appender name="ERROR_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_DIR}/error.log</file>
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>ERROR</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>${LOG_DIR}/error-%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
            <maxFileSize>10MB</maxFileSize>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
    </appender>

    <!-- Root Logger -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="FILE"/>
        <appender-ref ref="ERROR_FILE"/>
    </root>

    <!-- Package-specific loggers -->
    <logger name="com.example" level="DEBUG"/>
    <logger name="org.springframework" level="INFO"/>
    <logger name="org.hibernate" level="WARN"/>

</configuration>
```

### 4.2 Spring Boot Logging Configuration

```yaml
# application.yml
logging:
  # Default pattern: spring boot default
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
    file: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"

  # Log file configuration
  file:
    name: logs/application.log
    max-size: 10MB
    max-history: 30

  # Package-specific levels
  level:
    root: INFO
    com.example: DEBUG
    org.springframework: INFO
    org.hibernate: WARN
    org.springframework.security: DEBUG

  # Log groups
  group:
    web: org.springframework.web,org.springframework.security
    sql: org.hibernate.SQL,org.hibernate.type.descriptor.sql.BasicBinder
```

---

## 5. Structured Logging — JSON Format

### 5.1 JSON Logging with Logback

```xml
<!-- Maven: Logback JSON encoder -->
<dependency>
    <groupId>ch.qos.logback.contrib</groupId>
    <artifactId>logback-json-classic</artifactId>
    <version>0.1.5</version>
</dependency>

<dependency>
    <groupId>ch.qos.logback.contrib</groupId>
    <artifactId>logback-jackson</artifactId>
    <version>0.1.5</version>
</dependency>
```

```xml
<!-- logback-spring.xml with JSON appender -->
<configuration>
    <appender name="JSON_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/application.json</file>
        <encoder class="ch.qos.logback.contrib.json.classic.JsonEncoder">
            <jsonFormatter class="ch.qos.logback.contrib.jackson.JacksonJsonFormatter">
                <prettyPrint>true</prettyPrint>
            </jsonFormatter>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>logs/application-%d{yyyy-MM-dd}.%i.json</fileNamePattern>
            <maxFileSize>10MB</maxFileSize>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
    </appender>

    <root level="INFO">
        <appender-ref ref="JSON_FILE"/>
    </root>
</configuration>
```

### 5.2 Structured Logging with MDC

```java
import org.slf4j.MDC;

/**
 * MDC (Mapped Diagnostic Context): Attach context to thread-local storage.
 */
public class OrderController {

    private final OrderService orderService;

    @PostMapping("/orders")
    public ResponseEntity<Order> createOrder(
            @RequestBody CreateOrderRequest request) {

        // Generate correlation ID
        var correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        MDC.put("customerId", request.getCustomerId());

        try {
            var order = orderService.createOrder(request);
            MDC.put("orderId", order.getId().toString());
            logger.info("Order created successfully");
            return ResponseEntity.ok(order);

        } finally {
            MDC.clear();  // Clean up thread-local
        }
    }
}
```

### 5.3 JSON Log Output

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "thread": "http-nio-8080-exec-1",
  "logger": "com.example.OrderController",
  "message": "Order created successfully",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "customerId": "123",
  "orderId": "456",
  "exception": null
}
```

---

## 6. Async Logging — Performance Optimization

### 6.1 Async Appender Configuration

```xml
<!-- logback-spring.xml with async appender -->
<configuration>
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/application.log</file>
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>logs/application-%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
            <maxFileSize>10MB</maxFileSize>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
    </appender>

    <!-- Async wrapper around FILE appender -->
    <appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
        <!-- Queue size: how many events before blocking -->
        <queueSize>512</queueSize>
        <!-- Discard lower priority events if queue is full -->
        <discardingThreshold>0</discardingThreshold>
        <!-- Don't wait for queue to empty on shutdown -->
        <includeCallerData>false</includeCallerData>
        <appender-ref ref="FILE"/>
    </appender>

    <root level="INFO">
        <appender-ref ref="ASYNC_FILE"/>
    </root>
</configuration>
```

### 6.2 Performance Impact

```java
/**
 * Async logging significantly reduces latency for high-volume logging.
 *
 * Sync (blocking) logging:
 *   - Write to file: ~1-10ms per log statement
 *   - Application blocked during write
 *   - High throughput impact
 *
 * Async (non-blocking) logging:
 *   - Queue event: <1ms
 *   - Background thread writes to file
 *   - Minimal application latency impact
 */
public class LoggingPerformance {
    // With async logging:
    // - P99 latency reduced 10-100x
    // - Throughput increased 2-5x
    // - CPU overhead increased slightly
}
```

---

## 7. Log4j2 Configuration

### 7.1 Maven Dependency

```xml
<!-- Maven: Log4j2 with SLF4J adapter -->
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-slf4j-impl</artifactId>
    <version>2.20.0</version>
</dependency>

<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>2.20.0</version>
</dependency>

<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.20.0</version>
</dependency>
```

### 7.2 log4j2.xml Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Configuration packages="org.apache.logging.log4j.core">

    <Properties>
        <Property name="LOG_DIR">logs</Property>
        <Property name="LOG_PATTERN">%d{ISO8601} [%thread] %-5level %logger{36} - %msg%n</Property>
    </Properties>

    <Appenders>
        <!-- Console Appender -->
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="${LOG_PATTERN}"/>
        </Console>

        <!-- Rolling File Appender -->
        <RollingFile name="RollingFile" fileName="${LOG_DIR}/application.log"
                     filePattern="${LOG_DIR}/application-%d{yyyy-MM-dd}.%i.log.gz">
            <PatternLayout pattern="${LOG_PATTERN}"/>
            <Policies>
                <TimeBasedTriggeringPolicy interval="1" modulate="true"/>
                <SizeBasedTriggeringPolicy size="10MB"/>
            </Policies>
            <DefaultRolloverStrategy max="30"/>
        </RollingFile>

        <!-- Async Appender -->
        <Async name="AsyncFile">
            <AppenderRef ref="RollingFile"/>
        </Async>
    </Appenders>

    <Loggers>
        <Logger name="com.example" level="DEBUG"/>
        <Logger name="org.springframework" level="INFO"/>
        <Root level="INFO">
            <AppenderRef ref="Console"/>
            <AppenderRef ref="AsyncFile"/>
        </Root>
    </Loggers>

</Configuration>
```

---

## 8. Common Logging Patterns

### 8.1 Service Layer Logging

```java
@Service
public class OrderService {

    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);

    public Order createOrder(CreateOrderRequest request) {
        var correlationId = MDC.get("correlationId");
        logger.info("Creating order for customer: {}", request.getCustomerId());

        try {
            // Validate
            validateOrder(request);
            logger.debug("Order validation passed");

            // Create and save
            var order = new Order(request);
            orderRepository.save(order);
            logger.info("Order {} created and saved", order.getId());

            return order;

        } catch (ValidationException e) {
            logger.warn("Order validation failed: {}", e.getMessage());
            throw e;

        } catch (Exception e) {
            logger.error("Unexpected error creating order for customer {}", request.getCustomerId(), e);
            throw new OrderProcessingException("Failed to create order", e);
        }
    }
}
```

### 8.2 Controller Logging

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    private static final Logger logger = LoggerFactory.getLogger(OrderController.class);

    @PostMapping
    public ResponseEntity<Order> createOrder(@RequestBody CreateOrderRequest request) {
        var start = System.currentTimeMillis();
        var correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);

        try {
            logger.info("POST /api/orders - Creating order for customer: {}", request.getCustomerId());
            var order = orderService.createOrder(request);

            var duration = System.currentTimeMillis() - start;
            logger.info("Order {} created successfully in {}ms", order.getId(), duration);

            return ResponseEntity.status(HttpStatus.CREATED).body(order);

        } catch (ValidationException e) {
            logger.warn("Bad request: {}", e.getMessage());
            return ResponseEntity.badRequest().build();

        } catch (Exception e) {
            logger.error("Error creating order", e);
            return ResponseEntity.internalServerError().build();

        } finally {
            MDC.clear();
        }
    }
}
```

### 8.3 Database Access Logging

```java
@Repository
public class OrderRepository {

    private static final Logger logger = LoggerFactory.getLogger(OrderRepository.class);

    public Optional<Order> findById(Long id) {
        logger.debug("Querying order by id: {}", id);
        var start = System.currentTimeMillis();

        try {
            var order = entityManager.find(Order.class, id);
            var duration = System.currentTimeMillis() - start;

            if (order != null) {
                logger.debug("Order {} found in {}ms", id, duration);
            } else {
                logger.debug("Order {} not found ({}ms)", id, duration);
            }

            return Optional.ofNullable(order);

        } catch (Exception e) {
            logger.error("Error querying order {}", id, e);
            throw e;
        }
    }

    public Order save(Order order) {
        logger.debug("Saving order: {}", order.getId());
        var start = System.currentTimeMillis();

        try {
            var saved = entityManager.merge(order);
            entityManager.flush();

            var duration = System.currentTimeMillis() - start;
            logger.info("Order {} saved in {}ms", order.getId(), duration);

            return saved;

        } catch (Exception e) {
            logger.error("Error saving order {}", order.getId(), e);
            throw e;
        }
    }
}
```

---

## 9. Logging Best Practices

✅ Use SLF4J as facade, not JUL or commons-logging
✅ Use parameterized logging: logger.info("{}",value) not logger.info(""+value)
✅ Use appropriate log levels (INFO for business events, DEBUG for diagnostics)
✅ Include context: correlation IDs, user IDs, request IDs
✅ Use MDC for thread context propagation
✅ Avoid logging sensitive data (passwords, tokens, PII)
✅ Use async appenders to minimize logging latency
✅ Configure rolling file appenders to manage disk space
✅ Use separate error logs for ERROR level events
✅ Monitor log file sizes and retention policies
✅ Use structured logging (JSON) for production
✅ Avoid verbose TRACE/DEBUG in production
✅ Log exceptions with full stack trace (include exception)
✅ Use logback or log4j2, not java.util.logging
✅ Document logging strategy for your team

---

## 10. Logging Checklist

✅ Add SLF4J and Logback to dependencies
✅ Configure logback.xml or application.yml
✅ Use Logger from SLF4J, not direct implementation
✅ Apply parameterized logging throughout codebase
✅ Set appropriate log levels per package
✅ Configure rolling file appenders
✅ Enable async appenders for performance
✅ Implement structured logging (JSON)
✅ Use MDC for correlation IDs
✅ Monitor ERROR logs separately
✅ Exclude sensitive data from logs
✅ Configure log retention policy
✅ Test logging in different environments
✅ Document logging patterns for team
✅ Review and maintain log configuration regularly
