import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE_PATH = BASE_DIR / "google-ads.yaml"

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# Load YAML settings
DEFAULT_SETTINGS_PATH = BASE_DIR / "config" / "default_settings.yaml"
SETTINGS = {}
if DEFAULT_SETTINGS_PATH.exists():
    with open(DEFAULT_SETTINGS_PATH, "r", encoding="utf-8") as f:
        SETTINGS = yaml.safe_load(f) or {}

# API Constants
MICROS_PER_CURRENCY_UNIT = SETTINGS.get("api", {}).get("micros_per_currency_unit", 1_000_000)
BATCH_MUTATION_SIZE = SETTINGS.get("api", {}).get("batch_mutation_size", 50)
DEFAULT_SEARCH_LIMIT = SETTINGS.get("api", {}).get("default_search_limit", 50)
OAUTH_SERVER_PORT = int(os.getenv("OAUTH_SERVER_PORT", SETTINGS.get("api", {}).get("oauth_server_port", 8085)))

# Account & Credentials (Loaded dynamically from .env or environment)
DEFAULT_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "")
DEFAULT_MCC_ID = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").replace("-", "")
DEFAULT_LOGIN_CUSTOMER_ID = DEFAULT_MCC_ID
DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")

# Defaults
DEFAULT_CURRENCY = SETTINGS.get("defaults", {}).get("currency_code", "USD")
DEFAULT_TIME_ZONE = SETTINGS.get("defaults", {}).get("time_zone", "America/New_York")
DEFAULT_TARGET_COUNTRY = SETTINGS.get("defaults", {}).get("target_country", "United States")
DEFAULT_TARGET_LANGUAGE = SETTINGS.get("defaults", {}).get("target_language", "English")
DEFAULT_CHANNEL_TYPE = SETTINGS.get("defaults", {}).get("advertising_channel_type", "SEARCH")
DEFAULT_BIDDING_STRATEGY = SETTINGS.get("defaults", {}).get("bidding_strategy", "MANUAL_CPC")
DEFAULT_CPC_BID_USD = float(SETTINGS.get("defaults", {}).get("default_cpc_bid_usd", 0.50))
DEFAULT_DAILY_BUDGET_USD = float(SETTINGS.get("defaults", {}).get("default_daily_budget_usd", 20.00))
DEFAULT_CAMPAIGN_STATUS = SETTINGS.get("defaults", {}).get("default_campaign_status", "PAUSED")

# Constraints
HEADLINE_MAX_LEN = SETTINGS.get("ad_constraints", {}).get("headline_max_len", 30)
DESCRIPTION_MAX_LEN = SETTINGS.get("ad_constraints", {}).get("description_max_len", 90)
HEADLINES_MIN = SETTINGS.get("ad_constraints", {}).get("headlines_min", 3)
HEADLINES_MAX = SETTINGS.get("ad_constraints", {}).get("headlines_max", 15)
DESCRIPTIONS_MIN = SETTINGS.get("ad_constraints", {}).get("descriptions_min", 2)
DESCRIPTIONS_MAX = SETTINGS.get("ad_constraints", {}).get("descriptions_max", 4)
