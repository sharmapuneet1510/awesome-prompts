---
name: REST API Java Skill
version: 1.0
description: >
  Comprehensive REST API patterns for Java/Spring Boot. Covers HTTP methods, status codes,
  request/response handling, validation, error responses, HATEOAS, pagination, versioning.
applies_to: [java, spring-boot, rest-api, http, maven]
tags: [rest-api, http, spring, patterns, api-design]
---

# REST API Java Skill — v1.0

---

## 1. HTTP Method Design & Semantics

Match HTTP verbs to actions correctly:

| Method | Purpose | Idempotent | Safe | Response Body |
|--------|---------|-----------|------|----------------|
| **GET** | Retrieve resource(s) | ✓ | ✓ | Resource data |
| **POST** | Create new resource | ✗ | ✗ | Created resource + location |
| **PUT** | Replace entire resource | ✓ | ✗ | Updated resource |
| **PATCH** | Partial update | ✗ | ✗ | Updated resource |
| **DELETE** | Remove resource | ✓ | ✗ | Empty (204) or confirmation |
| **HEAD** | Like GET, no body | ✓ | ✓ | None (metadata only) |

**Anti-pattern:** `POST /api/orders/123/cancel` → Instead use `DELETE /api/orders/123` or `PATCH /api/orders/123` with `{"status": "cancelled"}`

---

## 2. Status Codes — Return the Right One

```java
// 2xx: Success
200 OK           // GET, PUT, PATCH successful
201 Created      // POST created resource
202 Accepted     // Async operation started
204 No Content   // DELETE, no response body

// 3xx: Redirection
301 Moved Permanently
302 Found / Temporary Redirect

// 4xx: Client error
400 Bad Request     // Validation failed, malformed JSON
401 Unauthorized    // Missing/invalid auth
403 Forbidden       // Authenticated but no permission
404 Not Found       // Resource doesn't exist
409 Conflict        // Version mismatch, concurrent update
422 Unprocessable   // Semantically invalid

// 5xx: Server error
500 Internal Server Error
503 Service Unavailable
```java

---

## 3. REST Controller Pattern — Spring Boot

```java
/**
 * REST API endpoint for managing customer orders.
 *
 * <p>Handles order creation, retrieval, updates, and cancellation.
 * All endpoints require Bearer token authentication.</p>
 */
@RestController
@RequestMapping("/api/v1/orders")
@RequiredArgsConstructor
public class OrderRestController {

    private final OrderService orderService;
    private final OrderMapper orderMapper;

    /**
     * GET /api/v1/orders — List all orders with pagination.
     *
     * @param page     zero-indexed page number (default 0)
     * @param size     items per page (default 20, max 100)
     * @param sort     sort criteria, e.g. "createdAt,desc"
     * @return paginated list of orders
     */
    @GetMapping
    public ResponseEntity<Page<OrderResponse>> getOrders(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt,desc") String sort) {

        Pageable pageable = PageRequest.of(page, Math.min(size, 100),
                Sort.by(Sort.Direction.DESC, "createdAt"));
        Page<Order> orders = orderService.findAllOrders(pageable);

        return ResponseEntity.ok(orders.map(orderMapper::toResponse));
    }

    /**
     * GET /api/v1/orders/{id} — Retrieve a single order by ID.
     *
     * @param id the order ID
     * @return the order details
     * @throws EntityNotFoundException if order does not exist
     */
    @GetMapping("/{id}")
    public ResponseEntity<OrderResponse> getOrderById(@PathVariable Long id) {
        Order order = orderService.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Order not found: " + id));
        return ResponseEntity.ok(orderMapper.toResponse(order));
    }

    /**
     * POST /api/v1/orders — Create a new order.
     *
     * <p>The response includes the Location header pointing to the created resource.</p>
     *
     * @param request the order creation request
     * @return 201 Created with order details
     */
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(@Valid @RequestBody CreateOrderRequest request) {
        Order order = orderService.createOrder(request);
        OrderResponse response = orderMapper.toResponse(order);

        return ResponseEntity
                .created(URI.create("/api/v1/orders/" + order.getId()))
                .body(response);
    }

    /**
     * PATCH /api/v1/orders/{id} — Partially update an order.
     *
     * @param id      the order ID
     * @param request the update request (only non-null fields are updated)
     * @return 200 OK with updated order
     */
    @PatchMapping("/{id}")
    public ResponseEntity<OrderResponse> updateOrder(
            @PathVariable Long id,
            @Valid @RequestBody UpdateOrderRequest request) {

        Order order = orderService.updateOrder(id, request);
        return ResponseEntity.ok(orderMapper.toResponse(order));
    }

    /**
     * DELETE /api/v1/orders/{id} — Cancel an order.
     *
     * @param id the order ID
     * @return 204 No Content
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> cancelOrder(@PathVariable Long id) {
        orderService.cancelOrder(id);
        return ResponseEntity.noContent().build();
    }
}
```java

---

## 4. Request DTOs — Validation & Constraints

```java
/**
 * Request DTO for creating a new order.
 *
 * <p>Includes validation constraints using Jakarta Bean Validation.</p>
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateOrderRequest {

    /** Customer ID — must be positive. */
    @NotNull(message = "customerId is required")
    @Positive(message = "customerId must be positive")
    private Long customerId;

    /** Order items — at least one item required. */
    @NotEmpty(message = "items must not be empty")
    @Size(min = 1, max = 100, message = "order can contain 1-100 items")
    private List<OrderItemRequest> items;

    /** Delivery address — required, 5-200 characters. */
    @NotBlank(message = "address is required")
    @Size(min = 5, max = 200, message = "address length must be 5-200 characters")
    private String address;

    /** Optional notes — max 500 characters. */
    @Size(max = 500, message = "notes max 500 characters")
    private String notes;
}

/**
 * Nested DTO for order items.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderItemRequest {

    @NotNull(message = "productId is required")
    @Positive(message = "productId must be positive")
    private Long productId;

    @NotNull(message = "quantity is required")
    @Positive(message = "quantity must be at least 1")
    private Integer quantity;
}
```java

---

## 5. Response DTOs — Always Use DTOs

```java
/**
 * Response DTO for a complete order.
 *
 * <p>Maps from internal Order entity, exposing only safe fields.
 * Includes pagination metadata.</p>
 */
@Data
@Builder
public class OrderResponse {

    private Long id;
    private Long customerId;
    private String status;  // PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
    private BigDecimal totalAmount;
    private List<OrderItemResponse> items;
    private String deliveryAddress;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    /** HATEOAS link to retrieve this order. */
    private String selfLink;
}

@Data
@Builder
public class OrderItemResponse {
    private Long productId;
    private String productName;
    private Integer quantity;
    private BigDecimal unitPrice;
    private BigDecimal subtotal;  // quantity × unitPrice
}
```java

---

## 6. Error Response Format — Consistent Errors

```java
/**
 * Unified error response returned on any error.
 */
@Data
@Builder
public class ErrorResponse {

    /** Machine-readable error code, e.g. "ORDER_NOT_FOUND", "VALIDATION_ERROR". */
    private String code;

    /** Human-readable message. */
    private String message;

    /** HTTP status code. */
    private int status;

    /** ISO 8601 timestamp when error occurred. */
    private LocalDateTime timestamp;

    /** Request path that caused the error. */
    private String path;

    /** Field-level validation errors, if applicable. */
    private Map<String, List<String>> fieldErrors;
}

/**
 * Global exception handler using @RestControllerAdvice.
 */
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    /**
     * Handles validation errors from @Valid.
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationError(
            MethodArgumentNotValidException ex,
            HttpServletRequest request) {

        Map<String, List<String>> fieldErrors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
                fieldErrors.computeIfAbsent(error.getField(), k -> new ArrayList<>())
                        .add(error.getDefaultMessage())
        );

        ErrorResponse response = ErrorResponse.builder()
                .code("VALIDATION_ERROR")
                .message("Request validation failed")
                .status(HttpStatus.BAD_REQUEST.value())
                .timestamp(LocalDateTime.now())
                .path(request.getRequestURI())
                .fieldErrors(fieldErrors)
                .build();

        return ResponseEntity.badRequest().body(response);
    }

    /**
     * Handles resource not found.
     */
    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleEntityNotFound(
            EntityNotFoundException ex,
            HttpServletRequest request) {

        ErrorResponse response = ErrorResponse.builder()
                .code("RESOURCE_NOT_FOUND")
                .message(ex.getMessage())
                .status(HttpStatus.NOT_FOUND.value())
                .timestamp(LocalDateTime.now())
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }

    /**
     * Handles all other exceptions.
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(
            Exception ex,
            HttpServletRequest request) {

        log.error("Unhandled exception", ex);

        ErrorResponse response = ErrorResponse.builder()
                .code("INTERNAL_SERVER_ERROR")
                .message("An unexpected error occurred")
                .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                .timestamp(LocalDateTime.now())
                .path(request.getRequestURI())
                .build();

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }
}
```java

---

## 7. Pagination Response

```java
/**
 * Wrapper for paginated API responses.
 */
@Data
@Builder
public class PagedResponse<T> {

    private List<T> content;
    private int pageNumber;
    private int pageSize;
    private long totalElements;
    private int totalPages;
    private boolean hasNext;
    private boolean hasPrevious;

    /**
     * Convert Spring Page to PagedResponse.
     */
    public static <T> PagedResponse<T> from(Page<T> page) {
        return PagedResponse.<T>builder()
                .content(page.getContent())
                .pageNumber(page.getNumber())
                .pageSize(page.getSize())
                .totalElements(page.getTotalElements())
                .totalPages(page.getTotalPages())
                .hasNext(page.hasNext())
                .hasPrevious(page.hasPrevious())
                .build();
    }
}
```java

---

## 8. API Versioning Strategy

```java
// Option 1: URL path versioning (most common)
@RequestMapping("/api/v1/orders")  // current
@RequestMapping("/api/v2/orders")  // new version

// Option 2: Header versioning
@RequestMapping("/api/orders")
// Client sends: Accept-Version: 1.0

// Option 3: Accept header (content negotiation)
@RequestMapping("/api/orders")
// Client sends: Accept: application/vnd.company.orders-v1+json
```java

**Rule:** Always version your API from day one. Changing `/api/orders` to `/api/v1/orders` later breaks clients.

---

## 9. HATEOAS — Links in Responses

```java
/**
 * Order response with HATEOAS links.
 */
@Data
@Builder
public class OrderHateoasResponse {

    private Long id;
    private String status;
    private BigDecimal totalAmount;

    /** Links for navigation. */
    @JsonProperty("_links")
    private LinksResponse links;

    /**
     * Links object (HATEOAS).
     */
    @Data
    @Builder
    public static class LinksResponse {
        private LinkResponse self;
        private LinkResponse cancel;
        private LinkResponse shipments;
    }

    @Data
    @AllArgsConstructor
    public static class LinkResponse {
        private String href;
        private String rel;
    }
}

/**
 * REST controller returning HATEOAS links.
 */
@RestController
@RequestMapping("/api/v1/orders")
public class OrderRestController {

    @GetMapping("/{id}")
    public ResponseEntity<OrderHateoasResponse> getOrder(@PathVariable Long id) {
        Order order = orderService.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Order not found"));

        OrderHateoasResponse response = OrderHateoasResponse.builder()
                .id(order.getId())
                .status(order.getStatus().name())
                .totalAmount(order.getTotalAmount())
                .links(OrderHateoasResponse.LinksResponse.builder()
                        .self(new OrderHateoasResponse.LinkResponse(
                                "/api/v1/orders/" + id, "self"))
                        .cancel(new OrderHateoasResponse.LinkResponse(
                                "/api/v1/orders/" + id, "cancel"))
                        .shipments(new OrderHateoasResponse.LinkResponse(
                                "/api/v1/orders/" + id + "/shipments", "shipments"))
                        .build())
                .build();

        return ResponseEntity.ok(response);
    }
}
```java

---

## 10. Content Negotiation & Filtering

```java
/**
 * Support multiple response formats (JSON, XML).
 */
@RestController
@RequestMapping("/api/v1/orders")
public class OrderRestController {

    /**
     * GET /api/v1/orders/123?fields=id,status,amount
     * Returns only requested fields (sparse fieldset).
     */
    @GetMapping("/{id}")
    public ResponseEntity<Object> getOrder(
            @PathVariable Long id,
            @RequestParam(required = false) String fields) {

        Order order = orderService.findById(id)
                .orElseThrow();

        if (fields != null && !fields.isEmpty()) {
            return ResponseEntity.ok(filterFields(order, fields));
        }

        return ResponseEntity.ok(order);
    }

    private Object filterFields(Order order, String fields) {
        // Implementation: return only requested fields
        Map<String, Object> filtered = new LinkedHashMap<>();
        for (String field : fields.split(",")) {
            switch (field.trim()) {
                case "id" -> filtered.put("id", order.getId());
                case "status" -> filtered.put("status", order.getStatus());
                case "amount" -> filtered.put("amount", order.getTotalAmount());
            }
        }
        return filtered;
    }
}
```java

---

## Summary — REST API Checklist

✅ Use correct HTTP methods (GET/POST/PUT/PATCH/DELETE semantically)
✅ Return appropriate status codes (200, 201, 204, 400, 404, 500)
✅ Always use DTOs for request/response (never expose entities)
✅ Implement consistent error responses with error codes
✅ Add pagination for list endpoints (page, size, sort)
✅ Version your API from day one (/api/v1/...)
✅ Include validation on all inputs (@NotNull, @Valid)
✅ Use ResponseEntity for full control over response
✅ Implement HATEOAS links for discoverability
✅ Document with Javadoc on public endpoints
