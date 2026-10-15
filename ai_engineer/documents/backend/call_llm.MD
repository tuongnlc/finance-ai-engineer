# Call LLM API Overview

## Endpoints Group

**Prefix:** `/call_llm`
**Tags:** `AI Chat`

## Schemas

### LLMCallerRequest

| Field              | Type         | Constraints | Description                  |
|--------------------|--------------|-------------|------------------------------|
| `id`               | UUID         | NOT NULL    | Request ID                   |
| `content`          | STRING       | NOT NULL    | User question / input text   |
| `question_context` | STRING       | NULL        | Additional context for the question |

### LLMCallerResponse

| Field      | Type   | Constraints | Description          |
|------------|--------|-------------|----------------------|
| `id`       | UUID   | NOT NULL    | Request ID (echoed)  |
| `response` | STRING | NOT NULL    | LLM response text    |

### ToolCallingRequest

| Field                       | Type   | Constraints | Description                                        |
|-----------------------------|--------|-------------|----------------------------------------------------|
| `id`                        | UUID   | NOT NULL    | Request ID                                         |
| `original_query`            | STRING | NOT NULL    | Original query of the request                      |
| `vietnamese_with_diacritics`| STRING | NOT NULL    | Vietnamese sentence with diacritics                |
| `question_type`             | STRING | NOT NULL    | Type of the question                               |
| `main_topic`                | STRING | NOT NULL    | Main topic of the question                         |
| `stock_id`                  | STRING | NOT NULL    | Stock ID of the question                           |
| `target_year`               | STRING | NOT NULL    | Target year of the question                        |
| `document_type`             | STRING | NOT NULL    | Type of the document                               |
| `optimized_search_query`    | STRING | NOT NULL    | Optimized search query of the question             |

### ToolCallingResponse

| Field          | Type   | Constraints | Description               |
|----------------|--------|-------------|---------------------------|
| `id`           | UUID   | NOT NULL    | Request ID (echoed)       |
| `tool_output`  | STRING | NOT NULL    | Output returned by tool   |
| `tool_name`    | STRING | NOT NULL    | Name of the executed tool |
| `input_message`| STRING | NOT NULL    | Input message to the tool |

## API List

| Method | URL                          | Purpose                                                                |
|--------|------------------------------|------------------------------------------------------------------------|
| POST   | `/call_llm/chat_with_llm/`   | Chat with LLM using question + context                                 |
| POST   | `/call_llm/query_understand/`| Understand a query with LLM (no context passed)                        |
| POST   | `/call_llm/tool_calling/`    | Run an agent tool-calling flow on the preprocessed Vietnamese query    |
