# Debug Session: message-422-error

- Status: OPEN
- Symptom: Frontend receive `HTTPStatusError: 422 Unprocessable Entity` when calling `POST /message/create_message`
- Expected: Message API accepts payload and returns created message response

## Hypotheses

1. Frontend is sending one or more required fields with invalid types or missing values for the message create schema.
2. Frontend is sending a field name that does not match backend `CreateMessageRequest`.
3. Frontend is using `conversation_id` or `space_id` in a format that Pydantic rejects.
4. Frontend is posting to the correct endpoint, but the backend request model has stricter optional/required rules than the frontend assumes.
5. The frontend callback is mutating `session` incorrectly, causing stale or empty IDs to be sent on later requests.

## Plan

1. Inspect backend request schema and current frontend payload builder.
2. Add minimal debug instrumentation to capture outbound message payload and response body/status.
3. Reproduce the failure and compare payload against schema.
4. Apply the smallest fix supported by evidence.
5. Verify with post-fix reproduction.
