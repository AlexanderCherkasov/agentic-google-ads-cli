from typing import List, Dict, Any
from src.campaigns.models import CampaignSpec, AdGroupSpec

class CampaignDiffEngine:
    """Compares local Markdown CampaignSpec with Live/Remote CampaignSpec."""

    @staticmethod
    def calculate_diff(local: CampaignSpec, remote: CampaignSpec) -> Dict[str, Any]:
        diffs = {
            "campaign_name": local.name,
            "has_changes": False,
            "budget": None,
            "status": None,
            "ad_groups_to_add": [],
            "ad_groups_to_update": [],
        }

        # 1. Budget check
        if round(local.daily_budget_usd, 2) != round(remote.daily_budget_usd, 2):
            diffs["budget"] = {
                "from": remote.daily_budget_usd,
                "to": local.daily_budget_usd
            }
            diffs["has_changes"] = True

        # 2. Status check
        if local.status.upper() != remote.status.upper():
            diffs["status"] = {
                "from": remote.status,
                "to": local.status
            }
            diffs["has_changes"] = True

        # 3. Ad Groups check
        remote_ag_map = {ag.name: ag for ag in remote.ad_groups}
        local_ag_map = {ag.name: ag for ag in local.ad_groups}

        for ag_name, local_ag in local_ag_map.items():
            if ag_name not in remote_ag_map:
                diffs["ad_groups_to_add"].append(local_ag)
                diffs["has_changes"] = True
            else:
                remote_ag = remote_ag_map[ag_name]
                ag_changes = CampaignDiffEngine._diff_ad_group(local_ag, remote_ag)
                if ag_changes["has_changes"]:
                    diffs["ad_groups_to_update"].append(ag_changes)
                    diffs["has_changes"] = True

        return diffs

    @staticmethod
    def _diff_ad_group(local_ag: AdGroupSpec, remote_ag: AdGroupSpec) -> Dict[str, Any]:
        ag_diff = {
            "name": local_ag.name,
            "has_changes": False,
            "cpc": None,
            "new_keywords": [],
        }

        if round(local_ag.max_cpc_usd, 2) != round(remote_ag.max_cpc_usd, 2):
            ag_diff["cpc"] = {
                "from": remote_ag.max_cpc_usd,
                "to": local_ag.max_cpc_usd
            }
            ag_diff["has_changes"] = True

        remote_kw_set = {(kw.text.lower(), kw.match_type.upper()) for kw in remote_ag.keywords}
        for kw in local_ag.keywords:
            if (kw.text.lower(), kw.match_type.upper()) not in remote_kw_set:
                ag_diff["new_keywords"].append(kw)
                ag_diff["has_changes"] = True

        return ag_diff

    @staticmethod
    def format_diff_report(diffs: Dict[str, Any]) -> str:
        report = []
        report.append(f"🔍 DIFF REPORT for Campaign: '{diffs['campaign_name']}'")
        report.append("=" * 60)

        if not diffs["has_changes"]:
            report.append("✅ Local Markdown spec is fully synchronized with Google Ads!")
            return "\n".join(report)

        if diffs["budget"]:
            report.append(f"💰 Budget change: ${diffs['budget']['from']:.2f} -> ${diffs['budget']['to']:.2f}")

        if diffs["status"]:
            report.append(f"🔄 Status change: {diffs['status']['from']} -> {diffs['status']['to']}")

        if diffs["ad_groups_to_add"]:
            report.append(f"\n➕ New Ad Groups to create ({len(diffs['ad_groups_to_add'])}):")
            for ag in diffs["ad_groups_to_add"]:
                report.append(f"   + Ad Group: '{ag.name}' (Max CPC: ${ag.max_cpc_usd:.2f})")

        if diffs["ad_groups_to_update"]:
            report.append(f"\n✏️ Existing Ad Groups to update:")
            for ag_up in diffs["ad_groups_to_update"]:
                report.append(f"   ~ Ad Group: '{ag_up['name']}'")
                if ag_up["cpc"]:
                    report.append(f"     - CPC: ${ag_up['cpc']['from']:.2f} -> ${ag_up['cpc']['to']:.2f}")
                if ag_up["new_keywords"]:
                    report.append(f"     - New keywords ({len(ag_up['new_keywords'])}):")
                    for kw in ag_up["new_keywords"]:
                        report.append(f"       + [{kw.match_type}] {kw.text}")

        report.append("=" * 60)
        return "\n".join(report)
