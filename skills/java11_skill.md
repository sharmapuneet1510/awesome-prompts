---
name: Java 11 Long-Term Support & Production Features
version: 1.0
description: >
  Complete Java 11 LTS features and best practices. Covers local variable syntax (var),
  HTTP client, module system, string methods, stream improvements, performance
  enhancements, and migration from Java 8.
applies_to: [java, java-11, spring-boot, production, best-practices]
tags: [java11, var, http-client, modules, lts, long-term-support]
---

# Java 11 Long-Term Support & Production Features — v1.0

---

## 1. Java 11 LTS Overview

### 1.1 Release Information

```
Java 11 (September 2018)
├── LTS: Supported until September 2026
├── Next LTS: Java 17 (September 2021)
├── Recommended: Use for production systems
├── Version: 11.0.x with regular updates
└── Recommended for: New projects, migration targets
```

**Major Features:**
- Local variable syntax (var)
- HTTP Client (new standard)
- Module system finalized
- String methods (strip, isBlank)
- Stream improvements
- Single-file source code execution
- Performance improvements

---

## 2. Local Variable Syntax — var Keyword

### 2.1 Basic var Usage

```java
/**
 * var: Infer type from assigned value.
 * Reduces boilerplate without losing type safety.
 */
public class VarKeyword {

    // ✗ OLD: Explicit type declaration
    public void oldWay() {
        String message = "Hello World";
        List<Order> orders = new ArrayList<>();
        Map<String, Customer> customerMap = new HashMap<>();
        Iterator<Order> iterator = orders.iterator();
    }

    // ✓ NEW: Type inference with var
    public void newWay() {
        var message = "Hello World";                          // String
        var orders = new ArrayList<Order>();                 // List<Order>
        var customerMap = new HashMap<String, Customer>();   // Map<String, Customer>
        var iterator = orders.iterator();                     // Iterator<Order>
    }

    // Type is still inferred: Compile error if used incorrectly
    public void typeCheckingStillWorks() {
        var number = 42;                                      // int
        // number = "string";  // ✗ Compile error: incompatible types
    }
}
```

### 2.2 var in Collections & Streams

```java
/**
 * var with collections and streams.
 */
public class VarWithCollections {

    public void processOrders(List<Order> orders) {
        // var in for-each loop
        for (var order : orders) {
            System.out.println(order.getId());
        }

        // var with stream processing
        var processedOrders = orders.stream()
                .filter(order -> order.getStatus().equals("PENDING"))
                .map(this::enrichOrder)
                .collect(Collectors.toList());

        // var with Map iteration
        var orderMap = orders.stream()
                .collect(Collectors.toMap(Order::getId, Function.identity()));

        for (var entry : orderMap.entrySet()) {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        }
    }

    private Order enrichOrder(Order order) {
        // Enrich order logic
        return order;
    }
}
```

### 2.3 var Best Practices

```java
/**
 * Best practices: When to use var, when not to.
 */
public class VarBestPractices {

    /**
     * ✓ GOOD: Type is obvious from right-hand side.
     */
    public void goodVarUsage() {
        var count = 10;                                       // Obviously int
        var message = "Order #123";                          // Obviously String
        var orders = new ArrayList<Order>();                // Obviously List<Order>
        var total = BigDecimal.valueOf(99.99);               // Obviously BigDecimal
    }

    /**
     * ✗ AVOID: Type is not obvious.
     */
    public void avoidAmbiguousVar() {
        // ✗ What is the type? Unclear without reading method return
        var result = processComplexLogic();

        // ✓ Better: Explicit type
        OrderResult result = processComplexLogic();

        // ✗ Multiple assignments (var doesn't allow this)
        // var x = 1, y = 2;  // Compile error
    }

    /**
     * ✗ AVOID: Public API signatures.
     */
    // ✗ Don't use var for method parameters
    // public void processOrder(var order) { }

    // ✗ Don't use var for return types
    // public var getOrder() { }

    // ✓ Explicit types for public APIs
    public Order getOrder(Long orderId) {
        var order = retrieveFromDatabase(orderId);
        return order;  // Return type is explicit: Order
    }

    private OrderResult processComplexLogic() {
        return new OrderResult();
    }
}
```

---

## 3. HTTP Client — Modern HTTP Requests

### 3.1 HTTP Client Basics

```java
/**
 * Java 11 HTTP Client: Modern, asynchronous HTTP requests.
 * Replaces URLConnection and third-party libraries.
 */
public class HttpClientBasics {

    /**
     * Simple GET request.
     */
    public void simpleGet() throws Exception {
        var client = HttpClient.newHttpClient();

        var request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.example.com/orders"))
                .GET()
                .build();

        var response = client.send(request, HttpResponse.BodyHandlers.ofString());

        System.out.println("Status: " + response.statusCode());
        System.out.println("Body: " + response.body());
    }

    /**
     * POST request with JSON body.
     */
    public void postJson() throws Exception {
        var client = HttpClient.newHttpClient();

        var jsonBody = """
                {
                  "customerId": 123,
                  "amount": 99.99,
                  "items": [...]
                }
                """;

        var request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.example.com/orders"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();

        var response = client.send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println("Response: " + response.body());
    }
}
```

### 3.2 Async HTTP Client

```java
/**
 * Asynchronous HTTP requests without blocking.
 */
public class AsyncHttpClient {

    /**
     * Non-blocking HTTP request with CompletableFuture.
     */
    public void asyncRequest() throws Exception {
        var client = HttpClient.newHttpClient();

        var request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.example.com/orders"))
                .GET()
                .timeout(java.time.Duration.ofSeconds(10))
                .build();

        // sendAsync returns CompletableFuture
        var futureResponse = client.sendAsync(request, HttpResponse.BodyHandlers.ofString());

        futureResponse
                .thenApply(HttpResponse::body)
                .thenAccept(body -> System.out.println("Response: " + body))
                .exceptionally(ex -> {
                    System.err.println("Error: " + ex.getMessage());
                    return null;
                })
                .join();  // Wait for completion
    }

    /**
     * Multiple async requests in parallel.
     */
    public void parallelRequests() throws Exception {
        var client = HttpClient.newBuilder()
                .followRedirects(HttpClient.Redirect.ALWAYS)
                .build();

        var urls = java.util.List.of(
                "https://api.example.com/orders",
                "https://api.example.com/customers",
                "https://api.example.com/inventory"
        );

        var futures = urls.stream()
                .map(url -> {
                    var request = HttpRequest.newBuilder()
                            .uri(URI.create(url))
                            .GET()
                            .build();
                    return client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
                })
                .collect(java.util.stream.Collectors.toList());

        java.util.concurrent.CompletableFuture.allOf(
                futures.toArray(new java.util.concurrent.CompletableFuture[0])
        ).join();

        futures.forEach(f -> System.out.println(f.join().body()));
    }
}
```

### 3.3 HTTP Client with Spring Boot

```java
/**
 * HTTP Client bean for Spring Boot injection.
 */
@Configuration
public class HttpClientConfig {

    @Bean
    public HttpClient httpClient() {
        return HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_2)
                .followRedirects(HttpClient.Redirect.ALWAYS)
                .connectTimeout(java.time.Duration.ofSeconds(10))
                .build();
    }
}

@Service
public class OrderApiClient {

    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;

    public OrderApiClient(HttpClient httpClient, ObjectMapper objectMapper) {
        this.httpClient = httpClient;
        this.objectMapper = objectMapper;
    }

    public Order fetchOrder(Long orderId) throws Exception {
        var request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.example.com/orders/" + orderId))
                .GET()
                .build();

        var response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() == 200) {
            return objectMapper.readValue(response.body(), Order.class);
        } else {
            throw new ApiException("Failed to fetch order: " + response.statusCode());
        }
    }

    public void createOrderAsync(Order order) {
        var jsonBody = objectMapper.writeValueAsString(order);

        var request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.example.com/orders"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();

        httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenAccept(response -> System.out.println("Order created: " + response.statusCode()))
                .exceptionally(ex -> {
                    System.err.println("Error creating order: " + ex.getMessage());
                    return null;
                });
    }
}
```

---

## 4. String Methods — Utility Enhancements

### 4.1 New String Methods

```java
/**
 * Java 11 introduces useful string manipulation methods.
 */
public class StringMethods {

    /**
     * isBlank(): Check if string is empty or whitespace.
     */
    public void blankCheck() {
        String blank = "   ";
        String empty = "";
        String valid = "hello";

        blank.isBlank();    // true
        empty.isBlank();    // true
        valid.isBlank();    // false

        // Useful for validation
        if (!userInput.isBlank()) {
            processInput(userInput);
        }
    }

    /**
     * strip(): Remove leading/trailing whitespace.
     */
    public void stripWhitespace() {
        String input = "  hello world  \n";

        var stripped = input.strip();              // "hello world"
        var stripLeading = input.stripLeading();   // "hello world  \n"
        var stripTrailing = input.stripTrailing(); // "  hello world"
    }

    /**
     * lines(): Split string by line breaks into stream.
     */
    public void processLines(String text) {
        var lineList = text.lines()
                .filter(line -> !line.isBlank())
                .map(String::strip)
                .collect(java.util.stream.Collectors.toList());

        lineList.forEach(System.out::println);
    }

    /**
     * repeat(): Repeat string n times.
     */
    public void repeatString() {
        var border = "=".repeat(50);      // "=================================================="
        var spaces = " ".repeat(10);      // "          "

        System.out.println(border);
        System.out.println("Content");
        System.out.println(border);
    }
}
```

---

## 5. Module System — Package Encapsulation

### 5.1 Module Basics

```java
/**
 * Module declaration: Encapsulate packages.
 * File: src/module-info.java
 */
module com.example.orders {
    // Require other modules
    requires java.base;                  // Always implicit
    requires java.logging;
    requires spring.core;
    requires spring.data.jpa;

    // Export public packages
    exports com.example.orders.api;
    exports com.example.orders.service;
    exports com.example.orders.model;

    // Hidden implementation packages (not exported)
    // - com.example.orders.internal
    // - com.example.orders.config
}
```

### 5.2 Module Exports and Services

```java
/**
 * Service provider interface pattern with modules.
 */
// Module: com.example.payment.api
module com.example.payment.api {
    exports com.example.payment.service;
}

// Module: com.example.payment.creditcard
module com.example.payment.creditcard {
    requires com.example.payment.api;
    provides com.example.payment.service.PaymentProcessor
        with com.example.payment.creditcard.CreditCardProcessor;
}

/**
 * Usage: Load service implementation.
 */
public class PaymentService {
    public void processPayment(String type) {
        // ServiceLoader uses module system to find implementations
        var loader = java.util.ServiceLoader.load(PaymentProcessor.class);
        var processor = loader.stream()
                .map(java.util.ServiceLoader.Provider::get)
                .filter(p -> p.supportsType(type))
                .findFirst()
                .orElseThrow();

        processor.process();
    }
}
```

---

## 6. Stream Improvements

### 6.1 New Stream Methods

```java
/**
 * Java 11 adds useful stream operations.
 */
public class StreamImprovements {

    /**
     * Stream.ofNullable(): Handle potential null values.
     */
    public void handleOptional(Order order) {
        java.util.stream.Stream.ofNullable(order)
                .forEach(o -> System.out.println(o.getId()));

        // Equivalent to:
        // if (order != null) System.out.println(order.getId());
    }

    /**
     * Collectors.toUnmodifiableList(), Set, Map.
     */
    public void unmodifiableCollections(List<Order> orders) {
        var immutableList = orders.stream()
                .filter(o -> o.getStatus().equals("COMPLETED"))
                .collect(java.util.stream.Collectors.toUnmodifiableList());

        var immutableSet = orders.stream()
                .map(Order::getCustomerId)
                .collect(java.util.stream.Collectors.toUnmodifiableSet());

        // immutableList.add(...);  // Throws UnsupportedOperationException
    }

    /**
     * Collectors.filtering(), flatMapping() for complex filtering.
     */
    public void complexFiltering(List<Order> orders) {
        var result = orders.stream()
                .collect(java.util.stream.Collectors.groupingBy(
                        Order::getStatus,
                        java.util.stream.Collectors.filtering(
                                o -> o.getAmount().compareTo(BigDecimal.valueOf(100)) > 0,
                                java.util.stream.Collectors.toUnmodifiableList()
                        )
                ));

        result.forEach((status, highValueOrders) ->
                System.out.println(status + ": " + highValueOrders.size())
        );
    }
}
```

---

## 7. Performance Improvements

### 7.1 Garbage Collection & Memory

```java
/**
 * Java 11 performance improvements:
 * - Epsilon GC (low-pause GC)
 * - ZGC (low-latency GC)
 * - Improved GC tuning
 */
// JVM flags for Java 11:
// -XX:+UseEpsilonGC         // Epsilon GC (no garbage collection)
// -XX:+UseZGC               // ZGC (ultra-low pause times)
// -XX:+UseG1GC              // G1GC (default, improved)
// -XX:MaxGCPauseMillis=200  // Target pause time

public class PerformanceOptimization {
    /**
     * Profile memory usage with Java Flight Recorder.
     */
    public void profileMemory() {
        // Run with: java -XX:+UnlockCommercialFeatures -XX:+FlightRecorder
        // Then use jdk.jfr API or JDK Mission Control for analysis
    }
}
```

---

## 8. Deprecations and Removals

### 8.1 Removed in Java 11

```java
/**
 * APIs removed in Java 11 from Java 10 and earlier.
 */
public class RemovedAPIs {

    // ✗ REMOVED: java.xml.ws (SOAP)
    // ✗ REMOVED: javax.xml.bind (JAXB)
    // ✗ REMOVED: javax.activation (Activation Framework)
    // ✗ REMOVED: Nashorn JavaScript Engine
    // ✗ REMOVED: Applet API
    // ✗ REMOVED: Java EE modules (use Jakarta EE)

    // ✓ Alternatives:
    // - JAXB → jakarta.xml.bind
    // - SOAP → Spring Web Services or Apache CXF
    // - Nashorn → GraalVM JavaScript or Rhino
}
```

### 8.2 Migration from Java 8

```
Step 1: Update build tools
  ├─ Maven: 3.6.0+
  ├─ Gradle: 5.0+
  └─ IDE: IntelliJ 2018.3+, Eclipse 2018.12+

Step 2: Add missing modules (for Java EE)
  ├─ If using JAXB: Add jakarta.xml.bind
  ├─ If using SOAP: Add spring-ws or Apache CXF
  └─ Update dependencies

Step 3: Migrate code to var keyword
  ├─ Use var for local variables
  ├─ Keep explicit types for public APIs
  └─ Test thoroughly

Step 4: Replace URLConnection with HttpClient
  ├─ Migrate HTTP code to Java 11 HttpClient
  ├─ Remove OkHttp, RestTemplate where possible
  └─ Test async code

Step 5: Use module system (optional)
  ├─ Add module-info.java for new projects
  ├─ Existing code can remain on classpath
  └─ Gradual migration

Step 6: Test and validate
  ├─ Unit tests
  ├─ Integration tests
  └─ Performance tests
```

---

## 9. Java 11 Best Practices

✅ Use var for local variables with obvious types
✅ Use HttpClient instead of URLConnection
✅ Use module system for new projects
✅ Use String.isBlank() for input validation
✅ Use Stream.ofNullable() for optional values
✅ Use unmodifiable collections where appropriate
✅ Keep Spring Boot 2.x or upgrade to 3.x with Java 17
✅ Profile with Java Flight Recorder for performance issues
✅ Remove deprecated API usage before Java 17 upgrade
✅ Use try-with-resources for automatic resource cleanup
✅ Leverage G1GC improvements for heap > 4GB
✅ Benchmark against Java 8 to confirm performance
✅ Update CI/CD to Java 11 LTS
✅ Document Java 11 minimum requirement for team
✅ Plan for Java 17 LTS upgrade path

---

## 10. Java 11 Production Checklist

✅ Set Java version to 11 in Maven/Gradle
✅ Update all dependencies to Java 11 compatible versions
✅ Remove Java EE dependencies (migrate to Jakarta EE)
✅ Migrate HTTP code to HttpClient
✅ Add module-info.java for public modules (optional)
✅ Use var keyword for readable code
✅ Profile with Java Flight Recorder
✅ Test all code on Java 11
✅ Update CI/CD pipeline to Java 11
✅ Document Java 11 LTS support until September 2026
✅ Plan Java 17 migration strategy
✅ Validate third-party libraries for Java 11 support
✅ Configure GC appropriately for workload
✅ Run performance benchmarks
✅ Train team on Java 11 idioms (var, HttpClient, modules)
