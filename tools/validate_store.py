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
    "id", "name", "type", "language", "version", "license", "author",
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


def fail(errors, message):
    errors.append(message)


def validate_manifest(path: Path, errors, registry_ids, aliases):
    data = load(path)
    missing = MANIFEST_REQUIRED - data.keys()
    if missing:
        fail(errors, f"{path}: missing fields: {sorted(missing)}")
        return

    if data["type"] not in TYPES:
        fail(errors, f"{path}: invalid type: {data['type']}")
    if data["language"] not in LANGUAGES:
        fail(errors, f"{path}: unsupported language: {data['language']}")
    if not VERSION_RE.match(str(data["version"])):
        fail(errors, f"{path}: version must use a numeric semver-like form such as 1.0.0")
    if not isinstance(data["dependencies"], list):
        fail(errors, f"{path}: dependencies must be a list")
    if not isinstance(data["architectures"], list) or not data["architectures"]:
        fail(errors, f"{path}: architectures must be a non-empty list")
    elif any(a not in ARCHITECTURES for a in data["architectures"]):
        fail(errors, f"{path}: unsupported architecture value")
    if not isinstance(data["author"], dict) or not data["author"].get("name"):
        fail(errors, f"{path}: author.name is required")

    package_id = str(data["id"]).strip()
    if not package_id:
        fail(errors, f"{path}: id cannot be empty")
    if package_id in registry_ids:
        fail(errors, f"{path}: package id already exists in registry: {package_id}")

    for alias in data.get("aliases", []):
        if alias in aliases or alias in registry_ids:
            fail(errors, f"{path}: alias already exists: {alias}")

    readme = path.parent / "README.md"
    if data["type"] == "library" and not readme.exists():
        fail(errors, f"{path}: library contributions require README.md")

    resource_files = [
        p for p in path.parent.rglob("*")
        if p.is_file() and p.name not in {"22-manifest.json", "README.md", "LICENSE", "NOTICE"}
    ]
    if not resource_files:
        fail(errors, f"{path}: no resource files found")


def main():
    errors = []

    index = load(REGISTRY / "index.json")
    schema = load(REGISTRY / "schema.json")
    aliases_file = load(REGISTRY / "aliases.json")

    if index.get("registry_version") != schema.get("registry_version"):
        fail(errors, "registry/index.json and registry/schema.json versions differ")

    packages = index.get("packages", {})
    if not isinstance(packages, dict) or not packages:
        fail(errors, "registry/index.json must contain packages")

    registry_ids = set(packages)
    aliases = set(aliases_file.get("aliases", {}))

    for package_id, metadata_path in packages.items():
        path = ROOT / metadata_path
        if not path.exists():
            fail(errors, f"index points to missing package metadata: {metadata_path}")
            continue
        data = load(path)
        missing = PACKAGE_REQUIRED - data.keys()
        if missing:
            fail(errors, f"{path}: missing fields: {sorted(missing)}")
            continue
        if data["id"] != package_id:
            fail(errors, f"{path}: metadata id does not match index key")
        if data["type"] not in TYPES:
            fail(errors, f"{path}: invalid type")
        if data["release"] not in RELEASES:
            fail(errors, f"{path}: invalid release")
        if not VERSION_RE.match(str(data["version"])):
            fail(errors, f"{path}: invalid version")
        if any(a not in ARCHITECTURES for a in data["architectures"]):
            fail(errors, f"{path}: invalid architecture")
        source = ROOT / data["source"]
        if not source.exists():
            fail(errors, f"{path}: source does not exist: {data['source']}")
        distribution = data["distribution"]
        if "path" not in distribution:
            fail(errors, f"{path}: distribution.path is required")

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
