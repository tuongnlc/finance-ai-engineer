# Frontend Structure for Gradio

This folder contains the Gradio-based frontend for the `chatbot` application.

The recommended design is to keep the frontend thin:

- Gradio is responsible for layout, user interaction, and UI state.
- Business logic should stay out of UI files.
- Data access should go through the backend API instead of calling databases or LLM infrastructure directly from the frontend.

## Goal

Keep the frontend easy to change without affecting the backend or domain logic.

This structure works well with the current module organization in `chatbot`, where backend and application logic are already separated into layers such as:

- `backend/`
- `app/`
- `domain/`

The frontend should follow the same idea, but in a lighter form suitable for Gradio.

## Recommended Folder Layout

```text
frontend/
  app.py
  config.py
  ui/
    blocks.py
    components/
      chat_input.py
      loading.py
  controllers/
    chat_controller.py
  services/
    chatbot_api.py
    conversation_api.py
  schemas/
    chat.py
  state/
    session.py
  utils/
    formatters.py
    validators.py
  tests/
    test_controller.py
    test_services.py
  README.MD
```

## Responsibility of Each Part

### `app.py`

Entry point for launching the Gradio app.

Suggested responsibility:

- initialize configuration
- build the Gradio app
- launch the app

This file should stay small and should not contain business logic.

### `config.py`

Central place for frontend configuration.

Examples:

- backend base URL
- environment flags
- feature toggles
- timeout values

This helps avoid scattering configuration values across UI files.

### `ui/`

Contains Gradio layout and reusable UI components.

Examples:

- `blocks.py`: assemble the full Gradio screen
- `components/chat_input.py`: input textbox, send button, output area
- `components/loading.py`: loading indicator or status message

Rules for this layer:

- should define how the UI looks
- should not contain database logic
- should not contain backend integration details
- should not contain core business rules

### `controllers/`

Handles user-driven flows from the UI.

This is the orchestration layer between Gradio components and service calls.

Examples of responsibilities:

- receive user input from Gradio events
- validate or normalize input
- call service methods
- map service results into UI-friendly output
- manage loading and error flow

If a button click triggers multiple steps, that flow should usually live here.

### `services/`

Contains the frontend-side clients that call backend APIs.

Examples:

- `chatbot_api.py`
- `conversation_api.py`

Rules for this layer:

- talk to FastAPI endpoints
- convert request and response payloads
- isolate HTTP details from controllers and UI

This separation makes it easier to change API contracts later without rewriting Gradio layout code.

### `schemas/`

Defines frontend-facing request and response models when needed.

Use this layer if:

- the frontend exchanges structured payloads with the backend
- you want typed models instead of loose dictionaries
- the response shape starts growing beyond a few simple fields

If the frontend remains very small, this layer can stay minimal.

### `state/`

Stores frontend session state and UI state.

Examples:

- current conversation ID
- chat history for the current session
- active user or space context
- loading flags
- temporary UI state

This is useful when the app grows beyond a single request-response interaction.

### `utils/`

Small helper utilities shared across the frontend.

Examples:

- `formatters.py`: render messages, timestamps, labels
- `validators.py`: input validation and simple guard checks

This layer should only contain reusable helper logic, not orchestration.

### `tests/`

Focused tests for the frontend-side logic.

Recommended priorities:

- test controller behavior
- test service request/response handling
- avoid over-testing Gradio layout unless the UI flow is complex

## Recommended Design Principles

### 1. Keep Gradio UI Thin

A Gradio file should mostly describe:

- components
- layout
- event bindings

Avoid putting processing logic directly inside `Blocks()` definitions.

### 2. Do Not Call Infrastructure Directly from the Frontend

Avoid placing direct calls to:

- Qdrant
- embedding models
- LLM providers
- internal repositories

inside frontend files.

Those concerns should normally be handled by backend or application services.

The frontend should prefer calling backend APIs and rendering the returned result.

### 3. Separate Event Flow from View Definition

Keep these concerns separate:

- `ui/`: what the user sees
- `controllers/`: what happens when the user clicks or submits
- `services/`: how the frontend communicates with the backend

This makes the app easier to debug and refactor.

### 4. Avoid Using a Demo File as the Main App

A file such as `test_gradio.py` is acceptable for experimentation, but it should not remain the long-term entry point.

Prefer names like:

- `app.py`
- `main.py`

This avoids confusion with actual test files.

## Practical Minimal Version

If you want a simpler structure at the beginning, this is enough:

```text
frontend/
  app.py
  ui.py
  controller.py
  api_client.py
  state.py
  README.MD
```

This is a good starting point for a small Gradio app, and it can later evolve into the larger structure if the frontend grows.

## Suggested Direction for the Current Codebase

Based on the current `chatbot` module structure, the most suitable direction is:

- keep Gradio in the frontend layer only
- move user interaction flow into controller files
- call backend APIs through service clients
- keep core business logic in backend or app services

In short, the frontend should act as an adapter between the user and the backend, not as the place where the main business logic lives.
