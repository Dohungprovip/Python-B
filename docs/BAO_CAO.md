# Báo cáo ngắn: Kiểm thử cho ứng dụng Python

**Tác giả:** Dohungprovip

## 1. Giới thiệu

Kiểm thử phần mềm giúp phát hiện lỗi sớm, cho phép sửa/refactor code mà vẫn yên tâm
(regression), và là tài liệu sống mô tả hành vi mong muốn của chương trình. Đề tài tìm hiểu
bốn công cụ phổ biến trong hệ sinh thái Python và áp dụng vào một ứng dụng mẫu.

## 2. Các loại kiểm thử

| Mức | Mục tiêu | Công cụ trong đề tài |
|---|---|---|
| Unit test | Kiểm tra một hàm/lớp riêng lẻ | unittest, pytest |
| Integration test | Kiểm tra nhiều thành phần phối hợp | pytest + mock (OrderService) |
| End-to-end (E2E) | Kiểm tra như người dùng thật qua giao diện | Selenium |

## 3. Các công cụ

### 3.1 unittest
- Có sẵn trong thư viện chuẩn, theo phong cách xUnit: test là method của lớp kế thừa `TestCase`.
- Có `setUp/tearDown`, `assertEqual`, `assertRaises`, `subTest`, `skip`, `expectedFailure`.
- Ưu: không cần cài đặt. Nhược: dài dòng, nhiều hàm `assertXxx` phải nhớ.

### 3.2 pytest
- Test là hàm thường, dùng `assert` thuần; khi sai pytest tự giải thích giá trị hai vế.
- Điểm mạnh: **parametrize** (một test nhiều bộ dữ liệu), **fixture** (chuẩn bị/dọn dẹp, tái sử dụng,
  chia sẻ qua `conftest.py`), **marker** (`skip`, `skipif`, `xfail`, tự đặt như `selenium`),
  chạy được cả test viết bằng unittest, hệ plugin lớn (pytest-cov, pytest-mock...).
- Fixture có sẵn hữu ích: `tmp_path` (thư mục tạm), `monkeypatch` (sửa biến môi trường/thuộc tính tạm thời).

### 3.3 Mock
- Mục đích: **cô lập** đơn vị cần test khỏi phụ thuộc chậm/không ổn định/có tác dụng phụ
  (mạng, thanh toán, gửi email, CSDL).
- `unittest.mock`: `Mock`, `MagicMock`, `patch`, `return_value`, `side_effect`, và các kiểm tra
  `assert_called_once_with`, `assert_not_called`, `call_args_list`.
- `pytest-mock`: fixture `mocker` bọc `patch`, tự hoàn tác sau test; có `mocker.spy`.
- Hai cách dùng trong đề tài: (a) **patch** nơi hàm được dùng (`myapp.weather.urllib.request.urlopen`);
  (b) **dependency injection** — truyền đối tượng giả vào constructor (`OrderService`), cách này sạch hơn.
- Lưu ý: chỉ mock thứ bên ngoài; mock quá nhiều làm test gắn chặt vào cài đặt.

### 3.4 Selenium
- Điều khiển trình duyệt thật (Chrome/Edge) qua WebDriver: tìm phần tử (`By.ID`, `By.CSS_SELECTOR`),
  nhập liệu, bấm nút, kiểm tra nội dung, dùng `WebDriverWait` để chờ.
- Dùng chế độ headless để chạy không cần mở cửa sổ (phù hợp CI). Selenium Manager (từ 4.6) tự tải driver.
- Test E2E chậm và dễ hỏng hơn unit test nên chỉ dùng cho luồng quan trọng ("kim tự tháp kiểm thử").

## 4. So sánh nhanh

| Tiêu chí | unittest | pytest |
|---|---|---|
| Cài đặt | Có sẵn | `pip install pytest` |
| Cú pháp | Class + `self.assertXxx` | Hàm + `assert` |
| Dữ liệu nhiều bộ | `subTest` | `@pytest.mark.parametrize` |
| Chuẩn bị dữ liệu | `setUp/tearDown` | fixture linh hoạt, tái sử dụng |
| Plugin | Ít | Rất nhiều |

## 5. Kết quả thực nghiệm

- Ứng dụng mẫu 6 module (107 câu lệnh), 62 test: **59 passed, 1 skipped, 2 xfailed**, 0 failed.
- Độ phủ (pytest-cov) đạt **100%**. Thời gian chạy khoảng 6 giây (phần lớn là khởi động trình duyệt Selenium).
- Kết quả chạy trên Windows 11, Python 3.12, pytest 9.2, selenium 4.52, Chrome headless.

## 6. Kết luận

- Dùng **pytest** làm công cụ chính nhờ cú pháp ngắn gọn, fixture và parametrize; vẫn hiểu **unittest** vì
  là chuẩn thư viện và nhiều dự án cũ dùng.
- Dùng **mock** để test đơn vị mà không gọi dịch vụ thật; ưu tiên dependency injection.
- Dùng **Selenium** cho vài luồng giao diện then chốt, phần còn lại viết unit test.
- Độ phủ 100% không đảm bảo hết lỗi; chất lượng assert quan trọng hơn con số.

## 7. Hướng phát triển

Tích hợp CI (GitHub Actions) chạy pytest tự động; thử `hypothesis` (property-based testing);
`pytest-xdist` chạy song song; mutation testing (`mutmut`) để đánh giá chất lượng test.
