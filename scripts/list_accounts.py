#!/usr/bin/env python3
"""
Queries accessible Google Ads accounts, filters ONLY accounts with currency USD,
and retrieves all campaign information.
"""

import sys
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.campaigns import CampaignManager
from src.sync import CampaignExporter

def get_accessible_customers(client) -> List[str]:
    customer_service = client.get_service("CustomerService")
    response = customer_service.list_accessible_customers()
    resource_names = response.resource_names
    customer_ids = [res.split("/")[-1] for res in resource_names]
    return customer_ids

def get_account_details(client, customer_id: str) -> Dict[str, str]:
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
            customer.id,
            customer.descriptive_name,
            customer.currency_code,
            customer.time_zone
        FROM customer
        LIMIT 1
    """
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            cust = row.customer
            return {
                "id": str(cust.id),
                "name": cust.descriptive_name or "Unnamed Account",
                "currency": cust.currency_code,
                "time_zone": cust.time_zone
            }
    except Exception as ex:
        print(f"[!] Warning: Could not fetch details for account {customer_id}: {ex}")
    return None

def main():
    print("=========================================================")
    print("      GOOGLE ADS USD ACCOUNT & CAMPAIGN INSPECTOR        ")
    print("=========================================================\n")

    try:
        client = get_ads_client()
        print("[+] Fetching accessible Google Ads accounts...")
        customer_ids = get_accessible_customers(client)
        print(f"[+] Found {len(customer_ids)} accessible customer accounts.")

        usd_accounts = []
        for cid in customer_ids:
            details = get_account_details(client, cid)
            if details and details["currency"] == "USD":
                usd_accounts.append(details)

        print(f"\n[+] Accounts with currency USD ({len(usd_accounts)}):")
        print("-" * 65)
        print(f"{'ACCOUNT ID':<15} | {'NAME':<30} | {'CURRENCY':<8}")
        print("-" * 65)
        for acc in usd_accounts:
            print(f"{acc['id']:<15} | {acc['name']:<30} | {acc['currency']:<8}")
        print("-" * 65)

        if not usd_accounts:
            print("\n[!] No USD accounts found among accessible customers.")
            return

        # Gather campaign details for USD accounts
        for acc in usd_accounts:
            cid = acc["id"]
            print(f"\n=========================================================")
            print(f"  CAMPAIGNS FOR USD ACCOUNT: {acc['name']} ({cid})")
            print(f"=========================================================")
            
            mgr = CampaignManager(client, cid)
            campaigns = mgr.list_campaigns()
            
            if not campaigns:
                print("   No campaigns found in this account.")
                continue

            exporter = CampaignExporter(client, cid)
            for c in campaigns:
                spec = exporter.export_campaign(c.id)
                md_content = exporter.spec_to_markdown(spec)
                out_path = f"campaign_specs/usd_{cid}_{spec.name.lower().replace(' ', '_')}.md"
                Path(out_path).write_text(md_content, encoding="utf-8")
                print(f"   📄 Exported Campaign '{spec.name}' -> {out_path}")

    except Exception as ex:
        print(f"\n[ERROR] Failed to query accounts: {ex}")
        print("Ensure GOOGLE_ADS_DEVELOPER_TOKEN and GOOGLE_ADS_CUSTOMER_ID are set in .env")

if __name__ == "__main__":
    main()
