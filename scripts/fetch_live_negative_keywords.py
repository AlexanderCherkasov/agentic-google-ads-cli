#!/usr/bin/env python3
"""
Queries exact live negative keywords from Google Ads API for campaign 24065370718 and 24086613335.
"""

import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from config.settings import DEFAULT_CUSTOMER_ID

def fetch_campaign_negative_keywords(client, customer_id: str, campaign_id: str) -> List[Dict[str, str]]:
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign_criterion.keyword.text,
            campaign_criterion.keyword.match_type
        FROM campaign_criterion
        WHERE campaign.id = {campaign_id}
          AND campaign_criterion.type = 'KEYWORD'
          AND campaign_criterion.negative = TRUE
    """
    results = []
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            kw = row.campaign_criterion.keyword
            results.append({
                "text": kw.text,
                "match_type": kw.match_type.name if kw.match_type else "EXACT"
            })
    except Exception as ex:
        print(f"[!] Exception fetching campaign negatives: {ex}")
    return results

def fetch_ad_group_negative_keywords(client, customer_id: str, ad_group_id: str) -> List[Dict[str, str]]:
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type
        FROM ad_group_criterion
        WHERE ad_group.id = {ad_group_id}
          AND ad_group_criterion.type = 'KEYWORD'
          AND ad_group_criterion.negative = TRUE
    """
    results = []
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            kw = row.ad_group_criterion.keyword
            results.append({
                "text": kw.text,
                "match_type": kw.match_type.name if kw.match_type else "EXACT"
            })
    except Exception as ex:
        print(f"[!] Exception fetching ad group negatives: {ex}")
    return results

def main():
    customer_id = DEFAULT_CUSTOMER_ID
    client = get_ads_client()
    
    for camp_id in ["24065370718", "24086613335"]:
        print(f"\n[+] Fetching live campaign-level negative keywords for Campaign ID: {camp_id}...")
        negatives = fetch_campaign_negative_keywords(client, customer_id, camp_id)
        print(f"    Found {len(negatives)} negative keywords:")
        for neg in negatives:
            print(f"    - [{neg['match_type']}] {neg['text']}")

if __name__ == "__main__":
    main()
