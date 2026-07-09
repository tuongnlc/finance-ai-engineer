
from ai_engineer.applications.topic_tagging.application.prompt.prompt_template import template
from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister

if __name__ == "__main__":
    prompt_register = PromptRegister()

    prompt_register.register_prompt(
        prompt_name='topic_tagging', 
        prompt_template=template
    )