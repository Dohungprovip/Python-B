from unittest.mock import Mock, call

import pytest

from myapp import weather
from myapp.order_service import OrderService, OutOfStockError


@pytest.fixture
def deps():
    inventory = Mock()
    inventory.has_stock.return_value = True
    gateway = Mock()
    gateway.charge.return_value = True
    email = Mock()
    return inventory, gateway, email


def test_checkout_success(deps):
    inventory, gateway, email = deps
    service = OrderService(inventory, gateway, email)

    assert service.checkout({"A": 2, "B": 1}, 500, "an@example.com") == "PAID"

    gateway.charge.assert_called_once_with(500)
    assert inventory.reduce.call_args_list == [call("A", 2), call("B", 1)]
    email.send.assert_called_once()
    assert email.send.call_args.args[0] == "an@example.com"


def test_checkout_payment_failed(deps):
    inventory, gateway, email = deps
    gateway.charge.return_value = False
    service = OrderService(inventory, gateway, email)

    assert service.checkout({"A": 1}, 100, "x@y.z") == "FAILED"

    inventory.reduce.assert_not_called()
    email.send.assert_not_called()


def test_checkout_out_of_stock(deps):
    inventory, gateway, email = deps
    inventory.has_stock.return_value = False
    service = OrderService(inventory, gateway, email)

    with pytest.raises(OutOfStockError, match="A"):
        service.checkout({"A": 1}, 100, "x@y.z")
    gateway.charge.assert_not_called()


def test_describe_weather_with_mocker(mocker):
    mocker.patch("myapp.weather.fetch_weather", return_value={"temp": 32})
    assert weather.describe_weather("Saigon") == "Nóng"


def test_spy_with_mocker(mocker):
    from myapp import calculator

    spy = mocker.spy(calculator, "add")
    assert calculator.add(2, 2) == 4
    spy.assert_called_once_with(2, 2)
