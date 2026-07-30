import logging
from typing import List, Dict
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from src.campaigns.models import (
    CampaignSpec, 
    AdGroupSpec, 
    ResponsiveSearchAdSpec, 
    KeywordSpec
)

logger = logging.getLogger(__name__)

class CampaignExporter:
    """Fetches campaign details from Google Ads API and reconstructs Markdown Campaign Specs."""

    def __init__(self, client: GoogleAdsClient, customer_id: str):
        self.client = client
        self.customer_id = str(customer_id).replace("-", "")

    def export_campaign(self, campaign_id: str) -> CampaignSpec:
        """Fetches a specific campaign by ID and builds a CampaignSpec object."""
        ga_service = self.client.get_service("GoogleAdsService")

        # 1. Fetch Campaign Details & Budget
        camp_query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign_budget.amount_micros
            FROM campaign
            WHERE campaign.id = {campaign_id}
        """
        response = ga_service.search(customer_id=self.customer_id, query=camp_query)
        camp_row = next(iter(response), None)
        if not camp_row:
            raise ValueError(f"Campaign with ID {campaign_id} not found.")

        camp = camp_row.campaign
        budget_usd = (camp_row.campaign_budget.amount_micros / 1_000_000) if camp_row.campaign_budget.amount_micros else 0.0

        # 2. Fetch Ad Groups
        ag_query = f"""
            SELECT
                ad_group.id,
                ad_group.name,
                ad_group.cpc_bid_micros,
                ad_group.status
            FROM ad_group
            WHERE campaign.id = {campaign_id}
        """
        ag_response = ga_service.search(customer_id=self.customer_id, query=ag_query)
        
        ad_groups: List[AdGroupSpec] = []
        for ag_row in ag_response:
            ag = ag_row.ad_group
            ag_id = ag.id
            max_cpc = (ag.cpc_bid_micros / 1_000_000) if ag.cpc_bid_micros else 1.0

            # 3. Fetch Responsive Search Ads (RSA)
            ad_query = f"""
                SELECT
                    ad_group_ad.ad.final_urls,
                    ad_group_ad.ad.responsive_search_ad.headlines,
                    ad_group_ad.ad.responsive_search_ad.descriptions
                FROM ad_group_ad
                WHERE ad_group.id = {ag_id}
                LIMIT 1
            """
            ad_response = ga_service.search(customer_id=self.customer_id, query=ad_query)
            ad_row = next(iter(ad_response), None)

            ad_spec = None
            if ad_row and ad_row.ad_group_ad.ad:
                ad = ad_row.ad_group_ad.ad
                final_url = ad.final_urls[0] if ad.final_urls else "https://example.com"
                headlines = [h.text for h in ad.responsive_search_ad.headlines]
                descriptions = [d.text for d in ad.responsive_search_ad.descriptions]
                ad_spec = ResponsiveSearchAdSpec(
                    headlines=headlines,
                    descriptions=descriptions,
                    final_url=final_url
                )

            # 4. Fetch Keywords
            kw_query = f"""
                SELECT
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type
                FROM ad_group_criterion
                WHERE ad_group.id = {ag_id}
                  AND ad_group_criterion.type = 'KEYWORD'
            """
            kw_response = ga_service.search(customer_id=self.customer_id, query=kw_query)
            keywords = []
            for kw_row in kw_response:
                kw = kw_row.ad_group_criterion.keyword
                keywords.append(KeywordSpec(text=kw.text, match_type=kw.match_type.name))

            ad_groups.append(
                AdGroupSpec(
                    name=ag.name,
                    max_cpc_usd=max_cpc,
                    ad=ad_spec,
                    keywords=keywords,
                    negative_keywords=[]
                )
            )

        return CampaignSpec(
            name=camp.name,
            channel=camp.advertising_channel_type.name,
            daily_budget_usd=budget_usd,
            status=camp.status.name,
            ad_groups=ad_groups
        )

    @staticmethod
    def spec_to_markdown(spec: CampaignSpec) -> str:
        """Converts a CampaignSpec instance into human-readable Markdown format."""
        md = []
        md.append(f"# Campaign Specification: {spec.name}\n")
        md.append("## Overview")
        md.append(f"Exported live campaign specification from Google Ads.\n")
        md.append("## Campaign Settings")
        md.append(f"- **Name**: {spec.name}")
        md.append(f"- **Channel**: {spec.channel}")
        md.append(f"- **Daily Budget (USD)**: {spec.daily_budget_usd:.2f}")
        md.append(f"- **Status**: {spec.status}")
        md.append(f"- **Target Country**: {spec.target_country or 'United States'}")
        md.append(f"- **Target Language**: {spec.target_language or 'English'}")
        md.append(f"- **Bidding Strategy**: {spec.bidding_strategy or 'MANUAL_CPC'}\n")
        md.append("---\n")

        for ag in spec.ad_groups:
            md.append(f"## Ad Group: {ag.name}")
            md.append(f"- **Max CPC (USD)**: {ag.max_cpc_usd:.2f}\n")

            if ag.ad:
                md.append("### Responsive Search Ad")
                md.append("#### Headlines")
                for idx, h in enumerate(ag.ad.headlines, 1):
                    md.append(f"{idx}. {h}")
                md.append("\n#### Descriptions")
                for idx, d in enumerate(ag.ad.descriptions, 1):
                    md.append(f"{idx}. {d}")
                md.append("\n#### Final URL")
                md.append(f"- {ag.ad.final_url}\n")

            if ag.keywords:
                md.append("### Keywords")
                for kw in ag.keywords:
                    md.append(f"- {kw.match_type.lower()}: {kw.text}")
                md.append("")

            if ag.negative_keywords:
                md.append("### Negative Keywords")
                for neg in ag.negative_keywords:
                    md.append(f"- {neg}")
                md.append("")

            md.append("---\n")

        return "\n".join(md)
