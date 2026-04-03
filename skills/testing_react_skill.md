---
name: React Testing Skill
version: 1.0
description: >
  Comprehensive React testing with React Testing Library. Covers test naming conventions,
  user interaction testing, mocks, async testing, accessibility testing, test organization.
applies_to: [react, javascript, testing, jest, react-testing-library, typescript]
tags: [testing, react, rtl, jest, naming-conventions, accessibility, mocks]
---

# React Testing Skill — v1.0

---

## 1. Test File Organization & Naming

### 1.1 Project Structure

```plaintext
src/
├── components/
│   ├── OrderCard/
│   │   ├── OrderCard.tsx
│   │   ├── OrderCard.test.tsx      # Test file next to component
│   │   └── OrderCard.types.ts
│   │
│   ├── OrderForm/
│   │   ├── OrderForm.tsx
│   │   ├── OrderForm.test.tsx
│   │   └── OrderForm.types.ts
│   │
│   └── __tests__/
│       ├── integration/
│       │   └── OrderWorkflow.test.tsx
│       └── e2e/
│           └── OrderCreation.test.tsx
│
├── hooks/
│   ├── useOrders.ts
│   └── useOrders.test.ts            # Test file next to hook
│
└── __mocks__/
    ├── handlers.ts                   # MSW request handlers
    └── server.ts                      # Mock server setup
```jsx

### 1.2 Test Naming Convention

```typescript
/**
 * Test naming: describe('<Component>', () => { test('should <action>', ...) })
 * Also use: describe.given_xxx_when_yyy_then_zzz pattern
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import OrderCard from './OrderCard';

describe('OrderCard', () => {
  /**
   * Test: GIVEN valid order data | WHEN rendering | THEN display all fields.
   */
  it('should display order details when rendered with valid data', () => {
    // Arrange
    const mockOrder = {
      id: 1,
      customerId: 100,
      status: 'PENDING',
      totalAmount: 99.99,
      items: [
        { productId: 1, productName: 'Product A', quantity: 2, unitPrice: 25.00, subtotal: 50.00 }
      ],
      deliveryAddress: '123 Main St',
      createdAt: new Date('2026-04-03'),
    };

    // Act
    render(<OrderCard order={mockOrder} />);

    // Assert
    expect(screen.getByText('Order #1')).toBeInTheDocument();
    expect(screen.getByText('PENDING')).toBeInTheDocument();
    expect(screen.getByText('$99.99')).toBeInTheDocument();
    expect(screen.getByText('123 Main St')).toBeInTheDocument();
  });

  /**
   * Test: GIVEN null order | WHEN rendering | THEN show empty state.
   */
  it('should display empty state when order is null', () => {
    // Act
    render(<OrderCard order={null} />);

    // Assert
    expect(screen.getByText('No order data')).toBeInTheDocument();
  });

  /**
   * Test: GIVEN order card | WHEN clicking cancel button | THEN call onCancel callback.
   */
  it('should call onCancel callback when cancel button clicked', async () => {
    // Arrange
    const mockOrder = {
      id: 1,
      customerId: 100,
      status: 'PENDING',
      totalAmount: 99.99,
      items: [],
      deliveryAddress: '123 Main St',
      createdAt: new Date(),
    };

    const mockOnCancel = jest.fn();

    // Act
    render(<OrderCard order={mockOrder} onCancel={mockOnCancel} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await userEvent.click(cancelButton);

    // Assert
    expect(mockOnCancel).toHaveBeenCalledWith(1);  // Called with order ID
    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });
});
```jsx

---

## 2. React Testing Library Patterns

### 2.1 Query Best Practices

```typescript
import React from 'react';
import { render, screen, within } from '@testing-library/react';
import OrderForm from './OrderForm';

describe('OrderForm', () => {
  /**
   * Prefer user-centric queries (what user sees/interacts with).
   */
  it('should render form with proper labels', () => {
    render(<OrderForm />);

    // ✓ GOOD: Query by label (user sees this)
    const customerInput = screen.getByLabelText(/customer id/i);
    expect(customerInput).toBeInTheDocument();

    // ✓ GOOD: Query by role (semantic HTML)
    const submitButton = screen.getByRole('button', { name: /submit/i });
    expect(submitButton).toBeInTheDocument();

    // ✓ GOOD: Query by visible text
    const heading = screen.getByText('Create New Order');
    expect(heading).toBeInTheDocument();

    // ✗ AVOID: Query by test ID (implementation detail)
    // const form = screen.getByTestId('order-form');

    // ✗ AVOID: Query by CSS class (implementation detail)
    // const form = screen.getByClassName('form-container');
  });

  /**
   * Use within() to scope queries to specific container.
   */
  it('should find elements within specific container', () => {
    render(<OrderForm />);

    // Find all buttons in the form
    const form = screen.getByRole('form');
    const buttons = within(form).getAllByRole('button');

    expect(buttons).toHaveLength(2);  // Submit and Cancel buttons
  });

  /**
   * Use queryBy for elements that may not exist (returns null, not error).
   */
  it('should not display error message on valid input', () => {
    render(<OrderForm />);

    // queryBy returns null if not found (no error thrown)
    const errorMessage = screen.queryByText(/required/i);
    expect(errorMessage).not.toBeInTheDocument();
  });
});
```jsx

---

## 3. User Interaction Testing

### 3.1 userEvent vs fireEvent

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import OrderCheckout from './OrderCheckout';

describe('OrderCheckout', () => {
  /**
   * ✓ PREFER userEvent: Simulates real user interactions.
   */
  it('should process checkout when form submitted', async () => {
    // Arrange
    const mockOnCheckout = jest.fn();
    render(<OrderCheckout onCheckout={mockOnCheckout} />);

    const user = userEvent.setup();

    // Act: Simulate real user typing
    const emailInput = screen.getByLabelText(/email/i);
    await user.type(emailInput, 'john@example.com');

    const addressInput = screen.getByLabelText(/address/i);
    await user.type(addressInput, '123 Main St');

    const submitButton = screen.getByRole('button', { name: /checkout/i });
    await user.click(submitButton);

    // Assert
    await waitFor(() => {
      expect(mockOnCheckout).toHaveBeenCalledWith({
        email: 'john@example.com',
        address: '123 Main St',
      });
    });
  });

  /**
   * ✗ AVOID fireEvent: Doesn't simulate real user interactions.
   */
  it('should NOT use fireEvent for normal interactions', () => {
    render(<OrderCheckout />);

    // ✗ AVOID: fireEvent doesn't bubble or trigger all event handlers
    // fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    // ✓ USE userEvent instead
  });
});
```jsx

---

## 4. Async & Waiting

### 4.1 waitFor and findBy

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import OrderList from './OrderList';

describe('OrderList', () => {
  /**
   * Test: GIVEN component with async data fetch | WHEN mounted | THEN load and display orders.
   */
  it('should load and display orders from API', async () => {
    // Arrange
    const mockOrders = [
      { id: 1, customerId: 100, status: 'PENDING', totalAmount: 50 },
      { id: 2, customerId: 200, status: 'SHIPPED', totalAmount: 75 },
    ];

    // Mock API call
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockOrders),
      })
    );

    // Act
    render(<OrderList />);

    // Assert: Use findBy for async elements (combines getBy + waitFor)
    const order1 = await screen.findByText(/Order #1/);
    const order2 = await screen.findByText(/Order #2/);

    expect(order1).toBeInTheDocument();
    expect(order2).toBeInTheDocument();
  });

  /**
   * Test: GIVEN async operation | WHEN waiting | THEN check element appears.
   */
  it('should show loading indicator while fetching', async () => {
    // Arrange
    render(<OrderList />);

    // Assert: Loading indicator visible immediately
    const loadingSpinner = screen.getByRole('progressbar', { hidden: true });
    expect(loadingSpinner).toBeInTheDocument();

    // Assert: Loading indicator disappears after data loads
    await waitFor(() => {
      expect(loadingSpinner).not.toBeInTheDocument();
    }, { timeout: 3000 });
  });
});
```jsx

---

## 5. Mocking with Jest

### 5.1 Mock Functions & Modules

```typescript
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import OrderForm from './OrderForm';

// Mock entire API module
jest.mock('../api/orderApi', () => ({
  submitOrder: jest.fn(),
}));

import { submitOrder } from '../api/orderApi';

describe('OrderForm with Mocks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Test: GIVEN form submission | WHEN API succeeds | THEN show success message.
   */
  it('should show success message when API returns success', async () => {
    // Arrange
    (submitOrder as jest.Mock).mockResolvedValue({ success: true, orderId: 123 });

    const user = userEvent.setup();
    render(<OrderForm />);

    // Act
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);

    // Assert
    const successMessage = await screen.findByText(/order created successfully/i);
    expect(successMessage).toBeInTheDocument();

    expect(submitOrder).toHaveBeenCalledTimes(1);
    expect(submitOrder).toHaveBeenCalledWith(
      expect.objectContaining({
        customerId: expect.any(Number),
      })
    );
  });

  /**
   * Test: GIVEN form submission | WHEN API fails | THEN show error message.
   */
  it('should show error message when API returns error', async () => {
    // Arrange
    (submitOrder as jest.Mock).mockRejectedValue(
      new Error('Network error')
    );

    const user = userEvent.setup();
    render(<OrderForm />);

    // Act
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);

    // Assert
    const errorMessage = await screen.findByText(/network error/i);
    expect(errorMessage).toBeInTheDocument();
  });
});
```jsx

---

## 6. Accessibility Testing

### 6.1 a11y Checks in Tests

```typescript
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import OrderCard from './OrderCard';

expect.extend(toHaveNoViolations);

describe('OrderCard Accessibility', () => {
  /**
   * Test: GIVEN component | WHEN rendered | THEN have no a11y violations.
   */
  it('should not have accessibility violations', async () => {
    // Arrange & Act
    const { container } = render(
      <OrderCard order={{
        id: 1,
        customerId: 100,
        status: 'PENDING',
        totalAmount: 99.99,
        items: [],
        deliveryAddress: '123 Main St',
        createdAt: new Date(),
      }} />
    );

    // Assert
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  /**
   * Test: GIVEN form with labels | WHEN testing | THEN ensure labels are associated.
   */
  it('should have proper label associations', () => {
    render(<OrderForm />);

    // Assert: All inputs have associated labels
    const inputs = screen.getAllByRole('textbox');
    inputs.forEach(input => {
      const label = screen.getByText(
        new RegExp(input.getAttribute('aria-label') || '', 'i')
      );
      expect(label).toBeInTheDocument();
    });
  });

  /**
   * Test: GIVEN interactive component | WHEN using keyboard | THEN remain accessible.
   */
  it('should be keyboard navigable', async () => {
    const user = userEvent.setup();
    render(<OrderForm />);

    // Act: Tab through form
    await user.tab();
    const firstInput = screen.getByLabelText(/customer id/i);
    expect(firstInput).toHaveFocus();

    await user.tab();
    const secondInput = screen.getByLabelText(/address/i);
    expect(secondInput).toHaveFocus();
  });
});
```jsx

---

## 7. Setup & Teardown

### 7.1 beforeEach, afterEach, setupFilesAfterEnv

```typescript
// jest.setup.ts — runs before all tests

import '@testing-library/jest-dom';
import { server } from './__mocks__/server';

// Start mock server before all tests
beforeAll(() => server.listen());

// Reset handlers after each test
afterEach(() => server.resetHandlers());

// Clean up after all tests
afterAll(() => server.close());

// Enable custom matchers
expect.extend({
  toHaveBeenCalledWithOrderData(received, expectedOrder) {
    const pass = received.mock.calls.some(
      call => call[0].id === expectedOrder.id
    );

    return {
      pass,
      message: () =>
        `expected mock to have been called with order ${expectedOrder.id}`,
    };
  },
});

declare global {
  namespace jest {
    interface Matchers<R> {
      toHaveBeenCalledWithOrderData(expectedOrder: any): R;
    }
  }
}
```jsx

```typescript
// OrderForm.test.tsx

beforeEach(() => {
  // Clear all mocks before each test
  jest.clearAllMocks();

  // Reset form to initial state
  // (sometimes not needed if rendering fresh component each time)
});

afterEach(() => {
  // Cleanup after each test
  jest.restoreAllMocks();
});
```jsx

---

## 8. React Testing Checklist

✅ Organize tests next to components (same folder)
✅ Use meaningful test names: `should <action> when <condition>`
✅ Query by user-centric selectors (label, role, text — not test ID)
✅ Use userEvent instead of fireEvent
✅ Use findBy for async elements (not getBy + waitFor)
✅ Test user interactions, not implementation details
✅ Mock external APIs and dependencies
✅ Test accessibility with jest-axe
✅ Verify keyboard navigation (Tab, Enter, Escape)
✅ Check ARIA labels and roles
✅ Mock hooks with jest.mock() for isolation
✅ Clear mocks between tests (jest.clearAllMocks)
✅ Test loading/error states
✅ Verify callback functions are called with correct args
✅ Keep tests independent — no shared state
