---
name: JUnit5 Testing Skill
version: 1.0
description: >
  Comprehensive testing patterns for Java with JUnit5, Mockito, test databases,
  parameterized tests, test naming conventions, mocks, and test fixtures.
applies_to: [java, junit5, testing, mockito, testcontainers, spring-boot]
tags: [testing, junit5, mockito, test-db, fixtures, naming-conventions]
---

# JUnit5 Testing Skill — v1.0

---

## 1. Test Method Naming Convention

### 1.1 Given-When-Then (GWT) Pattern

```java
/**
 * Test class for OrderService with meaningful test names.
 *
 * Naming pattern: givenXxx_whenYyy_thenZzz()
 *   - givenXxx: Setup/precondition
 *   - whenYyy: Action being tested
 *   - thenZzz: Expected outcome
 */
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @InjectMocks
    private OrderService orderService;

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private PaymentGateway paymentGateway;

    /**
     * Test: GIVEN a valid order exists | WHEN getOrderById is called | THEN return the order.
     */
    @Test
    @DisplayName("Given valid order exists, when fetching by ID, then return the order")
    void givenValidOrderExists_whenGetOrderById_thenReturnOrder() {
        // Arrange
        Long orderId = 123L;
        Order expectedOrder = Order.builder()
                .id(orderId)
                .customerId(456L)
                .status(OrderStatus.PENDING)
                .totalAmount(BigDecimal.valueOf(99.99))
                .build();

        when(orderRepository.findById(orderId)).thenReturn(Optional.of(expectedOrder));

        // Act
        Optional<Order> result = orderService.getOrderById(orderId);

        // Assert
        assertTrue(result.isPresent());
        assertEquals(expectedOrder.getId(), result.get().getId());
        assertEquals(expectedOrder.getStatus(), result.get().getStatus());
        verify(orderRepository, times(1)).findById(orderId);
    }

    /**
     * Test: GIVEN order doesn't exist | WHEN getOrderById is called | THEN throw exception.
     */
    @Test
    @DisplayName("Given order doesn't exist, when fetching by ID, then throw EntityNotFoundException")
    void givenOrderNotExists_whenGetOrderById_thenThrowException() {
        // Arrange
        Long orderId = 999L;
        when(orderRepository.findById(orderId)).thenReturn(Optional.empty());

        // Act & Assert
        assertThrows(EntityNotFoundException.class, () ->
                orderService.getOrderById(orderId)
        );

        verify(orderRepository, times(1)).findById(orderId);
        verify(paymentGateway, never()).processPayment(any());
    }

    /**
     * Test: GIVEN valid order and payment gateway succeeds | WHEN processing order | THEN return success.
     */
    @Test
    @DisplayName("Given valid order and successful payment, when processing, then return success")
    void givenValidOrderAndSuccessfulPayment_whenProcessing_thenReturnSuccess() {
        // Arrange
        Order order = Order.builder()
                .id(1L)
                .totalAmount(BigDecimal.valueOf(100.00))
                .build();

        PaymentResult paymentResult = PaymentResult.builder()
                .successful(true)
                .transactionId("TXN-12345")
                .build();

        when(paymentGateway.processPayment(any())).thenReturn(paymentResult);

        // Act
        OrderProcessResult result = orderService.processOrder(order);

        // Assert
        assertTrue(result.isSuccessful());
        assertEquals("TXN-12345", result.getTransactionId());
        verify(paymentGateway, times(1)).processPayment(order);
    }

    /**
     * Test: GIVEN order with insufficient funds | WHEN processing payment | THEN fail.
     */
    @Test
    @DisplayName("Given insufficient funds, when processing payment, then return failure")
    void givenInsufficientFunds_whenProcessingPayment_thenReturnFailure() {
        // Arrange
        Order order = Order.builder()
                .id(1L)
                .totalAmount(BigDecimal.valueOf(5000.00))
                .build();

        when(paymentGateway.processPayment(any()))
                .thenThrow(new InsufficientFundsException("Insufficient balance"));

        // Act & Assert
        assertThrows(InsufficientFundsException.class, () ->
                orderService.processOrder(order)
        );
    }
}
```plaintext

---

## 2. AAA Pattern — Arrange, Act, Assert

```java
@ExtendWith(MockitoExtension.class)
class OrderRepositoryTest {

    @InjectMocks
    private OrderService orderService;

    @Mock
    private OrderRepository orderRepository;

    /**
     * AAA Pattern:
     * - Arrange: Set up test data and mocks
     * - Act: Execute the code under test
     * - Assert: Verify the results
     */
    @Test
    void givenNewOrder_whenSaving_thenAssignIdAndReturnOrder() {
        // ===== ARRANGE =====
        Order newOrder = Order.builder()
                .customerId(100L)
                .status(OrderStatus.PENDING)
                .totalAmount(BigDecimal.valueOf(50.00))
                .items(List.of(
                    new OrderItem(1L, "Product A", 2, BigDecimal.valueOf(25.00))
                ))
                .build();

        Order savedOrder = newOrder.toBuilder()
                .id(1L)  // Database assigns ID
                .createdAt(LocalDateTime.now())
                .build();

        when(orderRepository.save(any(Order.class))).thenReturn(savedOrder);

        // ===== ACT =====
        Order result = orderService.createOrder(newOrder);

        // ===== ASSERT =====
        assertNotNull(result.getId(), "Order ID should be assigned by database");
        assertEquals(100L, result.getCustomerId());
        assertEquals(OrderStatus.PENDING, result.getStatus());
        assertEquals(1, result.getItems().size());
        assertNotNull(result.getCreatedAt());

        verify(orderRepository, times(1)).save(any(Order.class));
    }
}
```plaintext

---

## 3. Mocking with Mockito

### 3.1 Mock Creation and Verification

```java
@ExtendWith(MockitoExtension.class)
class PaymentServiceTest {

    @InjectMocks
    private OrderService orderService;

    @Mock
    private PaymentGateway paymentGateway;

    @Mock
    private EmailService emailService;

    /**
     * Mock setup with behavior configuration.
     */
    @Test
    void testMockConfiguration() {
        // Configure mock to return value
        when(paymentGateway.processPayment(any()))
                .thenReturn(PaymentResult.builder()
                        .successful(true)
                        .transactionId("TXN-001")
                        .build());

        // Configure mock to throw exception
        when(emailService.sendEmail(contains("invalid@")))
                .thenThrow(new EmailException("Invalid email"));

        // Configure mock for consecutive calls
        when(paymentGateway.retry(any()))
                .thenReturn(PaymentResult.builder().successful(false).build())
                .thenReturn(PaymentResult.builder().successful(true).build());

        // Verify interactions
        Order order = new Order();
        orderService.processOrder(order);

        verify(paymentGateway, times(1)).processPayment(order);
        verify(paymentGateway, atLeastOnce()).processPayment(any());
        verify(emailService, never()).sendEmail(any());
    }

    /**
     * ArgumentCaptor to capture and inspect arguments.
     */
    @Test
    void testArgumentCaptor() {
        // Arrange
        ArgumentCaptor<Order> orderCaptor = ArgumentCaptor.forClass(Order.class);

        Order order = Order.builder()
                .customerId(123L)
                .totalAmount(BigDecimal.valueOf(99.99))
                .build();

        when(paymentGateway.processPayment(any()))
                .thenReturn(PaymentResult.builder().successful(true).build());

        // Act
        orderService.processOrder(order);

        // Assert
        verify(paymentGateway).processPayment(orderCaptor.capture());
        Order capturedOrder = orderCaptor.getValue();

        assertEquals(123L, capturedOrder.getCustomerId());
        assertEquals(BigDecimal.valueOf(99.99), capturedOrder.getTotalAmount());
    }
}
```plaintext

### 3.2 Spy vs Mock

```java
class SpyVsMockTest {

    /**
     * Spy: Calls real methods by default, but can be configured.
     * Mock: Stubs all methods, no real implementations.
     */
    @Test
    void spyCallsRealMethods() {
        // Spy: calls real method unless stubbed
        OrderRepository realRepo = new OrderRepository();
        OrderRepository spyRepo = spy(realRepo);

        when(spyRepo.findById(999L)).thenReturn(Optional.empty());
        when(spyRepo.findById(1L)).thenCallRealMethod();

        // This calls the real method
        spyRepo.findById(1L);

        verify(spyRepo).findById(1L);
    }

    @Test
    void mockDoesNotCallRealMethods() {
        // Mock: all methods are stubbed, no real calls
        OrderRepository mockRepo = mock(OrderRepository.class);

        when(mockRepo.findById(any())).thenReturn(Optional.empty());

        // Never calls real implementation
        mockRepo.findById(123L);

        verify(mockRepo).findById(123L);
    }
}
```plaintext

---

## 4. Testing with Test Databases (Testcontainers)

### 4.1 PostgreSQL with Testcontainers

```java
/**
 * Integration test using real PostgreSQL database via Testcontainers.
 *
 * Testcontainers manages Docker containers for databases during testing.
 */
@DataJpaTest
@Testcontainers
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class OrderRepositoryIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("testuser")
            .withPassword("testpass");

    @DynamicPropertySource
    static void setProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private TestEntityManager em;

    /**
     * Test: GIVEN empty database | WHEN saving order | THEN persist to database.
     */
    @Test
    void givenEmptyDatabase_whenSavingOrder_thenPersistToDatabase() {
        // Arrange
        Order order = Order.builder()
                .customerId(1L)
                .status(OrderStatus.PENDING)
                .totalAmount(BigDecimal.valueOf(100.00))
                .build();

        // Act
        Order saved = orderRepository.save(order);
        em.flush();
        em.clear();

        // Assert
        Order retrieved = orderRepository.findById(saved.getId()).orElseThrow();

        assertEquals(1L, retrieved.getCustomerId());
        assertEquals(OrderStatus.PENDING, retrieved.getStatus());
    }

    /**
     * Test: GIVEN orders in database | WHEN finding by customer | THEN return orders.
     */
    @Test
    void givenOrdersInDatabase_whenFindByCustomer_thenReturnOrders() {
        // Arrange
        Long customerId = 100L;

        orderRepository.save(Order.builder()
                .customerId(customerId)
                .status(OrderStatus.PENDING)
                .totalAmount(BigDecimal.valueOf(50.00))
                .build());

        orderRepository.save(Order.builder()
                .customerId(customerId)
                .status(OrderStatus.CONFIRMED)
                .totalAmount(BigDecimal.valueOf(75.00))
                .build());

        orderRepository.save(Order.builder()
                .customerId(999L)  // Different customer
                .status(OrderStatus.PENDING)
                .totalAmount(BigDecimal.valueOf(25.00))
                .build());

        em.flush();

        // Act
        List<Order> orders = orderRepository.findByCustomerId(customerId);

        // Assert
        assertEquals(2, orders.size());
        assertTrue(orders.stream().allMatch(o -> o.getCustomerId().equals(customerId)));
    }
}
```plaintext

---

## 5. Parameterized Tests

### 5.1 @ParameterizedTest with Multiple Inputs

```java
class OrderValidationTest {

    /**
     * Test the same logic with multiple input combinations.
     *
     * Reduces code duplication and tests edge cases comprehensively.
     */
    @ParameterizedTest
    @CsvSource({
            "100.00, 1, 100.00",      // totalAmount, quantity, unitPrice
            "50.00, 2, 25.00",
            "1.00, 100, 0.01",
            "999.99, 1, 999.99",
    })
    @DisplayName("Given various prices, when calculating subtotal, then multiply correctly")
    void givenVariousPrices_whenCalculating_thenMultiplyCorrectly(
            String total, int quantity, String unitPrice) {

        // Act
        BigDecimal result = new BigDecimal(unitPrice).multiply(BigDecimal.valueOf(quantity));

        // Assert
        assertEquals(new BigDecimal(total), result);
    }

    /**
     * Test with value sources.
     */
    @ParameterizedTest
    @ValueSource(strings = {"PENDING", "CONFIRMED", "SHIPPED"})
    @DisplayName("Given valid status, when validating, then succeed")
    void givenValidStatus_whenValidating_thenSucceed(String status) {
        assertTrue(OrderStatus.isValid(status));
    }

    /**
     * Test with method source for complex test cases.
     */
    @ParameterizedTest
    @MethodSource("provideInvalidOrders")
    @DisplayName("Given invalid orders, when validating, then throw exception")
    void givenInvalidOrders_whenValidating_thenThrowException(Order order) {
        assertThrows(ValidationException.class, () ->
                OrderValidator.validate(order)
        );
    }

    static Stream<Order> provideInvalidOrders() {
        return Stream.of(
                Order.builder().customerId(null).build(),
                Order.builder().customerId(1L).totalAmount(BigDecimal.ZERO).build(),
                Order.builder().customerId(1L).totalAmount(BigDecimal.valueOf(-10)).build(),
                Order.builder().customerId(1L).totalAmount(BigDecimal.valueOf(100)).items(List.of()).build()
        );
    }
}
```plaintext

---

## 6. Test Fixtures and Lifecycle

### 6.1 Before/After and Setup

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceLifecycleTest {

    private OrderService orderService;
    private OrderRepository orderRepository;
    private PaymentGateway paymentGateway;

    /**
     * @BeforeEach: Runs before EVERY test.
     */
    @BeforeEach
    void setUp() {
        orderRepository = mock(OrderRepository.class);
        paymentGateway = mock(PaymentGateway.class);
        orderService = new OrderService(orderRepository, paymentGateway);
    }

    /**
     * @AfterEach: Runs after EVERY test (cleanup).
     */
    @AfterEach
    void tearDown() {
        reset(orderRepository, paymentGateway);
    }

    /**
     * @BeforeAll: Runs ONCE before ALL tests (static method).
     */
    @BeforeAll
    static void setUpClass() {
        System.out.println("Class setup: Initialize once for all tests");
    }

    /**
     * @AfterAll: Runs ONCE after ALL tests (static method, cleanup).
     */
    @AfterAll
    static void tearDownClass() {
        System.out.println("Class teardown: Final cleanup");
    }

    @Test
    void test1() {
        // setUp() was called before this
        assertTrue(true);
        // tearDown() will be called after this
    }

    @Test
    void test2() {
        // setUp() was called before this (fresh state)
        assertTrue(true);
        // tearDown() will be called after this
    }
}
```plaintext

---

## 7. Testing Exceptions

### 7.1 Assert Exception Type and Message

```java
class ExceptionHandlingTest {

    @Test
    void givenInvalidOrderId_whenGettingOrder_thenThrowException() {
        // Arrange
        OrderService orderService = new OrderService(mock(OrderRepository.class), mock(PaymentGateway.class));

        // Act & Assert
        assertThrows(EntityNotFoundException.class, () ->
                orderService.getOrderById(999L)
        );
    }

    /**
     * Verify exception message content.
     */
    @Test
    void givenNullOrder_whenValidating_thenThrowExceptionWithMessage() {
        // Act & Assert
        EntityNotFoundException e = assertThrows(EntityNotFoundException.class, () ->
                OrderValidator.validate(null)
        );

        assertTrue(e.getMessage().contains("Order"));
        assertTrue(e.getMessage().contains("not found"));
    }

    /**
     * Use assertAll to verify multiple assertions.
     */
    @Test
    void givenPaymentFailure_whenProcessing_thenThrowDetailedException() {
        OrderService orderService = new OrderService(mock(OrderRepository.class), mock(PaymentGateway.class));

        PaymentFailedException e = assertThrows(PaymentFailedException.class, () ->
                orderService.processOrder(new Order())
        );

        assertAll("Payment error details",
                () -> assertEquals("PAYMENT_DECLINED", e.getErrorCode()),
                () -> assertEquals("Card declined", e.getMessage()),
                () -> assertNotNull(e.getTransactionId())
        );
    }
}
```plaintext

---

## 8. JUnit5 Testing Checklist

✅ Use meaningful test method names: `givenXxx_whenYyy_thenZzz()`
✅ Follow AAA pattern: Arrange, Act, Assert
✅ Use @DisplayName for human-readable test descriptions
✅ Mock external dependencies with @Mock and @InjectMocks
✅ Use ArgumentCaptor to verify method arguments
✅ Use Testcontainers for real database integration tests
✅ Verify mock interactions with verify(), times(), atLeastOnce()
✅ Use parameterized tests to reduce code duplication
✅ Test both success and failure scenarios
✅ Use assertAll() for multiple assertions
✅ Implement setUp() and tearDown() for test isolation
✅ Test exception types and messages
✅ Use @Nested classes to group related tests
✅ Keep tests independent — no shared state between tests
