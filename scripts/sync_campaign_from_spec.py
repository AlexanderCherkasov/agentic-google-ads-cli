#!/usr/bin/env python3
"""
Syncs/Creates a Google Ads Campaign directly from a Markdown specification file.

Usage:
    python scripts/sync_campaign_from_spec.py campaign_specs/search_campaign_demo.md
"""

import sys
from pathlib import Path

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.parsers import MarkdownSpecParser
from src.campaigns import CampaignManager, CampaignCreate
from src.ad_groups import AdGroupManager
from config.settings import DEFAULT_CUSTOMER_ID

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/sync_campaign_from_spec.py <path_to_markdown_spec>")
        print("Example: python scripts/sync_campaign_from_spec.py campaign_specs/search_campaign_demo.md")
        sys.exit(1)

    spec_path = sys.argv[1]
    customer_id = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CUSTOMER_ID

    print(f"[+] Loading Markdown Campaign Specification: {spec_path}")
    spec = MarkdownSpecParser.parse_file(spec_path)

    print(f"\n[+] Parsed Campaign Spec:")
    print(f"    - Name: {spec.name}")
    print(f"    - Daily Budget: ${spec.daily_budget_usd:.2f}")
    print(f"    - Channel: {spec.channel}")
    print(f"    - Ad Groups: {len(spec.ad_groups)}")

    if not customer_id:
        print("\n[!] Error: Customer ID required. Set GOOGLE_ADS_CUSTOMER_ID in .env or pass as argument.")
        sys.exit(1)

    print(f"\n[+] Initializing Google Ads API for Customer ID: {customer_id}...")
    try:
        client = get_ads_client()
        campaign_mgr = CampaignManager(client, customer_id)
        ad_group_mgr = AdGroupManager(client, customer_id)

        # 1. Create Campaign & Budget
        budget_micros = int(spec.daily_budget_usd * 1_000_000)
        camp_create = CampaignCreate(
            name=spec.name,
            budget_amount_micros=budget_micros,
            advertising_channel_type=spec.channel,
            status=spec.status
        )

        print("[+] Creating Campaign and Budget in Google Ads...")
        campaign_resource = campaign_mgr.create_campaign(camp_create)
        print(f"    -> Created Campaign Resource: {campaign_resource}")

        # 2. Create Ad Groups, RSAs, Keywords
        for ag in spec.ad_groups:
            cpc_micros = int(ag.max_cpc_usd * 1_000_000)
            print(f"\n[+] Creating Ad Group: '{ag.name}' (Max CPC: ${ag.max_cpc_usd:.2f})...")
            ag_resource = ad_group_mgr.create_ad_group(campaign_resource, ag.name, cpc_micros)

            if ag.ad:
                print("    [+] Creating Responsive Search Ad...")
                rsa_resource = ad_group_mgr.create_responsive_search_ad(ag_resource, ag.ad)
                print(f"        -> RSA Resource: {rsa_resource}")

            if ag.keywords:
                print(f"    [+] Adding {len(ag.keywords)} Keywords...")
                kw_resources = ad_group_mgr.add_keywords(ag_resource, ag.keywords)
                print(f"        -> Added {len(kw_resources)} keywords successfully.")

        print(f"\n[SUCCESS] Campaign '{spec.name}' created and synchronized from Markdown specification!")

    except Exception as ex:
        print(f"\n[ERROR] Failed to sync campaign: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    main()
