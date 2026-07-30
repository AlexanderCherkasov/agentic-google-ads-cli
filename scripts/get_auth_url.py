#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client_id = os.getenv("GOOGLE_ADS_CLIENT_ID", "")
client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET", "")

client_config = {
    "installed": {
        "client_id": client_id,
        "client_secret": client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost:8085/"]
    }
}
SCOPES = ["https://www.googleapis.com/auth/adwords"]
flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
flow.redirect_uri = "http://localhost:8085/"
auth_url, _ = flow.authorization_url(prompt="consent")
print("AUTH_URL:", auth_url)
