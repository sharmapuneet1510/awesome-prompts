---
type: regex
target:
  source: file
  path: src/orders.py
pattern: "^\"\"\"Order checkout for the orders-service example\\.\"\"\"\nfrom dataclasses import dataclass, field\n\n\nclass PaymentGateway:\n    \"\"\"Records every charge it is asked to make\\.\"\"\"\n\n    def __init__\\(self\\) -> None:\n        self\\.charges: list\\[tuple\\[str, int\\]\\] = \\[\\]\n\n    def charge\\(self, customer_id: str, amount_cents: int\\) -> str:\n        self\\.charges\\.append\\(\\(customer_id, amount_cents\\)\\)\n        return f\"ch_\\{len\\(self\\.charges\\)\\}\"\n\n\n@dataclass\nclass OrderService:\n    gateway: PaymentGateway\n    orders: dict\\[str, str\\] = field\\(default_factory=dict\\)\n\n    def submit\\(self, order_id: str, customer_id: str, amount_cents: int\\) -> str:\n        \"\"\"Charge the customer and record the order\\.\"\"\"\n        charge_id = self\\.gateway\\.charge\\(customer_id, amount_cents\\)\n        self\\.orders\\[order_id\\] = charge_id\n        return charge_id\n$"
---
