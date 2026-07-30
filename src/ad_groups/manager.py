import logging
from typing import List
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from src.campaigns.models import ResponsiveSearchAdSpec, KeywordSpec

logger = logging.getLogger(__name__)

class AdGroupManager:
    """Manages Google Ads Ad Groups, Responsive Search Ads (RSA), and Keywords."""

    def __init__(self, client: GoogleAdsClient, customer_id: str):
        self.client = client
        self.customer_id = str(customer_id).replace("-", "")

    def create_ad_group(self, campaign_resource_name: str, name: str, cpc_bid_micros: int = 1000000) -> str:
        """Creates an Ad Group within a Campaign and returns resource name."""
        ad_group_service = self.client.get_service("AdGroupService")
        ad_group_operation = self.client.get_type("AdGroupOperation")
        
        ad_group = ad_group_operation.create
        ad_group.name = name
        ad_group.status = self.client.enums.AdGroupStatusEnum.ENABLED
        ad_group.campaign = campaign_resource_name
        ad_group.type_ = self.client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group.cpc_bid_micros = cpc_bid_micros

        try:
            response = ad_group_service.mutate_ad_groups(
                customer_id=self.customer_id,
                operations=[ad_group_operation]
            )
            created_resource = response.results[0].resource_name
            logger.info(f"Created Ad Group: {created_resource}")
            return created_resource
        except GoogleAdsException as ex:
            logger.error(f"Failed to create Ad Group '{name}': {ex}")
            raise ex

    def create_responsive_search_ad(self, ad_group_resource_name: str, ad_spec: ResponsiveSearchAdSpec) -> str:
        """Creates a Responsive Search Ad (RSA) in the specified Ad Group."""
        ad_group_ad_service = self.client.get_service("AdGroupAdService")
        ad_group_ad_operation = self.client.get_type("AdGroupAdOperation")
        
        ad_group_ad = ad_group_ad_operation.create
        ad_group_ad.ad_group = ad_group_resource_name
        ad_group_ad.status = self.client.enums.AdGroupAdStatusEnum.ENABLED

        # Set final URL
        ad_group_ad.ad.final_urls.append(ad_spec.final_url)

        # Set Headlines
        for text in ad_spec.headlines:
            headline = self.client.get_type("AdTextAsset")
            headline.text = text
            ad_group_ad.ad.responsive_search_ad.headlines.append(headline)

        # Set Descriptions
        for text in ad_spec.descriptions:
            description = self.client.get_type("AdTextAsset")
            description.text = text
            ad_group_ad.ad.responsive_search_ad.descriptions.append(description)

        try:
            response = ad_group_ad_service.mutate_ad_group_ads(
                customer_id=self.customer_id,
                operations=[ad_group_ad_operation]
            )
            created_resource = response.results[0].resource_name
            logger.info(f"Created Responsive Search Ad: {created_resource}")
            return created_resource
        except GoogleAdsException as ex:
            logger.error(f"Failed to create RSA: {ex}")
            raise ex

    def add_keywords(self, ad_group_resource_name: str, keywords: List[KeywordSpec]) -> List[str]:
        """Adds keywords to an Ad Group individually to ensure policy safety."""
        ad_group_criterion_service = self.client.get_service("AdGroupCriterionService")
        
        added_resources = []
        for kw in keywords:
            operation = self.client.get_type("AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = ad_group_resource_name
            criterion.status = self.client.enums.AdGroupCriterionStatusEnum.ENABLED
            criterion.keyword.text = kw.text
            criterion.keyword.match_type = getattr(
                self.client.enums.KeywordMatchTypeEnum,
                kw.match_type.upper()
            )

            try:
                response = ad_group_criterion_service.mutate_ad_group_criteria(
                    customer_id=self.customer_id,
                    operations=[operation]
                )
                res_name = response.results[0].resource_name
                added_resources.append(res_name)
            except GoogleAdsException as ex:
                logger.warning(f"Skipping keyword '{kw.text}' due to policy/API constraint: {ex}")

        logger.info(f"Successfully added {len(added_resources)} keywords out of {len(keywords)} to Ad Group.")
        return added_resources
