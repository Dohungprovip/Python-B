import unittest

from myapp.calculator import add, divide, factorial, is_prime


class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.cases_prime = [2, 3, 5, 97]

    def tearDown(self):
        pass

    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertAlmostEqual(add(0.1, 0.2), 0.3)

    def test_divide(self):
        self.assertEqual(divide(10, 4), 2.5)

    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError) as ctx:
            divide(1, 0)
        self.assertIn("chia cho 0", str(ctx.exception))

    def test_is_prime(self):
        for n in self.cases_prime:
            with self.subTest(n=n):
                self.assertTrue(is_prime(n))
        self.assertFalse(is_prime(1))
        self.assertFalse(is_prime(-7))

    def test_factorial(self):
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(5), 120)

    def test_factorial_invalid(self):
        self.assertRaises(ValueError, factorial, -1)
        self.assertRaises(TypeError, factorial, 2.5)

    @unittest.skip("Ví dụ cách bỏ qua một test")
    def test_skipped(self):
        self.fail("không bao giờ chạy")

    @unittest.expectedFailure
    def test_expected_failure(self):
        self.assertEqual(add(1, 1), 3)


if __name__ == "__main__":
    unittest.main()
