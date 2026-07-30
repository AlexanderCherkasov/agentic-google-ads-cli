#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.campaigns import CampaignManager
from config.settings import DEFAULT_CUSTOMER_ID

def main():
    customer_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CUSTOMER_ID
    if not customer_id:
        print("Error: Customer ID is required. Pass it as CLI argument or set GOOGLE_ADS_CUSTOMER_ID in .env")
        sys.exit(1)

    print(f"Connecting to Google Ads for Customer ID: {customer_id}...")
    try:
        client = get_ads_client()
        manager = CampaignManager(client, customer_id)
        campaigns = manager.list_campaigns()
        
        print(f"\nFound {len(campaigns)} campaigns:")
        print("-" * 75)
        print(f"{'ID':<15} | {'NAME':<30} | {'STATUS':<10} | {'CHANNEL':<10}")
        print("-" * 75)
        for c in campaigns:
            print(f"{c.id:<15} | {c.name:<30} | {c.status:<10} | {c.advertising_channel_type:<10}")
        print("-" * 75)
    except Exception as ex:
        print(f"Error executing list_campaigns: {ex}")

if __name__ == "__main__":
    main()
