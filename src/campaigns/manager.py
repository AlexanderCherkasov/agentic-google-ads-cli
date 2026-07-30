import logging
import time
from typing import List, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from src.campaigns.models import CampaignCreate, CampaignInfo

logger = logging.getLogger(__name__)

class CampaignManager:
    """Manages Google Ads campaigns: listing, creation, updates, and status changes."""

    def __init__(self, client: GoogleAdsClient, customer_id: str):
        self.client = client
        self.customer_id = str(customer_id).replace("-", "")

    def list_campaigns(self, limit: int = 50) -> List[CampaignInfo]:
        """Fetches list of campaigns for the specified customer ID."""
        ga_service = self.client.get_service("GoogleAdsService")
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign_budget.id,
                campaign_budget.amount_micros
            FROM campaign
            ORDER BY campaign.id
            LIMIT {limit}
        """

        campaigns = []
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                camp = row.campaign
                budget = row.campaign_budget
                campaigns.append(
                    CampaignInfo(
                        id=str(camp.id),
                        name=camp.name,
                        status=camp.status.name,
                        advertising_channel_type=camp.advertising_channel_type.name,
                        budget_id=str(budget.id) if budget.id else None,
                        budget_amount_micros=budget.amount_micros if budget.amount_micros else None
                    )
                )
        except GoogleAdsException as ex:
            logger.error(f"Google Ads API Error in list_campaigns: {ex}")
            raise ex

        return campaigns

    def find_budget_by_name(self, name: str) -> Optional[str]:
        """Finds existing budget resource name by name if exists."""
        ga_service = self.client.get_service("GoogleAdsService")
        query = f"SELECT campaign_budget.resource_name FROM campaign_budget WHERE campaign_budget.name = '{name}'"
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                return row.campaign_budget.resource_name
        except Exception:
            pass
        return None

    def create_budget(self, name: str, amount_micros: int) -> str:
        """Creates a campaign budget or reuses existing budget if name exists."""
        existing_resource = self.find_budget_by_name(name)
        if existing_resource:
            logger.info(f"Reusing existing campaign budget: {existing_resource}")
            return existing_resource

        campaign_budget_service = self.client.get_service("CampaignBudgetService")
        campaign_budget_operation = self.client.get_type("CampaignBudgetOperation")
        
        budget = campaign_budget_operation.create
        budget.name = name
        budget.amount_micros = amount_micros
        budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD

        try:
            response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[campaign_budget_operation]
            )
            return response.results[0].resource_name
        except GoogleAdsException as ex:
            # If name duplicate occurs unexpectedly, try fallback with timestamp
            unique_name = f"{name} {int(time.time())}"
            logger.warning(f"Budget name collision. Retrying with unique name '{unique_name}'")
            budget.name = unique_name
            response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=self.customer_id,
                operations=[campaign_budget_operation]
            )
            return response.results[0].resource_name

    def create_campaign(self, campaign_data: CampaignCreate) -> str:
        """Creates a Search campaign and returns created resource name."""
        budget_resource_name = self.create_budget(
            name=f"Budget for {campaign_data.name}",
            amount_micros=campaign_data.budget_amount_micros
        )

        campaign_service = self.client.get_service("CampaignService")
        campaign_operation = self.client.get_type("CampaignOperation")
        
        campaign = campaign_operation.create
        campaign.name = campaign_data.name
        campaign.advertising_channel_type = getattr(
            self.client.enums.AdvertisingChannelTypeEnum,
            campaign_data.advertising_channel_type
        )
        campaign.status = getattr(
            self.client.enums.CampaignStatusEnum,
            campaign_data.status
        )
        campaign.campaign_budget = budget_resource_name

        # Default bidding strategy: Manual CPC
        campaign.manual_cpc.enhanced_cpc_enabled = False

        # Required regulatory field for EU Political Advertising in Google Ads API
        campaign.contains_eu_political_advertising = (
            self.client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
        )

        try:
            response = campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[campaign_operation]
            )
            created_resource = response.results[0].resource_name
            logger.info(f"Successfully created campaign: {created_resource}")
            return created_resource
        except GoogleAdsException as ex:
            logger.error(f"Failed to create campaign: {ex}")
            raise ex

    def update_campaign_status(self, campaign_id: str, status: str) -> None:
        """Updates campaign status ('ENABLED', 'PAUSED', 'REMOVED')."""
        campaign_service = self.client.get_service("CampaignService")
        campaign_operation = self.client.get_type("CampaignOperation")

        campaign = campaign_operation.update
        campaign.resource_name = campaign_service.campaign_path(self.customer_id, campaign_id)
        campaign.status = getattr(self.client.enums.CampaignStatusEnum, status)

        # Field mask tells API which fields are being modified
        campaign_operation.update_mask.paths.append("status")

        try:
            campaign_service.mutate_campaigns(
                customer_id=self.customer_id,
                operations=[campaign_operation]
            )
            logger.info(f"Campaign {campaign_id} status changed to {status}")
        except GoogleAdsException as ex:
            logger.error(f"Failed to update campaign status: {ex}")
            raise ex
