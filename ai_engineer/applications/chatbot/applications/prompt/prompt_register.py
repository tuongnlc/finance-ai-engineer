
from ai_engineer.applications.chatbot.applications.prompt.prompt_template import chatbot_template, vietnam_language_format_prompt

from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister

if __name__ == "__main__":
    """
        Register prompt templates to prompt registry.
        Each time we run this code it will create a new prompt or update version in the prompt registry.
    """
    prompt_register = PromptRegister()

    prompt_register.register_prompt(
        prompt_name='chatbot_prompt', 
        prompt_template=chatbot_template
    )

    prompt_register.register_prompt(
        prompt_name='vietnam_language_format_prompt', 
        prompt_template=vietnam_language_format_prompt
    )

