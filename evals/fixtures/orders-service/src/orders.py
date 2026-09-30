"""Order checkout for the orders-service example."""
from dataclasses import dataclass, field


class PaymentGateway:
    """Records every charge it is asked to make."""

    def __init__(self) -> None:
        self.charges: list[tuple[str, int]] = []

    def charge(self, customer_id: str, amount_cents: int) -> str:
        self.charges.append((customer_id, amount_cents))
        return f"ch_{len(self.charges)}"


@dataclass
class OrderService:
    gateway: PaymentGateway
    orders: dict[str, str] = field(default_factory=dict)

    def submit(self, order_id: str, customer_id: str, amount_cents: int) -> str:
        """Charge the customer and record the order."""
        charge_id = self.gateway.charge(customer_id, amount_cents)
        self.orders[order_id] = charge_id
        return charge_id
