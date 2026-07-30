#!/usr/bin/env python3
"""
Unified Bidirectional Synchronization Tool for Modular Folder Structures.

Usage:
    # 1. Export entire account to modular specs directory
    python scripts/modular_sync.py export --customer_id <CUSTOMER_ID>

    # 2. Compare modular specs directory vs live Google Ads state
    python scripts/modular_sync.py diff campaign_specs/account_<CUSTOMER_ID>/

    # 3. Apply changes from modular specs directory to Google Ads
    python scripts/modular_sync.py apply campaign_specs/account_<CUSTOMER_ID>/
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.sync.modular_sync import ModularSpecParser, slugify
from src.sync.exporter import CampaignExporter
from src.sync.diff_engine import CampaignDiffEngine
from src.campaigns import CampaignManager, CampaignCreate
from src.ad_groups import AdGroupManager
from scripts.export_modular_specs import export_modular_campaign, fetch_live_campaign_negatives
from scripts.sync_negative_keywords import add_campaign_negative_keywords
from config.settings import DEFAULT_CUSTOMER_ID

def handle_export(args):
    customer_id = args.customer_id or DEFAULT_CUSTOMER_ID
    client = get_ads_client()
    exporter = CampaignExporter(client, customer_id)
    camp_mgr = CampaignManager(client, customer_id)

    account_dir = Path(f"campaign_specs/account_{customer_id}")
    account_dir.mkdir(parents=True, exist_ok=True)

    print(f"[+] EXPORTING live Google Ads state to modular folders: {account_dir}")
    campaigns = camp_mgr.list_campaigns()

    root_readme = f"""# Account: {customer_id}

## 📊 Overview
- **Customer ID**: `{customer_id}`
- **Total Campaigns**: {len(campaigns)}

## 📁 Campaigns Hierarchy
"""

    for c in campaigns:
        c_slug = slugify(c.name)
        c_dir = account_dir / c_slug
        print(f"  [+] Exporting campaign '{c.name}' (ID: {c.id})...")
        export_modular_campaign(client, exporter, c.id, c_dir, customer_id)
        root_readme += f"- [{c.name}](file://{c_dir}/README.md) (ID: `{c.id}`, Status: `{c.status}`)\n"

    (account_dir / "README.md").write_text(root_readme, encoding="utf-8")
    print(f"[SUCCESS] Export finished for all {len(campaigns)} campaigns in: {account_dir}")

def handle_diff(args):
    account_dir = Path(args.dir_path)
    if not account_dir.exists():
        print(f"[ERROR] Directory does not exist: {account_dir}")
        sys.exit(1)

    customer_id = args.customer_id or DEFAULT_CUSTOMER_ID
    client = get_ads_client()
    exporter = CampaignExporter(client, customer_id)
    camp_mgr = CampaignManager(client, customer_id)

    live_campaigns = camp_mgr.list_campaigns()
    live_camp_map = {c.name: c for c in live_campaigns}

    print(f"\n=========================================================")
    print(f"  MODULAR BIDIRECTIONAL DIFF REPORT ({account_dir})")
    print(f"=========================================================\n")

    for camp_folder in sorted(account_dir.iterdir()):
        if camp_folder.is_dir() and (camp_folder / "README.md").exists():
            parsed = ModularSpecParser.parse_campaign_dir(camp_folder)
            local_spec = parsed["campaign_spec"]
            local_negs = parsed["negative_keywords"]

            print(f"\n📌 Campaign: '{local_spec.name}'")
            print("-" * 60)

            if local_spec.name not in live_camp_map:
                print(f"  [+] NEW CAMPAIGN (Will be created in Google Ads)")
                print(f"      - Budget: ${local_spec.daily_budget_usd:.2f}")
                print(f"      - Status: {local_spec.status}")
                print(f"      - Ad Groups ({len(local_spec.ad_groups)}): {[ag.name for ag in local_spec.ad_groups]}")
                print(f"      - Negative Keywords ({len(local_negs)})")
            else:
                target_camp = live_camp_map[local_spec.name]
                remote_spec = exporter.export_campaign(target_camp.id)
                diffs = CampaignDiffEngine.calculate_diff(local_spec, remote_spec)

                # Check negative keywords diff
                live_negs = fetch_live_campaign_negatives(client, customer_id, target_camp.id)
                live_neg_set = {(n["text"].lower(), n["match_type"].upper()) for n in live_negs}
                local_neg_set = {(n["text"].lower(), n["match_type"].upper()) for n in local_negs}

                new_negs = [n for n in local_negs if (n["text"].lower(), n["match_type"].upper()) not in live_neg_set]

                if not diffs["has_changes"] and not new_negs:
                    print("  ✅ Fully synchronized with Google Ads!")
                else:
                    print(CampaignDiffEngine.format_diff_report(diffs))
                    if new_negs:
                        print(f"  🛑 New Negative Keywords to add ({len(new_negs)}):")
                        for n in new_negs:
                            print(f"     + [{n['match_type']}] {n['text']}")

def handle_apply(args):
    account_dir = Path(args.dir_path)
    if not account_dir.exists():
        print(f"[ERROR] Directory does not exist: {account_dir}")
        sys.exit(1)

    customer_id = args.customer_id or DEFAULT_CUSTOMER_ID
    client = get_ads_client()
    camp_mgr = CampaignManager(client, customer_id)
    ad_group_mgr = AdGroupManager(client, customer_id)

    live_campaigns = camp_mgr.list_campaigns()
    live_camp_map = {c.name: c for c in live_campaigns}

    print(f"\n[+] APPLYING modular folder specifications to Google Ads...")

    for camp_folder in sorted(account_dir.iterdir()):
        if camp_folder.is_dir() and (camp_folder / "README.md").exists():
            parsed = ModularSpecParser.parse_campaign_dir(camp_folder)
            local_spec = parsed["campaign_spec"]
            local_negs = parsed["negative_keywords"]

            print(f"\n[+] Processing Campaign: '{local_spec.name}'...")

            if local_spec.name not in live_camp_map:
                # Create New Campaign
                budget_micros = int(local_spec.daily_budget_usd * 1_000_000)
                c_create = CampaignCreate(
                    name=local_spec.name,
                    budget_amount_micros=budget_micros,
                    advertising_channel_type=local_spec.channel,
                    status=local_spec.status
                )
                camp_res = camp_mgr.create_campaign(c_create)
                print(f"    [+] Created Campaign Resource: {camp_res}")
                camp_id = camp_res.split("/")[-1]
            else:
                target_camp = live_camp_map[local_spec.name]
                camp_id = target_camp.id
                camp_res = f"customers/{customer_id}/campaigns/{camp_id}"
                print(f"    [+] Campaign ID {camp_id} already exists.")
                
                # Check status update
                if target_camp.status != local_spec.status:
                    camp_mgr.update_campaign_status(camp_id, local_spec.status)
                    print(f"        -> Status updated to {local_spec.status}")

            # Sync Negative Keywords
            if local_negs:
                live_negs = fetch_live_campaign_negatives(client, customer_id, camp_id)
                live_neg_set = {(n["text"].lower(), n["match_type"].upper()) for n in live_negs}
                missing_negs = [n for n in local_negs if (n["text"].lower(), n["match_type"].upper()) not in live_neg_set]
                
                if missing_negs:
                    print(f"    [+] Adding {len(missing_negs)} missing negative keywords...")
                    add_campaign_negative_keywords(client, customer_id, camp_id, missing_negs)

            # Sync Ad Groups & RSAs & Positive Keywords
            ga_service = client.get_service("GoogleAdsService")
            ag_query = f"SELECT ad_group.id, ad_group.name, ad_group.resource_name FROM ad_group WHERE campaign.id = {camp_id}"
            ag_resp = ga_service.search(customer_id=customer_id, query=ag_query)
            existing_ag_map = {row.ad_group.name: row.ad_group.resource_name for row in ag_resp}

            for ag in local_spec.ad_groups:
                cpc_micros = int(ag.max_cpc_usd * 1_000_000)
                if ag.name not in existing_ag_map:
                    print(f"    [+] Creating Ad Group '{ag.name}'...")
                    ag_res = ad_group_mgr.create_ad_group(camp_res, ag.name, cpc_micros)
                    if ag.ad:
                        ad_group_mgr.create_responsive_search_ad(ag_res, ag.ad)
                else:
                    ag_res = existing_ag_map[ag.name]

                if ag.keywords:
                    ad_group_mgr.add_keywords(ag_res, ag.keywords)

    print(f"\n[SUCCESS] Modular Synchronization completed for: {account_dir}")

def main():
    parser = argparse.ArgumentParser(description="Modular Bidirectional Sync Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Export
    exp_p = subparsers.add_parser("export", help="Export account to modular directory")
    exp_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID)
    exp_p.set_defaults(func=handle_export)

    # Diff
    diff_p = subparsers.add_parser("diff", help="Diff modular folder specs vs live Google Ads state")
    diff_p.add_argument("dir_path", help="Path to modular folder specs")
    diff_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID)
    diff_p.set_defaults(func=handle_diff)

    # Apply
    app_p = subparsers.add_parser("apply", help="Apply modular folder specs to live Google Ads")
    app_p.add_argument("dir_path", help="Path to modular folder specs")
    app_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID)
    app_p.set_defaults(func=handle_apply)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
