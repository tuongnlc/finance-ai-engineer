from ai_engineer.shared.llm.create_llm import create_gemini_llm



class LLMCallerService:
    def __init__(self, 
        api_key: str,
        model_name: str,
        temperature: float,
    ):
        self.llm = create_gemini_llm(api_key, model_name, temperature)

    def call_llm(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)
        
        content = response.content
        response_metadata = response.response_metadata
        tool_calls = response.tool_calls
        invalid_tool_calls = response.invalid_tool_calls
        usage_metadata = response.usage_metadata
        
        return content, response_metadata, tool_calls, invalid_tool_calls, usage_metadata
    