#!/usr/bin/env python3
"""Browser acceptance checks for the static design-to-build vertical slice fixture."""

from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright


BASE_URL = os.environ.get("VERTICAL_SLICE_URL", "http://127.0.0.1:4173")
SCREENSHOT_DIR = Path(os.environ.get("VERTICAL_SLICE_SCREENSHOTS", "/tmp/design-led-website-builder"))


def capture_console(page: Page) -> list[str]:
    errors: list[str] = []
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: errors.append(str(error)))
    return errors


def assert_no_horizontal_overflow(page: Page) -> None:
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert overflow <= 1, f"horizontal overflow: {overflow}px"


def test_desktop(browser: Browser) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = capture_console(page)
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")

    assert page.get_by_role("heading", name="Keep every conclusion tethered to its source.").is_visible()
    assert page.get_by_role("navigation", name="Primary navigation").is_visible()
    assert page.get_by_role("link", name="Inspect the workflow").get_attribute("href") == "#workflow"
    assert page.locator("main").count() == 1
    assert page.locator("h1").count() == 1
    assert_no_horizontal_overflow(page)

    page.keyboard.press("Tab")
    skip_link = page.get_by_role("link", name="Skip to content")
    assert skip_link.evaluate("element => element === document.activeElement")
    assert skip_link.is_visible()
    page.keyboard.press("Escape")

    broken_fragments = page.evaluate(
        """
        [...document.querySelectorAll('a[href^="#"]')]
          .map(link => link.getAttribute('href'))
          .filter(href => href.length > 1 && !document.querySelector(href))
        """
    )
    assert not broken_fragments, f"broken fragment links: {broken_fragments}"

    compare_tab = page.get_by_role("tab", name="02 Compare claims Keep conflicts visible")
    compare_tab.click()
    assert compare_tab.get_attribute("aria-selected") == "true"
    assert page.get_by_role("tabpanel", name="02 Compare claims Keep conflicts visible").is_visible()
    assert not page.get_by_role("tabpanel", name="01 Assemble sources Define scope and provenance").is_visible()

    compare_tab.press("ArrowRight")
    review_tab = page.get_by_role("tab", name="03 Review synthesis Return judgment to people")
    assert review_tab.get_attribute("aria-selected") == "true"
    assert review_tab.evaluate("element => element === document.activeElement")

    form = page.locator(".evaluation-form")
    form.get_by_role("button", name="Validate this fixture request").click()
    assert page.locator("#name").get_attribute("aria-invalid") == "true"
    assert page.locator("#name").evaluate("element => element === document.activeElement")
    assert "Nothing has been submitted" in page.get_by_role("status").inner_text()

    page.locator("#name").fill("Research lead")
    page.locator("#email").fill("lead@example.com")
    page.locator("#team").fill("Verify source trails and review states.")
    form.get_by_role("button", name="Validate this fixture request").click()
    assert "No request or personal data was sent" in page.get_by_role("status").inner_text()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=SCREENSHOT_DIR / "desktop.png", full_page=True)
    assert not errors, f"browser errors: {errors}"
    page.close()
    print("OK: desktop semantics, tabs, keyboard, form states, and overflow")


def test_mobile(browser: Browser) -> None:
    for width, height in ((390, 844), (320, 568)):
        page = browser.new_page(viewport={"width": width, "height": height})
        errors = capture_console(page)
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        assert_no_horizontal_overflow(page)

        menu = page.get_by_role("button", name="Menu")
        assert menu.is_visible()
        assert menu.get_attribute("aria-expanded") == "false"
        menu.click()
        assert menu.get_attribute("aria-expanded") == "true"
        assert page.get_by_role("navigation", name="Primary navigation").is_visible()
        page.get_by_role("link", name="How it works").click()
        assert menu.get_attribute("aria-expanded") == "false"

        if width == 390:
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=SCREENSHOT_DIR / "mobile.png", full_page=True)
        assert not errors, f"browser errors at {width}px: {errors}"
        page.close()
    print("OK: 390px and 320px navigation and overflow")


def test_reduced_motion(browser: Browser) -> None:
    page = browser.new_page(
        viewport={"width": 1024, "height": 768},
        reduced_motion="reduce",
    )
    errors = capture_console(page)
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
    duration = page.locator(".map-line").evaluate("element => getComputedStyle(element).animationDuration")
    duration_seconds = float(duration.removesuffix("s"))
    assert duration_seconds <= 0.001, f"unexpected reduced animation duration: {duration}"
    assert page.locator("html").evaluate("element => getComputedStyle(element).scrollBehavior") == "auto"
    assert not errors, f"browser errors: {errors}"
    page.close()
    print("OK: reduced-motion behavior")


def test_javascript_failure(browser: Browser) -> None:
    context = browser.new_context(
        viewport={"width": 390, "height": 844},
        java_script_enabled=False,
    )
    page = context.new_page()
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    assert page.get_by_role("navigation", name="Primary navigation").is_visible()
    panels = page.get_by_role("tabpanel").all()
    assert len(panels) == 3 and all(panel.is_visible() for panel in panels)
    assert page.locator("main noscript").is_visible()
    assert_no_horizontal_overflow(page)
    context.close()
    print("OK: JavaScript-disabled content and navigation fallback")


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            test_desktop(browser)
            test_mobile(browser)
            test_reduced_motion(browser)
            test_javascript_failure(browser)
        finally:
            browser.close()
    print(f"OK: vertical slice browser acceptance passed; screenshots: {SCREENSHOT_DIR}")


if __name__ == "__main__":
    main()
