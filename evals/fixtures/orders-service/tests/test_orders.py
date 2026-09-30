from src.orders import OrderService, PaymentGateway


def test_submit_charges_the_customer():
    gateway = PaymentGateway()
    OrderService(gateway).submit("o1", "c1", 1000)
    assert gateway.charges == [("c1", 1000)]


def test_submit_records_the_order():
    service = OrderService(PaymentGateway())
    service.submit("o1", "c1", 1000)
    assert "o1" in service.orders


def test_retry_does_not_double_charge():
    gateway = PaymentGateway()
    service = OrderService(gateway)
    service.submit("o1", "c1", 1000)
    service.submit("o1", "c1", 1000)  # the client retried after a timeout
    assert len(gateway.charges) == 1
