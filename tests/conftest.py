import pytest

from myapp.bank import BankAccount
from myapp.todo_storage import TodoList


@pytest.fixture
def account():
    return BankAccount("An", balance=100)


@pytest.fixture
def todo():
    return TodoList()
