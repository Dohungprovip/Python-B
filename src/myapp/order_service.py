class OutOfStockError(Exception):
    pass


class OrderService:
    def __init__(self, inventory, payment_gateway, email_sender):
        self.inventory = inventory
        self.payment_gateway = payment_gateway
        self.email_sender = email_sender

    def checkout(self, items, amount, email):
        for sku, qty in items.items():
            if not self.inventory.has_stock(sku, qty):
                raise OutOfStockError(f"Hết hàng: {sku}")

        if not self.payment_gateway.charge(amount):
            return "FAILED"

        for sku, qty in items.items():
            self.inventory.reduce(sku, qty)
        self.email_sender.send(email, "Đặt hàng thành công", f"Đã thanh toán {amount}")
        return "PAID"
