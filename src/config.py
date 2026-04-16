import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# RSS feeds
RSS_FEEDS = (
    os.getenv("RSS_FEEDS", "").split(",")
    if os.getenv("RSS_FEEDS")
    else [
        "https://arxiv.org/rss/stat.ML",
        "https://arxiv.org/rss/cs.CL",
        "https://arxiv.org/rss/cs.LG",
        "https://importai.io/feed",
    ]
)

# Keywords
KEYWORDS = (
    os.getenv("KEYWORDS", "").split(",")
    if os.getenv("KEYWORDS")
    else [
        "AI",
        "machine learning",
        "deep learning",
        "LLM",
        "NLP",
        "computer vision",
        "AGI",
        "GPT",
        "diffusion",
        "transformers",
        "multimodal",
    ]
)

# Collection settings
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "20"))
COLLECTION_TIME = os.getenv("COLLECTION_TIME", "00:00")  # UTC
