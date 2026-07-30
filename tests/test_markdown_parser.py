import pytest
from src.parsers.markdown_spec_parser import MarkdownSpecParser

def test_parse_search_campaign_demo():
    spec = MarkdownSpecParser.parse_file("campaign_specs/search_campaign_demo.md")
    
    assert spec.name == "Search_Automation_SaaS_US"
    assert spec.channel == "SEARCH"
    assert spec.daily_budget_usd == 50.00
    assert spec.status == "PAUSED"
    assert spec.target_country == "United States"
    assert spec.target_language == "English"
    
    assert len(spec.ad_groups) == 2
    
    ag1 = spec.ad_groups[0]
    assert ag1.name == "Cloud Automation Tools"
    assert ag1.max_cpc_usd == 2.50
    assert ag1.ad is not None
    assert len(ag1.ad.headlines) == 5
    assert len(ag1.ad.descriptions) == 3
    assert ag1.ad.final_url == "https://example.com/automation-software"
    
    assert len(ag1.keywords) == 4
    assert ag1.keywords[0].text == "ad automation software"
    assert ag1.keywords[0].match_type == "BROAD"
    assert ag1.keywords[2].text == "automated campaign manager"
    assert ag1.keywords[2].match_type == "EXACT"

def test_parse_display_campaign_demo():
    spec = MarkdownSpecParser.parse_file("campaign_specs/display_campaign_demo.md")
    
    assert spec.name == "Display_Remarketing_Global"
    assert spec.channel == "DISPLAY"
    assert spec.daily_budget_usd == 25.00
    assert len(spec.ad_groups) == 1
    assert spec.ad_groups[0].name == "Website Visitors Retargeting"
