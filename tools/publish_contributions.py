#!/usr/bin/env python3
"""Build approved contributions into Store artifacts and registry metadata.

This script is intended to run only after a contribution has passed review.
It does not execute submitted resource code.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[1]
CONTRIBUTIONS = ROOT / "contributions"
REGISTRY = ROOT / "registry"
PACKAGES = REGISTRY / "packages"
LANGUAGES = {"python", "java", "cpp", "web"}
TYPES = {"library", "script"}
ARCH = {"any", "source", "armv7", "arm64", "x86", "x86_64"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mit_license(author: str, year: str) -> str:
    return f"""MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def next_version(current: str | None, requested: str | None) -> str:
    if requested:
        return requested
    if not current:
        return "1.0.0"
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", current)
    if not match:
        raise ValueError(f"Cannot auto-bump non-standard version: {current}")
    major, minor, patch = map(int, match.groups())
    return f"{major}.{minor}.{patch + 1}"


def build_archive(contribution: Path, manifest: dict, destination: Path):
    author = manifest["author"]["name"]
    license_name = str(manifest["license"]).strip()
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / manifest["id"]
        shutil.copytree(contribution, stage, dirs_exist_ok=True)
        if license_name.upper() == "MIT" and not (stage / "LICENSE").exists():
            (stage / "LICENSE").write_text(
                mit_license(author, str(datetime.now(timezone.utc).year)),
                encoding="utf-8",
            )

        metadata = {
            "format": "22-store-metadata",
            "version": "1.0",
            "id": manifest["id"],
            "name": manifest["name"],
            "type": manifest["type"],
            "language": manifest["language"],
            "package_version": manifest["version"],
            "author": author,
            "author_username": manifest["author"].get("username") or os.getenv("GITHUB_ACTOR"),
            "license": license_name,
            "description": manifest["description"],
            "dependencies": manifest.get("dependencies", []),
            "architectures": manifest["architectures"],
            "maintainer": "22",
            "store": "22 Store",
            "store_url": f"https://github.com/22-in/22-Store",
        }
        write_json(stage / "22-METADATA.json", metadata)

        destination.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(stage.rglob("*")):
                if file.is_file():
                    archive.write(file, file.relative_to(stage.parent))


def main():
    index_path = REGISTRY / "index.json"
    aliases_path = REGISTRY / "aliases.json"
    index = load(index_path)
    aliases = load(aliases_path)

    candidates = sorted(CONTRIBUTIONS.glob("*/22-manifest.json"))
    if not candidates:
        print("No contribution manifests found.")
        return 0

    changed = False
    for manifest_path in candidates:
        manifest = load(manifest_path)
        package_id = str(manifest["id"]).strip()
        if not package_id or manifest["type"] not in TYPES or manifest["language"] not in LANGUAGES:
            raise ValueError(f"{manifest_path}: invalid id/type/language")

        architectures = manifest.get("architectures", [])
        if not architectures or any(a not in ARCH for a in architectures):
            raise ValueError(f"{manifest_path}: invalid architectures")

        # The first automated publisher supports universal/source archives.
        # Native per-architecture artifact publishing remains a deliberate manual path.
        if any(a not in {"any", "source"} for a in architectures):
            raise ValueError(
                f"{manifest_path}: native architecture publishing requires "
                "architecture-specific artifacts and is not yet handled automatically"
            )

        current_path = index["packages"].get(package_id)
        current_version = None
        if current_path:
            current = load(ROOT / current_path)
            current_version = current["version"]

        version = next_version(current_version, manifest.get("version"))
        if current_version == version:
            print(f"Skipping unchanged package: {package_id} {current_version}")
            continue

        manifest = dict(manifest)
        manifest["version"] = version
        author = manifest["author"]["name"]
        archive_path = (
            ROOT / ("libraries" if manifest["type"] == "library" else "scripts")
            / manifest["language"] / f"{package_id}.zip"
        )
        build_archive(manifest_path.parent, manifest, archive_path)

        metadata_path = PACKAGES / f"{package_id}.json"
        metadata = {
            "id": package_id,
            "name": manifest["name"],
            "type": manifest["type"],
            "language": manifest["language"],
            "version": manifest["version"],
            "release": manifest.get("release", "stable"),
            "status": "normal",
            "license": manifest["license"],
            "author": author,
            "maintainer": "22",
            "published": datetime.now(timezone.utc).date().isoformat(),
            "architectures": architectures,
            "source": str(archive_path.relative_to(ROOT)),
            "distribution": {
                "type": "archive",
                "path": str(archive_path.relative_to(ROOT)),
                "architectures": {a: str(archive_path.relative_to(ROOT)) for a in architectures},
                "dependencies": manifest.get("dependencies", []),
                "description": manifest["description"],
            },
        }
        if manifest["author"].get("username") or os.getenv("GITHUB_ACTOR"):
            metadata["author_username"] = manifest["author"].get("username") or os.getenv("GITHUB_ACTOR")
        if manifest.get("aliases"):
            metadata["aliases"] = manifest["aliases"]

        write_json(metadata_path, metadata)
        index["packages"][package_id] = str(metadata_path.relative_to(ROOT))

        for alias in manifest.get("aliases", []):
            owner = aliases["aliases"].get(alias)
            if owner and owner != package_id:
                raise ValueError(f"Alias collision: {alias} -> {owner}")
            if alias in index["packages"] and alias != package_id:
                raise ValueError(f"Alias collides with package ID: {alias}")
            aliases["aliases"][alias] = package_id

        changed = True
        print(f"Published: {package_id} {manifest['version']}")

    if changed:
        index["registry_version"] = "1.1"
        aliases["registry_version"] = "1.1"
        write_json(index_path, index)
        write_json(aliases_path, aliases)

    return 0


if __name__ == "__main__":
    sys.exit(main())
