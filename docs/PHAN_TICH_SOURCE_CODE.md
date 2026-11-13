# Phân tích mã nguồn (tài liệu đọc để báo cáo thầy)

Tài liệu giải thích từng file: **nó làm gì, vì sao viết như vậy, và các câu thầy có thể hỏi**.
Đọc theo thứ tự: cấu trúc → ứng dụng (`src`) → test (`tests`) → Selenium.

## 1. Cấu trúc và cách pytest tìm thấy code

```
src/myapp/   code cần test (6 module)
tests/       code test, tên file bắt đầu bằng test_
web/         trang HTML cho Selenium
pytest.ini   cấu hình pytest
```

`pytest.ini`:
- `pythonpath = src` → thêm `src` vào `sys.path` nên test viết `from myapp.bank import ...` mà không cần cài package.
- `testpaths = tests` → chỉ tìm test trong thư mục `tests`.
- `markers = selenium` → đăng ký marker tự đặt để chạy/loại riêng bằng `-m selenium` / `-m "not selenium"`.
- `addopts = -ra` → in tóm tắt lý do của test skip/xfail ở cuối.

Quy ước tìm test của pytest: file `test_*.py`, hàm `test_*`, lớp `Test*`; lớp con của `unittest.TestCase` cũng được chạy.

## 2. Ứng dụng mẫu (`src/myapp`)

| File | Ý tưởng chính | Vì sao chọn để minh hoạ |
|---|---|---|
| `calculator.py` | Hàm thuần: nhận vào → trả ra | Dễ test nhất; có nhánh lỗi (`ZeroDivisionError`, `ValueError`, `TypeError`) |
| `bank.py` | Lớp có trạng thái (`balance`, `history`) + exception tự định nghĩa | Cần fixture để mỗi test có đối tượng mới |
| `weather.py` | Gọi `urllib.request.urlopen` (mạng) | Phải mock để khỏi gọi mạng thật |
| `order_service.py` | Nhận `inventory`, `payment_gateway`, `email_sender` qua constructor | Dependency injection → dễ thay bằng Mock |
| `todo_storage.py` | Đọc/ghi file JSON, thư mục lấy từ biến môi trường | Dùng `tmp_path` và `monkeypatch` |

Chi tiết đáng chú ý:
- `is_prime`/`factorial` loại `bool` bằng `isinstance(n, bool)` vì trong Python `True` là `int` (`True == 1`).
- `BankAccount.withdraw` kiểm tra số tiền hợp lệ **trước**, rồi mới kiểm tra đủ số dư; nếu lỗi thì số dư không đổi (test có kiểm tra).
- `OrderService.checkout` có thứ tự cố ý: kiểm tra kho → thanh toán → trừ kho → gửi email.
  Thanh toán thất bại thì không trừ kho, không gửi email; test `payment_failed` chứng minh điều đó.
- `todo_storage.get_data_dir()` đọc `os.environ` **mỗi lần gọi** (không đọc một lần ở đầu file) nên `monkeypatch.setenv` có tác dụng.

## 3. Các file test

### 3.1 `test_unittest_calculator.py` — unittest
- Lớp `TestCalculator(unittest.TestCase)`; mỗi method `test_*` là một test.
- `setUp` chạy trước mỗi test, `tearDown` chạy sau mỗi test.
- `assertEqual`, `assertAlmostEqual` (so sánh số thực: 0.1+0.2 ≠ 0.3 chính xác), `assertTrue/False`, `assertIn`.
- `assertRaises` dùng 2 kiểu: context manager (`with`) để kiểm tra cả nội dung lỗi, và dạng gọi hàm `assertRaises(ValueError, factorial, -1)`.
- `subTest`: vòng lặp mà một giá trị lỗi không làm dừng cả test, báo cáo riêng từng giá trị.
- `@unittest.skip` bỏ qua test; `@unittest.expectedFailure` đánh dấu test dự kiến sai (kết quả `x`).
- `if __name__ == "__main__": unittest.main()` để chạy trực tiếp file.

### 3.2 `test_pytest_calculator.py` — pytest
- Không cần class, chỉ `assert`; khi sai pytest in giá trị hai vế (assertion rewriting).
- `@pytest.mark.parametrize("a, b, expected", [...])`: 1 hàm → nhiều test, mỗi bộ có tên riêng `test_add_parametrized[1-1-2]`.
- `pytest.raises(Exc, match="regex")`: kiểm tra có ném lỗi và thông báo khớp mẫu.
- `pytest.approx`: so sánh số thực có sai số.
- `skipif` (bỏ qua theo điều kiện) và `xfail(strict=True)` (dự kiến sai; nếu bất ngờ **đúng** thì báo lỗi).

### 3.3 `conftest.py` và `test_bank_fixtures.py` — fixture
- `conftest.py`: pytest tự nạp; fixture đặt ở đây dùng được ở mọi file test mà không cần import.
- Fixture mặc định `scope="function"`: tạo mới cho **từng test** → test độc lập (không phụ thuộc thứ tự chạy).
- `test_fixture_is_fresh_each_test` chứng minh điều đó.
- `account_with_history`: fixture dùng fixture khác, có `yield` — trước `yield` là setup, sau `yield` là teardown.
- Test nhận fixture bằng cách **đặt tên tham số trùng tên fixture**.

### 3.4 `test_unittest_mock_weather.py` — unittest.mock + patch
- `fake_response`: tạo `MagicMock` giả `urlopen()`. Dùng `MagicMock` (không phải `Mock`) vì hỗ trợ magic method `__enter__` cho câu lệnh `with`.
- `@patch("myapp.weather.urllib.request.urlopen")`: thay thế trong lúc chạy test, hoàn tác khi kết thúc. Tham số `mock_urlopen` được truyền vào test.
- **Nguyên tắc patch**: patch ở nơi đối tượng được *tra cứu khi chạy*, không phải nơi định nghĩa.
- `side_effect=[a, b, c]`: mỗi lần gọi trả giá trị kế tiếp. `side_effect=TimeoutError`: gọi sẽ ném lỗi — cách mô phỏng sự cố mạng mà không cần mạng hỏng thật.
- `assert_called_once()`, `call_args`, `call_count` kiểm tra **cách** hàm bị gọi.

### 3.5 `test_pytest_mock_order.py` — Mock + pytest-mock
- Fixture `deps` tạo 3 `Mock` (kho, cổng thanh toán, email); `return_value` định sẵn kết quả.
- `assert_called_once_with(500)`, `assert_not_called()`, `call_args_list == [call(...), ...]` kiểm tra tương tác giữa các đối tượng (**behavior verification**) thay vì chỉ kiểm tra giá trị trả về.
- Không cần `patch` vì `OrderService` nhận phụ thuộc qua constructor.
- `mocker` (pytest-mock): `mocker.patch(...)` tự hoàn tác sau test, gọn hơn `@patch`; `mocker.spy` chạy hàm thật nhưng ghi lại lời gọi.

### 3.6 `test_todo_storage.py` — tmp_path và monkeypatch
- `tmp_path`: thư mục tạm riêng cho mỗi test, pytest tự dọn.
- `monkeypatch.setenv/delenv`: đặt/xoá biến môi trường chỉ trong test, tự khôi phục.
- Test vòng lặp lưu rồi nạp lại (round-trip) và test file chưa tồn tại → danh sách rỗng.
- Kết quả: test không tạo file rác trong thư mục dự án.

### 3.7 `test_selenium_todo.py` — Selenium
Luồng: `browser` (module scope: mở 1 trình duyệt cho cả file, `driver.quit()` sau khi xong) → `page` (mỗi test nạp lại trang để trạng thái sạch) → các test.
- `pytest.importorskip("selenium")`: không có thư viện thì bỏ qua cả file.
- `_make_driver`: thử Chrome rồi Edge, bật `--headless=new`; không được thì `pytest.skip` thay vì làm hỏng bộ test.
- Selenium Manager tự tải driver phù hợp phiên bản trình duyệt (lần đầu cần internet).
- Mở trang bằng `file://` (`Path.as_uri()`) nên không cần chạy web server.
- Định vị phần tử: `By.ID`, `By.CSS_SELECTOR`, `By.TAG_NAME`; thao tác: `send_keys`, `click`, đọc `.text`, `get_attribute("value")`.
- `WebDriverWait(...).until(EC.text_to_be_present_in_element(...))`: **explicit wait**, chờ có điều kiện thay vì `time.sleep` cố định.
- `pytestmark = pytest.mark.selenium`: gắn marker cho cả file.
- Lưu ý: `li.text` gồm cả chữ "Xoá" của nút bên trong nên test dùng `in` thay vì `==`.

### 3.8 `web/todo.html`
Trang đơn giản với `input#task`, `button#add`, `ul#list`, `span#count`, `p#error`; JavaScript thêm mục, báo lỗi khi rỗng, xoá mục và cập nhật bộ đếm. Các `id` ổn định là thứ giúp test dễ định vị.

## 4. Đọc kết quả chạy

```
59 passed, 1 skipped, 2 xfailed
```
- `.` passed — `s` skipped — `x` xfailed (sai như dự kiến) — `F` failed.
- 1 skipped (unittest.skip) và 2 xfailed là **ví dụ cố ý**.
- Cột `Miss` của coverage = 0 → mọi câu lệnh trong `src/myapp` đã được chạy qua ít nhất một lần.

## 5. Điểm mạnh và hạn chế của bài

- Mạnh: đủ 4 công cụ, mỗi công cụ có ví dụ riêng; test độc lập, không gọi mạng/dịch vụ thật (trừ trình duyệt cục bộ); có kịch bản demo.
- Hạn chế: ứng dụng mẫu nhỏ; Selenium chạy trên trang cục bộ chứ không phải website thật; chưa có CI.

## 6. Bảng hỏi nhanh – đáp nhanh

| Câu hỏi | Trả lời ngắn |
|---|---|
| Mock khác Stub/Spy? | Mock: đối tượng giả có kiểm tra cách gọi; stub chỉ trả dữ liệu cố định; spy gọi hàm thật và ghi lại |
| `Mock` khác `MagicMock`? | `MagicMock` có sẵn magic method (`__enter__`, `__len__`...) |
| Vì sao fixture tốt hơn `setUp`? | Khai báo theo tên, tái sử dụng, nhiều scope, kết hợp fixture |
| Test độc lập nghĩa là gì? | Chạy theo thứ tự nào, hay chạy riêng lẻ, kết quả vẫn như nhau |
| Selenium đợi phần tử bằng cách nào? | Explicit wait (`WebDriverWait`) tốt hơn `sleep` |
| Làm sao chạy riêng một test? | `pytest tests/test_bank_fixtures.py::test_deposit` hoặc `-k deposit` |
