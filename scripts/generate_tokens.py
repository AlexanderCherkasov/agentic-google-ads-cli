#!/usr/bin/env python3
"""
Automated Google Ads OAuth2 Token Generator.
Runs authorization flow and persistently saves credentials to both .env and google-ads.yaml.
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]
BASE_DIR = Path(__file__).resolve().parent.parent
YAML_PATH = BASE_DIR / "google-ads.yaml"
ENV_PATH = BASE_DIR / ".env"

def main():
    parser = argparse.ArgumentParser(description="Automated OAuth2 Token Generator for Google Ads API")
    parser.add_argument("--client_id", help="OAuth2 Client ID")
    parser.add_argument("--client_secret", help="OAuth2 Client Secret")
    parser.add_argument("--developer_token", help="Google Ads Developer Token")
    parser.add_argument("--customer_id", help="Google Ads Account Customer ID (without hyphens)")
    parser.add_argument("--login_customer_id", help="MCC Manager Customer ID (without hyphens)")
    args = parser.parse_args()

    print("=========================================================", flush=True)
    print("      GOOGLE ADS API AUTOMATED TOKEN GENERATOR           ", flush=True)
    print("=========================================================\n", flush=True)

    client_id = args.client_id or os.getenv("GOOGLE_ADS_CLIENT_ID")
    client_secret = args.client_secret or os.getenv("GOOGLE_ADS_CLIENT_SECRET")
    developer_token = args.developer_token or os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "YOUR_DEVELOPER_TOKEN")
    customer_id = args.customer_id or os.getenv("GOOGLE_ADS_CUSTOMER_ID", "YOUR_CUSTOMER_ID")
    login_customer_id = args.login_customer_id or os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")

    if not client_id or not client_secret:
        print("[ERROR] Client ID and Client Secret are required.", flush=True)
        sys.exit(1)

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    print("\n[+] Launching local webserver for browser authentication...", flush=True)
    print("[+] Please log in with your Google Ads manager/account...\n", flush=True)
    
    try:
        credentials = flow.run_local_server(port=8085, prompt="consent", open_browser=True)
    except OSError:
        credentials = flow.run_local_server(port=0, prompt="consent", open_browser=True)

    # 1. Save to google-ads.yaml
    config_data = {
        "developer_token": developer_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": credentials.refresh_token,
    }
    if login_customer_id:
        config_data["login_customer_id"] = str(login_customer_id).replace("-", "")

    with open(YAML_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f, default_flow_style=False)

    # 2. Save to .env persistently
    env_content = f"""# Google Ads API Persistent Configuration
GOOGLE_ADS_CLIENT_ID={client_id}
GOOGLE_ADS_CLIENT_SECRET={client_secret}
GOOGLE_ADS_DEVELOPER_TOKEN={developer_token}
GOOGLE_ADS_REFRESH_TOKEN={credentials.refresh_token}
GOOGLE_ADS_CUSTOMER_ID={customer_id.replace('-', '')}
GOOGLE_ADS_CONFIGURATION_FILE_PATH=google-ads.yaml
"""
    if login_customer_id:
        env_content += f"GOOGLE_ADS_LOGIN_CUSTOMER_ID={login_customer_id.replace('-', '')}\n"

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(env_content)

    print(f"\n[SUCCESS] Credentials saved persistently to:", flush=True)
    print(f"          📄 {YAML_PATH}", flush=True)
    print(f"          📄 {ENV_PATH}", flush=True)
    print("\n[+] All keys and OAuth tokens are set up! You can now run bidirectional sync commands.", flush=True)

if __name__ == "__main__":
    main()
