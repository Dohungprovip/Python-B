# Kiểm thử dự án Trường Sinh Quyết (tu tiên)

Bộ kiểm thử áp dụng unittest, pytest, mock và Selenium lên dự án thật "Trường Sinh Quyết", dùng dữ liệu thật trong `tsq_data`.
Báo cáo đầy đủ: [../docs/Bao_cao_Kiem_thu_Tu_Tien.docx](../docs/Bao_cao_Kiem_thu_Tu_Tien.docx).

Kho này chỉ chứa mã kiểm thử và tài liệu. Mã nguồn game và dữ liệu người chơi **không** được đưa lên đây.

## Vị trí mã nguồn và dữ liệu

| Biến môi trường | Mặc định | Ý nghĩa |
|---|---|---|
| `TUTIEN_HOME` | `C:\Users\pc\Documents\My Web Sites\tt` | thư mục chứa `app.py` và `src/` của game |
| `TUTIEN_DATA` | `<TUTIEN_HOME>\..\tsq_data` | thư mục chứa `tutien.db` |

Test đọc dữ liệu bằng một bản sao chỉ đọc trong thư mục tạm; các test ghi (API, Selenium) dùng cơ sở dữ liệu tạm riêng.
Không test nào đọc ghi trực tiếp `tutien.db` thật.

## Cài đặt và chạy

```bash
pip install -r requirements.txt
```

```bash
python -m pytest
```

```bash
python -m pytest -m "not e2e"
python -m pytest -m data
python -m pytest -m unit
python -m pytest --cov=src --cov-report=term
```

Đổi vị trí game/dữ liệu (PowerShell):

```powershell
$env:TUTIEN_HOME = "D:\duong\dan\tt"
$env:TUTIEN_DATA = "D:\duong\dan\tsq_data"
python -m pytest
```

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `tests/unit` | hàm Thiên Phú, phản phệ thiên lôi, đường dẫn, sao lưu, mô tả kỹ năng, phiên đăng nhập, giới hạn tần suất, mock |
| `tests/data` | toàn vẹn tham chiếu, khoá duy nhất, cân bằng cảnh giới và cường hoá, bất biến dữ liệu người chơi |
| `tests/api` | đăng ký, đăng nhập, tạo nhân vật qua FastAPI TestClient |
| `tests/e2e` | giao diện đăng nhập bằng Selenium (Chrome headless) |
| `docs` | kết quả chạy đầy đủ, ảnh chụp màn hình |

## Kết quả

```
530 test: 528 passed, 2 xfailed
thời gian: ~90 giây (không gồm Selenium: ~22 giây)
```

Hai test xfail ghi nhận lỗi dữ liệu thật tìm được:

- `thanh_tri` id 40 và 41 trỏ tới bản đồ 138 và 147 không có trong `ban_do`.
- 11/15 tên cảnh giới trong `thien_kiep_cau_hinh` không khớp `cultivation_realm`.

Các test xfail đặt `strict=True`: khi dữ liệu được sửa, bộ test sẽ báo để gỡ nhãn.
