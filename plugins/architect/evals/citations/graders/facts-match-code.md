---
type: llm
focus: { source: file, path: docs/analysis/PROJ-1-technical-analysis.md }
---

This is src/orders.py in the project Claude analysed, with line numbers:

 1: """Order checkout for the orders-service example."""
 2: from dataclasses import dataclass, field
 3:
 4:
 5: class PaymentGateway:
 6:     """Records every charge it is asked to make."""
 7:
 8:     def __init__(self) -> None:
 9:         self.charges: list[tuple[str, int]] = []
10:
11:     def charge(self, customer_id: str, amount_cents: int) -> str:
12:         self.charges.append((customer_id, amount_cents))
13:         return f"ch_{len(self.charges)}"
14:
15:
16: @dataclass
17: class OrderService:
18:     gateway: PaymentGateway
19:     orders: dict[str, str] = field(default_factory=dict)
20:
21:     def submit(self, order_id: str, customer_id: str, amount_cents: int) -> str:
22:         """Charge the customer and record the order."""
23:         charge_id = self.gateway.charge(customer_id, amount_cents)
24:         self.orders[order_id] = charge_id
25:         return charge_id

PASS if every statement labelled FACT in the analysis that cites src/orders.py cites a line (or range) whose code, shown above, supports the statement, and no FACT cites a file or line that does not exist.
FAIL if any FACT cites src/orders.py at a line that does not support it, or cites a file or line that is not in the project. Ignore statements not labelled FACT.
