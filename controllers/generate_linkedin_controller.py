import logging
from datetime import datetime
from prompt_bank.linkedin_prompt_builder import build_linkedin_prompt
from controllers.generate_controller import GenerateController

logger = logging.getLogger(__name__)


def generate_linkedin_message(tone, name, company, purpose, word_limit=100, model_choice="groq"):
    """
    Builds the prompt using LinkedIn template, sends to selected model, trims output, and returns.
    """
    try:
        # Step 1: Build prompt
        prompt = build_linkedin_prompt(tone, name, company, purpose)

        # Step 2: Generate using selected model
        generated = GenerateController.generate_with_model(prompt, model_choice)

        # Step 3: Trim output to word limit
        trimmed = enforce_word_limit(generated, word_limit)

        return trimmed

    except Exception as e:
        logger.exception("Error generating LinkedIn message")
        return "Something went wrong. Please try again later."


def enforce_word_limit(text, word_limit):
    """
    Trims text to the specified word limit.
    """
    words = text.split()
    if len(words) <= word_limit:
        return text
    return ' '.join(words[:word_limit]) + '...'
