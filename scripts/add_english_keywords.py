#!/usr/bin/env python3
"""
Populates clean English keywords into campaign 24086613335 (Problem Based Leads EN).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.ad_groups import AdGroupManager
from src.campaigns.models import KeywordSpec
from config.settings import DEFAULT_CUSTOMER_ID

def main():
    customer_id = DEFAULT_CUSTOMER_ID
    client = get_ads_client()
    ga_service = client.get_service("GoogleAdsService")
    ad_group_mgr = AdGroupManager(client, customer_id)

    # 1. Fetch Ad Groups for Campaign 24086613335
    query = """
        SELECT ad_group.id, ad_group.name, ad_group.resource_name
        FROM ad_group
        WHERE campaign.id = 24086613335
    """
    response = ga_service.search(customer_id=customer_id, query=query)
    ad_groups = {row.ad_group.name: row.ad_group.resource_name for row in response}

    print(f"[+] Found Ad Groups in campaign 24086613335: {list(ad_groups.keys())}")

    sleep_keywords = [
        KeywordSpec(text="child won't sleep", match_type="PHRASE"),
        KeywordSpec(text="toddler sleep problems", match_type="PHRASE"),
        KeywordSpec(text="child bedtime struggles", match_type="PHRASE"),
        KeywordSpec(text="child night waking help", match_type="PHRASE"),
        KeywordSpec(text="how to fix child sleep", match_type="PHRASE"),
        KeywordSpec(text="child refuses to sleep alone", match_type="PHRASE"),
        KeywordSpec(text="pediatric sleep consultant", match_type="PHRASE"),
        KeywordSpec(text="bedtime routine for children", match_type="PHRASE"),
        KeywordSpec(text="child taking hours to fall asleep", match_type="PHRASE"),
        KeywordSpec(text="toddler waking up at night", match_type="PHRASE"),
        KeywordSpec(text="sleep consultant for parents", match_type="PHRASE"),
        KeywordSpec(text="personalized child sleep plan", match_type="PHRASE"),
        KeywordSpec(text="child sleep support online", match_type="PHRASE"),
        KeywordSpec(text="child not sleeping through night", match_type="PHRASE"),
        KeywordSpec(text="toddler bedtime tantrums", match_type="PHRASE"),
        KeywordSpec(text="how to get child to sleep in own bed", match_type="PHRASE"),
        KeywordSpec(text="3 year old won't sleep", match_type="PHRASE"),
        KeywordSpec(text="4 year old bedtime refusal", match_type="PHRASE"),
        KeywordSpec(text="5 year old night waking", match_type="PHRASE"),
        KeywordSpec(text="parent sleep coaching children", match_type="PHRASE"),
        KeywordSpec(text="child sleep problems", match_type="EXACT"),
        KeywordSpec(text="how to get child to sleep", match_type="EXACT"),
        KeywordSpec(text="child won't sleep in own bed", match_type="EXACT"),
        KeywordSpec(text="toddler bedtime battles", match_type="EXACT"),
    ]

    meltdown_keywords = [
        KeywordSpec(text="child meltdown help", match_type="PHRASE"),
        KeywordSpec(text="how to handle child meltdowns", match_type="PHRASE"),
        KeywordSpec(text="child emotional outbursts", match_type="PHRASE"),
        KeywordSpec(text="severe child tantrums and meltdowns", match_type="PHRASE"),
        KeywordSpec(text="sensory overload in children", match_type="PHRASE"),
        KeywordSpec(text="child behavior specialist online", match_type="PHRASE"),
        KeywordSpec(text="how to calm a child in meltdown", match_type="PHRASE"),
        KeywordSpec(text="child meltdown triggers", match_type="PHRASE"),
        KeywordSpec(text="deescalating child meltdowns", match_type="PHRASE"),
        KeywordSpec(text="child losing emotional control", match_type="PHRASE"),
        KeywordSpec(text="behavior consultant for parents", match_type="PHRASE"),
        KeywordSpec(text="child screaming and crying uncontrollably", match_type="PHRASE"),
        KeywordSpec(text="sensory breakdown in child", match_type="PHRASE"),
        KeywordSpec(text="how to prevent child meltdowns", match_type="PHRASE"),
        KeywordSpec(text="behavioral support for child meltdowns", match_type="PHRASE"),
        KeywordSpec(text="child meltdown action plan", match_type="PHRASE"),
        KeywordSpec(text="toddler aggressive meltdowns", match_type="PHRASE"),
        KeywordSpec(text="4 year old severe tantrums", match_type="PHRASE"),
        KeywordSpec(text="5 year old emotional outbursts", match_type="PHRASE"),
        KeywordSpec(text="anger outbursts in children", match_type="PHRASE"),
        KeywordSpec(text="parent coaching for child behavior", match_type="PHRASE"),
        KeywordSpec(text="child meltdowns", match_type="EXACT"),
        KeywordSpec(text="how to stop child meltdown", match_type="EXACT"),
        KeywordSpec(text="child behavior specialist", match_type="EXACT"),
        KeywordSpec(text="help for child meltdowns", match_type="EXACT"),
        KeywordSpec(text="sensory meltdown help", match_type="EXACT"),
    ]

    if "Sleep Challenges" in ad_groups:
        print("[+] Adding keywords to 'Sleep Challenges'...")
        res = ad_group_mgr.add_keywords(ad_groups["Sleep Challenges"], sleep_keywords)
        print(f"    -> Added {len(res)} keywords successfully.")

    if "Meltdowns" in ad_groups:
        print("[+] Adding keywords to 'Meltdowns'...")
        res = ad_group_mgr.add_keywords(ad_groups["Meltdowns"], meltdown_keywords)
        print(f"    -> Added {len(res)} keywords successfully.")

if __name__ == "__main__":
    main()
