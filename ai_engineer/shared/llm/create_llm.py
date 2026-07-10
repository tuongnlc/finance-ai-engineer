from langchain_google_genai import ChatGoogleGenerativeAI


def create_gemini_llm(
    api_key: str,
    model_name: str,
    temperature: float,
) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name,
        api_key=api_key,
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=0,
    )