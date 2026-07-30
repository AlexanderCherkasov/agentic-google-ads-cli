# Google Ads Automation & Bidirectional Sync Engine 🚀

Automated campaign management, bidirectional synchronization (Google Ads ↔️ Markdown Specs), and reporting platform for Google Ads accounts.

---

## 🤖 Agentic Skill & `npx skills` Integration

This repository is fully packaged as an **Agentic Skill** for AI coding assistants (Google Antigravity, Claude, Cursor, CodeCompanion, etc.) and `npx skills` ecosystem.

### Install Skill via `npx skills`
```bash
npx skills add AlexanderCherkasov/agentic-google-ads-cli
```

### Run CLI directly via `npx`
```bash
# Self-bootstraps Python venv and dependencies automatically on first run!
npx agentic-google-ads-cli --help
npx agentic-google-ads-cli list
npx agentic-google-ads-cli export
npx agentic-google-ads-cli diff
npx agentic-google-ads-cli apply
```

---

## 🔑 Required Tokens & Credentials Guide

To connect with Google Ads API, you need the following tokens and IDs:

| Token / Parameter | Source / Where to Obtain | Description |
| :--- | :--- | :--- |
| **`GOOGLE_ADS_CLIENT_ID`** | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) | OAuth 2.0 Client ID (Web/Desktop Application) |
| **`GOOGLE_ADS_CLIENT_SECRET`** | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) | OAuth 2.0 Client Secret |
| **`GOOGLE_ADS_DEVELOPER_TOKEN`** | Google Ads MCC (`Tools ➡️ API Center`) | Developer token to execute API operations |
| **`GOOGLE_ADS_CUSTOMER_ID`** | Google Ads Account (top-right header) | 10-digit target customer ID (e.g., `1234567890`) |
| **`GOOGLE_ADS_LOGIN_CUSTOMER_ID`** | Google Ads MCC Manager Account | *(Optional)* 10-digit MCC manager ID |
| **`GOOGLE_ADS_REFRESH_TOKEN`** | Auto-generated via `./bin/ads-cli auth` | Persistent OAuth2 refresh token |

### 🛠️ Step-by-Step Acquisition Guide:

1. **Get Client ID & Client Secret**:
   - Go to [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials).
   - Create a project and enable the **Google Ads API**.
   - Create **OAuth 2.0 Client IDs** (Application type: Desktop App or Web App with redirect URI `http://localhost:8085/`).
   - Copy your `Client ID` and `Client Secret`.

2. **Get Developer Token**:
   - Log into your Google Ads Manager (MCC) Account.
   - Go to `Tools & Settings ➡️ API Center`.
   - Request a **Developer Token** (Test Account Access or Basic Access).

3. **Generate OAuth Refresh Token Automatically**:
   Run the CLI authorization command:
   ```bash
   ./bin/ads-cli auth \
     --client_id "YOUR_CLIENT_ID" \
     --client_secret "YOUR_CLIENT_SECRET" \
     --developer_token "YOUR_DEVELOPER_TOKEN" \
     --customer_id "YOUR_CUSTOMER_ID"
   ```
   *This automatically launches a browser login window and saves your persistent `refresh_token` into `.env` and `google-ads.yaml`!*

---

## 🔄 Bidirectional Synchronization Overview

```text
[ Google Ads API ]  <====== (Export / Download) ======>  [ Local Markdown Specs ]
 (Google Ads Account) <====== (Apply / Upload)    ======>  (campaign_specs/*)
                                         ||
                                  [ Diff Engine ]
```

---

## 📁 Directory Structure

```text
./
├── config/
│   ├── default_settings.yaml      # Global default settings (currency, bidding, etc.)
│   └── settings.py                # Configuration and environment loader
├── campaign_specs/                # Human-readable Markdown Campaign Specs (Ignored by git)
├── bin/
│   └── ads-cli                    # Executable CLI tool (Self-bootstrapping)
├── skills/
│   └── google-ads-automation/
│       └── SKILL.md               # Agentic Skill for distribution
├── .skills/
│   └── google-ads-automation/
│       └── SKILL.md               # Standard Agentic Skill location
├── package.json                   # npx skills manifest
├── scripts/
│   ├── cli.py                     # Unified CLI entrypoint
│   ├── setup_account.py           # Account setup helper
│   ├── generate_tokens.py         # Automated OAuth2 flow: auto-saves to google-ads.yaml
│   ├── modular_sync.py            # Unified Sync CLI tool (export, diff, apply)
│   ├── list_campaigns.py          # List campaigns with status and budget info
│   ├── pause_campaign.py          # Quick campaign status switch (PAUSED / ENABLED)
│   └── run_report.py              # Export performance metrics (Markdown/CSV)
├── src/
│   ├── client.py                  # Google Ads API client wrapper
│   ├── parsers/
│   │   └── markdown_spec_parser.py# Parser for Markdown campaign specs
│   ├── sync/
│   │   ├── exporter.py            # Converts live campaign data -> Markdown specs
│   │   └── diff_engine.py         # Compares local Markdown spec vs live campaign state
│   ├── campaigns/
│   │   ├── manager.py             # Campaign lifecycle operations
│   │   └── models.py              # Pydantic data models
│   ├── ad_groups/
│   │   └── manager.py             # Ad group, Responsive Search Ad, & Keyword manager
│   └── reporting/
│       └── fetcher.py             # Analytics reporting via GAQL
├── tests/
│   ├── test_markdown_parser.py    # Unit tests for Markdown parser
│   └── test_sync_engine.py        # Unit tests for Bidirectional Sync Engine
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚡ Bidirectional Synchronization Workflows

### 1. Export Live Campaigns (Google Ads ➡️ Modular Markdown Folder)
To download all campaigns from Google Ads and generate modular `.md` specification files:
```bash
./bin/ads-cli export --customer_id <CUSTOMER_ID>
```

### 2. Compare Diffs (Local Markdown 🆚 Live Google Ads)
Before pushing changes, compare your local Markdown files against live Google Ads state:
```bash
./bin/ads-cli diff campaign_specs/account_<CUSTOMER_ID>/
```

### 3. Apply Local Changes (Markdown Files ➡️ Google Ads)
Upload/synchronize your Markdown campaign specifications to Google Ads:
```bash
./bin/ads-cli apply campaign_specs/account_<CUSTOMER_ID>/
```

---

## 📊 Analytics Reporting
Print report to console as Markdown table:
```bash
./bin/ads-cli report --period LAST_30_DAYS --format markdown
```
Save report to CSV:
```bash
./bin/ads-cli report --period THIS_MONTH --format csv --output reports/monthly_performance.csv
```

---

## 🧪 Unit Verification
```bash
PYTHONPATH=. ./venv/bin/pytest
```
