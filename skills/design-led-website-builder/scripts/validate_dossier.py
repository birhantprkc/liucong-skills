#!/usr/bin/env python3
"""Validate a structured design-to-build experience dossier."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml


EVIDENCE_LEVELS = {"observed", "detected", "source-claimed", "inferred", "unknown"}
RIGHTS_STATES = {
    "owned",
    "licensed",
    "open-license",
    "public-domain",
    "generated",
    "pending",
    "not-required",
}
ASSET_STATUSES = {"approved", "placeholder", "pending", "rejected"}
REQUIRED_BRIEF_FIELDS = {
    "scenario",
    "audience",
    "primary_action",
    "belief_change",
    "content_inventory",
    "content_gaps",
    "desired_emotion",
    "anti_direction",
    "constraints",
    "acceptance_criteria",
}
REQUIRED_DIRECTION_FIELDS = {
    "composition",
    "typography",
    "palette",
    "assets",
    "motion",
    "ambition_test",
    "fit",
    "sacrifice",
}
REQUIRED_COMPONENT_FIELDS = {
    "id",
    "semantic_role",
    "responsive",
    "states",
    "inputs",
    "motion",
    "reduced_motion",
    "fallback",
}
REQUIRED_ASSET_FIELDS = {
    "id",
    "role",
    "origin",
    "provenance",
    "rights",
    "license_attribution",
    "status",
    "replacement_brief",
    "release_blocking",
    "format",
    "loading",
    "fallback",
}
REQUIRED_SCENARIOS = {
    "primary-path",
    "keyboard",
    "reduced-motion",
    "slow-network",
    "media-failure",
}


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Dossier not found: {path}") from None
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Dossier root must be a mapping.")
    return data


def nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def require_fields(
    mapping: Any,
    required: set[str],
    label: str,
    errors: list[str],
) -> bool:
    if not isinstance(mapping, dict):
        errors.append(f"{label} must be a mapping.")
        return False
    for field in sorted(required):
        if field not in mapping or not nonempty(mapping[field]):
            errors.append(f"{label}.{field} must be non-empty.")
    return True


def validate_dossier(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data.get("schema_version"), str):
        errors.append("schema_version must be a quoted string.")

    require_fields(data.get("brief"), REQUIRED_BRIEF_FIELDS, "brief", errors)

    directions = data.get("directions")
    direction_ids: set[str] = set()
    if not isinstance(directions, list) or len(directions) < 2:
        errors.append("directions must contain at least two genuinely different options.")
    else:
        for index, direction in enumerate(directions):
            label = f"directions[{index}]"
            if not require_fields(direction, {"id", "concept", "consequences"}, label, errors):
                continue
            direction_id = direction.get("id")
            if not isinstance(direction_id, str) or not direction_id.strip():
                errors.append(f"{label}.id must be a non-empty string.")
            elif direction_id in direction_ids:
                errors.append(f"Duplicate direction id: {direction_id}")
            else:
                direction_ids.add(direction_id)
            require_fields(
                direction.get("consequences"),
                REQUIRED_DIRECTION_FIELDS,
                f"{label}.consequences",
                errors,
            )

    chosen = data.get("chosen_direction")
    if not isinstance(chosen, str) or chosen not in direction_ids:
        errors.append("chosen_direction must reference one of the direction ids.")

    research = data.get("research")
    if require_fields(research, {"mode", "source_route", "reference_matrix"}, "research", errors):
        route = research.get("source_route")
        source_ids: set[str] = set()
        source_types: set[str] = set()
        if not isinstance(route, list) or len(route) < 2:
            errors.append("research.source_route must contain at least two sources.")
        else:
            for index, source in enumerate(route):
                label = f"research.source_route[{index}]"
                if not require_fields(
                    source,
                    {"id", "source_type", "role", "coverage", "gap"},
                    label,
                    errors,
                ):
                    continue
                source_ids.add(str(source["id"]))
                source_types.add(str(source["source_type"]))
            if len(source_types) < 2:
                errors.append("research.source_route must triangulate at least two source types.")

        matrix = research.get("reference_matrix")
        if not isinstance(matrix, list) or len(matrix) < 2:
            errors.append("research.reference_matrix must contain at least two adaptations.")
        else:
            for index, item in enumerate(matrix):
                label = f"research.reference_matrix[{index}]"
                if not require_fields(
                    item,
                    {"source_id", "principle", "evidence_level", "evidence", "adaptation", "do_not_copy"},
                    label,
                    errors,
                ):
                    continue
                if item.get("source_id") not in source_ids:
                    errors.append(f"{label}.source_id must exist in research.source_route.")
                if item.get("evidence_level") not in EVIDENCE_LEVELS:
                    errors.append(
                        f"{label}.evidence_level must be one of {sorted(EVIDENCE_LEVELS)}."
                    )

    require_fields(
        data.get("experience_contract"),
        {"purpose", "taste", "content", "constraints", "research", "quality"},
        "experience_contract",
        errors,
    )

    content_path = data.get("content_path")
    if not isinstance(content_path, list) or len(content_path) < 3:
        errors.append("content_path must contain at least three audience-question steps.")
    else:
        for index, step in enumerate(content_path):
            require_fields(
                step,
                {"question", "message", "proof", "component", "action"},
                f"content_path[{index}]",
                errors,
            )

    require_fields(
        data.get("design_system"),
        {"typography", "layout", "spacing", "color", "media", "interaction", "motion"},
        "design_system",
        errors,
    )

    components = data.get("components")
    if not isinstance(components, list) or len(components) < 3:
        errors.append("components must define at least three consequential component contracts.")
    else:
        component_ids: set[str] = set()
        for index, component in enumerate(components):
            label = f"components[{index}]"
            if not require_fields(component, REQUIRED_COMPONENT_FIELDS, label, errors):
                continue
            component_id = str(component["id"])
            if component_id in component_ids:
                errors.append(f"Duplicate component id: {component_id}")
            component_ids.add(component_id)
            states = component.get("states")
            if not isinstance(states, list) or "focus" not in states:
                errors.append(f"{label}.states must include a focus state.")

    enhancement = data.get("enhancement")
    if require_fields(
        enhancement,
        {"level", "purpose", "essential", "decorative", "loading", "reduced_motion", "fallback", "verification_plan"},
        "enhancement",
        errors,
    ):
        level = enhancement.get("level")
        if not isinstance(level, int) or level not in range(4):
            errors.append("enhancement.level must be an integer from 0 to 3.")

    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty manifest.")
    else:
        for index, asset in enumerate(assets):
            label = f"assets[{index}]"
            if not require_fields(
                asset,
                REQUIRED_ASSET_FIELDS,
                label,
                errors,
            ):
                continue
            if asset.get("rights") not in RIGHTS_STATES:
                errors.append(f"{label}.rights must be one of {sorted(RIGHTS_STATES)}.")
            if asset.get("status") not in ASSET_STATUSES:
                errors.append(f"{label}.status must be one of {sorted(ASSET_STATUSES)}.")
            if not isinstance(asset.get("release_blocking"), bool):
                errors.append(f"{label}.release_blocking must be a boolean.")

    dependencies = data.get("dependencies")
    if not isinstance(dependencies, list):
        errors.append("dependencies must be a list, including an empty list when none are added.")
    else:
        for index, dependency in enumerate(dependencies):
            require_fields(
                dependency,
                {"name", "behavior", "rationale", "bundle_runtime", "ssr_hydration", "cleanup", "reduced_motion", "license"},
                f"dependencies[{index}]",
                errors,
            )

    verification = data.get("verification")
    if require_fields(
        verification,
        {"viewports", "scenarios", "release_gates", "untested"},
        "verification",
        errors,
    ):
        viewports = verification.get("viewports")
        widths: list[int] = []
        if isinstance(viewports, list):
            for viewport in viewports:
                match = re.match(r"^(\d+)x\d+$", str(viewport))
                if match:
                    widths.append(int(match.group(1)))
        if not widths or min(widths) > 480 or max(widths) < 1024:
            errors.append("verification.viewports must include narrow mobile and desktop sizes as WIDTHxHEIGHT.")
        scenarios = verification.get("scenarios")
        if not isinstance(scenarios, list):
            errors.append("verification.scenarios must be a list.")
        else:
            missing = sorted(REQUIRED_SCENARIOS - set(scenarios))
            if missing:
                errors.append(f"verification.scenarios missing: {', '.join(missing)}")

    if not nonempty(data.get("known_gaps")):
        errors.append("known_gaps must be non-empty.")
    if not nonempty(data.get("next_improvement")):
        errors.append("next_improvement must be non-empty.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier", type=Path)
    args = parser.parse_args()
    try:
        data = load_yaml(args.dossier)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    errors = validate_dossier(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: dossier is decision-complete: {args.dossier}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
