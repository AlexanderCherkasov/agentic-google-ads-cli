#!/usr/bin/env python3
"""
Account Setup Helper.
Helps configure credentials and run initial OAuth authorization.
"""

import sys
import os
from pathlib import Path

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def main():
    print("=========================================================")
    print("         Google Ads Account Setup Helper                 ")
    print("=========================================================\n")

    env_file = Path(".env")
    if not env_file.exists():
        print("[+] Creating .env file...")
        customer_id = input("Enter Customer ID (e.g., 1234567890): ").strip()
        env_content = f"GOOGLE_ADS_CUSTOMER_ID={customer_id}\nGOOGLE_ADS_CONFIGURATION_FILE_PATH=google-ads.yaml\n"
        env_file.write_text(env_content, encoding="utf-8")
        print("[SUCCESS] .env file created.")

    print("\n[+] Next steps for OAuth2 setup:")
    print("1. Ensure you have your Client ID, Client Secret, and Developer Token.")
    print("2. Run the token generator command:")
    print("\n   ./bin/ads-cli auth --client_id YOUR_CLIENT_ID --client_secret YOUR_CLIENT_SECRET --developer_token YOUR_DEV_TOKEN\n")
    print("3. Log in with your Google Ads account in the opened browser window.")
    print("4. Perform bidirectional synchronization:")
    print("   - Export live campaigns: ./bin/ads-cli export")
    print("   - Compare diffs:          ./bin/ads-cli diff")
    print("   - Apply changes:          ./bin/ads-cli apply\n")

if __name__ == "__main__":
    main()
