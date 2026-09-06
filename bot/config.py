import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

SUBGRAM_PUBLISHER_KEY = os.getenv("SUBGRAM_PUBLISHER_KEY", "")
SUBGRAM_BOT_API_KEY = os.getenv("SUBGRAM_BOT_API_KEY", "")
SUBGRAM_API_URL = os.getenv("SUBGRAM_API_URL", "https://api.subgram.org")

DEMO_MODE = os.getenv("DEMO_MODE", "1").lower() in ("1", "true", "yes")

ADMIN_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]

DB_PATH = BASE_DIR / "data" / "bot.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

TASK_COOLDOWN_SECONDS = int(os.getenv("TASK_COOLDOWN_SECONDS", "45"))
OPEN_CASE_COOLDOWN_SECONDS = int(os.getenv("OPEN_CASE_COOLDOWN_SECONDS", "10"))

STAR_MIN = int(os.getenv("STAR_MIN", "1"))
STAR_MAX = int(os.getenv("STAR_MAX", "3"))

MARGIN_MODE = os.getenv("MARGIN_MODE", "percent")
MARGIN_VALUE = float(os.getenv("MARGIN_VALUE", "50"))

WEBAPP_URL = os.getenv("WEBAPP_URL", "")