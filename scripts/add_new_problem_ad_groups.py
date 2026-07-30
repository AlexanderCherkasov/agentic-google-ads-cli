#!/usr/bin/env python3
"""
Adds RSAs and Keywords to the 3 newly created Ad Groups (Aggression, Noncompliance, Screen Time).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import get_ads_client
from src.ad_groups import AdGroupManager
from src.campaigns.models import ResponsiveSearchAdSpec, KeywordSpec
from config.settings import DEFAULT_CUSTOMER_ID

def main():
    customer_id = DEFAULT_CUSTOMER_ID
    if not customer_id:
        print("[ERROR] GOOGLE_ADS_CUSTOMER_ID is not set.")
        return

    client = get_ads_client()
    ad_group_mgr = AdGroupManager(client, customer_id)

    ad_groups = [
        {
            "resource_name": f"customers/{customer_id}/adGroups/199423293512",
            "name": "Aggression",
            "url": "https://guideddays.com/en-US/problems/aggression",
            "headlines": [
                "Child Hitting & Biting?",
                "How to Handle Child Anger",
                "Aggressive Outburst Support",
                "Stop Hitting & Tantrums",
                "Behavioral Parent Guidance",
                "Understand Child Anger",
                "Calming Strategies for Home",
                "Why Is My Child Aggressive?",
                "Parent Action Plan for Anger",
                "De-escalate Child Aggression",
                "Aggression Parent Support",
                "Licensed Behavior Experts",
                "Personal Support for Families",
                "Free Parent Assessment",
                "Guided Days Behavior Support"
            ],
            "descriptions": [
                "Get a step-by-step action plan and expert support to manage child aggression & hitting.",
                "Understand the root causes of aggressive outbursts and de-escalate without punishment.",
                "Practical home strategies for parents of neurodivergent children facing anger challenges.",
                "Take a quick assessment to get matched with a licensed behavior specialist today."
            ],
            "keywords": [
                KeywordSpec(text="child aggression help", match_type="PHRASE"),
                KeywordSpec(text="how to stop child hitting", match_type="PHRASE"),
                KeywordSpec(text="child biting and hitting parents", match_type="PHRASE"),
                KeywordSpec(text="aggressive behavior in toddlers", match_type="PHRASE"),
                KeywordSpec(text="child anger outbursts", match_type="PHRASE"),
                KeywordSpec(text="how to handle aggressive child", match_type="PHRASE"),
                KeywordSpec(text="child hitting when angry", match_type="PHRASE"),
                KeywordSpec(text="why is my child so aggressive", match_type="PHRASE"),
                KeywordSpec(text="child aggressive behavior support", match_type="PHRASE"),
                KeywordSpec(text="parent coaching aggressive child", match_type="PHRASE"),
                KeywordSpec(text="child aggression", match_type="EXACT"),
                KeywordSpec(text="how to stop child hitting", match_type="EXACT"),
                KeywordSpec(text="child aggressive behavior", match_type="EXACT"),
                KeywordSpec(text="aggressive toddler help", match_type="EXACT"),
            ]
        },
        {
            "resource_name": f"customers/{customer_id}/adGroups/204500643491",
            "name": "Noncompliance",
            "url": "https://guideddays.com/en-US/problems/noncompliance",
            "headlines": [
                "Child Refuses to Listen?",
                "Fix Defiance & Disobedience",
                "Stop Constant Power Struggles",
                "Get Children to Cooperate",
                "Behavior Parent Guidance",
                "Understand Child Defiance",
                "Practical Parent Strategies",
                "Why Child Won't Follow Rules",
                "Step-by-Step Action Plan",
                "Improve Parent Communication",
                "Defiance & Disobedience Help",
                "Licensed Behavior Experts",
                "Individual Family Coaching",
                "Free Parent Assessment",
                "Guided Days Parent Support"
            ],
            "descriptions": [
                "End power struggles & bedtime refusal with a clear behavioral plan and specialist support.",
                "Learn practical strategies to get your child to listen & follow rules without yelling.",
                "Specialized guidance for parents dealing with extreme defiance and noncompliance.",
                "Start with a 2-minute assessment to connect with an experienced behavior coach."
            ],
            "keywords": [
                KeywordSpec(text="child refuses to listen", match_type="PHRASE"),
                KeywordSpec(text="how to handle defiant child", match_type="PHRASE"),
                KeywordSpec(text="child disobedience help", match_type="PHRASE"),
                KeywordSpec(text="power struggles with children", match_type="PHRASE"),
                KeywordSpec(text="child won't follow instructions", match_type="PHRASE"),
                KeywordSpec(text="extreme child defiance", match_type="PHRASE"),
                KeywordSpec(text="how to get child to cooperate", match_type="PHRASE"),
                KeywordSpec(text="parent coaching defiant child", match_type="PHRASE"),
                KeywordSpec(text="child defiance strategies", match_type="PHRASE"),
                KeywordSpec(text="dealing with noncompliant child", match_type="PHRASE"),
                KeywordSpec(text="defiant child help", match_type="EXACT"),
                KeywordSpec(text="child won't listen", match_type="EXACT"),
                KeywordSpec(text="child disobedience", match_type="EXACT"),
                KeywordSpec(text="child power struggles", match_type="EXACT"),
            ]
        },
        {
            "resource_name": f"customers/{customer_id}/adGroups/198157437105",
            "name": "Screen Time",
            "url": "https://guideddays.com/en-US/problems/screen-time",
            "headlines": [
                "Child Screen Time Addiction?",
                "End iPad & Phone Meltdowns",
                "Healthy Screen Limits Plan",
                "Screen Addiction Support",
                "Stop Screen Time Tantrums",
                "Manage Gaming & Tablet Use",
                "Gentle Screen Detox Plan",
                "No Screentime Tantrums Help",
                "Balanced Family Routine",
                "Transition Off Screens Easily",
                "Screen Time Parent Support",
                "Licensed Behavior Experts",
                "Personalized Parent Plan",
                "Free Parent Assessment",
                "Guided Days Behavior Support"
            ],
            "descriptions": [
                "Get a step-by-step plan to transition off screens without crying, tantrums, or meltdowns.",
                "Establish healthy screen limits and build engaging offline routines for your child.",
                "Expert behavioral support for parents dealing with screen addiction & iPad refusal.",
                "Complete a quick assessment to match with a licensed parent coach for screen challenges."
            ],
            "keywords": [
                KeywordSpec(text="child screen time addiction", match_type="PHRASE"),
                KeywordSpec(text="how to reduce child screen time", match_type="PHRASE"),
                KeywordSpec(text="screen time tantrums child", match_type="PHRASE"),
                KeywordSpec(text="ipad addiction in toddlers", match_type="PHRASE"),
                KeywordSpec(text="stopping screen meltdowns", match_type="PHRASE"),
                KeywordSpec(text="healthy screen limits kids", match_type="PHRASE"),
                KeywordSpec(text="child obsession with screens", match_type="PHRASE"),
                KeywordSpec(text="child meltdown taking phone", match_type="PHRASE"),
                KeywordSpec(text="screen detox for children", match_type="PHRASE"),
                KeywordSpec(text="parent guide to screen time", match_type="PHRASE"),
                KeywordSpec(text="child screen addiction", match_type="EXACT"),
                KeywordSpec(text="how to limit screen time", match_type="EXACT"),
                KeywordSpec(text="screen time meltdowns", match_type="EXACT"),
                KeywordSpec(text="child ipad addiction", match_type="EXACT"),
            ]
        }
    ]

    for ag_info in ad_groups:
        print(f"\n[+] Populating RSA and Keywords for '{ag_info['name']}' ({ag_info['resource_name']})...")
        rsa_spec = ResponsiveSearchAdSpec(
            headlines=ag_info["headlines"],
            descriptions=ag_info["descriptions"],
            final_url=ag_info["url"]
        )
        rsa_res = ad_group_mgr.create_responsive_search_ad(ag_info["resource_name"], rsa_spec)
        print(f"    -> Created RSA: {rsa_res}")

        kw_res = ad_group_mgr.add_keywords(ag_info["resource_name"], ag_info["keywords"])
        print(f"    -> Added {len(kw_res)} keywords successfully.")

if __name__ == "__main__":
    main()
