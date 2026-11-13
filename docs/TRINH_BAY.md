# Dàn bài trình bày và kịch bản demo (khoảng 10–12 phút)

## Slide 1 — Tiêu đề
Tìm hiểu kiểm thử cho ứng dụng Python: unittest, pytest, mock, Selenium.

## Slide 2 — Vì sao phải kiểm thử?
- Phát hiện lỗi sớm, rẻ hơn sửa lỗi sau khi triển khai.
- Cho phép sửa code mà không sợ hỏng chỗ khác (regression).
- Test là tài liệu mô tả hành vi.

## Slide 3 — Kim tự tháp kiểm thử
Nhiều unit test (nhanh, rẻ) → ít integration test → rất ít E2E (chậm, dễ hỏng).

## Slide 4 — unittest
Class `TestCase`, `setUp/tearDown`, `assertEqual`, `assertRaises`, `subTest`.
→ **Demo bước 1.**

## Slide 5 — pytest
Hàm + `assert`, `parametrize`, `pytest.raises`, `approx`, `skip/xfail`. So sánh với unittest.
→ **Demo bước 2.**

## Slide 6 — Fixture
Chuẩn bị/dọn dẹp bằng `yield`, `conftest.py`, mỗi test nhận dữ liệu mới.
→ **Demo bước 3.**

## Slide 7 — Mock
Vì sao: tránh mạng, thanh toán, email thật. `patch`, `MagicMock`, `side_effect`, `assert_called_*`.
Hai cách: patch và dependency injection. `pytest-mock` (`mocker`, `spy`).
→ **Demo bước 4 và 5.**

## Slide 8 — tmp_path và monkeypatch
Test ghi file/biến môi trường mà không đụng dữ liệu thật.
→ **Demo bước 6.**

## Slide 9 — Selenium
WebDriver, định vị phần tử, headless, `WebDriverWait`.
→ **Demo bước 7** (mở `web/todo.html`, thêm/xoá việc, báo lỗi khi để trống).

## Slide 10 — Độ phủ (coverage)
`pytest --cov`: 100% nhưng không có nghĩa là không còn lỗi.
→ **Demo bước 8.**

## Slide 11 — Kết luận và hướng phát triển
pytest làm chính, mock để cô lập, Selenium cho luồng quan trọng; CI, hypothesis, mutation testing.

---

## Kịch bản demo

Chuẩn bị trước: `pip install -r requirements.txt`, đóng cửa sổ thừa, mở sẵn terminal tại thư mục dự án.

```bash
python run_demo.py --pause
```

Mỗi lần nhấn Enter chạy một bước tương ứng slide. Gợi ý lời thoại và điểm cần nhấn:

1. **unittest**: chỉ ra `skipped` và `expected failure` ở cuối kết quả.
2. **pytest parametrize**: "một hàm nhưng ra nhiều test"; nhìn tên test có tham số trong `-v`.
3. **Fixture**: mở `tests/conftest.py`, giải thích fixture `account` tạo mới cho mỗi test.
4. **Mock weather**: mở `weather.py`, nhấn mạnh test **không gọi mạng thật** (tắt wifi vẫn chạy).
5. **Mock order**: mở `order_service.py`, chỉ test `payment_failed` kiểm tra không gửi email, không trừ kho.
6. **tmp_path**: sau test, không có thư mục `data/` trong dự án.
7. **Selenium**: nếu muốn xem trình duyệt, xoá dòng `--headless=new` trong `tests/test_selenium_todo.py`.
8. **Coverage**: chỉ cột `Miss` bằng 0.

**Demo bắt lỗi (tuỳ chọn, rất thuyết phục):** sửa `if b == 0` thành `if b == 1` trong `calculator.py`,
chạy `python -m pytest -q` để thấy test đỏ, rồi hoàn tác bằng `git checkout src/myapp/calculator.py`.

## Câu hỏi thầy có thể hỏi
- *unittest khác pytest?* — xem bảng so sánh trong báo cáo.
- *Khi nào dùng mock?* — khi phụ thuộc chậm, không ổn định, có tác dụng phụ hoặc khó tạo tình huống lỗi.
- *Vì sao patch `myapp.weather.urllib...` chứ không patch ở nơi định nghĩa?* — patch ở nơi đối tượng được tra cứu khi chạy.
- *Coverage 100% có an toàn?* — không, vì có thể thiếu assert hoặc thiếu trường hợp biên.
