#!/usr/bin/env python3
"""
Exports complete Google Ads campaign structure into a clean, modular folder hierarchy:
campaign_specs/account_<CUSTOMER_ID>/
    ├── <campaign_name>/
    │   ├── README.md
    │   ├── negative_keywords.md  <-- Live negative keywords from API
    │   ├── assets.md             <-- Live Sitelinks, Callouts & Snippets from API
    │   └── ad_groups/
    │       └── <ad_group_name>/
    │           ├── ad_spec.md
    │           └── keywords.md
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.campaigns import CampaignManager
from src.sync.exporter import CampaignExporter
from scripts.fetch_live_assets import fetch_campaign_assets
from config.settings import DEFAULT_CUSTOMER_ID

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "_", text)

def fetch_live_campaign_negatives(client, customer_id: str, campaign_id: str) -> List[Dict[str, str]]:
    ga_service = client.get_service("GoogleAdsService")
    query = f"""
        SELECT
            campaign_criterion.keyword.text,
            campaign_criterion.keyword.match_type
        FROM campaign_criterion
        WHERE campaign.id = {campaign_id}
          AND campaign_criterion.type = 'KEYWORD'
          AND campaign_criterion.negative = TRUE
    """
    results = []
    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            kw = row.campaign_criterion.keyword
            results.append({
                "text": kw.text,
                "match_type": kw.match_type.name if kw.match_type else "EXACT"
            })
    except Exception as ex:
        print(f"[!] Exception fetching campaign negatives for {campaign_id}: {ex}")
    return results

def export_modular_campaign(client, exporter, campaign_id: str, campaign_dir: Path, customer_id: str):
    spec = exporter.export_campaign(campaign_id)
    campaign_dir.mkdir(parents=True, exist_ok=True)

    # 1. Campaign README.md
    readme_content = f"""# Campaign: {spec.name}

## ⚙️ Campaign Settings
- **ID**: `{campaign_id}`
- **Channel**: `{spec.channel}`
- **Daily Budget (USD)**: `${spec.daily_budget_usd:.2f}`
- **Status**: `{spec.status}`
- **Target Country**: `{spec.target_country or 'United States'}`
- **Target Language**: `{spec.target_language or 'English'}`
- **Bidding Strategy**: `{spec.bidding_strategy or 'MANUAL_CPC'}`

## 📁 Ad Groups ({len(spec.ad_groups)})
"""
    for ag in spec.ad_groups:
        ag_slug = slugify(ag.name)
        readme_content += f"- [{ag.name}](file://{campaign_dir}/ad_groups/{ag_slug}/ad_spec.md) (Max CPC: `${ag.max_cpc_usd:.2f}`, Keywords: {len(ag.keywords)})\n"

    (campaign_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # 2. FETCH LIVE CAMPAIGN NEGATIVE KEYWORDS FROM GOOGLE ADS API
    live_negatives = fetch_live_campaign_negatives(client, customer_id, campaign_id)
    
    neg_content = f"# Campaign Negative Keywords: {spec.name}\n\n"
    neg_content += f"Total Live Negative Keywords: {len(live_negatives)}\n\n"
    for neg in live_negatives:
        neg_content += f"- [{neg['match_type']}] {neg['text']}\n"

    (campaign_dir / "negative_keywords.md").write_text(neg_content, encoding="utf-8")

    # 3. FETCH LIVE CAMPAIGN ASSETS (SITELINKS, CALLOUTS, SNIPPETS) FROM GOOGLE ADS API
    live_assets = fetch_campaign_assets(client, customer_id, campaign_id)
    
    asset_content = f"# Campaign Assets & Extensions: {spec.name}\n\n"
    
    asset_content += f"## 🔗 Sitelinks ({len(live_assets['sitelinks'])})\n"
    for idx, sl in enumerate(live_assets['sitelinks'], 1):
        asset_content += f"{idx}. **{sl['text']}**\n"
        if sl['desc1']:
            asset_content += f"   - Line 1: {sl['desc1']}\n"
        if sl['desc2']:
            asset_content += f"   - Line 2: {sl['desc2']}\n"
        if sl['url']:
            asset_content += f"   - Final URL: [{sl['url']}]({sl['url']})\n"
        asset_content += "\n"

    asset_content += f"## 📢 Callouts ({len(live_assets['callouts'])})\n"
    for co in live_assets['callouts']:
        asset_content += f"- {co}\n"
    asset_content += "\n"

    asset_content += f"## 📌 Structured Snippets ({len(live_assets['snippets'])})\n"
    for ss in live_assets['snippets']:
        asset_content += f"- **Header**: {ss['header']}\n"
        asset_content += f"  - **Values**: {', '.join(ss['values'])}\n"

    (campaign_dir / "assets.md").write_text(asset_content, encoding="utf-8")

    # 4. Ad Groups Folder
    ad_groups_dir = campaign_dir / "ad_groups"
    ad_groups_dir.mkdir(exist_ok=True)

    for ag in spec.ad_groups:
        ag_dir = ad_groups_dir / slugify(ag.name)
        ag_dir.mkdir(exist_ok=True)

        # ad_spec.md
        ad_spec_md = f"# Ad Group: {ag.name}\n\n"
        ad_spec_md += f"## Settings\n- **Max CPC (USD)**: `${ag.max_cpc_usd:.2f}`\n\n"

        if ag.ad:
            ad_spec_md += "## Responsive Search Ad (RSA)\n\n### Headlines\n"
            for idx, h in enumerate(ag.ad.headlines, 1):
                ad_spec_md += f"{idx}. {h}\n"
            ad_spec_md += "\n### Descriptions\n"
            for idx, d in enumerate(ag.ad.descriptions, 1):
                ad_spec_md += f"{idx}. {d}\n"
            ad_spec_md += f"\n### Final Landing URL\n- [{ag.ad.final_url}]({ag.ad.final_url})\n"

        (ag_dir / "ad_spec.md").write_text(ad_spec_md, encoding="utf-8")

        # keywords.md
        kw_md = f"# Keywords: {ag.name}\n\n"
        kw_md += f"Total Keywords: {len(ag.keywords)}\n\n"
        
        exact_kws = [k for k in ag.keywords if k.match_type.upper() == "EXACT"]
        phrase_kws = [k for k in ag.keywords if k.match_type.upper() == "PHRASE"]
        broad_kws = [k for k in ag.keywords if k.match_type.upper() == "BROAD"]

        if exact_kws:
            kw_md += "## Exact Match Keywords ([keyword])\n"
            for k in exact_kws:
                kw_md += f"- [{k.text}]\n"
            kw_md += "\n"

        if phrase_kws:
            kw_md += "## Phrase Match Keywords (\"keyword\")\n"
            for k in phrase_kws:
                kw_md += f"- \"{k.text}\"\n"
            kw_md += "\n"

        if broad_kws:
            kw_md += "## Broad Match Keywords (keyword)\n"
            for k in broad_kws:
                kw_md += f"- {k.text}\n"
            kw_md += "\n"

        (ag_dir / "keywords.md").write_text(kw_md, encoding="utf-8")

def main():
    customer_id = DEFAULT_CUSTOMER_ID
    if not customer_id:
        print("[ERROR] GOOGLE_ADS_CUSTOMER_ID is not configured.")
        return

    client = get_ads_client()
    exporter = CampaignExporter(client, customer_id)
    camp_mgr = CampaignManager(client, customer_id)

    root_dir = Path(f"campaign_specs/account_{customer_id}")
    root_dir.mkdir(parents=True, exist_ok=True)

    print(f"[+] Exporting modular campaign specs with LIVE negative keywords & LIVE ASSETS to: {root_dir}")

    campaigns = camp_mgr.list_campaigns()
    
    root_readme = f"""# Account: {customer_id}

## 📊 Overview
- **Customer ID**: `{customer_id}`
- **Total Campaigns**: {len(campaigns)}

## 📁 Campaigns Hierarchy
"""
    for c in campaigns:
        c_slug = slugify(c.name)
        c_dir = root_dir / c_slug
        print(f"  [+] Exporting campaign '{c.name}' (ID: {c.id})...")
        export_modular_campaign(client, exporter, c.id, c_dir, customer_id)
        root_readme += f"- [{c.name}](file://{c_dir}/README.md) (ID: `{c.id}`, Status: `{c.status}`)\n"

    (root_dir / "README.md").write_text(root_readme, encoding="utf-8")
    print(f"[SUCCESS] Complete modular specification hierarchy created in: {root_dir}")

if __name__ == "__main__":
    main()
