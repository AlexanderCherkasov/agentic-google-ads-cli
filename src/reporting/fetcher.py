import logging
import pandas as pd
from typing import Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger(__name__)

class ReportFetcher:
    """Fetches analytics and performance data using GAQL (Google Ads Query Language)."""

    def __init__(self, client: GoogleAdsClient, customer_id: str):
        self.client = client
        self.customer_id = str(customer_id).replace("-", "")

    def get_campaign_performance(
        self, 
        start_date: str = "LAST_30_DAYS", 
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieves campaign performance metrics (impressions, clicks, cost, conversions).
        date range can be a preset like 'LAST_30_DAYS', 'THIS_MONTH' or explicit YYYY-MM-DD.
        """
        ga_service = self.client.get_service("GoogleAdsService")
        
        date_condition = f"DURING {start_date}" if not end_date else f"BETWEEN '{start_date}' AND '{end_date}'"

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.ctr,
                metrics.average_cpc
            FROM campaign
            WHERE segments.date {date_condition}
            ORDER BY metrics.impressions DESC
        """

        rows = []
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                camp = row.campaign
                metrics = row.metrics
                rows.append({
                    "Campaign ID": camp.id,
                    "Campaign Name": camp.name,
                    "Status": camp.status.name,
                    "Impressions": metrics.impressions,
                    "Clicks": metrics.clicks,
                    "Cost (USD)": metrics.cost_micros / 1_000_000,
                    "Conversions": metrics.conversions,
                    "CTR (%)": round(metrics.ctr * 100, 2),
                    "Avg CPC (USD)": metrics.average_cpc / 1_000_000 if metrics.average_cpc else 0.0
                })
        except GoogleAdsException as ex:
            logger.error(f"Failed to fetch report: {ex}")
            raise ex

        return pd.DataFrame(rows)
