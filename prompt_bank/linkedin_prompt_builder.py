import os
from jinja2 import Environment, FileSystemLoader

PROMPT_DIR = os.path.join("templates", "prompt_bank", "linkedin_prompts")
env = Environment(loader=FileSystemLoader(PROMPT_DIR))

def build_linkedin_prompt(tone: str, name: str, company: str, purpose: str) -> str:
    """
    Loads the LinkedIn prompt template based on tone and injects variables.
    """
    try:
        template_file = f"{tone}.txt"
        template = env.get_template(template_file)
        prompt = template.render(name=name, company=company, purpose=purpose)
        return prompt
    except Exception as e:
        return f"Error generating prompt: {str(e)}"
