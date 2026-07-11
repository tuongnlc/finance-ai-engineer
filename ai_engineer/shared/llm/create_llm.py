from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


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


def create_gemini_embedding(
    api_key: str,
    model_name: str,
    output_dimensionality: int,
) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        google_api_key=api_key,
        model=model_name,
        output_dimensionality=output_dimensionality,
    )