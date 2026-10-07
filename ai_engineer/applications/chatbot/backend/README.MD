# Chatbot Backend - Tài liệu hoạt động

## Tổng quan

Backend chatbot được xây dựng trên **FastAPI**, áp dụng kiến trúc phân lớp rõ ràng:
- **API Layer**: `api.py` + `routes/` - Định nghĩa endpoints REST
- **Dependency Layer**: `dependencies.py` - Tiêm phụ thuộc (DI) cho services, repositories, LLM clients
- **Schema Layer**: `schemas/` - Định nghĩa cấu trúc request/response bằng Pydantic
- **Service Layer**: `ai_engineer/applications/chatbot/service/` - Logic nghiệp vụ
- **Repository Layer**: `ai_engineer/infrastructure/database/repositories/` - Truy cập DB (PostgreSQL)
- **Infrastructure**: Qdrant (vector DB), Gemini (LLM), MLflow (quản lý prompt + observability)

---

## Khởi động ứng dụng

File entry point: [api.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/api.py)

```
create_chatbot_api()
  ├─ setup_mlflow()           # Khởi tạo MLflow cho observability
  ├─ FastAPI(title="Chatbot API")
  └─ include_router(...) x 6  # Đăng ký 6 routers
```

Ứng dụng instance: `app = create_chatbot_api()`

Các biến môi trường bắt buộc:
| Biến | Mô tả |
|---|---|
| `LLM_CHAT_API_KEY_1` | API key cho Gemini |
| `LLM_CHAT_MODEL` | Tên model Gemini (vd: gemini-1.5-pro) |
| `QDRANT_URL` | URL Qdrant server (default: `http://localhost:6333`) |
| `RAG_COLLECTION_NAMES` | Danh sách Qdrant collections (default: `newspaper_embedded,stock_price_embedded`) |
| `SPARSE_MODEL_NAME` | Model BM25 (default: `Qdrant/bm25`) |
| `SPARSE_VECTOR_NAME` | Tên sparse vector field (default: `bm25_sparse`) |
| `DENSE_MODEL_NAME` | Model embedding (default: `gemini-embedding-2`) |
| `DENSE_VECTOR_NAME` | Tên dense vector field (default: `gemini_dense_vector`) |

---

## Dependency Injection Container

File: [dependencies.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/dependencies.py)

Nguyên tắc:
- Services cần DB session (AsyncSession): **Không cache** - mỗi request có 1 session riêng
- Services không trạng thái (LLMCaller, Qdrant): Dùng `@lru_cache` → singleton

### 1. Database Services (không cache)

| Factory | Trả về | Phụ thuộc |
|---|---|---|
| `get_conversation_service()` | `ConversationService` | `AsyncSession` → `PostgresConversationRepository` |
| `get_message_service()` | `MessageService` | `AsyncSession` → `PostgresMessageRepository` |
| `get_llm_response_service()` | `LLMResponseService` | `AsyncSession` → `PostgresLLMResponseRepository` |

### 2. LLM Services (singleton - `@lru_cache`)

| Factory | Service | Prompt name | Temp | Mục đích |
|---|---|---|---|---|
| `get_llm_caller_service()` | `LLMCallerService` | `chatbot_prompt` | 0.7 | Chat trả lời tự do, có parser Pydantic |
| `get_llm_caller_service_vietnam_language_format_prompt()` | `LLMCallerService` | `vietnam_language_format_prompt` | 0 | Chuẩn hóa câu tiếng Việt (thêm dấu) |
| `get_llm_caller_service_query_understand()` | `LLMCallerService` | `query_understand_prompt` | 0 | Phân tích cấu trúc câu hỏi → `QueryUnderstandOutput` (Pydantic) |
| `get_llm_caller_service_tool_calling()` | `AgentCallerService` | `tool_calling_prompt_v1` | 0 | Agent gọi công cụ qua MCP → `ToolCallingOutput` (Pydantic) |

### 3. RAG / Vector Search (singleton)

| Factory | Mô tả |
|---|---|
| `get_qdrant_client()` | `QdrantClient` kết nối tới Qdrant server |
| `get_rag_collection_names()` | Tuple collection names từ env (mặc định 2 collections) |
| `get_document_search_service(collection_name)` | `DocumentSearchService` cho 1 collection cụ thể (cache theo tên collection) |

---

## API Endpoints

### 1. Health Check
Router: [health.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/routes/health.py)  
Prefix: `/health`

| Method | Path | Mô tả |
|---|---|---|
| GET | `/health/` | Trả về `{"status": "healthy"}` để kiểm tra server sống |

---

### 2. Conversation (Cuộc hội thoại)
Router: [conversation.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/routes/conversation.py)  
Prefix: `/conversation`  
Schema: [schemas/conversation.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/schemas/conversation.py)

| Method | Path | Request | Response | Mô tả |
|---|---|---|---|---|
| POST | `/conversation/create_conversation` | `CreateConversationRequest` | `CreateConversationResponse` (status=`PENDING`) | Tạo cuộc hội thoại mới trong PostgreSQL |
| GET | `/conversation/conversation/{conversation_id}` | UUID path param | `GetConversationResponse` | Lấy info 1 hội thoại theo ID |

Trạng thái hội thoại (`ConversationStatus`): `SUCCESS` / `PENDING` / `FAILED`

---

### 3. Message (Tin nhắn người dùng)
Router: [message.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/routes/message.py)  
Prefix: `/message`  
Schema: [schemas/message.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/schemas/message.py)

| Method | Path | Request | Response | Mô tả |
|---|---|---|---|---|
| POST | `/message/create_message` | `CreateMessageRequest` | `CreateMessageResponse` (status=`PENDING`) | Lưu tin nhắn người dùng vào DB |
| GET | `/message/message/{message_id}` | UUID | `GetMessageResponse` | Lấy 1 tin nhắn theo ID |
| GET | `/message/conversation/{conversation_id}` | UUID | `list[GetMessageResponse]` | Lấy toàn bộ tin nhắn trong 1 hội thoại |

---

### 4. LLM Response (Kết quả trả lời từ AI)
Router: [llm_response.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/routes/llm_response.py)  
Prefix: `/llm_response`  
Schema: [schemas/llm_response.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/schemas/llm_response.py)

| Method | Path | Request | Response | Mô tả |
|---|---|---|---|---|
| POST | `/llm_response/create_llm_response` | `LLMResponseRequest` | `LLMResponseResponse` | Lưu kết quả trả lời của LLM vào DB (liên kết `message_id` + `conversation_id`) |
| GET | `/llm_response/llm_response/{llm_response_id}` | UUID | `LLMResponseResponse` | Lấy 1 response theo ID |
| GET | `/llm_response/conversation/{conversation_id}` | UUID | `list[LLMResponseResponse]` | Lấy toàn bộ LLM responses trong 1 hội thoại |

---

### 5. AI Chat (Gọi LLM / Agent trực tiếp)
Router: [ai_chat.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/routes/ai_chat.py)  
Prefix: `/ai_chat`  
Schema: [schemas/llm_caller.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/schemas/llm_caller.py)

| Method | Path | Service sử dụng | I/O | Mô tả |
|---|---|---|---|---|
| POST | `/ai_chat/chat_with_llm/` | `LLMCallerService` (chatbot_prompt, temp=0.7) | `LLMCallerRequest` → `LLMCallerResponse` | Chat thông thường, LLM trả lời dựa trên `content` + `question_context` (nếu có) |
| POST | `/ai_chat/normalize_vietnam_sentence/` | `LLMCallerService` (vietnam_language_format_prompt, temp=0) | `LLMCallerRequest` → `LLMCallerResponse` | Chuẩn hóa câu tiếng Việt (thêm dấu, sửa lỗi chính tả), **không dùng context** |
| POST | `/ai_chat/query_understand/` | `LLMCallerService` (query_understand_prompt, temp=0) + parser `QueryUnderstandOutput` | `LLMCallerRequest` → `LLMCallerResponse` | Phân tích câu hỏi: trích xuất stock_id, year, document_type, question_type,... |
| POST | `/ai_chat/tool_calling/` | `AgentCallerService` (tool_calling_prompt_v1, LangGraph) | `ToolCallingRequest` → `ToolCallingResponse` | Agent điều phối gọi công cụ qua MCP. Trả về `{tool_output, tool_name, input_message}` |

**Flow tool_calling chi tiết:**
```
ToolCallingRequest.vietnamese_with_diacritics
  └─> AgentCallerService.call_agent()
        ├─ LangGraph StateGraph (node: agent → tools → agent ...)
        ├─ Gemini quyết định gọi tool nào
        ├─ Tool execution qua MCP protocol
        └─ Trả về kết quả cuối cùng sau khi agent tổng hợp
```

---

### 6. RAG (Tìm kiếm tài liệu bằng Vector)
Router: [rag.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/routes/rag.py)  
Prefix: `/rag`  
Schema: [schemas/rag.py](file:///Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/chatbot/backend/schemas/rag.py)

| Method | Path | I/O | Mô tả |
|---|---|---|---|
| POST | `/rag/get_documents_with_user_query` | `InputVectorSearch{query}` → `OutputVectorSearch{results: list[dict]}` | Hybrid search (dense + sparse vector) trên **tất cả Qdrant collections** song song |

**Luồng RAG chi tiết:**
```
POST /rag/get_documents_with_user_query
  │
  ├─ Lấy danh sách collections từ get_rag_collection_names()
  │    vd: ("newspaper_embedded", "stock_price_embedded")
  │
  ├─ Tạo task search cho mỗi collection (song song)
  │    for collection_name in collections:
  │        asyncio.create_task( search_collection(...) )
  │
  ├─ asyncio.gather(*search_tasks)  # Chạy tất cả đồng thời
  │
  │   Mỗi DocumentSearchService.retrieve_database_with_user_query():
  │     ├─ Embed query → dense vector (Gemini embedding)
  │     ├─ Embed query → sparse vector (BM25)
  │     └─ Hybrid search trên Qdrant (kết hợp dense + sparse scores)
  │
  └─ Flatten kết quả → list[dict] → OutputVectorSearch
```

Lưu ý: Mỗi collection search trả về `limit=5` tài liệu, tổng kết quả có thể lên đến `5 * số_collections`.

---

## Luồng xử lý End-to-End (E2E) điển hình

### Scenario: Người dùng gửi tin nhắn mới

```
[Frontend]
   │
   ├─ 1. POST /conversation/create_conversation  (nếu là hội thoại mới)
   │     └─ Lưu conversation → nhận conversation_id
   │
   ├─ 2. POST /message/create_message
   │     └─ Lưu tin nhắn người dùng → nhận message_id
   │
   ├─ 3. POST /ai_chat/normalize_vietnam_sentence
   │     └─ Chuẩn hóa câu hỏi tiếng Việt (thêm dấu)
   │
   ├─ 4. POST /ai_chat/query_understand
   │     └─ Phân tích cấu trúc câu hỏi → query_type, stock_id, year...
   │
   ├─ 5a. (Nếu cần context) POST /rag/get_documents_with_user_query
   │      └─ Tìm tài liệu liên quan từ Qdrant
   │
   ├─ 5b. (Nếu cần công cụ) POST /ai_chat/tool_calling
   │      └─ Agent gọi tool (MCP) → lấy dữ liệu động (cổ phiếu, báo cáo...)
   │
   ├─ 6. POST /ai_chat/chat_with_llm  (với question_context = kết quả RAG/Tools)
   │     └─ LLM tổng hợp → câu trả lời cuối
   │
   └─ 7. POST /llm_response/create_llm_response
         └─ Lưu kết quả LLM vào DB (liên kết message_id + conversation_id)
```

---

## Cấu trúc thư mục

```
backend/
├── api.py                # FastAPI app entry point, đăng ký routers
├── dependencies.py       # DI container (services, LLM clients, Qdrant)
├── README.MD             # File này
├── __init__.py
├── routes/               # API Routers (mỗi file = 1 nhóm endpoints)
│   ├── health.py
│   ├── conversation.py
│   ├── message.py
│   ├── llm_response.py
│   ├── ai_chat.py
│   └── rag.py
└── schemas/              # Pydantic schemas (request/response validation)
    ├── conversation.py
    ├── message.py
    ├── llm_response.py
    ├── llm_caller.py
    └── rag.py
```

---

## Design Patterns & Quy ước code

1. **Dependency Injection**: Mọi endpoint nhận service thông qua `Depends()`, không khởi tạo trực tiếp.
2. **Annotated Type Hint**: Sử dụng `Annotated[Type, Depends(...)]` theo chuẩn FastAPI mới.
3. **Singleton cho LLM/Qdrant**: `@lru_cache` để tránh tạo lại client mỗi request.
4. **Async DB**: PostgreSQL sử dụng `AsyncSession` (SQLAlchemy async), tất cả service methods là `async def`.
5. **Parallel RAG**: Dùng `asyncio.gather()` để search nhiều Qdrant collections đồng thời.
6. **Pydantic Strict**: Mọi input/output đi qua Pydantic schema validation.
7. **Status PENDING**: Khi tạo conversation/message, status mặc định là `PENDING` (sẽ cập nhật sau khi xử lý xong).
