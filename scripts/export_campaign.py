#!/usr/bin/env python3
"""
Exports a live Google Ads campaign into a human-readable Markdown specification file.

Usage:
    python scripts/export_campaign.py --campaign_id 123456789 --output campaign_specs/exported_campaign.md
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.sync import CampaignExporter
from config.settings import DEFAULT_CUSTOMER_ID

def main():
    parser = argparse.ArgumentParser(description="Export live Google Ads campaign to Markdown spec")
    parser.add_argument("--campaign_id", required=True, help="Campaign ID to export")
    parser.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID, help="Customer ID")
    parser.add_argument("--output", help="Path to save Markdown file (default: campaign_specs/<name>.md)")
    args = parser.parse_args()

    if not args.customer_id:
        print("[ERROR] Customer ID is required. Pass --customer_id or set GOOGLE_ADS_CUSTOMER_ID in .env")
        sys.exit(1)

    print(f"[+] Connecting to Google Ads API (Customer ID: {args.customer_id})...")
    try:
        client = get_ads_client()
        exporter = CampaignExporter(client, args.customer_id)

        print(f"[+] Exporting campaign ID: {args.campaign_id}...")
        spec = exporter.export_campaign(args.campaign_id)

        md_content = exporter.spec_to_markdown(spec)

        output_path = args.output or f"campaign_specs/{spec.name.lower().replace(' ', '_')}.md"
        Path(output_path).write_text(md_content, encoding="utf-8")

        print(f"\n[SUCCESS] Exported campaign '{spec.name}' into Markdown specification:")
        print(f"          📄 {output_path}")

    except Exception as ex:
        print(f"[ERROR] Failed to export campaign: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    main()
