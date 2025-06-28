# Handles prompt selection logic
import os
import logging

logger = logging.getLogger(__name__)

# 🔹 Set the folder where your prompt templates will live
PROMPT_DIR = os.path.join(os.getcwd(), "prompt_bank")

def get_prompt_path(tone, focus):
    """
    Returns the file path of the prompt based on tone and focus.
    Example: tone='friendly', focus='sales' → prompt_bank/friendly_sales_v1.txt
    """
    filename = f"{tone.lower()}_{focus.lower()}_v1.txt"
    return os.path.join(PROMPT_DIR, filename)

def build_prompt(tone, focus, company_name, context):
    """
    Loads the template file and replaces placeholders with real values.
    """
    prompt_path = get_prompt_path(tone, focus)

    # 🔍 Check if file exists
    if not os.path.exists(prompt_path):
        logger.warning(f"Prompt file not found: {prompt_path}")
        return f"⚠️ Prompt template not found for: {tone} + {focus}"

    try:
        with open(prompt_path, "r") as f:
            template = f.read()

        # 🪄 Replace placeholders
        prompt = (
            template.replace("{{company_name}}", company_name)
                    .replace("{{context}}", context)
        )

        logger.info(f"Prompt generated successfully for {tone}_{focus}")
        return prompt

    except Exception as e:
        logger.error("Error while building prompt", exc_info=True)
        return "❌ Error generating the prompt."
