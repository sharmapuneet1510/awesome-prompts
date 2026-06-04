---
name: React Advanced Coding Skill
version: 2.0
description: >
  Reusable skill module for React/TypeScript development. Covers React 18/19
  features, component design, typed props with JSDoc, hooks, TanStack Query,
  accessibility, and Vitest + RTL test generation.
applies_to: [react, typescript, vite, tanstack-query, zustand, tailwindcss]
---

# React Advanced Coding Skill — v2.0

---

## 1. Version Detection First

Check what is installed before writing code:

```bash
node -v
cat package.json | grep '"react"'
cat package.json | grep '"typescript"'
```jsx

| React Version | Key Features |
|--------------|-------------|
| React 17 | Stable, no concurrent features |
| React 18 | Concurrent rendering, `useTransition`, `useDeferredValue`, `Suspense` for data |
| React 19 | `use()` hook, `useFormStatus`, `useOptimistic`, Server Actions |

---

## 2. Component Design Principles

### One Component = One Job

Each component should do exactly one thing. If it does more, split it.

```jsx
❌ UserDashboard — renders layout, fetches data, shows charts, handles modals
✅ UserDashboard  — layout only
✅ useUserStats   — fetches the data (custom hook)
✅ StatsChart     — renders one chart
✅ UserModal      — one modal
```jsx

### Component File Structure

Every non-trivial component lives in its own folder:

```jsx
features/orders/
  components/
    OrderCard/
      OrderCard.tsx         ← the component
      OrderCard.test.tsx    ← the tests
      index.ts              ← export: export { OrderCard } from './OrderCard'
  hooks/
    useOrders.ts            ← TanStack Query hook
  types/
    order.types.ts          ← TypeScript types for orders
```jsx

---

## 3. TypeScript — Always Strict

### Typed Props with JSDoc (Documentation)

Every exported component must have a named interface for its props, with JSDoc:

```tsx
/**
 * Displays a summary card for a single customer order.
 *
 * Shows the order ID, current status (colour-coded), and formatted total.
 * Clicking the card triggers the onClick handler.
 *
 * @example
 * <OrderCard
 *   orderId={42}
 *   status="SHIPPED"
 *   totalAmount={99.99}
 *   currency="GBP"
 *   onClick={(id) => navigate(`/orders/${id}`)}
 * />
 */
interface OrderCardProps {
  /** Unique identifier for this order. */
  orderId: number;

  /** Current status of the order. Determines the badge colour. */
  status: 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';

  /** Total monetary value of the order. */
  totalAmount: number;

  /** ISO 4217 currency code for formatting (e.g. 'GBP', 'USD'). */
  currency: string;

  /** Called when the user clicks the card. Receives the orderId. */
  onClick: (orderId: number) => void;
}

export function OrderCard({ orderId, status, totalAmount, currency, onClick }: OrderCardProps) {
  // ...
}
```jsx

### Type Aliases and Discriminated Unions

Use discriminated unions to make impossible states impossible:

```tsx
/**
 * Represents the state of an async operation.
 * Only one state can be active at a time.
 */
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

// Usage in a component — TypeScript narrows the type in each branch
function renderState<T>(state: AsyncState<T>) {
  switch (state.status) {
    case 'idle':    return <EmptyState />;
    case 'loading': return <Spinner />;
    case 'success': return <DataView data={state.data} />;  // state.data is T here
    case 'error':   return <ErrorMessage error={state.error} />;
  }
}
```jsx

---

## 4. Hooks — Best Practices

### Custom Hooks for Data Fetching (TanStack Query)

Never put `fetch` calls inside component bodies. Put them in custom hooks.

```tsx
// hooks/useOrders.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

/**
 * Query key factory for orders.
 *
 * Centralises all order-related cache keys so they are consistent
 * across the app and easy to invalidate.
 */
const orderKeys = {
  all: ['orders'] as const,
  byCustomer: (customerId: number) => [...orderKeys.all, 'customer', customerId] as const,
  detail: (orderId: number) => [...orderKeys.all, 'detail', orderId] as const,
};

/**
 * Fetches all orders for a given customer.
 *
 * Handles caching, background refetching, and error state automatically.
 * The component using this hook does not need any useState or useEffect.
 *
 * @param customerId - The customer whose orders to load. Must be > 0.
 * @returns TanStack Query result — { data, isPending, isError }
 */
export function useOrders(customerId: number) {
  return useQuery({
    queryKey: orderKeys.byCustomer(customerId),
    queryFn: () => fetchOrdersForCustomer(customerId),
    enabled: customerId > 0,  // Don't fetch if customerId is not ready
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
  });
}

/**
 * Provides a mutation for creating a new order.
 *
 * On success, automatically invalidates the customer's order list
 * so the UI refreshes with the new order.
 *
 * @param customerId - Used to invalidate the correct cache entry on success.
 */
export function useCreateOrder(customerId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateOrderRequest) => createOrder(request),
    onSuccess: () => {
      // Tell TanStack Query that the customer's order list is stale
      queryClient.invalidateQueries({ queryKey: orderKeys.byCustomer(customerId) });
    },
  });
}
```jsx

### Custom State Hook

```tsx
/**
 * Manages the open/closed state of a modal dialog.
 *
 * @returns isOpen flag and open/close handlers.
 *
 * @example
 * const { isOpen, open, close } = useModal();
 * <button onClick={open}>Open</button>
 * <Modal isOpen={isOpen} onClose={close} />
 */
export function useModal() {
  const [isOpen, setIsOpen] = useState(false);

  /** Opens the modal. */
  const open = useCallback(() => setIsOpen(true), []);

  /** Closes the modal. */
  const close = useCallback(() => setIsOpen(false), []);

  return { isOpen, open, close };
}
```jsx

---

## 5. Always Handle All States

Never render a component that might receive `undefined` data.

```tsx
/**
 * Displays the list of orders for the current customer.
 *
 * Handles loading, error, empty, and populated states explicitly.
 * The user always sees something meaningful — never a blank screen.
 */
export function OrderList({ customerId }: { customerId: number }) {
  const { data: orders, isPending, isError } = useOrders(customerId);

  // While data is loading — show a skeleton
  if (isPending) {
    return <OrderListSkeleton />;
  }

  // If the request failed — show a helpful message
  if (isError) {
    return (
      <ErrorMessage
        title="Could not load orders"
        description="Please check your connection and try refreshing."
      />
    );
  }

  // If the list is empty — explain why
  if (orders.length === 0) {
    return <EmptyState message="You have no orders yet." />;
  }

  // Happy path — render the list
  return (
    <ul aria-label="Your orders">
      {orders.map((order) => (
        // Never use array index as key — use a stable unique ID
        <li key={order.id}>
          <OrderCard {...order} />
        </li>
      ))}
    </ul>
  );
}
```jsx

---

## 6. Forms — react-hook-form + Zod

```tsx
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

/**
 * Validation schema for the create order form.
 *
 * Zod validates all fields before the submit handler is called.
 * Error messages are defined here, not in the component.
 */
const createOrderSchema = z.object({
  customerName: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be 100 characters or fewer'),
  email: z
    .string()
    .email('Please enter a valid email address'),
  quantity: z
    .number({ invalid_type_error: 'Quantity must be a number' })
    .int('Quantity must be a whole number')
    .min(1, 'Quantity must be at least 1'),
});

/** TypeScript type is derived from the schema — always stays in sync */
type CreateOrderFormValues = z.infer<typeof createOrderSchema>;

/**
 * Form for creating a new order.
 *
 * Validates all fields before submitting. Shows field-level error
 * messages when validation fails. Disables the button while submitting.
 */
export function CreateOrderForm({ onSuccess }: { onSuccess: () => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateOrderFormValues>({
    resolver: zodResolver(createOrderSchema),
  });

  async function onSubmit(data: CreateOrderFormValues) {
    await submitOrder(data);
    onSuccess();
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>

      {/* Customer Name field with accessible error message */}
      <div>
        <label htmlFor="customerName">Customer Name</label>
        <input
          id="customerName"
          type="text"
          aria-required="true"
          aria-invalid={!!errors.customerName}
          aria-describedby={errors.customerName ? 'customerName-error' : undefined}
          {...register('customerName')}
        />
        {errors.customerName && (
          <span id="customerName-error" role="alert" className="text-red-600">
            {errors.customerName.message}
          </span>
        )}
      </div>

      {/* Submit button — disabled and shows feedback while submitting */}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Create Order'}
      </button>

    </form>
  );
}
```jsx

---

## 7. Accessibility Checklist

Every component must pass these checks before being complete:

- [ ] Every `<input>` has a linked `<label>` via `htmlFor` / `id`
- [ ] Error messages use `role="alert"` so screen readers announce them
- [ ] Interactive elements (`button`, `a`, custom) are reachable via `Tab`
- [ ] Custom clickable elements have `role="button"` and handle `Enter`/`Space` keys
- [ ] Images have meaningful `alt` text (or `alt=""` if decorative)
- [ ] Colour is not the only way to convey status (use text or icons too)
- [ ] Focus is managed correctly when modals open/close

---

## 8. Testing Standards — Vitest + React Testing Library

### Component Unit Tests

```tsx
// OrderCard.test.tsx

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { OrderCard } from './OrderCard';

describe('OrderCard', () => {
  const defaultProps = {
    orderId: 42,
    status: 'PENDING' as const,
    totalAmount: 99.99,
    currency: 'GBP',
    onClick: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays the order ID, status, and formatted amount', () => {
    // Arrange & Act
    render(<OrderCard {...defaultProps} />);

    // Assert — test what the user sees, not the internal state
    expect(screen.getByText('Order #42')).toBeInTheDocument();
    expect(screen.getByText('PENDING')).toBeInTheDocument();
    expect(screen.getByText('£99.99')).toBeInTheDocument();
  });

  it('calls onClick with the correct order ID when clicked', async () => {
    // Arrange
    const user = userEvent.setup();
    render(<OrderCard {...defaultProps} />);

    // Act
    await user.click(screen.getByRole('button'));

    // Assert
    expect(defaultProps.onClick).toHaveBeenCalledOnce();
    expect(defaultProps.onClick).toHaveBeenCalledWith(42);
  });

  it('can be activated with the Enter key for keyboard users', async () => {
    // Accessibility: keyboard users must be able to interact
    const user = userEvent.setup();
    render(<OrderCard {...defaultProps} />);

    await user.tab();
    await user.keyboard('{Enter}');

    expect(defaultProps.onClick).toHaveBeenCalledWith(42);
  });

  it('has an accessible label describing the order', () => {
    render(<OrderCard {...defaultProps} />);

    // Screen readers should announce this clearly
    expect(screen.getByRole('button', { name: /order 42/i })).toBeInTheDocument();
  });
});
```jsx

### Hook Tests

```tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { http, HttpResponse } from 'msw';
import { server } from '../../../mocks/server';

describe('useOrders', () => {
  it('returns orders when API responds successfully', async () => {
    // Arrange — mock the API response
    server.use(
      http.get('/api/v1/orders', () =>
        HttpResponse.json([{ id: 1, status: 'PENDING' }])
      )
    );

    const queryClient = new QueryClient();
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    // Act
    const { result } = renderHook(() => useOrders(1), { wrapper });

    // Assert
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(1);
  });
});
```jsx

---

## 9. Code Quality Rules (Quick Reference)

| Rule | Detail |
|------|--------|
| `any` type | Never — use `unknown`, generics, or proper types |
| Array key | Never use index — use stable unique IDs |
| Server state | TanStack Query only — never in Zustand or useState |
| Inline styles | Never — use Tailwind classes or CSS Modules |
| `console.log` | Remove before committing |
| useEffect deps | Must be exhaustive — use ESLint `react-hooks` rule |
| Missing states | Always handle loading, error, and empty |
| Tests | Always in the same response as the component |
