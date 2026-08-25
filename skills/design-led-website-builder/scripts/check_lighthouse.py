#!/usr/bin/env python3
"""Run a pinned Lighthouse lab check without adding project dependencies or report files."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys


BASE_URL = os.environ.get("VERTICAL_SLICE_URL", "http://127.0.0.1:4173")
LIGHTHOUSE_PACKAGE = os.environ.get("LIGHTHOUSE_PACKAGE", "lighthouse@13.4.1")
DEFAULT_CHROME_CANDIDATES = (
    os.environ.get("CHROME_PATH", ""),
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


def resolve_chrome() -> str | None:
    for candidate in DEFAULT_CHROME_CANDIDATES:
        if candidate and os.path.exists(candidate):
            return candidate
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    return None



def score(report: dict, category: str) -> float:
    value = report.get("categories", {}).get(category, {}).get("score")
    if not isinstance(value, (int, float)):
        raise ValueError(f"Lighthouse report has no numeric {category} score.")
    return float(value)


def metric(report: dict, audit_id: str) -> str:
    audit = report.get("audits", {}).get(audit_id, {})
    display = audit.get("displayValue")
    if isinstance(display, str):
        return display
    numeric = audit.get("numericValue")
    return str(round(numeric, 2)) if isinstance(numeric, (int, float)) else "not reported"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=BASE_URL)
    parser.add_argument("--min-performance", type=float, default=0.95)
    parser.add_argument("--min-accessibility", type=float, default=1.0)
    parser.add_argument("--min-best-practices", type=float, default=1.0)
    args = parser.parse_args()

    npx = shutil.which("npx")
    if not npx:
        print("ERROR: npx is required for the ephemeral Lighthouse check.", file=sys.stderr)
        return 2

    environment = os.environ.copy()
    chrome = resolve_chrome()
    if "CHROME_PATH" not in environment and chrome:
        environment["CHROME_PATH"] = chrome

    command = [
        npx,
        "--yes",
        LIGHTHOUSE_PACKAGE,
        args.url,
        "--only-categories=performance,accessibility,best-practices",
        "--output=json",
        "--output-path=stdout",
        "--quiet",
        "--disable-full-page-screenshot",
        "--no-enable-error-reporting",
        "--chrome-flags=--headless=new --no-sandbox --disable-gpu",
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
        timeout=120,
    )
    if result.returncode:
        print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
        return result.returncode
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Lighthouse did not return valid JSON: {exc}", file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        return 1

    thresholds = {
        "performance": args.min_performance,
        "accessibility": args.min_accessibility,
        "best-practices": args.min_best_practices,
    }
    scores = {category: score(report, category) for category in thresholds}
    failed_categories = {
        category
        for category, minimum in thresholds.items()
        if scores[category] < minimum
    }
    failures = [
        f"{category} {scores[category]:.0%} < {minimum:.0%}"
        for category, minimum in thresholds.items()
        if category in failed_categories
    ]

    print(
        "Lighthouse scores: "
        + ", ".join(f"{category} {value:.0%}" for category, value in scores.items())
    )
    print(
        "Lab metrics: "
        f"FCP {metric(report, 'first-contentful-paint')}, "
        f"LCP {metric(report, 'largest-contentful-paint')}, "
        f"TBT {metric(report, 'total-blocking-time')}, "
        f"CLS {metric(report, 'cumulative-layout-shift')}, "
        f"transfer {metric(report, 'total-byte-weight')}"
    )

    if failures:
        print("ERROR: " + "; ".join(failures), file=sys.stderr)
        category_audits = {
            reference["id"]
            for category in failed_categories
            for reference in report["categories"][category].get("auditRefs", [])
        }
        failed_audits = []
        for audit_id in sorted(category_audits):
            audit = report.get("audits", {}).get(audit_id, {})
            audit_score = audit.get("score")
            if isinstance(audit_score, (int, float)) and audit_score < 1:
                display = audit.get("displayValue")
                suffix = f" — {display}" if isinstance(display, str) else ""
                failed_audits.append(f"{audit_id}: {audit.get('title', audit_id)}{suffix}")
        if failed_audits:
            print("Named audit signals:\n- " + "\n- ".join(failed_audits), file=sys.stderr)
        return 1

    print("OK: pinned Lighthouse category thresholds passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
