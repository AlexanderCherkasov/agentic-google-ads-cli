---
name: google-ads-automation
description: Complete Google Ads API automation engine with bidirectional Markdown synchronization, asset management (Sitelinks, Callouts), negative keyword management, and self-bootstrapping CLI tools for AI agents.
---

# Google Ads Automation Skill 🚀

This skill enables AI agents and developers to automate Google Ads campaign management, perform bidirectional synchronization between live Google Ads state and modular human-readable Markdown specifications, manage ad assets (Sitelinks, Callouts), manage negative keywords, and export performance reports.

---

## 🛠️ Zero-Setup & Self-Bootstrapping CLI (`./bin/ads-cli`)

The CLI launcher is **100% self-bootstrapping**: running `./bin/ads-cli` automatically checks, creates the Python virtual environment (`venv`), and installs all required dependencies on-the-fly.

### Authentication Setup
Provide OAuth2 Client ID, Client Secret, Developer Token, and Customer ID:
```bash
./bin/ads-cli auth \
  --client_id "YOUR_CLIENT_ID" \
  --client_secret "YOUR_CLIENT_SECRET" \
  --developer_token "YOUR_DEVELOPER_TOKEN" \
  --customer_id "YOUR_CUSTOMER_ID"
```

---

## 📁 Modular Markdown Specifications Hierarchy

Campaign specifications are stored in a human-readable, modular folder structure under `campaign_specs/`:

```text
campaign_specs/account_<CUSTOMER_ID>/
├── README.md                                  # Account overview & campaigns summary
└── <campaign_slug>/                           # Campaign folder
    ├── README.md                              # Campaign settings (budget, status, bidding, target country/lang)
    ├── negative_keywords.md                   # Live campaign negative keywords
    ├── assets.md                              # Live Sitelinks (Fast links) and Callouts (Highlights)
    └── ad_groups/                             # Ad groups folder
        └── <ad_group_slug>/
            ├── ad_spec.md                     # RSA Headlines (1-15), Descriptions (1-4), Landing URL, Max CPC
            └── keywords.md                    # Target keywords ([exact], "phrase", broad)
```

---

## 🔄 Agentic Workflows

### 1. Export Live Account State to Markdown (`ads-cli export`)
Fetch live campaigns, budgets, ad groups, Responsive Search Ads, Sitelinks, Callouts, and Negative Keywords from Google Ads API and reconstruct the modular Markdown directory tree:
```bash
./bin/ads-cli export --customer_id <CUSTOMER_ID>
```

### 2. Compare Local Markdown Specs vs Live State (`ads-cli diff`)
Before applying changes, calculate exact diffs between your local Markdown spec files and the live Google Ads state:
```bash
./bin/ads-cli diff campaign_specs/account_<CUSTOMER_ID>/
```

### 3. Apply Local Markdown Changes to Google Ads (`ads-cli apply`)
Push all local edits from `README.md`, `negative_keywords.md`, `assets.md`, `ad_spec.md`, and `keywords.md` directly into Google Ads API:
```bash
./bin/ads-cli apply campaign_specs/account_<CUSTOMER_ID>/
```

### 4. List Active Campaigns (`ads-cli list`)
View a clean status table of all active campaigns and budgets:
```bash
./bin/ads-cli list
```

### 5. Generate Performance Reports (`ads-cli report`)
Export performance analytics (impressions, clicks, cost, conversions, CTR, avg CPC) to Markdown table or CSV:
```bash
./bin/ads-cli report --period LAST_30_DAYS --format markdown
./bin/ads-cli report --period THIS_MONTH --format csv --output reports/monthly_performance.csv
```

---

## 🛡️ Best Practices & Constraints for Agents

1. **RSA Headline Length Limit**: Headlines MUST NOT exceed **30 characters**.
2. **RSA Description Length Limit**: Descriptions MUST NOT exceed **90 characters**.
3. **Sensitive Health Information**: Avoid targeting health condition terms that violate Google Ads `HEALTH_IN_PERSONALIZED_ADS` policy.
4. **Idempotency**: `ads-cli apply` checks for existing resources before creating duplicates, ensuring safe re-runs.
