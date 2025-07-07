import uuid
import logging
import asyncio
from datetime import datetime
from config.config import Config
from groq import Groq
from openai import OpenAI
import anthropic

from controllers.prompt_controller import PromptController

logger = logging.getLogger(__name__)

DEFAULT_TONES = ["professional", "friendly", "direct"]


class GenerateController:
    """
    Controller for:
      - building prompts for each tone
      - calling the chosen LLM in parallel
      - persisting a 'generation' row via FeedbackController
      - returning a list of {tone, message_id, message}
    """

    @classmethod
    def _call_groq(cls, prompt: str) -> str:
        client = Groq(api_key=Config.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
        )
        text = ""
        for chunk in completion:
            delta = chunk.choices[0].delta.content
            if delta:
                text += delta
        return text

    @classmethod
    def _call_claude(cls, prompt: str) -> str:
        client = anthropic.Client(api_key=Config.ANTHROPIC_API_KEY)
        full_prompt = f"{anthropic.HUMAN_PROMPT}{prompt}{anthropic.AI_PROMPT}"
        resp = client.completions.create(
            model="claude-2",
            prompt=full_prompt,
            max_tokens_to_sample=Config.CLAUDE_MAX_TOKENS,
            temperature=0.7
        )
        return resp.completion

    @classmethod
    def _call_deepseek(cls, prompt: str) -> str:
        client = OpenAI(
            api_key=Config.DEEPSEEK_API_KEY,
            base_url=Config.OPENAI_BASE_URL
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content

    @classmethod
    def generate_with_model(cls, prompt: str, model_choice: str) -> str:
        key = model_choice.strip().lower()
        if key == "groq":
            return cls._call_groq(prompt)
        if key in ("claude", "anthropic"):
            return cls._call_claude(prompt)
        if key == "deepseek":
            return cls._call_deepseek(prompt)
        raise ValueError(f"Unsupported model_choice: {model_choice}")

    @classmethod
    def generate_all(cls, data: dict):
        """
        data must contain:
          - company_name, industry, focus, model_choice
          - additional_context (list of at least 3 strings)
          - user_id (optional)
          - optionally parent_message_id (for regenerations)
          - optionally tones (single-tone list to override DEFAULT_TONES)
        """
        # In‐function import to avoid circular dependency
        from controllers.feedback_controller import FeedbackController
        feedback_ctrl = FeedbackController()

        # 1) extract & validate
        company  = data.get("company_name", "").strip()
        industry = data.get("industry", "").strip()
        focus    = data.get("focus", "")
        model    = data.get("model_choice", "")
        contexts = data.get("additional_context", [])
        parent   = data.get("parent_message_id")  # may be None

        if not (company and industry and focus and model and contexts):
            raise ValueError("Missing required fields")
        for i, pt in enumerate(contexts[:3]):
            if len(pt.split()) < 20:
                raise ValueError(f"Context point {i+1} must be ≥20 words.")
        context = " ".join(contexts)

        tones  = data.get("tones") or DEFAULT_TONES
        user_id = data.get("user_id", "anonymous")

        # 2) build & call LLMs in parallel
        async def call_tone(tone: str):
            prompt = PromptController.build_prompt(tone, focus, company, industry, context)
            message = await asyncio.to_thread(cls.generate_with_model, prompt, model)
            return tone, prompt, message

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = [call_tone(t) for t in tones]
            raw_results = loop.run_until_complete(asyncio.gather(*tasks))
        except Exception:
            logger.exception("Parallel generation error")
            raise
        finally:
            loop.close()

        # 3) persist feedback rows & build output
        output = []
        for tone, prompt_text, msg in raw_results:
            msg_id = str(uuid.uuid4())
            feedback_ctrl.capture_feedback({
                "message_id":        msg_id,
                "parent_message_id": parent,
                "feedback_type":     "generation",
                "user_id":           user_id,
                "company_name":      company,
                "industry":          industry,
                "tone":              tone,
                "focus":             focus,
                "context":           context,
                "model_used":        model,
                "prompt_template":   f"{tone}_{focus}_{Config.PROMPT_TEMPLATE_VERSION}",
                "prompt_text":       prompt_text,
                "generated_message": {
                    "message":      msg,
                    "generated_at": datetime.utcnow().isoformat()
                }
            })
            output.append({
                "tone":       tone,
                "message_id": msg_id,
                "message":    msg
            })

        return output
