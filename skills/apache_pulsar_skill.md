---
name: Apache Pulsar Advanced Skill
version: 1.0
description: >
  Advanced knowledge skill for Apache Pulsar messaging. Covers architecture,
  producers, consumers, subscription types, schemas, error handling, dead letter
  topics, Spring for Apache Pulsar, and debugging. Used by coding and health
  inspection agents.
applies_to: [java, python, apache-pulsar, spring-boot, messaging, streaming]
tags: [pulsar, messaging, streaming, pub-sub, dead-letter, schema-registry]
---

# Apache Pulsar Advanced Skill — v1.0

---

## 1. Architecture Mental Model

```java
Pulsar Cluster
  ├── Broker(s)        — stateless, route messages; can scale horizontally
  ├── BookKeeper       — durable message storage (write-ahead log)
  └── ZooKeeper        — metadata, broker coordination

Topic naming:
  persistent://  {tenant} / {namespace} / {topic-name}
  Example:       persistent://orders/payments/card-transactions

  persistent://  → messages survive broker restart (backed by BookKeeper)
  non-persistent:// → messages lost if broker restarts (high throughput, low durability)
```java

### Key Concepts vs Kafka

| Concept | Kafka | Pulsar |
|---------|-------|--------|
| Message storage | Broker (stateful) | BookKeeper (separate) |
| Consumer model | Consumer Group | Subscription (4 types) |
| Rebalancing | Required on membership change | Not needed (per-message ack) |
| Multi-tenancy | Manual (naming convention) | Built-in (tenant/namespace) |
| Schema | Schema Registry (separate) | Built-in Schema Registry |
| Geo-replication | MirrorMaker2 | Built-in |

---

## 2. Producers

### Java Producer (Spring for Apache Pulsar)

```java
import org.springframework.pulsar.core.PulsarTemplate;

/**
 * Publishes order events to the Pulsar order-events topic.
 *
 * <p>Uses Spring's {@link PulsarTemplate} — the Spring-managed, lifecycle-aware
 * wrapper around the Pulsar client. Always prefer PulsarTemplate over creating
 * PulsarClient directly in Spring apps.</p>
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderEventPublisher {

    private final PulsarTemplate<OrderEvent> pulsarTemplate;

    // Topic name — use a constant to avoid typos across the codebase
    private static final String ORDER_EVENTS_TOPIC = "persistent://orders/default/order-events";

    /**
     * Publishes an order created event.
     *
     * <p>This is a fire-and-forget send — the method returns immediately.
     * Use {@link #publishAndWait} if you need confirmation before continuing.</p>
     *
     * @param event the order event to publish
     * @throws PulsarClientException if the broker rejects the message
     */
    public void publish(OrderEvent event) {
        pulsarTemplate.sendAsync(ORDER_EVENTS_TOPIC, event)
            .thenAccept(messageId ->
                log.info("OrderEvent published. MessageId: {}, OrderId: {}",
                         messageId, event.getOrderId()))
            .exceptionally(ex -> {
                log.error("Failed to publish OrderEvent for order {}: {}",
                          event.getOrderId(), ex.getMessage(), ex);
                // Re-throw or handle based on your reliability requirements
                throw new EventPublishException("Failed to publish order event", ex);
            });
    }

    /**
     * Publishes an event and waits for broker acknowledgment before returning.
     *
     * <p>Use this when the caller must know the message was persisted
     * before proceeding (e.g. within a database transaction boundary).</p>
     *
     * @param event the event to publish
     * @return the Pulsar MessageId assigned to this message
     */
    public MessageId publishAndWait(OrderEvent event) {
        return pulsarTemplate.send(ORDER_EVENTS_TOPIC, event);
    }
}
```java

### Producer with Custom Configuration

```java
/**
 * Sends payment events with batching and compression enabled.
 *
 * <p>Batching groups multiple messages into one network round trip —
 * dramatically improves throughput at the cost of a small latency increase.</p>
 */
@Bean
public PulsarTemplate<PaymentEvent> paymentEventTemplate(PulsarClient pulsarClient) {
    ProducerBuilder<PaymentEvent> builder = pulsarClient
        .newProducer(Schema.JSON(PaymentEvent.class))
        .topic("persistent://payments/default/payment-events")
        .producerName("payment-service-producer")
        .batchingMaxMessages(500)           // batch up to 500 messages
        .batchingMaxPublishDelay(10, TimeUnit.MILLISECONDS)  // or send after 10ms
        .compressionType(CompressionType.LZ4)               // fast compression
        .sendTimeout(5, TimeUnit.SECONDS);  // fail if broker doesn't ack in 5s

    return new PulsarTemplate<>(new DefaultPulsarProducerFactory<>(pulsarClient, builder));
}
```java

---

## 3. Consumers — The Four Subscription Types

This is the most important concept in Pulsar. Choose the wrong subscription type and
you get duplicate processing, missed messages, or ordering violations.

```java
// Type 1: EXCLUSIVE
// → Only ONE consumer active at a time. If it dies, the next consumer takes over.
// → Use for: ordered processing, single-instance workers
// → Risk: no parallelism; one slow consumer blocks everything

// Type 2: SHARED (Round-Robin)
// → Many consumers, messages distributed round-robin
// → Use for: high-throughput parallel processing where order doesn't matter
// → Risk: no ordering guarantee; a slow consumer can hold up acks

// Type 3: FAILOVER
// → One ACTIVE consumer, others are standbys. Hot standby — instant failover.
// → Use for: ordered processing with high availability
// → Ordered within each partition

// Type 4: KEY_SHARED
// → Like SHARED but all messages with the same key always go to the same consumer
// → Use for: parallel processing WITH per-key ordering (e.g. all events for customer 42 in order)
// → Best of both worlds for keyed workloads
```java

### Spring for Apache Pulsar Consumer

```java
/**
 * Listens to the order-events topic and processes each order.
 *
 * <p>Uses SHARED subscription so multiple instances can process in parallel.
 * Each message is individually acknowledged — if processing fails, only
 * that message is redelivered, not the whole batch.</p>
 */
@Service
@Slf4j
public class OrderEventConsumer {

    /**
     * Processes an incoming order event.
     *
     * <p>Spring calls this method for each message. The framework handles
     * acknowledging the message when the method returns normally, and
     * negative-acknowledging (nack) when it throws.</p>
     *
     * @param event the deserialized order event
     */
    @PulsarListener(
        topics     = "persistent://orders/default/order-events",
        subscriptionName = "order-processor-subscription",
        subscriptionType = SubscriptionType.Shared,
        schemaType  = SchemaType.JSON
    )
    public void onOrderEvent(OrderEvent event) {
        log.info("Processing order event: orderId={}, type={}", event.getOrderId(), event.getType());

        // If this throws, Spring Pulsar will nack the message
        // → Pulsar will redeliver after the nack delay
        orderProcessingService.process(event);

        log.info("Order event {} processed successfully", event.getOrderId());
        // Method returns normally → Spring Pulsar auto-acks the message
    }
}
```java

### KEY_SHARED Consumer (Ordered Per Customer)

```java
/**
 * Processes payment events in order per customer.
 *
 * <p>KEY_SHARED ensures all payments for customer 42 go to the same consumer
 * instance, preserving order for that customer. Different customers are
 * processed in parallel across multiple instances.</p>
 */
@PulsarListener(
    topics           = "persistent://payments/default/payment-events",
    subscriptionName = "payment-processor-subscription",
    subscriptionType = SubscriptionType.Key_Shared,
    schemaType       = SchemaType.JSON
)
public void onPaymentEvent(Message<PaymentEvent> message) {
    // The key is the customer ID — set by the producer
    String customerId = message.getKey();
    PaymentEvent event = message.getValue();

    log.info("Processing payment for customer {} (key={}) : paymentId={}",
             customerId, message.getKey(), event.getPaymentId());

    paymentService.process(event);
}
```java

---

## 4. Schema Registry

Pulsar has a built-in schema registry. Always use it — it prevents consumers from
receiving messages they can't deserialize.

```java
// ── Define the schema (the message contract) ─────────────────────────────

/**
 * Represents an order event published to Pulsar.
 *
 * <p>Schema is registered automatically in Pulsar's schema registry
 * when the first producer or consumer connects with this type.</p>
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OrderEvent {
    private Long     orderId;
    private Long     customerId;
    private String   eventType;    // CREATED, UPDATED, CANCELLED, SHIPPED
    private BigDecimal totalAmount;
    private Instant  occurredAt;
}

// ── Producer registers the schema automatically ───────────────────────────
PulsarTemplate<OrderEvent> template = ...;
// Spring Pulsar registers Schema.JSON(OrderEvent.class) on first send

// ── Consumer validates against the registered schema ─────────────────────
@PulsarListener(
    topics     = "...",
    schemaType = SchemaType.JSON   // Pulsar validates incoming messages against the schema
)
public void onOrderEvent(OrderEvent event) { ... }
```java

### Schema Evolution Rules

```json
BACKWARD COMPATIBLE (safe):
  ✅ Add a new optional field (with default value)
  ✅ Delete a field (consumers ignore unknown fields)

NOT BACKWARD COMPATIBLE (breaking):
  ❌ Change a field's type (e.g. String → Integer)
  ❌ Rename a required field
  ❌ Remove a field that consumers depend on
```java

---

## 5. Dead Letter Topics

When a message fails to process after all retries, Pulsar sends it to a
Dead Letter Topic (DLT) automatically. Always monitor your DLTs.

```java
/**
 * Consumer with Dead Letter Topic configuration.
 *
 * <p>If processing fails 3 times (maxRedeliverCount), the message is
 * automatically moved to the DLT. A separate DLT consumer handles
 * alerting and manual review.</p>
 */
@PulsarListener(
    topics           = "persistent://orders/default/order-events",
    subscriptionName = "order-processor-subscription",
    subscriptionType = SubscriptionType.Shared,
    deadLetterPolicy = @DeadLetterPolicy(
        maxRedeliverCount    = 3,
        deadLetterTopic      = "persistent://orders/default/order-events-DLT",
        retryLetterTopic     = "persistent://orders/default/order-events-RETRY"
    ),
    // Negative ack redelivery: wait 5 seconds before retrying a failed message
    negativeAckRedeliveryDelay = "5000"
)
public void onOrderEvent(OrderEvent event) {
    orderProcessingService.process(event);
}


/**
 * Separate consumer for the Dead Letter Topic.
 *
 * <p>Messages here have failed all retries and need manual intervention.
 * This consumer logs, alerts, and stores them for review.</p>
 */
@PulsarListener(
    topics           = "persistent://orders/default/order-events-DLT",
    subscriptionName = "order-dlt-handler",
    subscriptionType = SubscriptionType.Shared
)
public void onDeadLetter(Message<OrderEvent> deadMessage) {
    log.error("Message moved to DLT after {} redeliveries. OrderId: {}. " +
              "MessageId: {}. Payload: {}",
              deadMessage.getRedeliveryCount(),
              deadMessage.getValue().getOrderId(),
              deadMessage.getMessageId(),
              deadMessage.getValue());

    // Save to a review table for human intervention
    deadLetterRepository.save(new DeadLetterRecord(
        deadMessage.getMessageId().toString(),
        deadMessage.getValue(),
        deadMessage.getRedeliveryCount()
    ));

    // Alert the on-call engineer
    alertingService.sendAlert("DLT message received for order: " + deadMessage.getValue().getOrderId());
}
```java

---

## 6. Spring for Apache Pulsar — application.yml

```yaml
spring:
  pulsar:
    client:
      service-url: pulsar://localhost:6650     # broker URL
      # For TLS:
      # service-url: pulsar+ssl://pulsar.prod.example.com:6651

    producer:
      send-timeout: 5s                         # fail if not acked in 5 seconds
      batching-enabled: true
      batching-max-messages: 500
      compression-type: lz4

    consumer:
      subscription-initial-position: earliest  # start from beginning of topic if new subscription
      receiver-queue-size: 1000                # how many messages to pre-fetch
      ack-timeout: 10s                         # if not acked in 10s, redeliver

    listener:
      observation-enabled: true                # integrates with Micrometer for metrics
      schema-type: json                        # default schema for all listeners
```java

---

## 7. Python Producer and Consumer

```python
import pulsar
from pulsar.schema import JsonSchema
from dataclasses import dataclass


@dataclass
class OrderEvent:
    """Schema for order events in Pulsar.

    Attributes:
        order_id: Unique identifier for the order.
        customer_id: The customer who placed the order.
        event_type: What happened (CREATED, UPDATED, CANCELLED).
        total_amount: Order total in the order currency.
    """
    order_id: int
    customer_id: int
    event_type: str
    total_amount: float


# ── Producer ──────────────────────────────────────────────────────────────
client   = pulsar.Client("pulsar://localhost:6650")
producer = client.create_producer(
    topic           = "persistent://orders/default/order-events",
    schema          = JsonSchema(OrderEvent),
    send_timeout_millis = 5000,    # fail after 5 seconds
    compression_type    = pulsar.CompressionType.LZ4,
)

def publish_order_event(event: OrderEvent) -> None:
    """Publishes an order event to Pulsar.

    Args:
        event: The order event to publish.

    Raises:
        pulsar.exceptions.PulsarException: If the broker rejects the message.
    """
    message_id = producer.send(event)
    print(f"Published order {event.order_id}, messageId={message_id}")


# ── Consumer ──────────────────────────────────────────────────────────────
consumer = client.subscribe(
    topic             = "persistent://orders/default/order-events",
    subscription_name = "python-order-processor",
    schema            = JsonSchema(OrderEvent),
    consumer_type     = pulsar.ConsumerType.Shared,
)

def consume_events() -> None:
    """Continuously consumes and processes order events.

    Acknowledges messages on success, negative-acknowledges on failure.
    Failed messages are redelivered after the nack delay.
    """
    while True:
        message = consumer.receive(timeout_millis=5000)
        if message is None:
            continue

        try:
            event: OrderEvent = message.value()
            print(f"Processing order {event.order_id}")
            process_order(event)                       # your processing logic
            consumer.acknowledge(message)              # success → ack
        except Exception as e:
            print(f"Processing failed for order {event.order_id}: {e}")
            consumer.negative_acknowledge(message)     # failure → nack → redeliver
```java

---

## 8. Debugging Pulsar Issues

### Common Problems and Fixes

| Problem | Symptom | Investigation | Fix |
|---------|---------|---------------|-----|
| Messages not received | Consumer shows 0 messages | Check `pulsar-admin topics stats` — is backlog growing? | Verify subscription name matches publisher's topic exactly |
| Message redelivered forever | Same message keeps appearing | Check `redelivery_count` header; check DLT | Add DLT config; fix the root cause in the processor |
| Schema incompatibility | `IncompatibleSchemaException` on connect | Check schema registry via admin API | Add field as optional with default; bump schema version |
| Consumer lag growing | Backlog increasing | `pulsar-admin topics stats --subscriptions` | Scale consumers; increase `receiverQueueSize`; check processing time |
| Messages out of order | Order violation on keyed data | Check subscription type is `Key_Shared`, not `Shared` | Use `Key_Shared`; ensure producer sets message key |

### Useful Admin Commands

```bash
# Check topic status and consumer lag
pulsar-admin topics stats persistent://orders/default/order-events

# List all subscriptions on a topic
pulsar-admin topics subscriptions persistent://orders/default/order-events

# Check DLT backlog
pulsar-admin topics stats persistent://orders/default/order-events-DLT

# Skip a stuck message (use carefully — message is lost)
pulsar-admin topics skip \
  --count 1 \
  --subscription order-processor-subscription \
  persistent://orders/default/order-events

# Peek at messages without consuming them
pulsar-admin topics peek-messages \
  --count 5 \
  --subscription order-processor-subscription \
  persistent://orders/default/order-events
```java
