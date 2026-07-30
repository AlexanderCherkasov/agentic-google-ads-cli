import re
from pathlib import Path
from typing import List
from src.campaigns.models import (
    CampaignSpec, 
    AdGroupSpec, 
    ResponsiveSearchAdSpec, 
    KeywordSpec
)

class MarkdownSpecParser:
    """Parses Markdown campaign specification documents into CampaignSpec data structures."""

    @staticmethod
    def parse_file(file_path: str) -> CampaignSpec:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {file_path}")
        
        content = path.read_text(encoding="utf-8")
        return MarkdownSpecParser.parse_text(content)

    @staticmethod
    def parse_text(content: str) -> CampaignSpec:
        # Extract Campaign Settings
        campaign_name_match = re.search(r"- \*\*Name\*\*:\s*(.+)", content)
        channel_match = re.search(r"- \*\*Channel\*\*:\s*(.+)", content)
        budget_match = re.search(r"- \*\*Daily Budget \(USD\)\*\*:\s*([\d.]+)", content)
        status_match = re.search(r"- \*\*Status\*\*:\s*(.+)", content)
        bidding_match = re.search(r"- \*\*Bidding Strategy\*\*:\s*(.+)", content)
        country_match = re.search(r"- \*\*Target Country\*\*:\s*(.+)", content)
        lang_match = re.search(r"- \*\*Target Language\*\*:\s*(.+)", content)

        if not campaign_name_match or not budget_match:
            raise ValueError("Markdown spec missing required Campaign Name or Daily Budget.")

        campaign_name = campaign_name_match.group(1).strip()
        daily_budget = float(budget_match.group(1).strip())
        channel = channel_match.group(1).strip() if channel_match else "SEARCH"
        status = status_match.group(1).strip() if status_match else "PAUSED"
        bidding_strategy = bidding_match.group(1).strip() if bidding_match else "MANUAL_CPC"

        # Split content by Ad Group sections (## Ad Group:)
        ad_group_sections = re.split(r"^##\s+Ad Group:\s*", content, flags=re.MULTILINE)
        
        ad_groups: List[AdGroupSpec] = []

        # Skip header section (index 0)
        for section in ad_group_sections[1:]:
            ag_lines = section.strip().split("\n")
            ag_name = ag_lines[0].strip()

            cpc_match = re.search(r"- \*\*Max CPC \(USD\)\*\*:\s*([\d.]+)", section)
            max_cpc = float(cpc_match.group(1).strip()) if cpc_match else 1.0

            # Headlines
            headlines = []
            headlines_block = re.search(r"#### Headlines\n(.*?)(?=\n####|\n###|\n##|\Z)", section, re.DOTALL)
            if headlines_block:
                headlines = [
                    re.sub(r"^\d+\.\s*", "", line).strip() 
                    for line in headlines_block.group(1).strip().split("\n") 
                    if line.strip() and re.match(r"^\d+\.", line.strip())
                ]

            # Descriptions
            descriptions = []
            desc_block = re.search(r"#### Descriptions\n(.*?)(?=\n####|\n###|\n##|\Z)", section, re.DOTALL)
            if desc_block:
                descriptions = [
                    re.sub(r"^\d+\.\s*", "", line).strip() 
                    for line in desc_block.group(1).strip().split("\n") 
                    if line.strip() and re.match(r"^\d+\.", line.strip())
                ]

            # Final URL
            url_match = re.search(r"#### Final URL\n-\s*(https?://[^\s]+)", section)
            final_url = url_match.group(1).strip() if url_match else "https://example.com"

            ad_spec = ResponsiveSearchAdSpec(
                headlines=headlines,
                descriptions=descriptions,
                final_url=final_url
            ) if headlines and descriptions else None

            # Keywords
            keywords = []
            kw_block = re.search(r"### Keywords\n(.*?)(?=\n###|\n##|\Z)", section, re.DOTALL)
            if kw_block:
                for line in kw_block.group(1).strip().split("\n"):
                    m = re.match(r"^-\s*(broad|phrase|exact):\s*(.+)", line.strip(), re.IGNORECASE)
                    if m:
                        match_type = m.group(1).upper()
                        text = m.group(2).strip()
                        keywords.append(KeywordSpec(text=text, match_type=match_type))

            # Negative Keywords
            negatives = []
            neg_block = re.search(r"### Negative Keywords\n(.*?)(?=\n###|\n##|\Z)", section, re.DOTALL)
            if neg_block:
                negatives = [
                    re.sub(r"^-\s*", "", line).strip()
                    for line in neg_block.group(1).strip().split("\n")
                    if line.strip().startswith("-")
                ]

            ad_groups.append(
                AdGroupSpec(
                    name=ag_name,
                    max_cpc_usd=max_cpc,
                    ad=ad_spec,
                    keywords=keywords,
                    negative_keywords=negatives
                )
            )

        return CampaignSpec(
            name=campaign_name,
            channel=channel,
            daily_budget_usd=daily_budget,
            status=status,
            target_country=country_match.group(1).strip() if country_match else "United States",
            target_language=lang_match.group(1).strip() if lang_match else "English",
            bidding_strategy=bidding_strategy,
            ad_groups=ad_groups
        )
