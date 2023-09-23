import os
import yaml
import logging
from telegram.ext import Application
from dotenv import load_dotenv

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv("../.env/voenka-bot.env")


with open("bot/config/strings.yaml", "r") as f:
    strings = yaml.safe_load(f)


SHEET_NAME_TECH = "tech"
SHEET_NAME_USERS = "users"
TOKEN_NAMES_LIST = [
    "type",
    "project_id",
    "private_key_id",
    "private_key",
    "client_email",
    "client_id",
    "auth_uri",
    "token_uri",
    "auth_provider_x509_cert_url",
    "client_x509_cert_url",
    "universe_domain",
]
TOKEN = {item: os.environ[item].replace("\\n", "\n") for item in TOKEN_NAMES_LIST}

TELEGRAM_BOT_TOKEN = os.environ["telegram_bot_token"]

SHEET_KEY = os.environ["sheet_key"]

PARSE_MODE = "Markdown"

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
