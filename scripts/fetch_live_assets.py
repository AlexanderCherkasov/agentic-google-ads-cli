#!/usr/bin/env python3
"""
Queries live Campaign Assets (Sitelinks, Callouts, Structured Snippets) from Google Ads API.
"""

import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from config.settings import DEFAULT_CUSTOMER_ID

def fetch_campaign_assets(client, customer_id: str, campaign_id: str) -> Dict[str, List]:
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign.id,
            campaign_asset.field_type,
            asset.id,
            asset.name,
            asset.type,
            asset.final_urls,
            asset.sitelink_asset.link_text,
            asset.sitelink_asset.description1,
            asset.sitelink_asset.description2,
            asset.callout_asset.callout_text,
            asset.structured_snippet_asset.header,
            asset.structured_snippet_asset.values
        FROM campaign_asset
        WHERE campaign.id = {campaign_id}
    """
    assets = {
        "sitelinks": [],
        "callouts": [],
        "snippets": []
    }
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            asset = row.asset
            
            if asset.type.name == "SITELINK":
                sl = asset.sitelink_asset
                assets["sitelinks"].append({
                    "text": sl.link_text,
                    "desc1": sl.description1,
                    "desc2": sl.description2,
                    "url": asset.final_urls[0] if asset.final_urls else ""
                })
            elif asset.type.name == "CALLOUT":
                assets["callouts"].append(asset.callout_asset.callout_text)
            elif asset.type.name == "STRUCTURED_SNIPPET":
                ss = asset.structured_snippet_asset
                assets["snippets"].append({
                    "header": ss.header,
                    "values": list(ss.values)
                })
    except Exception as ex:
        print(f"[!] Exception fetching campaign assets for {campaign_id}: {ex}")
    return assets

def main():
    customer_id = DEFAULT_CUSTOMER_ID
    client = get_ads_client()
    for camp_id in ["24065370718", "24086613335"]:
        print(f"\n[+] Fetching live campaign assets for Campaign ID: {camp_id}...")
        assets = fetch_campaign_assets(client, customer_id, camp_id)
        print(f"    - Sitelinks ({len(assets['sitelinks'])}): {assets['sitelinks']}")
        print(f"    - Callouts ({len(assets['callouts'])}): {assets['callouts']}")
        print(f"    - Snippets ({len(assets['snippets'])}): {assets['snippets']}")

if __name__ == "__main__":
    main()
