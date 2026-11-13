def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Không thể chia cho 0")
    return a / b


def is_prime(n):
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n phải là số nguyên")
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def factorial(n):
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("n phải là số nguyên")
    if n < 0:
        raise ValueError("n phải >= 0")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
