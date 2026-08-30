import time
from langchain_core.output_parsers import PydanticOutputParser
from ai_engineer.helpers.prompt.prompt_loading import MLFlowPromptLoading
from ai_engineer.shared.llm.create_llm import create_gemini_llm


class CallLLMWithStructuredOutput:
    def __init__(self, llm, prompt_name: str, llm_api_key: str, structure_output):    
        self.llm = llm
        self.prompt_name = prompt_name
        self.llm_api_key = llm_api_key
        self.structure_output = structure_output

    def _prompt_loading_from_mlflow(self):
        parser = PydanticOutputParser(pydantic_object=self.structure_output)
        return MLFlowPromptLoading(
            prompt_name=self.prompt_name
        ).load_and_parse_prompt().partial(
            format_instructions=parser.get_format_instructions()
        )

    def _create_llm_with_structured_output(self):
        llm = create_gemini_llm(
                api_key=self.llm_api_key,
                model_name="gemini-3.5-flash-lite",
                temperature=0,
            )
        structured_llm = llm.with_structured_output(self.structure_output)
        return structured_llm


    def call_llm_in_batch(self, inputs: list[dict], batch_size: int = 15, waiting_time: int = 60):
        """
            Inputs is data getting from qdrant db.
            This method will different between each applications.
        """
        chain = self._prompt_loading_from_mlflow() | self._create_llm_with_structured_output()

        #Reprocess inputs to fit with prompt format
        text_contents = [{"text_content": row["newspaper_content"]} for row in inputs]
        all_responses = []
        for i in range(0, len(text_contents), batch_size):
            chunk = text_contents[i:i + batch_size]
            chunk_responses = chain.batch(chunk, config={"max_concurrency": batch_size})
            all_responses.extend(chunk_responses)
            if i + batch_size < len(text_contents):
                print(f"Đã xử lý xong batch {i // batch_size + 1}, đợi {waiting_time}s trước batch tiếp theo...")
                time.sleep(waiting_time)
        return all_responses