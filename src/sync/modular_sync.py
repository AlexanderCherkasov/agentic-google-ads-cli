import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from google.ads.googleads.client import GoogleAdsClient
from src.campaigns.models import CampaignSpec, AdGroupSpec, ResponsiveSearchAdSpec, KeywordSpec
from src.sync.exporter import CampaignExporter
from src.sync.diff_engine import CampaignDiffEngine
from config.settings import (
    MICROS_PER_CURRENCY_UNIT,
    DEFAULT_CPC_BID_USD,
    DEFAULT_DAILY_BUDGET_USD,
    DEFAULT_TARGET_COUNTRY,
    DEFAULT_TARGET_LANGUAGE,
    DEFAULT_BIDDING_STRATEGY,
    DEFAULT_CHANNEL_TYPE,
    DEFAULT_CAMPAIGN_STATUS
)

logger = logging.getLogger(__name__)

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "_", text)

class ModularSpecParser:
    """Parses modular directory trees (README.md, negative_keywords.md, ad_groups/*) into CampaignSpec objects."""

    @staticmethod
    def parse_campaign_dir(campaign_dir: Path) -> Dict[str, Any]:
        readme_path = campaign_dir / "README.md"
        neg_path = campaign_dir / "negative_keywords.md"
        ad_groups_dir = campaign_dir / "ad_groups"

        if not readme_path.exists():
            raise FileNotFoundError(f"Missing README.md in {campaign_dir}")

        readme_content = readme_path.read_text(encoding="utf-8")

        # Parse Campaign Settings from README.md
        name_match = re.search(r"# Campaign:\s*(.+)", readme_content)
        channel_match = re.search(r"- \*\*Channel\*\*:\s*`?([^`\n]+)`?", readme_content)
        budget_match = re.search(r"- \*\*Daily Budget \(USD\)\*\*:\s*`?\$?([\d.]+)`?", readme_content)
        status_match = re.search(r"- \*\*Status\*\*:\s*`?([^`\n]+)`?", readme_content)
        country_match = re.search(r"- \*\*Target Country\*\*:\s*`?([^`\n]+)`?", readme_content)
        lang_match = re.search(r"- \*\*Target Language\*\*:\s*`?([^`\n]+)`?", readme_content)
        bidding_match = re.search(r"- \*\*Bidding Strategy\*\*:\s*`?([^`\n]+)`?", readme_content)

        campaign_name = name_match.group(1).strip() if name_match else campaign_dir.name
        daily_budget = float(budget_match.group(1).strip()) if budget_match else DEFAULT_DAILY_BUDGET_USD
        channel = channel_match.group(1).strip() if channel_match else DEFAULT_CHANNEL_TYPE
        status = status_match.group(1).strip() if status_match else DEFAULT_CAMPAIGN_STATUS

        # Parse Negative Keywords from negative_keywords.md
        negative_keywords = []
        if neg_path.exists():
            neg_content = neg_path.read_text(encoding="utf-8")
            for line in neg_content.split("\n"):
                line = line.strip()
                m = re.match(r"^-\s*(?:\[([A-Z]+)\]\s*)?(.+)", line)
                if m:
                    match_type = m.group(1) or "BROAD"
                    text = m.group(2).strip()
                    if text and not text.startswith("Total") and not text.startswith("#"):
                        negative_keywords.append({"text": text, "match_type": match_type.upper()})

        # Parse Ad Groups from ad_groups/
        ad_groups: List[AdGroupSpec] = []
        if ad_groups_dir.exists():
            for ag_folder in sorted(ad_groups_dir.iterdir()):
                if ag_folder.is_dir():
                    ad_spec_file = ag_folder / "ad_spec.md"
                    keywords_file = ag_folder / "keywords.md"

                    if not ad_spec_file.exists():
                        continue

                    ad_spec_content = ad_spec_file.read_text(encoding="utf-8")
                    ag_name_match = re.search(r"# Ad Group:\s*(.+)", ad_spec_content)
                    cpc_match = re.search(r"- \*\*Max CPC \(USD\)\*\*:\s*`?\$?([\d.]+)`?", ad_spec_content)
                    
                    ag_name = ag_name_match.group(1).strip() if ag_name_match else ag_folder.name
                    max_cpc = float(cpc_match.group(1).strip()) if cpc_match else DEFAULT_CPC_BID_USD

                    # Headlines
                    headlines = []
                    h_block = re.search(r"### Headlines\n(.*?)(?=\n###|\n##|\Z)", ad_spec_content, re.DOTALL)
                    if h_block:
                        for l in h_block.group(1).strip().split("\n"):
                            l = l.strip()
                            if l and re.match(r"^\d+\.", l):
                                headlines.append(re.sub(r"^\d+\.\s*", "", l).strip())

                    # Descriptions
                    descriptions = []
                    d_block = re.search(r"### Descriptions\n(.*?)(?=\n###|\n##|\Z)", ad_spec_content, re.DOTALL)
                    if d_block:
                        for l in d_block.group(1).strip().split("\n"):
                            l = l.strip()
                            if l and re.match(r"^\d+\.", l):
                                descriptions.append(re.sub(r"^\d+\.\s*", "", l).strip())

                    # Final URL
                    url_match = re.search(r"### Final Landing URL\n-\s*\[.*?\]\((https?://[^\s)]+)\)", ad_spec_content)
                    if not url_match:
                        url_match = re.search(r"-\s*(https?://[^\s]+)", ad_spec_content)
                    final_url = url_match.group(1).strip() if url_match else "https://guideddays.com"

                    rsa = ResponsiveSearchAdSpec(
                        headlines=headlines,
                        descriptions=descriptions,
                        final_url=final_url
                    ) if headlines and descriptions else None

                    # Keywords from keywords.md
                    keywords = []
                    if keywords_file.exists():
                        kw_content = keywords_file.read_text(encoding="utf-8")
                        for l in kw_content.split("\n"):
                            l = l.strip()
                            m_exact = re.match(r"^-\s*\[(.*?)\]$", l)
                            m_phrase = re.match(r"^-\s*\"(.*?)\"$", l)
                            m_broad = re.match(r"^-\s*([^\"\[].*)$", l)

                            if m_exact:
                                keywords.append(KeywordSpec(text=m_exact.group(1).strip(), match_type="EXACT"))
                            elif m_phrase:
                                keywords.append(KeywordSpec(text=m_phrase.group(1).strip(), match_type="PHRASE"))
                            elif m_broad and not l.startswith("Total") and not l.startswith("#"):
                                keywords.append(KeywordSpec(text=m_broad.group(1).strip(), match_type="BROAD"))

                    ad_groups.append(
                        AdGroupSpec(
                            name=ag_name,
                            max_cpc_usd=max_cpc,
                            ad=rsa,
                            keywords=keywords
                        )
                    )

        spec = CampaignSpec(
            name=campaign_name,
            channel=channel,
            daily_budget_usd=daily_budget,
            status=status,
            target_country=country_match.group(1).strip() if country_match else DEFAULT_TARGET_COUNTRY,
            target_language=lang_match.group(1).strip() if lang_match else DEFAULT_TARGET_LANGUAGE,
            bidding_strategy=bidding_match.group(1).strip() if bidding_match else DEFAULT_BIDDING_STRATEGY,
            ad_groups=ad_groups
        )

        return {
            "campaign_spec": spec,
            "negative_keywords": negative_keywords
        }
