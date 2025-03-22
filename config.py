import os
from dotenv import load_dotenv # type: ignore

# Load environment variables
load_dotenv()

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

# API keys for other services
SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # For web search

# LLM Configuration
CLAUDE_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"  # Claude Sonnet 3.5 model ID
TEMPERATURE = 0.7
MAX_TOKENS = 4096

# Web scraping settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 40  # seconds

# Content generation settings
MAX_ITERATIONS = 4
BLOG_POST_LENGTH = 1200  # words

# Image generation settings
STABLE_DIFFUSION_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # Hugging Face API token
IMAGE_SIZE = (1024, 1024)

# HTML generation settings
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "utils", "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

# Validate required credentials
def validate_credentials():
    missing_credentials = []
    
    if not AWS_ACCESS_KEY_ID:
        missing_credentials.append("AWS_ACCESS_KEY_ID")
    if not AWS_SECRET_ACCESS_KEY:
        missing_credentials.append("AWS_SECRET_ACCESS_KEY")
    if not SERPER_API_KEY:
        missing_credentials.append("SERPER_API_KEY")
    
    return missing_credentials