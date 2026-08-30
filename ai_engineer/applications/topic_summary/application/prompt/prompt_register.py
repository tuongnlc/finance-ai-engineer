from ai_engineer.applications.topic_summary.application.prompt.prompt_template import business_template, macro_template
from ai_engineer.helpers.prompt.prompt_registry.prompt_register import PromptRegister

if __name__ == "__main__":
    prompt_register = PromptRegister()

    # Register business template
    # prompt_register.register_prompt(
    #     prompt_name='topic_summary__business', 
    #     prompt_template=business_template
    # )

    # Register macro summary template
    prompt_register.register_prompt(
        prompt_name='topic_summary__macro', 
        prompt_template=macro_template
    )