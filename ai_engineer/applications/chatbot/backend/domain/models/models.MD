# Domain Models

## Định nghĩa

Thư mục này chứa các **data class** (`@dataclass`) định nghĩa các thực thể nghiệp vụ cốt lõi của hệ thống chatbot. Mỗi model đại diện cho một đối tượng dữ liệu trong thế giới thực với các trường dữ liệu (attributes) và kiểu dữ liệu rõ ràng.

**Các model hiện có:**
- `Conversation`: Lưu thông tin một cuộc trò chuyện (conversation)
- `Message`: Lưu thông tin một tin nhắn (của user hoặc AI)
- `LLMResponse`: Lưu kết quả phản hồi từ LLM (kèm attachments nếu có)
- Mỗi model đi kèm các Enum trạng thái (`PENDING`, `COMPLETED`, `FAILED`)

## Dùng vào mục đích gì

1. **Tách biệt business logic khỏi infrastructure**: Models là lớp trung gian "thuần túy" (plain Python dataclass), không phụ thuộc vào database hay framework nào.
2. **Chuyển đổi dữ liệu giữa các lớp**: Dùng làm "ngôn ngữ chung" để truyền dữ liệu giữa các lớp:
   - Database ORM → Domain Model → API Response
   - API Request → Domain Model → Database ORM
3. **Ràng buộc kiểu dữ liệu (type safety)**: Đảm bảo các trường bắt buộc, kiểu dữ liệu đúng (UUID, int, str, date) xuyên suốt luồng xử lý.

## Dùng ở đâu

1. **Lớp Repository** (`repositories/`): Đọc dữ liệu từ database → chuyển ORM object sang Domain Model, hoặc nhận Domain Model → chuyển sang ORM để lưu DB (qua các hàm `_to_orm()` / `_to_domain()`).
2. **Lớp Service** (`service/`): Nhận Domain Model từ Repository, xử lý logic nghiệp vụ, trả về Domain Model.
3. **Lớp API** (`backend/routes/`): Nhận Domain Model từ Service, map sang Pydantic schema để trả response cho client.
