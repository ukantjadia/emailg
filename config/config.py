import os
from dotenv import load_dotenv
import requests
from groq import Groq
from openai import OpenAI, APIStatusError
import anthropic

# Load .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dev.db')

    # LLM API keys
    GROQ_API_KEY        = os.getenv('GROQ_API_KEY')
    ANTHROPIC_API_KEY   = os.getenv('ANTHROPIC_API_KEY')
    DEEPSEEK_API_KEY    = os.getenv('DEEPSEEK_API_KEY')

    # Endpoints & token caps
    OPENAI_BASE_URL     = "https://api.deepseek.com"
    CLAUDE_MAX_TOKENS   = 1024    # stay under your remaining credit

def call_groq(prompt: str) -> str:
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

def call_claude(prompt: str) -> str:
    """
    Official Claude via Anthropic SDK.
    """
    client = anthropic.Client(api_key=Config.ANTHROPIC_API_KEY)
    # Wrap the prompt between the required tokens
    full_prompt = f"{anthropic.HUMAN_PROMPT}{prompt}{anthropic.AI_PROMPT}"
    resp = client.completions.create(
        model="claude-2",                   # or "claude-3" if you have access
        prompt=full_prompt,
        max_tokens_to_sample=Config.CLAUDE_MAX_TOKENS,
        temperature=0.7
    )
    return resp.completion

def call_deepseek(prompt: str) -> str:
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

def generate_with_model(prompt: str, model_choice: str) -> str:
    key = model_choice.strip().lower()
    if key == "groq":
        return call_groq(prompt)
    if key in ("claude", "anthropic"):
        return call_claude(prompt)
    if key == "deepseek":
        return call_deepseek(prompt)
    raise ValueError(f"Unsupported model_choice: {model_choice}")

# Flask config classes
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# What app.py imports
config = DevelopmentConfig
