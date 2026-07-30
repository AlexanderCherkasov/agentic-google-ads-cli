#!/usr/bin/env python3
"""
Bidirectional Synchronization Tool for Google Ads API and Markdown Specifications.

Usage:
    # 1. Export live campaign to Markdown
    python scripts/bidirectional_sync.py export --campaign_id <ID> --output campaign_specs/live_campaign.md

    # 2. Compare local Markdown spec vs live Google Ads state
    python scripts/bidirectional_sync.py diff campaign_specs/search_campaign_demo.md

    # 3. Apply local Markdown changes to Google Ads
    python scripts/bidirectional_sync.py apply campaign_specs/search_campaign_demo.md
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.parsers import MarkdownSpecParser
from src.sync import CampaignExporter, CampaignDiffEngine
from src.campaigns import CampaignManager, CampaignCreate
from src.ad_groups import AdGroupManager
from config.settings import DEFAULT_CUSTOMER_ID

def handle_export(args):
    client = get_ads_client()
    exporter = CampaignExporter(client, args.customer_id)
    spec = exporter.export_campaign(args.campaign_id)
    md_content = exporter.spec_to_markdown(spec)
    output_path = args.output or f"campaign_specs/{spec.name.lower().replace(' ', '_')}.md"
    Path(output_path).write_text(md_content, encoding="utf-8")
    print(f"[SUCCESS] Exported campaign '{spec.name}' to: {output_path}")

def handle_diff(args):
    local_spec = MarkdownSpecParser.parse_file(args.spec_file)
    client = get_ads_client()
    exporter = CampaignExporter(client, args.customer_id)
    
    # Try to find campaign by name
    camp_mgr = CampaignManager(client, args.customer_id)
    live_campaigns = camp_mgr.list_campaigns()
    target_camp = next((c for c in live_campaigns if c.name == local_spec.name), None)

    if not target_camp:
        print(f"[!] Campaign '{local_spec.name}' does not exist yet in Google Ads.")
        print(f"[+] 'apply' will create a NEW campaign with {len(local_spec.ad_groups)} Ad Groups.")
        return

    remote_spec = exporter.export_campaign(target_camp.id)
    diffs = CampaignDiffEngine.calculate_diff(local_spec, remote_spec)
    print("\n" + CampaignDiffEngine.format_diff_report(diffs))

def handle_apply(args):
    local_spec = MarkdownSpecParser.parse_file(args.spec_file)
    client = get_ads_client()
    camp_mgr = CampaignManager(client, args.customer_id)
    ad_group_mgr = AdGroupManager(client, args.customer_id)

    print(f"[+] Applying Markdown spec '{local_spec.name}' to Google Ads...")
    
    # Check if campaign already exists
    live_campaigns = camp_mgr.list_campaigns()
    target_camp = next((c for c in live_campaigns if c.name == local_spec.name), None)

    if not target_camp:
        # Create campaign
        budget_micros = int(local_spec.daily_budget_usd * 1_000_000)
        c_create = CampaignCreate(
            name=local_spec.name,
            budget_amount_micros=budget_micros,
            advertising_channel_type=local_spec.channel,
            status=local_spec.status
        )
        camp_resource = camp_mgr.create_campaign(c_create)
        print(f"    [+] Created Campaign: {camp_resource}")

        for ag in local_spec.ad_groups:
            cpc_micros = int(ag.max_cpc_usd * 1_000_000)
            ag_res = ad_group_mgr.create_ad_group(camp_resource, ag.name, cpc_micros)
            if ag.ad:
                ad_group_mgr.create_responsive_search_ad(ag_res, ag.ad)
            if ag.keywords:
                ad_group_mgr.add_keywords(ag_res, ag.keywords)
    else:
        print(f"    [+] Campaign ID {target_camp.id} already exists.")
        # Perform updates
        if target_camp.status != local_spec.status:
            camp_mgr.update_campaign_status(target_camp.id, local_spec.status)

    print(f"\n[SUCCESS] Synchronization finished for '{local_spec.name}'.")

def main():
    parser = argparse.ArgumentParser(description="Bidirectional Sync CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Export subcommand
    export_p = subparsers.add_parser("export", help="Export live campaign to Markdown spec")
    export_p.add_argument("--campaign_id", required=True, help="Campaign ID")
    export_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID)
    export_p.add_argument("--output", help="Output .md file path")
    export_p.set_defaults(func=handle_export)

    # Diff subcommand
    diff_p = subparsers.add_parser("diff", help="Diff local Markdown spec against live campaign")
    diff_p.add_argument("spec_file", help="Path to Markdown spec file")
    diff_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID)
    diff_p.set_defaults(func=handle_diff)

    # Apply subcommand
    apply_p = subparsers.add_parser("apply", help="Apply local Markdown spec to live Google Ads")
    apply_p.add_argument("spec_file", help="Path to Markdown spec file")
    apply_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID)
    apply_p.set_defaults(func=handle_apply)

    args = parser.parse_args()
    if not args.customer_id:
        print("[ERROR] Customer ID required. Set GOOGLE_ADS_CUSTOMER_ID in .env or pass --customer_id")
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()
