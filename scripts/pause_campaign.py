#!/usr/bin/env python3
"""
Quick utility script to change status (PAUSED / ENABLED / REMOVED) of a campaign.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.campaigns import CampaignManager
from config.settings import DEFAULT_CUSTOMER_ID

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/pause_campaign.py <campaign_id> <STATUS> [customer_id]")
        print("Status options: PAUSED, ENABLED, REMOVED")
        sys.exit(1)

    campaign_id = sys.argv[1]
    status = sys.argv[2].upper()
    customer_id = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_CUSTOMER_ID

    if not customer_id:
        print("Error: Customer ID required.")
        sys.exit(1)

    print(f"[+] Updating Campaign {campaign_id} status to {status}...")
    try:
        client = get_ads_client()
        mgr = CampaignManager(client, customer_id)
        mgr.update_campaign_status(campaign_id, status)
        print(f"[SUCCESS] Campaign {campaign_id} status updated to {status}.")
    except Exception as ex:
        print(f"[ERROR] Failed to update status: {ex}")

if __name__ == "__main__":
    main()
