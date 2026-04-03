---
name: Apache Camel & Pulsar Integration Skill
version: 1.0
description: >
  Integration patterns for Apache Camel with Apache Pulsar. Covers Camel Pulsar
  components, message routing, consumer/producer patterns, error handling, and
  Spring Boot integration with Camel-Pulsar pipelines.
applies_to: [java, apache-camel, apache-pulsar, integration, spring-boot, messaging]
tags: [camel, pulsar, integration, messaging, patterns, spring-boot]
---

# Apache Camel & Pulsar Integration Skill — v1.0

---

## 1. Camel-Pulsar Component Overview

### 1.1 Maven Dependency

```xml
<dependency>
    <groupId>org.apache.camel.springboot</groupId>
    <artifactId>camel-pulsar-starter</artifactId>
    <version>4.0.0</version>
</dependency>

<dependency>
    <groupId>org.apache.pulsar</groupId>
    <artifactId>pulsar-client</artifactId>
    <version>3.0.0</version>
</dependency>
```

### 1.2 Camel Pulsar URI Scheme

```java
// Consumer: Read from Pulsar topic
from("pulsar:persistent://public/default/my-topic"
    + "?numberOfConsumers=1"
    + "&subscriptionName=my-subscription"
    + "&subscriptionType=EXCLUSIVE"
)
.to("direct:processMessage");

// Producer: Send to Pulsar topic
from("direct:sendMessage")
    .to("pulsar:persistent://public/default/my-topic"
        + "?numberOfProducers=1"
        + "&compressionType=LZ4"
    );
```

---

## 2. Consumer Patterns with Camel

### 2.1 Simple Topic Consumer

```java
/**
 * Simple Pulsar consumer route with Camel.
 */
@Configuration
public class PulsarConsumerRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        from("pulsar:persistent://public/default/orders"
                + "?numberOfConsumers=5"
                + "&subscriptionName=order-processor"
                + "&subscriptionType=SHARED"
                + "&acknowledgeInterval=1000")
                .log("Received message: ${body}")
                .process(exchange -> {
                    String message = exchange.getIn().getBody(String.class);
                    OrderEvent order = parseOrder(message);
                    exchange.setProperty("orderId", order.getId());
                })
                .to("direct:processOrder");

        from("direct:processOrder")
                .log("Processing order: ${property.orderId}")
                .to("bean:orderService?method=process");
    }

    private OrderEvent parseOrder(String json) {
        // Parse JSON to OrderEvent
        return new ObjectMapper().readValue(json, OrderEvent.class);
    }
}
```

### 2.2 Failure Handler with DLT

```java
/**
 * Consumer with dead letter topic (DLT) for failed messages.
 */
@Configuration
public class PulsarConsumerWithDLT extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        onException(Exception.class)
                .handled(true)
                .maximumRedeliveries(3)
                .redeliveryDelay(1000)
                .log("Error processing message: ${exception.message}")
                .to("pulsar:persistent://public/default/orders-dlq"
                        + "?numberOfProducers=1");

        from("pulsar:persistent://public/default/orders"
                + "?numberOfConsumers=3"
                + "&subscriptionName=order-dlt-processor"
                + "&subscriptionType=FAILOVER")
                .log("Order received: ${body}")
                .doTry()
                    .process(exchange -> {
                        String body = exchange.getIn().getBody(String.class);
                        validateOrder(body);  // May throw exception
                    })
                    .to("direct:processOrder")
                .doCatch(Exception.class)
                    .log(LoggingLevel.ERROR, "Validation failed: ${exception}")
                    .to("pulsar:persistent://public/default/orders-dlq")
                .end();

        from("direct:processOrder")
                .to("bean:orderService?method=saveOrder");
    }

    private void validateOrder(String json) throws Exception {
        // Validation logic
        if (json == null || json.isEmpty()) {
            throw new ValidationException("Order JSON is empty");
        }
    }
}
```

---

## 3. Producer Patterns with Camel

### 3.1 Batch Sending Messages

```java
/**
 * Batch producer: Collect messages and send in batches to Pulsar.
 */
@Configuration
public class PulsarBatchProducer extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Collect 100 messages or wait 5 seconds, whichever comes first
        from("direct:incomingOrders")
                .aggregate(constant(true), new ArrayListAggregationStrategy())
                    .completionSize(100)
                    .completionTimeout(5000)
                    .log("Batch ready: ${header.CamelAggregatedSize} messages")
                    .process(exchange -> {
                        List<OrderEvent> batch = exchange.getIn().getBody(List.class);
                        String batchJson = new ObjectMapper().writeValueAsString(batch);
                        exchange.getIn().setBody(batchJson);
                    })
                    .to("pulsar:persistent://public/default/orders-batch"
                            + "?numberOfProducers=2"
                            + "&batchingEnabled=true"
                            + "&batchingMaxMessages=100"
                            + "&batchingMaxPublishDelayMicros=1000000");
    }
}
```

### 3.2 Async Producer with Callback

```java
/**
 * Async producer with success/failure callbacks.
 */
@Configuration
public class PulsarAsyncProducer extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        from("direct:sendOrderAsync")
                .process(exchange -> {
                    OrderEvent order = exchange.getIn().getBody(OrderEvent.class);
                    String json = new ObjectMapper().writeValueAsString(order);
                    exchange.getIn().setBody(json);
                })
                .to("pulsar:persistent://public/default/orders"
                        + "?numberOfProducers=3"
                        + "&asyncSend=true"
                        .log("Message sent to Pulsar with ID: ${property.messageId}")
                .choice()
                    .when(simple("${header.sendingFailed} == true"))
                        .log(LoggingLevel.ERROR, "Send failed: ${header.failureReason}")
                        .to("direct:handleSendFailure")
                    .otherwise()
                        .log(LoggingLevel.INFO, "Send successful")
                .end();
    }
}
```

---

## 4. Request-Reply Pattern

### 4.1 RPC-Style Messaging

```java
/**
 * Request-reply pattern: Send message to Pulsar, wait for response.
 */
@Configuration
public class PulsarRequestReply extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Request route: Send to Pulsar topic and wait for reply
        from("direct:requestOrderStatus")
                .setHeader("JMSReplyTo", simple("status-replies"))
                .setHeader("JMSCorrelationID", simple("${property.correlationId}"))
                .to("pulsar:persistent://public/default/status-requests"
                        + "?numberOfProducers=1")
                .log("Status request sent: ${property.correlationId}");

        // Reply consumer: Listen for responses
        from("pulsar:persistent://public/default/status-replies"
                + "?numberOfConsumers=1"
                + "&subscriptionName=status-reply-consumer"
                + "&subscriptionType=EXCLUSIVE")
                .log("Received status reply: ${body}")
                .recipientList(simple("direct:processStatusReply"));
    }
}
```

---

## 5. Topic Pattern Subscription

### 5.1 Multi-Topic Consumer

```java
/**
 * Subscribe to multiple topics using pattern matching.
 */
@Configuration
public class PulsarPatternSubscription extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        // Pattern: Subscribe to all topics matching prefix
        from("pulsar:persistent://public/default/events-*"
                + "?numberOfConsumers=3"
                + "&subscriptionName=event-processor"
                + "&patternSubscriptionPattern=persistent://public/default/events-*"
                + "&subscriptionType=SHARED")
                .log("Event from topic: ${header.PulsarTopicName}")
                .choice()
                    .when(simple("${header.PulsarTopicName} contains 'orders'"))
                        .to("direct:handleOrderEvent")
                    .when(simple("${header.PulsarTopicName} contains 'payments'"))
                        .to("direct:handlePaymentEvent")
                    .when(simple("${header.PulsarTopicName} contains 'inventory'"))
                        .to("direct:handleInventoryEvent")
                .end();
    }
}
```

---

## 6. Message Transformation

### 6.1 Content Enrichment

```java
/**
 * Enrich messages from Pulsar with additional data.
 */
@Configuration
public class PulsarEnrichment extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        from("pulsar:persistent://public/default/orders"
                + "?numberOfConsumers=2"
                + "&subscriptionName=order-enricher"
                + "&subscriptionType=EXCLUSIVE")
                .log("Order received: ${body}")
                .process(exchange -> {
                    String orderJson = exchange.getIn().getBody(String.class);
                    OrderEvent order = new ObjectMapper().readValue(orderJson, OrderEvent.class);

                    // Enrich with customer data
                    Customer customer = customerService.findById(order.getCustomerId());
                    order.setCustomerName(customer.getName());
                    order.setCustomerEmail(customer.getEmail());

                    // Enrich with pricing
                    List<OrderItem> items = order.getItems();
                    BigDecimal total = items.stream()
                            .map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
                            .reduce(BigDecimal.ZERO, BigDecimal::add);
                    order.setTotalAmount(total);

                    exchange.getIn().setBody(new ObjectMapper().writeValueAsString(order));
                })
                .to("pulsar:persistent://public/default/enriched-orders");
    }
}
```

---

## 7. Pulsar Admin Operations via Camel

### 7.1 Create Topics Dynamically

```java
/**
 * Dynamically create Pulsar topics when needed.
 */
@Service
public class PulsarAdminService {

    private final PulsarAdmin pulsarAdmin;

    public PulsarAdminService(PulsarAdmin pulsarAdmin) {
        this.pulsarAdmin = pulsarAdmin;
    }

    /**
     * Create topic if it doesn't exist.
     */
    public void ensureTopicExists(String topicName) throws Exception {
        try {
            pulsarAdmin.topics().getStats(topicName);
            log.info("Topic exists: {}", topicName);
        } catch (NotFoundException e) {
            log.info("Creating topic: {}", topicName);
            pulsarAdmin.topics().createPartitionedTopic(topicName, 3);
        }
    }

    /**
     * Get topic statistics.
     */
    public TopicStats getTopicStats(String topicName) throws Exception {
        return pulsarAdmin.topics().getStats(topicName);
    }

    /**
     * Get subscription stats.
     */
    public SubscriptionStats getSubscriptionStats(String topicName, String subscriptionName) throws Exception {
        return pulsarAdmin.topics().getSubscriptionStats(topicName, subscriptionName);
    }
}
```

---

## 8. Spring Boot Configuration

### 8.1 Camel-Pulsar in Spring Boot

```java
/**
 * Spring Boot application with Camel-Pulsar integration.
 */
@SpringBootApplication
@EnableScheduling
public class CamelPulsarApplication {

    public static void main(String[] args) {
        SpringApplication.run(CamelPulsarApplication.class, args);
    }

    /**
     * Configure Pulsar connection.
     */
    @Bean
    public PulsarClient pulsarClient() throws PulsarClientException {
        return PulsarClient.builder()
                .serviceUrl("pulsar://localhost:6650")
                .build();
    }

    /**
     * Configure Camel context.
     */
    @Bean
    public CamelContextConfiguration camelContextConfiguration() {
        return new CamelContextConfiguration() {
            @Override
            public void configureCamelContext(CamelContext camelContext) throws Exception {
                camelContext.getRegistry().bind("pulsarClient", pulsarClient());
            }

            @Override
            public void onCamelContextStarted(CamelContext camelContext, boolean alreadyStarted) throws Exception {
                log.info("Camel context started with Pulsar integration");
            }
        };
    }
}
```

### 8.2 application.yml Configuration

```yaml
camel:
  springboot:
    name: camel-pulsar-app
    main-run-controller: true

  component:
    pulsar:
      # Connection settings
      service-url: pulsar://localhost:6650
      authentication: null

      # Consumer defaults
      number-of-consumers: 1
      consumer-name: camel-consumer
      subscription-name: camel-subscription
      subscription-type: EXCLUSIVE
      acknowledgement-group-time: 100

      # Producer defaults
      number-of-producers: 1
      producer-name: camel-producer
      batching-enabled: true
      batching-max-messages: 100
      compression-type: LZ4

logging:
  level:
    org.apache.camel: INFO
    org.apache.pulsar: INFO
```

---

## 9. Error Handling Patterns

### 9.1 Retry with Exponential Backoff

```java
/**
 * Pulsar consumer with exponential backoff retry.
 */
@Configuration
public class PulsarRetryRoute extends RouteBuilder {

    @Override
    public void configure() throws Exception {
        onException(PulsarClientException.class)
                .handled(true)
                .maximumRedeliveries(5)
                .redeliveryDelay(100)
                .backOffMultiplier(2.0)
                .useExponentialBackOff()
                .log("Retrying after error: ${exception.message}");

        from("pulsar:persistent://public/default/reliable-orders"
                + "?numberOfConsumers=2"
                + "&subscriptionName=reliable-processor"
                + "&subscriptionType=SHARED")
                .doTry()
                    .to("direct:processWithRetry")
                .doCatch(Exception.class)
                    .log(LoggingLevel.ERROR, "Failed after retries: ${exception}")
                    .to("pulsar:persistent://public/default/failed-orders")
                .end();
    }
}
```

---

## 10. Camel-Pulsar Integration Checklist

✅ Add Camel Pulsar starter dependency
✅ Configure PulsarClient bean
✅ Use pulsar: URI scheme in routes
✅ Set numberOfConsumers/numberOfProducers
✅ Configure subscriptionType (EXCLUSIVE, SHARED, FAILOVER, KEY_SHARED)
✅ Implement error handling (onException, DLT)
✅ Use batch sending for high throughput
✅ Implement acknowledgment strategies
✅ Monitor with PulsarAdmin API
✅ Test with embedded Pulsar or Docker
✅ Configure logging for debugging
✅ Use pattern-based subscriptions for multi-topic routing
✅ Implement request-reply patterns where needed
✅ Use Spring Boot auto-configuration
✅ Handle timeouts and connection failures gracefully
