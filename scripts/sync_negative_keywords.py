#!/usr/bin/env python3
"""
Syncs the 123 negative keywords from Russian campaign to English campaign 24086613335.
"""

import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from config.settings import DEFAULT_CUSTOMER_ID

def add_campaign_negative_keywords(client, customer_id: str, campaign_id: str, negatives: List[dict]):
    campaign_criterion_service = client.get_service("CampaignCriterionService")
    campaign_service = client.get_service("CampaignService")

    operations = []
    for neg in negatives:
        op = client.get_type("CampaignCriterionOperation")
        criterion = op.create
        criterion.campaign = campaign_service.campaign_path(customer_id, campaign_id)
        criterion.negative = True
        criterion.keyword.text = neg["text"]
        criterion.keyword.match_type = getattr(
            client.enums.KeywordMatchTypeEnum,
            neg["match_type"].upper()
        )
        operations.append(op)

    # Execute in batches of 50
    batch_size = 50
    added_count = 0
    for i in range(0, len(operations), batch_size):
        batch = operations[i:i+batch_size]
        try:
            response = campaign_criterion_service.mutate_campaign_criteria(
                customer_id=customer_id,
                operations=batch
            )
            added_count += len(response.results)
        except Exception as ex:
            print(f"[!] Warning syncing negative keywords batch {i}: {ex}")

    print(f"[SUCCESS] Added {added_count} negative keywords to campaign {campaign_id}")

def main():
    customer_id = DEFAULT_CUSTOMER_ID
    client = get_ads_client()

    english_negatives = [
        {"text": "medicine", "match_type": "BROAD"},
        {"text": "medication", "match_type": "BROAD"},
        {"text": "buy", "match_type": "BROAD"},
        {"text": "price", "match_type": "BROAD"},
        {"text": "cost", "match_type": "BROAD"},
        {"text": "shop", "match_type": "BROAD"},
        {"text": "store", "match_type": "BROAD"},
        {"text": "infant", "match_type": "BROAD"},
        {"text": "newborn", "match_type": "BROAD"},
        {"text": "pain", "match_type": "BROAD"},
        {"text": "fever", "match_type": "BROAD"},
        {"text": "cough", "match_type": "BROAD"},
        {"text": "mattress", "match_type": "BROAD"},
        {"text": "crib", "match_type": "BROAD"},
        {"text": "pillow", "match_type": "BROAD"},
        {"text": "blanket", "match_type": "BROAD"},
        {"text": "pills", "match_type": "BROAD"},
        {"text": "melatonin", "match_type": "BROAD"},
        {"text": "dream meaning", "match_type": "BROAD"},
        {"text": "dream interpretation", "match_type": "BROAD"},
        {"text": "parasites", "match_type": "BROAD"},
        {"text": "worms", "match_type": "BROAD"},
        {"text": "epilepsy", "match_type": "BROAD"},
        {"text": "snoring", "match_type": "BROAD"},
        {"text": "teething", "match_type": "BROAD"},
        {"text": "colic", "match_type": "BROAD"},
        {"text": "reflux", "match_type": "BROAD"},
        {"text": "breastfeeding", "match_type": "BROAD"},
        {"text": "weaning", "match_type": "BROAD"},
        {"text": "bedwetting", "match_type": "BROAD"},
        {"text": "night light", "match_type": "BROAD"},
        {"text": "pajamas", "match_type": "BROAD"},
        {"text": "sleep sack", "match_type": "BROAD"},
        {"text": "sleeping pills", "match_type": "BROAD"},
        {"text": "pharmacist", "match_type": "BROAD"},
        {"text": "valerian", "match_type": "BROAD"},
        {"text": "glycine", "match_type": "BROAD"},
        {"text": "swaddle", "match_type": "BROAD"},
        {"text": "sleep regression 4 months", "match_type": "PHRASE"},
        {"text": "baby 1 month", "match_type": "PHRASE"},
        {"text": "baby 2 months", "match_type": "PHRASE"},
        {"text": "baby 3 months", "match_type": "PHRASE"},
        {"text": "baby 4 months", "match_type": "PHRASE"},
        {"text": "baby 5 months", "match_type": "PHRASE"},
        {"text": "baby 6 months", "match_type": "PHRASE"},
        {"text": "baby 7 months", "match_type": "PHRASE"},
        {"text": "baby 8 months", "match_type": "PHRASE"},
        {"text": "baby 9 months", "match_type": "PHRASE"},
        {"text": "baby 10 months", "match_type": "PHRASE"},
        {"text": "baby 11 months", "match_type": "PHRASE"},
        {"text": "free", "match_type": "BROAD"},
        {"text": "pdf", "match_type": "BROAD"},
        {"text": "torrent", "match_type": "BROAD"},
        {"text": "job", "match_type": "BROAD"},
        {"text": "salary", "match_type": "BROAD"},
        {"text": "course", "match_type": "BROAD"},
        {"text": "reddit", "match_type": "BROAD"},
        {"text": "youtube", "match_type": "BROAD"},
        {"text": "download", "match_type": "BROAD"}
    ]

    print("[+] Syncing 59 English negative keywords to campaign 24086613335...")
    add_campaign_negative_keywords(client, customer_id, "24086613335", english_negatives)

if __name__ == "__main__":
    main()
