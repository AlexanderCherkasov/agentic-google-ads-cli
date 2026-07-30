#!/usr/bin/env python3
"""
Google Ads Automation & Bidirectional Sync Engine CLI.

Usage:
    ads-cli auth       # Run OAuth2 login flow & save credentials
    ads-cli export     # Export live Google Ads state to modular Markdown specs
    ads-cli diff       # Compare local Markdown specs vs live Google Ads state
    ads-cli apply      # Apply local Markdown spec changes to Google Ads
    ads-cli list       # List active campaigns and budgets
    ads-cli report     # Generate performance analytics reports
"""

import sys
import argparse
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.generate_tokens import main as generate_tokens_main
from scripts.modular_sync import handle_export, handle_diff, handle_apply
from scripts.list_campaigns import main as list_campaigns_main
from scripts.run_report import main as run_report_main
from config.settings import DEFAULT_CUSTOMER_ID

def main():
    parser = argparse.ArgumentParser(
        prog="ads-cli",
        description="Google Ads Automation & Bidirectional Sync Engine CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. auth
    auth_p = subparsers.add_parser("auth", help="Run OAuth2 authorization & save tokens persistently")
    auth_p.add_argument("--client_id", help="Google Cloud OAuth2 Client ID")
    auth_p.add_argument("--client_secret", help="Google Cloud OAuth2 Client Secret")
    auth_p.add_argument("--developer_token", help="Google Ads Developer Token")
    auth_p.add_argument("--customer_id", help="Google Ads Customer ID")

    # 2. export
    exp_p = subparsers.add_parser("export", help="Export live Google Ads state to modular Markdown specs")
    exp_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID, help="Customer ID")

    # 3. diff
    diff_p = subparsers.add_parser("diff", help="Compare local Markdown specs vs live Google Ads state")
    diff_p.add_argument("dir_path", nargs="?", default=f"campaign_specs/account_{DEFAULT_CUSTOMER_ID}", help="Modular specs folder path")
    diff_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID, help="Customer ID")

    # 4. apply
    app_p = subparsers.add_parser("apply", help="Apply local Markdown spec changes to Google Ads")
    app_p.add_argument("dir_path", nargs="?", default=f"campaign_specs/account_{DEFAULT_CUSTOMER_ID}", help="Modular specs folder path")
    app_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID, help="Customer ID")

    # 5. list
    list_p = subparsers.add_parser("list", help="List active campaigns and budgets")
    list_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID, help="Customer ID")

    # 6. report
    rep_p = subparsers.add_parser("report", help="Generate performance analytics reports")
    rep_p.add_argument("--customer_id", default=DEFAULT_CUSTOMER_ID, help="Customer ID")
    rep_p.add_argument("--period", default="LAST_30_DAYS", help="Date period (e.g., LAST_30_DAYS, THIS_MONTH)")
    rep_p.add_argument("--format", choices=["markdown", "csv"], default="markdown", help="Report format")
    rep_p.add_argument("--output", help="Save report to file path")

    args = parser.parse_args()

    if args.command == "auth":
        sys.argv = [sys.argv[0]]
        if args.client_id:
            sys.argv.extend(["--client_id", args.client_id])
        if args.client_secret:
            sys.argv.extend(["--client_secret", args.client_secret])
        if args.developer_token:
            sys.argv.extend(["--developer_token", args.developer_token])
        if args.customer_id:
            sys.argv.extend(["--customer_id", args.customer_id])
        generate_tokens_main()

    elif args.command == "export":
        handle_export(args)

    elif args.command == "diff":
        handle_diff(args)

    elif args.command == "apply":
        handle_apply(args)

    elif args.command == "list":
        sys.argv = [sys.argv[0], args.customer_id or DEFAULT_CUSTOMER_ID]
        list_campaigns_main()

    elif args.command == "report":
        sys.argv = [sys.argv[0], "--customer_id", args.customer_id or DEFAULT_CUSTOMER_ID, "--period", args.period, "--format", args.format]
        if args.output:
            sys.argv.extend(["--output", args.output])
        run_report_main()

if __name__ == "__main__":
    main()
