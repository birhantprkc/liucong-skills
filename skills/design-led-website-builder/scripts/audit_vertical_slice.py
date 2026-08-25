#!/usr/bin/env python3
"""Audit the vertical-slice fixture for accessibility and lightweight performance budgets."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Browser, Page, sync_playwright


BASE_URL = os.environ.get("VERTICAL_SLICE_URL", "http://127.0.0.1:4173")
SKILL_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_ROOT = SKILL_ROOT / "assets" / "e2e-fixture"
INTERACTIVE_ROLES = {
    "button",
    "checkbox",
    "combobox",
    "link",
    "radio",
    "searchbox",
    "slider",
    "spinbutton",
    "switch",
    "tab",
    "textbox",
}


def load_page(browser: Browser, width: int, height: int) -> tuple[Page, list[str], list[str]]:
    page = browser.new_page(viewport={"width": width, "height": height})
    console_errors: list[str] = []
    requests: list[str] = []
    page.on(
        "console",
        lambda message: console_errors.append(message.text) if message.type == "error" else None,
    )
    page.on("pageerror", lambda error: console_errors.append(str(error)))
    page.on("request", lambda request: requests.append(request.url))
    page.add_init_script(
        """
        window.__auditMetrics = { cls: 0, longTasks: 0, lcp: 0 };
        new PerformanceObserver(list => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) window.__auditMetrics.cls += entry.value;
          }
        }).observe({ type: 'layout-shift', buffered: true });
        new PerformanceObserver(list => {
          window.__auditMetrics.longTasks += list.getEntries().length;
        }).observe({ type: 'longtask', buffered: true });
        new PerformanceObserver(list => {
          const entries = list.getEntries();
          if (entries.length) window.__auditMetrics.lcp = entries.at(-1).startTime;
        }).observe({ type: 'largest-contentful-paint', buffered: true });
        """
    )
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    return page, console_errors, requests


def audit_axe(browser: Browser, width: int, height: int) -> dict[str, object]:
    page, errors, _requests = load_page(browser, width, height)
    results = Axe().run(
        page,
        options={
            "runOnly": {
                "type": "tag",
                "values": ["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"],
            },
            "resultTypes": ["violations"],
        },
    )
    if results.violations_count:
        raise AssertionError(
            f"axe found {results.violations_count} violation groups at {width}x{height}:\n"
            f"{results.generate_report()}"
        )
    assert not errors, f"browser errors at {width}x{height}: {errors}"
    page.close()
    print(f"OK: axe WCAG A/AA scan at {width}x{height}: 0 violation groups")
    return {"viewport": f"{width}x{height}", "violation_groups": results.violations_count}


def audit_accessibility_tree(page: Page) -> dict[str, object]:
    session = page.context.new_cdp_session(page)
    nodes = session.send("Accessibility.getFullAXTree")["nodes"]
    exposed = [node for node in nodes if not node.get("ignored")]

    def value(node: dict, field: str) -> str:
        item = node.get(field) or {}
        return str(item.get("value") or "")

    roles = [value(node, "role") for node in exposed]
    unnamed = [
        value(node, "role")
        for node in exposed
        if value(node, "role") in INTERACTIVE_ROLES and not value(node, "name").strip()
    ]
    assert not unnamed, f"unnamed interactive accessibility nodes: {unnamed}"
    assert roles.count("main") == 1, f"expected one main landmark, found {roles.count('main')}"
    assert roles.count("banner") == 1, f"expected one banner landmark, found {roles.count('banner')}"
    assert roles.count("contentinfo") == 1, (
        f"expected one contentinfo landmark, found {roles.count('contentinfo')}"
    )
    assert roles.count("tab") == 3, f"expected three tabs, found {roles.count('tab')}"
    print(
        "OK: accessibility tree has named controls and unique banner/main/contentinfo landmarks"
    )
    return {
        "exposed_nodes": len(exposed),
        "named_interactive_nodes": sum(role in INTERACTIVE_ROLES for role in roles),
        "landmarks": {
            role: roles.count(role)
            for role in ("banner", "navigation", "main", "contentinfo")
        },
    }


def audit_budget(page: Page, requests: list[str]) -> dict[str, object]:
    origin = urlparse(BASE_URL).netloc
    external_requests = [
        request
        for request in requests
        if urlparse(request).scheme in {"http", "https"} and urlparse(request).netloc != origin
    ]
    assert not external_requests, f"external requests detected: {external_requests}"

    resources = page.evaluate(
        """
        () => {
          const nav = performance.getEntriesByType('navigation')[0];
          const paint = Object.fromEntries(
            performance.getEntriesByType('paint').map(entry => [entry.name, entry.startTime])
          );
          return {
            resources: performance.getEntriesByType('resource').map(entry => ({
              name: entry.name,
              transferSize: entry.transferSize,
              decodedBodySize: entry.decodedBodySize,
            })),
            domContentLoaded: nav.domContentLoadedEventEnd,
            load: nav.loadEventEnd,
            paint,
            observed: window.__auditMetrics,
            domNodes: document.querySelectorAll('*').length,
          };
        }
        """
    )
    local_source_bytes = sum(
        path.stat().st_size
        for path in FIXTURE_ROOT.iterdir()
        if path.suffix in {".html", ".css", ".js"}
    )
    transfer_bytes = sum(item["transferSize"] for item in resources["resources"])
    request_count = len(set(requests))

    assert request_count <= 4, f"request budget exceeded: {request_count}"
    assert local_source_bytes <= 100_000, f"local source budget exceeded: {local_source_bytes} bytes"
    assert transfer_bytes <= 150_000, f"transfer budget exceeded: {transfer_bytes} bytes"
    assert resources["domNodes"] <= 500, f"DOM node budget exceeded: {resources['domNodes']}"
    assert resources["observed"]["cls"] <= 0.05, (
        f"layout-shift budget exceeded: {resources['observed']['cls']}"
    )
    assert resources["observed"]["longTasks"] <= 2, (
        f"long-task budget exceeded: {resources['observed']['longTasks']}"
    )

    summary = {
        "requests": request_count,
        "external_requests": len(external_requests),
        "local_source_bytes": local_source_bytes,
        "transfer_bytes": transfer_bytes,
        "dom_nodes": resources["domNodes"],
        "cls": round(resources["observed"]["cls"], 4),
        "long_tasks": resources["observed"]["longTasks"],
        "fcp_ms": round(resources["paint"].get("first-contentful-paint", 0), 1),
        "lcp_ms": round(resources["observed"]["lcp"], 1),
        "dom_content_loaded_ms": round(resources["domContentLoaded"], 1),
        "load_ms": round(resources["load"], 1),
    }
    print(
        "OK: resource budget: "
        f"{request_count} requests, {local_source_bytes} source bytes, "
        f"{transfer_bytes} transfer bytes, {resources['domNodes']} DOM nodes, "
        f"CLS {summary['cls']}, {summary['long_tasks']} long tasks"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()
    report: dict[str, object] = {"url": BASE_URL, "axe": []}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for width, height in ((1440, 900), (390, 844)):
                report["axe"].append(audit_axe(browser, width, height))
            page, errors, requests = load_page(browser, 1440, 900)
            assert not errors, f"browser errors: {errors}"
            report["accessibility_tree"] = audit_accessibility_tree(page)
            report["performance_budget"] = audit_budget(page, requests)
            page.close()
        finally:
            browser.close()

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Report: {args.report}")
    print("OK: vertical-slice accessibility and performance audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
