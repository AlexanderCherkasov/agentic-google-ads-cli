#!/usr/bin/env python3
"""
Creates and attaches Sitelinks and Callouts to campaign 24086613335 (Problem Based Leads EN).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from config.settings import DEFAULT_CUSTOMER_ID

def create_sitelink_asset(client, customer_id: str, text: str, desc1: str, desc2: str, url: str) -> str:
    asset_service = client.get_service("AssetService")
    asset_operation = client.get_type("AssetOperation")

    asset = asset_operation.create
    asset.name = f"Sitelink - {text}"
    asset.type_ = client.enums.AssetTypeEnum.SITELINK
    asset.sitelink_asset.link_text = text
    asset.sitelink_asset.description1 = desc1
    asset.sitelink_asset.description2 = desc2
    asset.final_urls.append(url)

    response = asset_service.mutate_assets(customer_id=customer_id, operations=[asset_operation])
    return response.results[0].resource_name

def create_callout_asset(client, customer_id: str, text: str) -> str:
    asset_service = client.get_service("AssetService")
    asset_operation = client.get_type("AssetOperation")

    asset = asset_operation.create
    asset.name = f"Callout - {text}"
    asset.type_ = client.enums.AssetTypeEnum.CALLOUT
    asset.callout_asset.callout_text = text

    response = asset_service.mutate_assets(customer_id=customer_id, operations=[asset_operation])
    return response.results[0].resource_name

def attach_assets_to_campaign(client, customer_id: str, campaign_id: str, asset_resources: list, field_type_name: str):
    campaign_asset_service = client.get_service("CampaignAssetService")
    campaign_service = client.get_service("CampaignService")

    operations = []
    for res_name in asset_resources:
        op = client.get_type("CampaignAssetOperation")
        ca = op.create
        ca.campaign = campaign_service.campaign_path(customer_id, campaign_id)
        ca.asset = res_name
        ca.field_type = getattr(client.enums.AssetFieldTypeEnum, field_type_name)
        operations.append(op)

    try:
        campaign_asset_service.mutate_campaign_assets(customer_id=customer_id, operations=operations)
        print(f"[+] Attached {len(operations)} {field_type_name} assets to campaign {campaign_id}")
    except Exception as ex:
        print(f"[!] Warning attaching assets: {ex}")

def main():
    customer_id = DEFAULT_CUSTOMER_ID
    campaign_id = "24086613335"
    client = get_ads_client()

    sitelinks_data = [
        {"text": "Child Sleep Support", "desc1": "Sleep plans & night wakings", "desc2": "Restful bedtime routines", "url": "https://guideddays.com/en-US/problems/sleep-challenges"},
        {"text": "Meltdown Support", "desc1": "Identify root triggers", "desc2": "No yelling or punishment", "url": "https://guideddays.com/en-US/problems/meltdowns"},
        {"text": "Child Aggression Help", "desc1": "Stop hitting & tantrums", "desc2": "Calming strategies for home", "url": "https://guideddays.com/en-US/problems/aggression"},
        {"text": "Screen Time Limits", "desc1": "End iPad & phone tantrums", "desc2": "Gentle screen detox plan", "url": "https://guideddays.com/en-US/problems/screen-time"},
        {"text": "Find a Specialist", "desc1": "Licensed behavior experts", "desc2": "Matched in 48 hours", "url": "https://guideddays.com/en-US/start-with-therapist"},
        {"text": "Explore Programs", "desc1": "Solutions for daily struggles", "desc2": "Select your family's needs", "url": "https://guideddays.com/en-US/problems"}
    ]

    callouts_data = [
        "Licensed Specialists",
        "2-Minute Assessment",
        "Zero Yelling",
        "Parent-Centered Care",
        "Autism & ADHD Support",
        "Individual Coaching"
    ]

    print("[+] Creating Sitelink Assets...")
    sitelink_resources = []
    for sl in sitelinks_data:
        res = create_sitelink_asset(client, customer_id, sl["text"], sl["desc1"], sl["desc2"], sl["url"])
        sitelink_resources.append(res)

    print("[+] Attaching Sitelinks to English Campaign...")
    attach_assets_to_campaign(client, customer_id, campaign_id, sitelink_resources, "SITELINK")

    print("[+] Creating Callout Assets...")
    callout_resources = []
    for co in callouts_data:
        res = create_callout_asset(client, customer_id, co)
        callout_resources.append(res)

    print("[+] Attaching Callouts to English Campaign...")
    attach_assets_to_campaign(client, customer_id, campaign_id, callout_resources, "CALLOUT")

    print("[SUCCESS] All Sitelinks and Callouts successfully created and attached to campaign!")

if __name__ == "__main__":
    main()
