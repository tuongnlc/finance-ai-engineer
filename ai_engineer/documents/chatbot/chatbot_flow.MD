+ Here is most simplest chat flow for users:
Step 1: User open chatbot page
- Check conversation exist or not
- If not, create new conversation and session
- If exist, continue with existing conversation only creating new session

## Chatbot flow sequence

```mermaid
sequenceDiagram
    participant UI as UI chat
    participant Session as Create Session
    participant Conv as Create Conversation

    Note over UI,Conv: Step 1: Open chat
    UI->>Session: Open chat

    Note over Session,Conv: Step 2: Start chart
    Session->>Conv: Start chart
    Conv-->>Session: Response

    Note over Session,Conv: Step 3: Assign session ID to conversation
    Session->>Session: Assign session ID to conversation
```