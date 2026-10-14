# Conversation API Overview

## Table

**Name:** `conversation`

## Schema

| Column            | Type         | Constraints          | Description                          |
|-------------------|--------------|----------------------|--------------------------------------|
| `id`              | UUID         | PK, auto (uuid4)     | Conversation ID                      |
| `session_id`      | UUID         | NOT NULL             | Related session ID                   |
| `title`           | VARCHAR(255) | NULL                 | Conversation title                   |
| `space_id`        | VARCHAR(255) | NULL                 | Workspace ID                         |
| `user_id`         | VARCHAR(255) | NULL                 | Owner user ID                        |
| `created_timestamp` | BIGINT     | NOT NULL             | Creation epoch timestamp             |
| `status`          | VARCHAR(255) | NOT NULL, default `PENDING` | `SUCCESS` / `PENDING` / `FAILED` |
| `created_at`      | DATE         | NOT NULL, default today | Creation date                      |

## API List

| Method | URL                                              | Purpose                                             |
|--------|--------------------------------------------------|-----------------------------------------------------|
| POST   | `/conversations`                                 | Create a new conversation                           |
| GET    | `/conversations/{conversation_id}`               | Get a single conversation by ID                     |
| GET    | `/conversations?user_id=...&status=...`          | List conversations, filterable by `user_id` / `status` |

### Query Params (List endpoint)

- `user_id` (optional) — filter by owner
- `status` (optional) — filter by status (`SUCCESS` / `PENDING` / `FAILED`)
