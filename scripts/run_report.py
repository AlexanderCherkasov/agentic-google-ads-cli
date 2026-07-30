#!/usr/bin/env python3
"""
Exports analytics report to Markdown table or CSV file.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.reporting import ReportFetcher
from config.settings import DEFAULT_CUSTOMER_ID

def main():
    parser = argparse.ArgumentParser(description="Export Google Ads Performance Report")
    parser.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID, help="Google Ads Customer ID")
    parser.add_argument("--period", default="LAST_30_DAYS", help="Date range (e.g. LAST_30_DAYS, THIS_MONTH)")
    parser.add_argument("--format", choices=["markdown", "csv"], default="markdown", help="Output format")
    parser.add_argument("--output", help="Save to file path")
    args = parser.parse_args()

    if not args.customer_id:
        print("Error: Customer ID required.")
        sys.exit(1)

    print(f"[+] Fetching performance report for Customer ID: {args.customer_id} ({args.period})...")
    try:
        client = get_ads_client()
        fetcher = ReportFetcher(client, args.customer_id)
        df = fetcher.get_campaign_performance(start_date=args.period)

        if df.empty:
            print("[!] No campaign data found for this period.")
            return

        if args.format == "markdown":
            result = df.to_markdown(index=False)
        else:
            result = df.to_csv(index=False)

        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"[SUCCESS] Report saved to {args.output}")
        else:
            print("\n" + result)

    except Exception as ex:
        print(f"[ERROR] Failed to fetch report: {ex}")

if __name__ == "__main__":
    main()
