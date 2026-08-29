from ai_engineer.applications.topic_summary.application.prompt.prompt_template import business_template
from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister

if __name__ == "__main__":
    prompt_register = PromptRegister()

    prompt_register.register_prompt(
        prompt_name='topic_summary__business', 
        prompt_template=business_template
    )