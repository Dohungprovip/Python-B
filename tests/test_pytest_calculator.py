import pytest

from myapp.calculator import add, divide, factorial, is_prime


def test_add_simple():
    assert add(2, 3) == 5


@pytest.mark.parametrize(
    "a, b, expected",
    [(1, 1, 2), (0, 0, 0), (-1, 1, 0), (10, -4, 6)],
)
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected


@pytest.mark.parametrize("n", [2, 3, 5, 7, 11, 97])
def test_is_prime_true(n):
    assert is_prime(n)


@pytest.mark.parametrize("n", [-5, 0, 1, 4, 9, 100])
def test_is_prime_false(n):
    assert not is_prime(n)


def test_is_prime_wrong_type():
    with pytest.raises(TypeError):
        is_prime("7")


def test_divide_by_zero_message():
    with pytest.raises(ZeroDivisionError, match="chia cho 0"):
        divide(5, 0)


def test_divide_float_approx():
    assert divide(1, 3) == pytest.approx(0.3333, rel=1e-3)


@pytest.mark.parametrize(
    "n, expected", [(0, 1), (1, 1), (5, 120), (10, 3628800)]
)
def test_factorial(n, expected):
    assert factorial(n) == expected


@pytest.mark.parametrize("bad, exc", [(-1, ValueError), (1.5, TypeError), (True, TypeError)])
def test_factorial_invalid(bad, exc):
    with pytest.raises(exc):
        factorial(bad)


@pytest.mark.skipif(not hasattr(pytest, "approx"), reason="ví dụ skipif")
def test_skipif_example():
    assert True


@pytest.mark.xfail(reason="Ví dụ test dự kiến thất bại", strict=True)
def test_xfail_example():
    assert add(1, 1) == 3
