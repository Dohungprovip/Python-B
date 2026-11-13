class InsufficientFundsError(Exception):
    pass


class BankAccount:
    def __init__(self, owner, balance=0):
        if balance < 0:
            raise ValueError("Số dư ban đầu không được âm")
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Số tiền gửi phải > 0")
        self.balance += amount
        self.history.append(("deposit", amount))
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Số tiền rút phải > 0")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Số dư {self.balance} không đủ để rút {amount}"
            )
        self.balance -= amount
        self.history.append(("withdraw", amount))
        return self.balance
