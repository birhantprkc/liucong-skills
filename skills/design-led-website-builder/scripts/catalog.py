#!/usr/bin/env python3
"""Validate and query the design reference source catalog."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = SKILL_ROOT / "references" / "site-catalog.yaml"
DEFAULT_FORWARD_TESTS = SKILL_ROOT / "references" / "forward-tests.yaml"
TAG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEARCH_FIELDS = {
    "scenario": ("scenarios", 5),
    "style": ("styles", 4),
    "component": ("components", 3),
    "motion": ("motion", 3),
    "tech": ("tech_lenses", 2),
    "strength": ("strengths", 2),
}
REQUIRED_FIELDS = {
    "id",
    "name",
    "url",
    "source_type",
    "access",
    "coverage",
    "scenarios",
    "styles",
    "components",
    "motion",
    "tech_lenses",
    "strengths",
    "use_when",
    "caveats",
    "evidence",
}


def load_catalog(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Catalog not found: {path}") from None
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Catalog root must be a mapping.")
    return data


def load_forward_tests(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Forward tests not found: {path}") from None
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid forward-test YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Forward-test root must be a mapping.")
    return data


def validate_catalog(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data.get("schema_version"), str):
        errors.append("schema_version must be a quoted string.")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        return errors + ["sources must be a non-empty list."]

    seen_ids: set[str] = set()
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be a mapping.")
            continue
        missing = sorted(REQUIRED_FIELDS - source.keys())
        if missing:
            errors.append(f"{label} missing fields: {', '.join(missing)}")
        source_id = source.get("id")
        if not isinstance(source_id, str) or not TAG_PATTERN.fullmatch(source_id):
            errors.append(f"{label}.id must be a lowercase slug.")
        elif source_id in seen_ids:
            errors.append(f"Duplicate id: {source_id}")
        else:
            seen_ids.add(source_id)

        url = source.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"{label}.url must be an https URL.")

        for field in (
            "coverage",
            "scenarios",
            "styles",
            "components",
            "motion",
            "tech_lenses",
            "strengths",
        ):
            values = source.get(field)
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                errors.append(f"{label}.{field} must be a list of strings.")
                continue
            duplicates = sorted({value for value in values if values.count(value) > 1})
            if duplicates:
                errors.append(f"{label}.{field} has duplicates: {', '.join(duplicates)}")
            invalid = sorted(value for value in values if not TAG_PATTERN.fullmatch(value))
            if invalid:
                errors.append(f"{label}.{field} has invalid tags: {', '.join(invalid)}")

        evidence = source.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{label}.evidence must be a non-empty list.")
        else:
            for evidence_index, item in enumerate(evidence):
                if not isinstance(item, dict):
                    errors.append(f"{label}.evidence[{evidence_index}] must be a mapping.")
                    continue
                for field in ("url", "checked_at", "basis"):
                    if not isinstance(item.get(field), str) or not item[field].strip():
                        errors.append(f"{label}.evidence[{evidence_index}].{field} is required.")
    return errors


def normalize(values: list[str] | None) -> list[str]:
    result: list[str] = []
    for value in values or []:
        for item in value.split(","):
            item = item.strip().lower()
            if item and item not in result:
                result.append(item)
    return result


def match_sources(data: dict[str, Any], requested: dict[str, list[str]]) -> list[dict[str, Any]]:
    requested_labels = [
        f"{argument}:{tag}"
        for argument in SEARCH_FIELDS
        for tag in requested[argument]
    ]
    requested_count = len(requested_labels)
    results: list[dict[str, Any]] = []
    for source in data["sources"]:
        score = 0
        matches: list[str] = []
        for argument, (field, weight) in SEARCH_FIELDS.items():
            available = set(source.get(field, []))
            for tag in requested[argument]:
                if tag in available:
                    score += weight
                    matches.append(f"{argument}:{tag}")
        if score:
            missing = [label for label in requested_labels if label not in matches]
            results.append(
                {
                    "score": score,
                    "matches": matches,
                    "missing": missing,
                    "matched_count": len(matches),
                    "requested_count": requested_count,
                    "coverage": len(matches) / requested_count if requested_count else 0.0,
                    "source": source,
                }
            )
    return sorted(
        results,
        key=lambda item: (-item["coverage"], -item["score"], item["source"]["id"]),
    )


def cmd_validate(data: dict[str, Any]) -> int:
    errors = validate_catalog(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(data['sources'])} catalog sources are valid.")
    return 0


def cmd_match(data: dict[str, Any], args: argparse.Namespace) -> int:
    requested = {name: normalize(getattr(args, name)) for name in SEARCH_FIELDS}
    if not any(requested.values()):
        print("Provide at least one match filter.", file=sys.stderr)
        return 2
    if not 0.0 <= args.min_coverage <= 1.0:
        print("--min-coverage must be between 0 and 1.", file=sys.stderr)
        return 2
    results = [
        result
        for result in match_sources(data, requested)
        if result["coverage"] >= args.min_coverage
    ]
    for result in results[: args.limit]:
        source = result["source"]
        coverage = f"{result['coverage']:.0%}"
        missing = ", ".join(result["missing"]) if result["missing"] else "none"
        print(
            f"{result['score']:>2}  {source['id']:<20}  {source['name']}\n"
            f"    {source['url']}\n"
            f"    coverage: {result['matched_count']}/{result['requested_count']} ({coverage})\n"
            f"    matches: {', '.join(result['matches'])}\n"
            f"    missing: {missing}\n"
            f"    use when: {source['use_when']}"
        )
    if not results:
        print("No catalog matches at the requested coverage. Broaden one axis or research live sources.")
    return 0


def validate_forward_tests(catalog: dict[str, Any], tests: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(tests.get("schema_version"), str):
        errors.append("forward tests schema_version must be a quoted string.")
    cases = tests.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["forward tests cases must be a non-empty list."]

    tag_universe = {
        argument: {
            value
            for source in catalog["sources"]
            for value in source[field]
        }
        for argument, (field, _weight) in SEARCH_FIELDS.items()
    }
    seen_ids: set[str] = set()
    allowed_modes = {"direct-build", "reference-pass", "forensic-audit"}

    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be a mapping.")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not TAG_PATTERN.fullmatch(case_id):
            errors.append(f"{label}.id must be a lowercase slug.")
        elif case_id in seen_ids:
            errors.append(f"Duplicate forward-test id: {case_id}")
        else:
            seen_ids.add(case_id)

        prompt = case.get("prompt")
        if not isinstance(prompt, str) or len(prompt.strip()) < 30:
            errors.append(f"{label}.prompt must be a realistic request of at least 30 characters.")
        if case.get("research_mode") not in allowed_modes:
            errors.append(f"{label}.research_mode must be one of {sorted(allowed_modes)}.")

        for field in ("behavioral_invariants", "failure_signals"):
            values = case.get(field)
            if not isinstance(values, list) or not values or any(
                not isinstance(value, str) or not value.strip() for value in values
            ):
                errors.append(f"{label}.{field} must be a non-empty list of strings.")

        raw_query = case.get("catalog_query")
        if not isinstance(raw_query, dict) or not raw_query:
            errors.append(f"{label}.catalog_query must be a non-empty mapping.")
            continue
        unknown_fields = sorted(set(raw_query) - set(SEARCH_FIELDS))
        if unknown_fields:
            errors.append(f"{label}.catalog_query has unknown fields: {', '.join(unknown_fields)}")
            continue

        requested = {
            argument: normalize(raw_query.get(argument))
            for argument in SEARCH_FIELDS
        }
        if not any(requested.values()):
            errors.append(f"{label}.catalog_query must request at least one tag.")
            continue
        for argument, tags in requested.items():
            unknown_tags = sorted(set(tags) - tag_universe[argument])
            if unknown_tags:
                errors.append(
                    f"{label}.catalog_query.{argument} has unknown tags: "
                    f"{', '.join(unknown_tags)}"
                )

        minimum = case.get("minimum")
        if not isinstance(minimum, dict):
            errors.append(f"{label}.minimum must be a mapping.")
            continue
        threshold = minimum.get("coverage_threshold")
        min_results = minimum.get("results_at_threshold")
        min_types = minimum.get("source_types")
        if not isinstance(threshold, (int, float)) or not 0.0 <= threshold <= 1.0:
            errors.append(f"{label}.minimum.coverage_threshold must be between 0 and 1.")
            continue
        if not isinstance(min_results, int) or min_results < 1:
            errors.append(f"{label}.minimum.results_at_threshold must be a positive integer.")
            continue
        if not isinstance(min_types, int) or min_types < 1:
            errors.append(f"{label}.minimum.source_types must be a positive integer.")
            continue

        results = match_sources(catalog, requested)
        qualified = [result for result in results if result["coverage"] >= threshold]
        if len(qualified) < min_results:
            errors.append(
                f"{label} expected {min_results} results at {threshold:.0%} coverage; "
                f"found {len(qualified)}."
            )
        source_types = {result["source"]["source_type"] for result in qualified}
        if len(source_types) < min_types:
            errors.append(
                f"{label} expected {min_types} source types at {threshold:.0%} coverage; "
                f"found {len(source_types)}."
            )
    return errors


def cmd_forward_test(catalog: dict[str, Any], path: Path) -> int:
    try:
        tests = load_forward_tests(path)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    errors = validate_forward_tests(catalog, tests)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    for case in tests["cases"]:
        requested = {
            argument: normalize(case["catalog_query"].get(argument))
            for argument in SEARCH_FIELDS
        }
        threshold = case["minimum"]["coverage_threshold"]
        qualified = [
            result
            for result in match_sources(catalog, requested)
            if result["coverage"] >= threshold
        ]
        ids = ", ".join(result["source"]["id"] for result in qualified)
        print(f"OK: {case['id']} -> {ids}")
    print(f"OK: {len(tests['cases'])} forward-routing cases passed.")
    return 0


def cmd_tags(data: dict[str, Any], field: str) -> int:
    catalog_field = SEARCH_FIELDS[field][0]
    values = sorted({value for source in data["sources"] for value in source[catalog_field]})
    print("\n".join(values))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")

    match_parser = subparsers.add_parser("match")
    for argument in SEARCH_FIELDS:
        match_parser.add_argument(f"--{argument}", action="append")
    match_parser.add_argument("--limit", type=int, default=6)
    match_parser.add_argument("--min-coverage", type=float, default=0.0)

    tags_parser = subparsers.add_parser("tags")
    tags_parser.add_argument("field", choices=sorted(SEARCH_FIELDS))
    test_parser = subparsers.add_parser("test")
    test_parser.add_argument("--cases", type=Path, default=DEFAULT_FORWARD_TESTS)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        data = load_catalog(args.catalog)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.command == "validate":
        return cmd_validate(data)
    if args.command == "match":
        return cmd_match(data, args)
    if args.command == "tags":
        return cmd_tags(data, args.field)
    if args.command == "test":
        return cmd_forward_test(data, args.cases)
    parser.error("Unknown command.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
