#!/usr/bin/env python3
"""Validate 22 Store registry and contribution manifests without executing submitted code."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
CONTRIBUTIONS = ROOT / "contributions"

PACKAGE_REQUIRED = {
    "id", "name", "type", "language", "version", "release", "status",
    "license", "author", "maintainer", "published", "architectures",
    "source", "distribution",
}
MANIFEST_REQUIRED = {
    "id", "name", "type", "language", "license", "author",
    "description", "dependencies", "architectures",
}
TYPES = {"library", "script"}
RELEASES = {"stable", "beta", "experimental", "deprecated"}
ARCHITECTURES = {"any", "source", "armv7", "arm64", "x86", "x86_64"}
LANGUAGES = {"python", "java", "cpp", "web"}
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def validate_dependencies(path: Path, dependencies, errors):
    if not isinstance(dependencies, list):
        errors.append(f"{path}: dependencies must be a list")
        return

    for index, dependency in enumerate(dependencies):
        prefix = f"{path}: dependencies[{index}]"
        if not isinstance(dependency, dict):
            errors.append(f"{prefix}: dependency must be an object with id and version")
            continue
        dependency_id = dependency.get("id")
        version_constraint = dependency.get("version")
        if not isinstance(dependency_id, str) or not dependency_id.strip():
            errors.append(f"{prefix}: id must be a non-empty string")
        if not isinstance(version_constraint, str) or not version_constraint.strip():
            errors.append(f"{prefix}: version must be a non-empty version constraint string")


def validate_manifest(path: Path, errors, registry_ids, aliases):
    data = load(path)
    missing = MANIFEST_REQUIRED - data.keys()
    if missing:
        errors.append(f"{path}: missing fields: {sorted(missing)}")
        return

    if data["type"] not in TYPES:
        errors.append(f"{path}: invalid type: {data['type']}")
    if data["language"] not in LANGUAGES:
        errors.append(f"{path}: unsupported language: {data['language']}")
    if "version" in data and not VERSION_RE.match(str(data["version"])):
        errors.append(f"{path}: version must use a numeric semver-like form such as 1.0.0")
    validate_dependencies(path, data["dependencies"], errors)
    if not isinstance(data["architectures"], list) or not data["architectures"]:
        errors.append(f"{path}: architectures must be a non-empty list")
    elif any(a not in ARCHITECTURES for a in data["architectures"]):
        errors.append(f"{path}: unsupported architecture value")
    elif any(a not in {"any", "source"} for a in data["architectures"]):
        artifacts = data.get("architecture_artifacts", {})
        for arch in data["architectures"]:
            if arch in {"any", "source"}:
                continue
            if arch not in artifacts:
                errors.append(f"{path}: architecture_artifacts missing {arch}")
            elif not (path.parent / artifacts[arch]).is_file():
                errors.append(f"{path}: architecture artifact missing for {arch}: {artifacts[arch]}")
    if not isinstance(data["author"], dict) or not data["author"].get("name"):
        errors.append(f"{path}: author.name is required")

    package_id = str(data["id"]).strip()
    if not package_id:
        errors.append(f"{path}: id cannot be empty")
    if package_id in registry_ids and "version" not in data:
        pass  # publisher will perform the default patch bump
    for alias in data.get("aliases", []):
        if alias in aliases or alias in registry_ids:
            errors.append(f"{path}: alias already exists: {alias}")

    readme = path.parent / "README.md"
    if data["type"] == "library" and not readme.exists():
        errors.append(f"{path}: library contributions require README.md")

    resource_files = [
        p for p in path.parent.rglob("*")
        if p.is_file() and p.name not in {"22-manifest.json", "README.md", "LICENSE", "NOTICE"}
    ]
    if not resource_files:
        errors.append(f"{path}: no resource files found")


def main():
    errors = []

    index = load(REGISTRY / "index.json")
    schema = load(REGISTRY / "schema.json")
    aliases_file = load(REGISTRY / "aliases.json")

    if index.get("registry_version") != schema.get("registry_version"):
        errors.append("registry/index.json and registry/schema.json versions differ")

    packages = index.get("packages", {})
    if not isinstance(packages, dict) or not packages:
        errors.append("registry/index.json must contain packages")

    registry_ids = set(packages)
    alias_map = aliases_file.get("aliases", {})
    aliases = set(alias_map)

    for alias, package_id in alias_map.items():
        if package_id not in registry_ids:
            errors.append(f"registry/aliases.json: alias points to unknown package: {alias} -> {package_id}")
        if alias in registry_ids:
            errors.append(f"registry/aliases.json: alias collides with package ID: {alias}")

    for package_id, metadata_path in packages.items():
        path = ROOT / metadata_path
        if not path.exists():
            errors.append(f"index points to missing package metadata: {metadata_path}")
            continue
        data = load(path)
        missing = PACKAGE_REQUIRED - data.keys()
        if missing:
            errors.append(f"{path}: missing fields: {sorted(missing)}")
            continue
        if data["id"] != package_id:
            errors.append(f"{path}: metadata id does not match index key")
        if data["type"] not in TYPES:
            errors.append(f"{path}: invalid type")
        if data["release"] not in RELEASES:
            errors.append(f"{path}: invalid release")
        if not VERSION_RE.match(str(data["version"])):
            errors.append(f"{path}: invalid version")
        if any(a not in ARCHITECTURES for a in data["architectures"]):
            errors.append(f"{path}: invalid architecture")
        source = ROOT / data["source"]
        if not source.exists():
            errors.append(f"{path}: source does not exist: {data["source"]}")
        distribution = data["distribution"]
        if "path" not in distribution:
            errors.append(f"{path}: distribution.path is required")
        elif not (ROOT / distribution["path"]).exists():
            errors.append(f"{path}: distribution.path does not exist: {distribution["path"]}")

    for manifest in sorted(CONTRIBUTIONS.glob("*/22-manifest.json")):
        validate_manifest(manifest, errors, registry_ids, aliases)

    if errors:
        print("22 Store validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("22 Store validation passed.")
    print(f"Registry packages: {len(packages)}")
    print(f"Contribution manifests checked: {len(list(CONTRIBUTIONS.glob('*/22-manifest.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
