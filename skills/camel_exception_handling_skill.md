---
name: Apache Camel Exception Handling & Routing Skill
version: 1.0
description: >
  Advanced exception handling in Apache Camel. Covers error routes, retry logic,
  dead letter channels, error handlers, exception mapping, and recovery strategies.
applies_to: [java, apache-camel, spring-boot, integration, error-handling]
tags: [camel, exception-handling, error-routes, dlc, resilience, integration]
---

# Apache Camel Exception Handling & Routing Skill — v1.0

---

## 1. Exception Handler in Camel Routes

### 1.1 Global Exception Handler

```java
/**
 * Configure global exception handlers for all routes.
 *
 * Catches exceptions and routes them to error processing endpoints.
 */
@Configuration
public class CamelExceptionConfig implements RoutesBuilder {

    @Override
    public void addRoutes(RouteBuilder builder) throws Exception {
        // Global exception handler
        builder.onException(Exception.class)
                .handled(true)
                .maximumRedeliveries(3)
                .redeliveryDelay(1000)
                .backOffMultiplier(2.0)
                .log("Global error handler caught: ${exception.message}")
                .to("direct:errorHandler");

        // Specific exception handler: Business validation errors
        builder.onException(ValidationException.class)
                .handled(true)
                .maximumRedeliveries(0)  // Don't retry validation errors
                .log("Validation error: ${body}")
                .setBody(constant(new ErrorResponse(
                    "VALIDATION_ERROR",
                    "Request validation failed",
                    400
                )))
                .to("direct:sendErrorResponse");

        // Specific exception handler: Transient failures (network, timeout)
        builder.onException(TimeoutException.class, ConnectException.class)
                .handled(false)  // Don't suppress exception, let caller handle
                .maximumRedeliveries(5)
                .redeliveryDelay(500)
                .backOffMultiplier(1.5)
                .log("Transient error, retrying: ${exception.message}");

        // Specific exception handler: Database errors
        builder.onException(SQLException.class)
                .handled(true)
                .maximumRedeliveries(2)
                .redeliveryDelay(2000)
                .log("Database error: ${exception.message}")
                .to("direct:notifyDatabaseTeam");
    }
}
```java

### 1.2 Route-Specific Exception Handler

```java
@Configuration
public class OrderProcessingRoutes extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Route-specific exception handler (overrides global for this route)
        from("direct:processOrder")
                .onException(InsufficientStockException.class)
                    .handled(true)
                    .log("Insufficient stock: ${exception.message}")
                    .setBody(constant(new ErrorResponse(
                        "INSUFFICIENT_STOCK",
                        "Product is out of stock",
                        409
                    )))
                    .to("direct:sendErrorResponse")
                .end()
                .onException(PaymentGatewayException.class)
                    .handled(true)
                    .maximumRedeliveries(3)
                    .redeliveryDelay(1000)
                    .log("Payment gateway error: ${exception.message}")
                    .to("direct:notifyPaymentTeam")
                .end()
                .choice()
                    .when(simple("${header.CamelHttpResponseCode} == 200"))
                        .log("Order processed successfully")
                        .to("direct:updateOrderStatus")
                    .otherwise()
                        .log("Order processing failed: ${body}")
                        .to("direct:handleFailure")
                .end();
    }
}
```java

---

## 2. Dead Letter Channel (DLC) Configuration

### 2.1 Dead Letter Channel Setup

```java
/**
 * Configure dead letter channel for handling unprocessable messages.
 *
 * Messages that fail after all retries are sent to DLC for manual investigation.
 */
@Configuration
public class DeadLetterChannelConfig extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Define dead letter channel
        errorHandler(deadLetterChannel("direct:deadLetterHandler")
                .maximumRedeliveries(5)
                .redeliveryDelay(1000)
                .backOffMultiplier(2.0)
                .useExponentialBackOff()
                .retryAttemptedLogLevel(LoggingLevel.WARN)
                .asyncDelayedRedelivery()
                .logRetryAttempted(true)
                .logStackTrace(true)
        );

        // DLC endpoint: Log and store failed message
        from("direct:deadLetterHandler")
                .log(LoggingLevel.ERROR,
                    "Message moved to DLC: exchange=${exchangeId}, error=${exception.message}")
                .setHeader("DLC_TIMESTAMP", simple("${date:now:yyyy-MM-dd HH:mm:ss}"))
                .setHeader("DLC_EXCEPTION", simple("${exception.message}"))
                .setHeader("DLC_STACKTRACE", simple("${exception.stacktrace}"))
                .to("jpa:{{package}}.model.DeadLetterMessage?useExecuteUpdate=false")
                .to("log:deadletter?level=ERROR");

        // Process main route with DLC
        from("direct:processOrder")
                .log("Processing order: ${body}")
                .doTry()
                    .to("direct:validateOrder")
                    .to("direct:chargePayment")
                    .to("direct:confirmOrder")
                .doCatch(Exception.class)
                    .log(LoggingLevel.ERROR, "Error processing order: ${exception}")
                    .to("direct:deadLetterHandler")
                .end();
    }
}
```java

### 2.2 Retrieve and Reprocess DLC Messages

```java
/**
 * REST endpoint to reprocess messages from dead letter channel.
 */
@RestController
@RequestMapping("/api/dlc")
@RequiredArgsConstructor
public class DeadLetterChannelController {

    private final ProducerTemplate producerTemplate;
    private final DeadLetterMessageRepository dlcRepository;

    /**
     * Retrieve all failed messages in DLC.
     */
    @GetMapping("/messages")
    public ResponseEntity<List<DeadLetterMessage>> getFailedMessages() {
        List<DeadLetterMessage> messages = dlcRepository.findAll();
        return ResponseEntity.ok(messages);
    }

    /**
     * Reprocess a specific message from DLC.
     *
     * @param messageId the DLC message ID
     * @return success or error
     */
    @PostMapping("/messages/{id}/reprocess")
    public ResponseEntity<String> reprocessMessage(@PathVariable Long messageId) {
        DeadLetterMessage msg = dlcRepository.findById(messageId)
                .orElseThrow(() -> new EntityNotFoundException("DLC Message", messageId));

        try {
            // Reprocess the original message
            producerTemplate.sendBody("direct:processOrder", msg.getOriginalPayload());
            dlcRepository.delete(msg);
            return ResponseEntity.ok("Message reprocessed");

        } catch (Exception e) {
            return ResponseEntity.status(500).body("Reprocessing failed: " + e.getMessage());
        }
    }
}
```java

---

## 3. Error Routes & Conditional Processing

### 3.1 Error Routing Based on Exception Type

```java
@Configuration
public class OrderProcessingWithErrorRouting extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Main order processing route
        from("kafka:orders")
                .id("order-processor")
                .log("Received order: ${body}")
                .doTry()
                    // Validate order
                    .to("direct:validateOrder")
                    // Reserve inventory
                    .to("direct:reserveInventory")
                    // Process payment
                    .to("direct:processPayment")
                    // Confirm order
                    .to("direct:confirmOrder")

                .doCatch(StockUnavailableException.class)
                    .log(LoggingLevel.WARN, "Stock unavailable for order: ${body}")
                    .setHeader("ERROR_TYPE", constant("STOCK"))
                    .to("direct:handleStockError")

                .doCatch(PaymentFailedException.class)
                    .log(LoggingLevel.ERROR, "Payment failed: ${exception.message}")
                    .setHeader("ERROR_TYPE", constant("PAYMENT"))
                    .to("direct:handlePaymentError")
                    .to("direct:reverseReservation")

                .doCatch(ValidationException.class)
                    .log(LoggingLevel.WARN, "Validation failed: ${body}")
                    .setHeader("ERROR_TYPE", constant("VALIDATION"))
                    .to("direct:handleValidationError")

                .doCatch(Exception.class)
                    .log(LoggingLevel.ERROR, "Unexpected error: ${exception}")
                    .setHeader("ERROR_TYPE", constant("SYSTEM"))
                    .to("direct:handleSystemError")

                .doFinally()
                    .log("Order processing completed (success or error)")
                .end();

        // Error handlers
        from("direct:handleStockError")
                .setBody(constant("{\"status\": \"PENDING\", \"reason\": \"Stock unavailable\"}"))
                .to("kafka:order-events");

        from("direct:handlePaymentError")
                .setBody(constant("{\"status\": \"PAYMENT_FAILED\"}"))
                .to("kafka:order-events")
                .to("direct:notifyPaymentTeam");

        from("direct:handleValidationError")
                .setBody(constant("{\"status\": \"INVALID\"}"))
                .to("kafka:order-events");

        from("direct:handleSystemError")
                .to("direct:deadLetterHandler");
    }
}
```java

---

## 4. Retry Policy with Predicates

### 4.1 Conditional Retry Logic

```java
@Configuration
public class ConditionalRetryRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        from("direct:callExternalApi")
                .onException(HttpOperationFailedException.class)
                    .onWhen(exchange -> {
                        HttpOperationFailedException e =
                            exchange.getProperty(Exchange.EXCEPTION_CAUGHT,
                                    HttpOperationFailedException.class);
                        // Retry on 5xx errors, not 4xx
                        return e.getStatusCode() >= 500;
                    })
                    .maximumRedeliveries(5)
                    .redeliveryDelay(1000)
                    .backOffMultiplier(2.0)
                    .log("Retrying on server error: ${exception.statusCode}")
                .end()
                .onException(HttpOperationFailedException.class)
                    .onWhen(exchange -> {
                        HttpOperationFailedException e =
                            exchange.getProperty(Exchange.EXCEPTION_CAUGHT,
                                    HttpOperationFailedException.class);
                        // Fail immediately on 4xx errors
                        return e.getStatusCode() < 500;
                    })
                    .handled(true)
                    .log("Client error, not retrying: ${exception.statusCode}")
                    .setBody(constant("{\"error\": \"Client error\"}"))
                .end()
                .log("Calling external API: ${body}")
                .to("https://api.example.com/process?bridgeEndpoint=true");
    }
}
```java

---

## 5. Compensating Transactions (Saga Pattern)

### 5.1 Distributed Transaction with Compensation

```java
/**
 * Order processing with compensating transactions for failure scenarios.
 *
 * If payment fails after reserving inventory, we compensate (release reservation).
 */
@Configuration
public class OrderProcessingSaga extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        from("direct:processOrderWithCompensation")
                .log("=== Order Processing Started ===")
                .setProperty("orderId", simple("${body.id}"))
                .doTry()
                    // Step 1: Reserve inventory
                    .log("Step 1: Reserving inventory")
                    .to("direct:reserveInventory")
                    .setProperty("inventoryReserved", constant(true))

                    // Step 2: Process payment
                    .log("Step 2: Processing payment")
                    .to("direct:processPayment")
                    .setProperty("paymentProcessed", constant(true))

                    // Step 3: Confirm order
                    .log("Step 3: Confirming order")
                    .to("direct:confirmOrder")

                    .log("=== Order Processing Completed Successfully ===")

                .doCatch(PaymentFailedException.class)
                    .log(LoggingLevel.ERROR, "Payment failed, compensating...")
                    // Compensation: Release inventory reservation
                    .choice()
                        .when(simple("${property.inventoryReserved} == true"))
                            .log("Releasing inventory reservation for order ${property.orderId}")
                            .to("direct:releaseInventory")
                        .otherwise()
                            .log("Inventory not reserved, nothing to compensate")
                    .end()
                    // Notify customer
                    .to("direct:notifyPaymentFailure")

                .doCatch(Exception.class)
                    .log(LoggingLevel.ERROR, "Unexpected error: ${exception}")
                    // Compensation: Release all acquired resources
                    .choice()
                        .when(simple("${property.inventoryReserved} == true"))
                            .log("Releasing inventory reservation")
                            .to("direct:releaseInventory")
                        .end()
                    .choice()
                        .when(simple("${property.paymentProcessed} == true"))
                            .log("Refunding payment")
                            .to("direct:refundPayment")
                        .end()
                    .to("direct:notifySystemError")

                .end();

        // Inventory compensation
        from("direct:releaseInventory")
                .log("Releasing inventory for order ${property.orderId}")
                .to("http://inventory-service/api/reservations/${property.orderId}?method=DELETE");

        // Payment compensation
        from("direct:refundPayment")
                .log("Issuing refund for order ${property.orderId}")
                .to("direct:callPaymentGateway");
    }
}
```java

---

## 6. Exception Monitoring & Alerting

### 6.1 Monitor and Alert on Exceptions

```java
/**
 * Route to monitor and alert on critical exceptions.
 */
@Configuration
public class ExceptionMonitoringRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Catch critical exceptions and alert
        from("direct:errorHandler")
                .choice()
                    .when(simple("${exception} instanceof " +
                            "com.example.exception.CriticalSystemException"))
                        .log(LoggingLevel.ERROR, "CRITICAL EXCEPTION DETECTED")
                        .setHeader("x-exception-severity", constant("CRITICAL"))
                        .to("direct:sendSlackAlert")
                        .to("direct:createPagerDutyIncident")
                        .to("direct:deadLetterHandler")

                    .when(simple("${exception} instanceof " +
                            "com.example.exception.PaymentGatewayException"))
                        .log(LoggingLevel.ERROR, "PAYMENT ERROR")
                        .setHeader("x-exception-severity", constant("HIGH"))
                        .to("direct:sendEmailAlert")

                    .otherwise()
                        .log(LoggingLevel.WARN, "Standard error")
                .end();

        // Send Slack alert
        from("direct:sendSlackAlert")
                .setBody(simple("{\"text\": \"ERROR: ${exception.message}\"}"))
                .to("https://hooks.slack.com/services/YOUR/WEBHOOK/URL");

        // Create PagerDuty incident
        from("direct:createPagerDutyIncident")
                .setHeader("Content-Type", constant("application/json"))
                .to("https://events.pagerduty.com/v2/enqueue");
    }
}
```java

---

## 7. Camel Exception Handling Checklist

✅ Define global exception handlers as fallback
✅ Use route-specific handlers to override global behavior
✅ Implement dead letter channel for failed messages
✅ Use conditional retry logic (retry on 5xx, fail on 4xx)
✅ Implement compensating transactions for multi-step operations
✅ Log exceptions with context (exchange ID, body, headers)
✅ Use async redelivery to avoid blocking threads
✅ Use exponential backoff to avoid overwhelming services
✅ Monitor and alert on critical exceptions
✅ Provide recovery endpoints to reprocess DLC messages
✅ Use error routes to handle different exception types differently
✅ Clean up resources (rollback, release) on failure
