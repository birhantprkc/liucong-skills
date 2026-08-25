#!/usr/bin/env python3
"""Run deterministic structural acceptance checks for this Skill package."""

from __future__ import annotations

import argparse
import re
import sys
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

import yaml

sys.dont_write_bytecode = True

import catalog
import validate_dossier


DEFAULT_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_NAME = "design-led-website-builder"
LOCAL_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
CSS_URL_PATTERN = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)")
SCAFFOLD_PATTERN = re.compile(
    r"\b(?:TODO|FIXME)\b|Replace with description of the skill",
    re.IGNORECASE,
)
REQUIRED_PATHS = {
    "SKILL.md",
    "agents/openai.yaml",
    "references/brief-to-direction.md",
    "references/design-taxonomy.md",
    "references/design-to-build.md",
    "references/example-audit-gionatan-nese.md",
    "references/example-dossier-ai-research.yaml",
    "references/example-reference-pass-ai-research.md",
    "references/example-thin-brief.md",
    "references/forward-tests.yaml",
    "references/intake.md",
    "references/quality-rubric.md",
    "references/research-pass.md",
    "references/site-audit-protocol.md",
    "references/site-catalog.yaml",
    "references/visual-craft.md",
    "references/visual-evidence-and-assets.md",
    "scripts/catalog.py",
    "scripts/audit_vertical_slice.py",
    "scripts/check_lighthouse.py",
    "scripts/test_vertical_slice.py",
    "scripts/validate_dossier.py",
    "scripts/validate_skill.py",
    "scripts/with_server.py",
    "pyproject.toml",
    "assets/e2e-fixture/index.html",
    "assets/e2e-fixture/styles.css",
    "assets/e2e-fixture/app.js",
}


class LocalAssetParser(HTMLParser):
    """Collect local href and src references from one HTML document."""

    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


def load_mapping(path: Path, label: str, errors: list[str]) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{label} could not be read as YAML: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{label} must contain a YAML mapping.")
        return {}
    return data


def local_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
        return None
    if "://" in target:
        return None
    target = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not target:
        return None
    return (source.parent / target).resolve()


def validate_entrypoint(root: Path, errors: list[str]) -> None:
    skill_path = root / "SKILL.md"
    try:
        text = skill_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"SKILL.md could not be read: {exc}")
        return
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        errors.append("SKILL.md must begin with YAML frontmatter delimited by ---.")
        return
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        errors.append(f"SKILL.md frontmatter is invalid YAML: {exc}")
        return
    if not isinstance(frontmatter, dict):
        errors.append("SKILL.md frontmatter must be a mapping.")
        return
    if frontmatter.get("name") != EXPECTED_NAME:
        errors.append(f"SKILL.md name must be {EXPECTED_NAME!r}.")
    description = frontmatter.get("description")
    if not isinstance(description, str) or len(description.strip()) < 40:
        errors.append("SKILL.md description must state a discriminating capability and trigger.")
    if SCAFFOLD_PATTERN.search(text):
        errors.append("SKILL.md contains an unfinished scaffold marker.")

    metadata = load_mapping(root / "agents/openai.yaml", "agents/openai.yaml", errors)
    interface = metadata.get("interface")
    if not isinstance(interface, dict):
        errors.append("agents/openai.yaml.interface must be a mapping.")
        return
    for field in ("display_name", "short_description", "default_prompt"):
        if not isinstance(interface.get(field), str) or not interface[field].strip():
            errors.append(f"agents/openai.yaml.interface.{field} must be non-empty.")
    prompt = interface.get("default_prompt", "")
    if isinstance(prompt, str) and f"${EXPECTED_NAME}" not in prompt:
        errors.append(f"agents/openai.yaml default_prompt must invoke ${EXPECTED_NAME}.")


def validate_markdown(root: Path, errors: list[str]) -> None:
    markdown_files = sorted(root.rglob("*.md"))
    graph: dict[Path, set[Path]] = {path.resolve(): set() for path in markdown_files}
    for source in markdown_files:
        try:
            text = source.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{source.relative_to(root)} could not be read: {exc}")
            continue
        for raw_target in LOCAL_LINK_PATTERN.findall(text):
            destination = local_target(source, raw_target)
            if destination is None:
                continue
            if not destination.exists():
                errors.append(
                    f"Broken local link in {source.relative_to(root)}: {raw_target}"
                )
                continue
            if destination.suffix.lower() == ".md" and destination in graph:
                graph[source.resolve()].add(destination)

    entrypoint = (root / "SKILL.md").resolve()
    reachable: set[Path] = set()
    queue: deque[Path] = deque([entrypoint])
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(graph.get(current, set()) - reachable)
    unreachable = sorted(
        path.relative_to(root)
        for path in graph
        if path != entrypoint and path not in reachable
    )
    if unreachable:
        errors.append(
            "Markdown references not discoverable from SKILL.md: "
            + ", ".join(str(path) for path in unreachable)
        )


def validate_fixture_assets(root: Path, errors: list[str]) -> None:
    fixture = root / "assets/e2e-fixture"
    html_path = fixture / "index.html"
    try:
        parser = LocalAssetParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"Fixture HTML could not be read: {exc}")
        return
    for raw_target in parser.references:
        destination = local_target(html_path, raw_target)
        if destination is not None and not destination.exists():
            errors.append(f"Broken fixture asset reference in index.html: {raw_target}")

    for stylesheet in fixture.glob("*.css"):
        try:
            text = stylesheet.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{stylesheet.relative_to(root)} could not be read: {exc}")
            continue
        for _quote, raw_target in CSS_URL_PATTERN.findall(text):
            destination = local_target(stylesheet, raw_target)
            if destination is not None and not destination.exists():
                errors.append(
                    f"Broken fixture asset reference in {stylesheet.name}: {raw_target}"
                )


def validate_scripts(root: Path, errors: list[str]) -> None:
    for script in sorted((root / "scripts").glob("*.py")):
        try:
            source = script.read_text(encoding="utf-8")
            compile(source, str(script), "exec")
        except (OSError, SyntaxError) as exc:
            errors.append(f"{script.relative_to(root)} failed syntax validation: {exc}")


def validate_domain_artifacts(root: Path, errors: list[str]) -> None:
    try:
        catalog_data = catalog.load_catalog(root / "references/site-catalog.yaml")
        errors.extend(f"catalog: {item}" for item in catalog.validate_catalog(catalog_data))
        tests = catalog.load_forward_tests(root / "references/forward-tests.yaml")
        errors.extend(
            f"forward tests: {item}"
            for item in catalog.validate_forward_tests(catalog_data, tests)
        )
    except ValueError as exc:
        errors.append(str(exc))

    try:
        dossier = validate_dossier.load_yaml(
            root / "references/example-dossier-ai-research.yaml"
        )
        errors.extend(
            f"example dossier: {item}"
            for item in validate_dossier.validate_dossier(dossier)
        )
    except ValueError as exc:
        errors.append(str(exc))


def validate_skill(root: Path) -> list[str]:
    errors: list[str] = []
    if root.name != EXPECTED_NAME:
        errors.append(f"Skill directory must be named {EXPECTED_NAME!r}.")
    missing = sorted(path for path in REQUIRED_PATHS if not (root / path).exists())
    if missing:
        errors.append("Missing required package paths: " + ", ".join(missing))
    generated = sorted(
        path.relative_to(root)
        for path in root.rglob("*")
        if path.name in {"__pycache__", ".DS_Store"} or path.suffix == ".pyc"
    )
    if generated:
        errors.append(
            "Generated artifacts must not ship in the Skill package: "
            + ", ".join(str(path) for path in generated)
        )
    validate_entrypoint(root, errors)
    validate_markdown(root, errors)
    validate_fixture_assets(root, errors)
    validate_scripts(root, errors)
    validate_domain_artifacts(root, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", nargs="?", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.skill_root.resolve()
    errors = validate_skill(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: structural Skill acceptance passed: {root}")
    print("NOTE: run the documented browser, accessibility, and Lighthouse checks separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
