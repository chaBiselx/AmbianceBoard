#!/usr/bin/env python3
"""Summarize the ZAP JSON report for a GitHub Actions run."""

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "zap-reports" / "zap-report.json"
RISK_NAMES = {3: "High", 2: "Medium", 1: "Low", 0: "Informational"}
RISK_ORDER = ("High", "Medium", "Low", "Informational", "Unknown")


def risk_name(alert: dict) -> str:
    try:
        risk_code = int(alert.get("riskcode"))
    except (TypeError, ValueError):
        return "Unknown"
    return RISK_NAMES.get(risk_code, "Unknown")


def instance_count(alert: dict) -> int:
    try:
        return int(alert.get("count", 0))
    except (TypeError, ValueError):
        return len(alert.get("instances", []))


def markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_summary() -> tuple[list[str], bool, bool]:
    summary = ["### OWASP ZAP security scan", ""]
    has_high = False
    try:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        alerts = [
            alert
            for site in report.get("site", [])
            for alert in site.get("alerts", [])
        ]
        alert_counts: dict[str, int] = {}
        instance_counts: dict[str, int] = {}

        for alert in alerts:
            risk = risk_name(alert)
            alert_counts[risk] = alert_counts.get(risk, 0) + 1
            instance_counts[risk] = instance_counts.get(risk, 0) + instance_count(alert)
            has_high |= risk == "High"

        summary.extend(
            [
                f"Scan report generated: `{markdown_cell(report.get('created', 'unknown'))}`.",
                "",
                "| Risk | Alerts | Instances |",
                "|---|---:|---:|",
            ]
        )
        for risk in RISK_ORDER:
            if alert_counts.get(risk, 0):
                summary.append(
                    f"| {risk} | {alert_counts[risk]} | {instance_counts[risk]} |"
                )

        summary.extend(["", "| Risk | Rule | Instances |", "|---|---|---:|"])
        for alert in sorted(alerts, key=lambda item: RISK_ORDER.index(risk_name(item))):
            summary.append(
                f"| {risk_name(alert)} | {markdown_cell(alert.get('pluginid', 'n/a'))} — "
                f"{markdown_cell(alert.get('alert', 'Unknown rule'))} | {instance_count(alert)} |"
            )
        if not alerts:
            summary.append("| None | No alerts found | 0 |")
        return summary, has_high, True
    except Exception as error:
        summary.extend(
            [
                "ZAP did not produce a readable JSON report.",
                f"Details: `{type(error).__name__}`.",
            ]
        )
        return summary, False, False


def append_github_file(environment_key: str, content: str) -> None:
    path = os.environ.get(environment_key)
    if path:
        with open(path, "a", encoding="utf-8") as output_file:
            output_file.write(content)
    else:
        print(content, end="")


def main() -> None:
    summary, has_high, report_valid = build_summary()
    append_github_file("GITHUB_STEP_SUMMARY", "\n".join(summary) + "\n")
    append_github_file(
        "GITHUB_OUTPUT",
        f"has_high={'true' if has_high else 'false'}\n"
        f"report_valid={'true' if report_valid else 'false'}\n",
    )


if __name__ == "__main__":
    main()