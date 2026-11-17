# Python-B: Kiểm thử cho ứng dụng Python

Bài tập môn Python, phần B (đề tài tìm hiểu). Repo này thử các công cụ kiểm thử phổ biến của Python
trên một ứng dụng nhỏ: unittest, pytest, mock và Selenium.

Tác giả: Dohungprovip

## Thư mục

- `src/myapp/`: các module cần kiểm thử
- `tests/`: các file test
- `web/todo.html`: trang web dùng cho test Selenium
- `run_demo.py`: chạy lần lượt từng nhóm test để demo
- `docs/`: báo cáo, dàn bài thuyết trình, ghi chú đọc code

## Mỗi file test dùng công cụ gì

| File test | Module được test | Nội dung |
|---|---|---|
| `test_unittest_calculator.py` | `calculator.py` | unittest: `TestCase`, `setUp`, `subTest`, `assertRaises` |
| `test_pytest_calculator.py` | `calculator.py` | pytest: `parametrize`, `raises`, `approx`, `skipif`, `xfail` |
| `test_bank_fixtures.py` | `bank.py` | fixture và `conftest.py` |
| `test_unittest_mock_weather.py` | `weather.py` | `unittest.mock.patch`, `MagicMock`, `side_effect` |
| `test_pytest_mock_order.py` | `order_service.py` | `Mock` truyền vào constructor, pytest-mock |
| `test_todo_storage.py` | `todo_storage.py` | `tmp_path`, `monkeypatch` |
| `test_selenium_todo.py` | `web/todo.html` | Selenium với Chrome hoặc Edge chế độ headless |

## Cài đặt

Cần Python 3.9 trở lên. Test Selenium cần Chrome hoặc Edge, nếu máy không có thì các test đó tự bỏ qua.

```bash
pip install -r requirements.txt
```

## Chạy test

```bash
python -m pytest
```

Kèm độ phủ:

```bash
python -m pytest --cov=myapp --cov-report=term-missing
```

Chỉ chạy hoặc bỏ qua Selenium:

```bash
python -m pytest -m selenium
python -m pytest -m "not selenium"
```

Chạy một test theo tên:

```bash
python -m pytest -k checkout -v
```

Demo từng bước, nhấn Enter để sang bước kế:

```bash
python run_demo.py --pause
```

## Kết quả

```
59 passed, 1 skipped, 2 xfailed
coverage: 100%
```

Một test bị skip và hai test xfail được để lại có chủ ý để minh hoạ `skip` và `xfail`.

## Kiểm thử dự án tu tiên

Xem [tutien/README.md](tutien/README.md) và [báo cáo 20 trang](docs/Bao_cao_Kiem_thu_Tu_Tien.docx).

## Tài liệu

- [Báo cáo ngắn](docs/BAO_CAO.md)
- [Dàn bài thuyết trình và kịch bản demo](docs/TRINH_BAY.md)
- [Ghi chú đọc source code](docs/PHAN_TICH_SOURCE_CODE.md)
