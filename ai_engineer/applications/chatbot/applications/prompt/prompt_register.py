
from ai_engineer.applications.chatbot.applications.prompt.prompt_template import template

from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister

if __name__ == "__main__":
    prompt_register = PromptRegister()

    prompt_register.register_prompt(
        prompt_name='chatbot_prompt', 
        prompt_template=template
    )