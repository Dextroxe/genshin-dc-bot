import os


from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env"))
load_dotenv(override=True)

DISCORD_BOT_TOKEN = os.getenv("BOT_TOKEN")

if not DISCORD_BOT_TOKEN:
    print("Bot token is not provided. Enter it here or use .env:")
    DISCORD_BOT_TOKEN = input().strip()

CODE_URL = os.getenv("CODE_URL", "")

IMAGE_HOSTING_CHANNEL_ID = int(os.getenv("IMAGE_HOSTING_CHANNEL_ID")) if os.getenv("IMAGE_HOSTING_CHANNEL_ID") else None
ROUTE_CHANNEL_IDS = list(
    map(int, filter(None, os.getenv("ROUTE_CHANNEL_IDS", "").split(",")))
)
NEWS_CHANNEL_IDS = list(
    map(int, filter(None, os.getenv("NEWS_CHANNEL_IDS", "").split(",")))
)

PIXIV_REFRESH_TOKEN = os.getenv("PIXIV_REFRESH_TOKEN", "")
PIXIV_CHANNEL_ID = os.getenv("PIXIV_CHANNEL_ID", "")
PIXIV_BLOCKED_TAGS = list(
    filter(None, os.getenv("PIXIV_BLOCKED_TAGS", "").split(","))
)
