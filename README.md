# Permission Tool

Một công cụ nhỏ bằng Python để chọn `file` hoặc `thư mục/ổ đĩa` và thiết lập quyền truy cập cùng owner/group.

## Cách dùng

1. Kích hoạt môi trường ảo nếu có:
   ```bash
   source venv/bin/activate
   ```
2. Chạy ứng dụng:
   ```bash
   python3 permission_tool.py
   ```
3. Chọn kiểu target:
   - `File` để chọn một file
   - `Thư mục/ổ đĩa` để chọn một thư mục hoặc mount point
4. Nhập `User owner` và `Group` nếu muốn đổi chủ sở hữu trên Linux.
5. Chọn quyền đọc/ghi/thực thi cho owner, group và others trên Linux.
6. Nhấn `Áp dụng quyền`.

## Tab Windows

- Tab `Quyền Windows` sẽ mặc định đặt `Everyone` full control và xóa ACL khác khi chạy trên Windows.
- Tab `Đổi tên không dấu` cho phép chọn file hoặc thư mục và chuyển tên sang dạng không dấu, sau đó đổi tên trực tiếp.
- Nếu chọn thư mục, có thể bật tùy chọn đổi tên đệ quy để đổi tên tất cả thư mục con và file nằm trong.

## Lưu ý

- Để đổi owner/group cần quyền `root` hoặc chạy bằng `sudo`.
- Trên Linux, ổ đĩa cũng được xử lý như thư mục mount point.
