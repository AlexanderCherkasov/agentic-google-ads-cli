import pytest
from src.campaigns.models import CampaignSpec, AdGroupSpec, KeywordSpec
from src.sync.exporter import CampaignExporter
from src.sync.diff_engine import CampaignDiffEngine

def test_exporter_spec_to_markdown():
    spec = CampaignSpec(
        name="Test_Sync_Campaign",
        channel="SEARCH",
        daily_budget_usd=100.0,
        status="ENABLED",
        ad_groups=[
            AdGroupSpec(
                name="Group_Alpha",
                max_cpc_usd=3.5,
                keywords=[
                    KeywordSpec(text="automation python", match_type="EXACT"),
                    KeywordSpec(text="ppc tools", match_type="BROAD")
                ]
            )
        ]
    )

    md = CampaignExporter.spec_to_markdown(spec)
    assert "# Campaign Specification: Test_Sync_Campaign" in md
    assert "- **Daily Budget (USD)**: 100.00" in md
    assert "## Ad Group: Group_Alpha" in md
    assert "- exact: automation python" in md

def test_diff_engine_detects_changes():
    local = CampaignSpec(
        name="Test_Sync_Campaign",
        channel="SEARCH",
        daily_budget_usd=150.0,  # Changed from 100.0
        status="PAUSED",        # Changed from ENABLED
        ad_groups=[
            AdGroupSpec(
                name="Group_Alpha",
                max_cpc_usd=3.5,
                keywords=[
                    KeywordSpec(text="automation python", match_type="EXACT"),
                    KeywordSpec(text="ppc tools", match_type="BROAD"),
                    KeywordSpec(text="new keyword", match_type="PHRASE") # Added
                ]
            )
        ]
    )

    remote = CampaignSpec(
        name="Test_Sync_Campaign",
        channel="SEARCH",
        daily_budget_usd=100.0,
        status="ENABLED",
        ad_groups=[
            AdGroupSpec(
                name="Group_Alpha",
                max_cpc_usd=3.5,
                keywords=[
                    KeywordSpec(text="automation python", match_type="EXACT"),
                    KeywordSpec(text="ppc tools", match_type="BROAD")
                ]
            )
        ]
    )

    diffs = CampaignDiffEngine.calculate_diff(local, remote)
    assert diffs["has_changes"] is True
    assert diffs["budget"] == {"from": 100.0, "to": 150.0}
    assert diffs["status"] == {"from": "ENABLED", "to": "PAUSED"}
    assert len(diffs["ad_groups_to_update"]) == 1
    assert len(diffs["ad_groups_to_update"][0]["new_keywords"]) == 1
