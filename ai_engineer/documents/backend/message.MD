# Message API Overview

## Table

**Name:** `message`

## Schema

| Column            | Type         | Constraints          | Description                          |
|-------------------|--------------|----------------------|--------------------------------------|
| `id`              | UUID         | PK                   | Message ID                           |
| `conversation_id` | UUID         | NOT NULL             | Related conversation ID              |
| `created_timestamp` | BIGINT     | NOT NULL             | Creation epoch timestamp             |
| `content`         | TEXT         | NOT NULL             | Message content                      |
| `space_id`        | VARCHAR(255) | NULL                 | Workspace ID                         |
| `user_id`         | VARCHAR(255) | NULL                 | Owner user ID                        |
| `message_url`     | VARCHAR(255) | NULL                 | Message URL                          |
| `status`          | VARCHAR(255) | NOT NULL, default `PENDING` | `PENDING` / `COMPLETED` / `FAILED` |
| `created_at`      | DATE         | NOT NULL, default today | Creation date                      |

## API List

| Method | URL                                              | Purpose                                             |
|--------|--------------------------------------------------|-----------------------------------------------------|
| POST   | `/message/`                                      | Create a new message                                |
| GET    | `/message/{message_id}`                          | Get a single message by ID                          |
| GET    | `/message/?conversation_id=...&user_id=...`      | List messages, filterable by `conversation_id` / `user_id` |

### Query Params (List endpoint)

- `conversation_id` (optional) — filter by related conversation
- `user_id` (optional) — filter by owner
