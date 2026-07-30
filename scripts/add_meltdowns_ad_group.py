#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.ad_groups import AdGroupManager
from src.campaigns.models import KeywordSpec

def main():
    client = get_ads_client()
    customer_id = "7623719666"
    ad_group_resource = "customers/7623719666/adGroups/194070630650"
    ad_group_mgr = AdGroupManager(client, customer_id)

    keywords = [
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

    print(f"[+] Adding {len(keywords)} Keywords to existing 'Meltdowns' Ad Group ({ad_group_resource})...")
    kw_res = ad_group_mgr.add_keywords(ad_group_resource, keywords)
    print(f"[SUCCESS] Added {len(kw_res)} keywords successfully.")

if __name__ == "__main__":
    main()
