import os
import subprocess
import sys

STEPS = [
    ("1. unittest (thư viện chuẩn)",
     [sys.executable, "-m", "unittest", "-v", "tests.test_unittest_calculator"]),
    ("2. pytest + parametrize + exception",
     [sys.executable, "-m", "pytest", "-v", "tests/test_pytest_calculator.py"]),
    ("3. pytest fixture",
     [sys.executable, "-m", "pytest", "-v", "tests/test_bank_fixtures.py"]),
    ("4. unittest.mock (patch API mạng)",
     [sys.executable, "-m", "pytest", "-v", "tests/test_unittest_mock_weather.py"]),
    ("5. Mock + pytest-mock (dependency injection)",
     [sys.executable, "-m", "pytest", "-v", "tests/test_pytest_mock_order.py"]),
    ("6. tmp_path + monkeypatch (file, biến môi trường)",
     [sys.executable, "-m", "pytest", "-v", "tests/test_todo_storage.py"]),
    ("7. Selenium (giao diện web, Chrome/Edge headless)",
     [sys.executable, "-m", "pytest", "-v", "-m", "selenium"]),
    ("8. Toàn bộ + độ phủ (coverage)",
     [sys.executable, "-m", "pytest", "--cov=myapp", "--cov-report=term-missing"]),
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pause = "--pause" in sys.argv
    failed = 0
    for title, cmd in STEPS:
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70, flush=True)
        env = dict(os.environ, PYTHONPATH="src", PYTHONIOENCODING="utf-8")
        failed += subprocess.call(cmd, env=env) != 0
        if pause:
            input("\n[Enter] để sang bước tiếp theo...")
    print(f"\nHoàn tất: {len(STEPS) - failed}/{len(STEPS)} bước thành công.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
