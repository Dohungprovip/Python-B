import pytest

from myapp.bank import BankAccount, InsufficientFundsError


def test_deposit(account):
    assert account.deposit(50) == 150
    assert account.history == [("deposit", 50)]


def test_withdraw(account):
    account.withdraw(30)
    assert account.balance == 70


def test_fixture_is_fresh_each_test(account):
    assert account.balance == 100


def test_withdraw_too_much(account):
    with pytest.raises(InsufficientFundsError, match="không đủ"):
        account.withdraw(1000)
    assert account.balance == 100


@pytest.mark.parametrize("amount", [0, -10])
def test_invalid_amount(account, amount):
    with pytest.raises(ValueError):
        account.deposit(amount)
    with pytest.raises(ValueError):
        account.withdraw(amount)


def test_negative_initial_balance():
    with pytest.raises(ValueError):
        BankAccount("Bình", balance=-1)


@pytest.fixture
def account_with_history(account):
    account.deposit(20)
    account.withdraw(10)
    yield account
    account.history.clear()


def test_history(account_with_history):
    assert account_with_history.history == [("deposit", 20), ("withdraw", 10)]
    assert account_with_history.balance == 110
