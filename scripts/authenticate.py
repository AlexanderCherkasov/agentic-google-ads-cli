#!/usr/bin/env python3
"""
OAuth2 Helper Script for Google Ads API.
This script performs local webserver OAuth2 flow to retrieve a Refresh Token.

Prerequisites:
- Client ID and Client Secret from Google Cloud Console (Desktop application flow).
"""

import sys
import argparse
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Ads API Scope
SCOPES = ["https://www.googleapis.com/auth/adwords"]

def main():
    parser = argparse.ArgumentParser(description="Generate Refresh Token for Google Ads API.")
    parser.add_argument("--client_id", required=True, help="Google Cloud OAuth2 Client ID")
    parser.add_argument("--client_secret", required=True, help="Google Cloud OAuth2 Client Secret")
    args = parser.parse_args()

    client_config = {
        "installed": {
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    
    print("\n--- GOOGLE ADS OAUTH2 AUTHORIZATION ---")
    print("Opening browser for authorization...")
    credentials = flow.run_local_server(port=8080, prompt="consent")

    print("\nSUCCESS!")
    print("Add the following lines to your google-ads.yaml file:\n")
    print(f'client_id: "{args.client_id}"')
    print(f'client_secret: "{args.client_secret}"')
    print(f'refresh_token: "{credentials.refresh_token}"')

if __name__ == "__main__":
    main()
