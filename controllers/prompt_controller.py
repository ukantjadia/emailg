import os
import logging
from config.config import Config

logger = logging.getLogger(__name__)

class PromptController:
    """
    Handles prompt template path resolution and prompt building.
    """
    @classmethod
    def get_prompt_path(cls, tone, focus):
        """
        Returns the file path of the prompt based on tone and focus.
        Example: tone='friendly', focus='sales' → prompt_bank/friendly_sales_v1.txt
        """
        filename = f"{tone.lower()}_{focus.lower()}_{Config.PROMPT_TEMPLATE_VERSION}.txt"
        return os.path.join(Config.PROMPT_DIR, filename)

    @classmethod
    def build_prompt(cls, tone, focus, company_name, industry, context):
        """
        Loads the template file and replaces placeholders with real values.
        Raises FileNotFoundError if the template is missing, or Exception on other errors.
        """
        prompt_path = cls.get_prompt_path(tone, focus)

        if not os.path.exists(prompt_path):
            logger.warning(f"Prompt file not found: {prompt_path}")
            raise FileNotFoundError(f"Prompt template not found for: {tone} + {focus}")

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                template = f.read()

            prompt = (
                template.replace("{{company_name}}", company_name)
                        .replace("{{context}}", context)
                        .replace("{{industry}}", industry)
            )

            logger.info(f"Prompt generated successfully for {tone}_{focus}")
            return prompt

        except Exception as e:
            logger.error("Error while building prompt", exc_info=True)
            raise Exception("Error generating the prompt.")
