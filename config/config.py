import os
from dotenv import load_dotenv

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
    PROMPT_DIR          = os.getenv('PROMPT_DIR', os.path.join(os.getcwd(), 'prompt_bank'))
    PROMPT_TEMPLATE_VERSION = 'v1'

# Flask config classes
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# What app.py imports
config = DevelopmentConfig
