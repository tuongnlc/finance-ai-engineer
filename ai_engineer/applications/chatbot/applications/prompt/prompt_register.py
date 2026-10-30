
from ai_engineer.applications.chatbot.applications.prompt.prompt_template import (
    chatbot_template,
    tool_calling_v1, 
    query_understand_prompt
)
from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister

if __name__ == "__main__":
    """
        Register prompt templates to prompt registry.
        Each time we run this code it will create a new prompt or update version in the prompt registry.
    """
    prompt_register = PromptRegister()

    prompt_register.register_prompt(
        prompt_name='finance_agent_2026.finance_agent_2026_prompt.chatbot_prompt', 
        prompt_template=chatbot_template,
        enable=False
    )

    prompt_register.register_prompt(
        prompt_name="finance_agent_2026.finance_agent_2026_prompt.query_understand_prompt",
        prompt_template=query_understand_prompt,
        enable=False
    )

    prompt_register.register_prompt(
        prompt_name='finance_agent_2026.finance_agent_2026_prompt.tool_calling_prompt_v1', 
        prompt_template=tool_calling_v1,
        enable=True
    )