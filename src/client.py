import os
from pathlib import Path
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from config.settings import CONFIG_FILE_PATH, DEFAULT_LOGIN_CUSTOMER_ID

class AdsClientWrapper:
    """Wrapper around GoogleAdsClient to provide convenient initialization and error handling."""

    def __init__(self, config_path: str = None, login_customer_id: str = None):
        self.config_path = config_path or CONFIG_FILE_PATH
        self.login_customer_id = login_customer_id or DEFAULT_LOGIN_CUSTOMER_ID
        self._client = None

    def get_client(self) -> GoogleAdsClient:
        """Initializes and returns a GoogleAdsClient instance."""
        if not self._client:
            if not Path(self.config_path).exists():
                raise FileNotFoundError(
                    f"Configuration file not found at '{self.config_path}'. "
                    f"Please copy 'config/google-ads.yaml.template' to '{self.config_path}' and fill in credentials."
                )
            
            self._client = GoogleAdsClient.load_from_storage(
                path=self.config_path
            )
            
            if self.login_customer_id and not self._client.login_customer_id:
                self._client.login_customer_id = str(self.login_customer_id).replace("-", "")

        return self._client


def get_ads_client(config_path: str = None) -> GoogleAdsClient:
    """Helper function to quickly obtain a GoogleAdsClient instance."""
    wrapper = AdsClientWrapper(config_path=config_path)
    return wrapper.get_client()
