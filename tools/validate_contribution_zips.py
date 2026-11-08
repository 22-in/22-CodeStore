#!/usr/bin/env python3
"""Safely validate and stage ZIP-based 22 Code Store contributions.

ZIP contents are treated as untrusted data. This tool never imports or executes
submitted code. Validation runs on pull requests; extraction runs only on main
after the contribution has been reviewed and merged.
"""
from __future__ import annotations

import argparse
import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "contributions" / "inbox"
DESTINATION = ROOT / "contributions"
MAX_ARCHIVE_BYTES = 50 * 1024 * 1024
MAX_TOTAL_BYTES = 150 * 1024 * 1024
MAX_FILES = 1000
MAX_COMPRESSION_RATIO = 100
PACKAGE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
REQUIRED = {
    "id", "name", "type", "language", "license", "author",
    "description", "dependencies", "architectures",
}
TYPES = {"library", "script"}
LANGUAGES = {"python", "java", "cpp", "web"}
ARCHITECTURES = {"any", "source", "armv7", "arm64", "x86", "x86_64"}


def inspect_archive(path: Path):
    if path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError(f"{path.name}: archive exceeds 50 MiB")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if not entries or len(entries) > MAX_FILES:
            raise ValueError(f"{path.name}: archive must contain 1-{MAX_FILES} entries")
        total = 0
        seen = set()
        for item in entries:
            name = item.filename.replace("\\", "/")
            pure = PurePosixPath(name)
            mode = item.external_attr >> 16
            if (not name or pure.is_absolute() or
                any(part in {"", ".", ".."} for part in pure.parts) or
                (pure.parts and ":" in pure.parts[0])):
                raise ValueError(f"{path.name}: unsafe archive path: {item.filename}")
            if name in seen:
                raise ValueError(f"{path.name}: duplicate archive path: {name}")
            seen.add(name)
            if stat.S_ISLNK(mode):
                raise ValueError(f"{path.name}: symbolic links are not allowed: {name}")
            if item.flag_bits & 0x1:
                raise ValueError(f"{path.name}: encrypted entries are not allowed")
            total += item.file_size
            if total > MAX_TOTAL_BYTES:
                raise ValueError(f"{path.name}: expanded archive exceeds 150 MiB")
            if item.file_size and item.compress_size == 0:
                raise ValueError(f"{path.name}: invalid compression metadata: {name}")
            if item.compress_size and item.file_size / item.compress_size > MAX_COMPRESSION_RATIO:
                raise ValueError(f"{path.name}: suspicious compression ratio: {name}")
        roots = {PurePosixPath(x.filename.replace("\\", "/")).parts[0] for x in entries}
        # Accept either a single top-level package directory or a flat ZIP.
        if len(roots) != 1:
            raise ValueError(f"{path.name}: ZIP must contain one package folder or flat package files")
        archive.extractall  # extraction is performed only after the checks above
        return archive, entries


def locate_package(extracted: Path) -> Path:
    if (extracted / "22-manifest.json").is_file():
        return extracted
    children = [p for p in extracted.iterdir() if p.is_dir()]
    if len(children) == 1 and (children[0] / "22-manifest.json").is_file():
        return children[0]
    raise ValueError("ZIP must contain 22-manifest.json at its root or inside one top-level folder")


def validate_package(folder: Path, archive_name: str) -> dict:
    manifest_path = folder / "22-manifest.json"
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"{archive_name}: invalid 22-manifest.json: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{archive_name}: manifest must be a JSON object")
    missing = REQUIRED - data.keys()
    if missing:
        raise ValueError(f"{archive_name}: manifest missing fields: {sorted(missing)}")
    package_id = data.get("id")
    if not isinstance(package_id, str) or not PACKAGE_ID.fullmatch(package_id):
        raise ValueError(f"{archive_name}: id must be 2-64 lowercase letters, numbers, dots, underscores or hyphens")
    if data["type"] not in TYPES:
        raise ValueError(f"{archive_name}: type must be library or script")
    if data["language"] not in LANGUAGES:
        raise ValueError(f"{archive_name}: unsupported language")
    if not isinstance(data["name"], str) or not data["name"].strip():
        raise ValueError(f"{archive_name}: name is required")
    if not isinstance(data["description"], str) or not data["description"].strip():
        raise ValueError(f"{archive_name}: description is required")
    if not isinstance(data["license"], str) or not data["license"].strip():
        raise ValueError(f"{archive_name}: license is required")
    if not isinstance(data["author"], dict) or not isinstance(data["author"].get("name"), str) or not data["author"]["name"].strip():
        raise ValueError(f"{archive_name}: author.name is required")
    if not isinstance(data["dependencies"], list):
        raise ValueError(f"{archive_name}: dependencies must be a list")
    for dep in data["dependencies"]:
        if not isinstance(dep, dict) or not isinstance(dep.get("id"), str) or not dep["id"].strip() or not isinstance(dep.get("version"), str) or not dep["version"].strip():
            raise ValueError(f"{archive_name}: every dependency needs id and version")
    architectures = data["architectures"]
    if not isinstance(architectures, list) or not architectures or any(a not in ARCHITECTURES for a in architectures):
        raise ValueError(f"{archive_name}: architectures must be a non-empty list of supported values")
    for arch in architectures:
        if arch not in {"any", "source"}:
            artifact_map = data.get("architecture_artifacts", {})
            rel = artifact_map.get(arch) if isinstance(artifact_map, dict) else None
            if not isinstance(rel, str) or not rel.strip():
                raise ValueError(f"{archive_name}: architecture_artifacts must map {arch} to a file")
            artifact = (folder / rel).resolve()
            if folder.resolve() not in artifact.parents or not artifact.is_file():
                raise ValueError(f"{archive_name}: invalid or missing architecture artifact for {arch}")
    if data["type"] == "library" and not (folder / "README.md").is_file():
        raise ValueError(f"{archive_name}: libraries require README.md")
    ignored = {"22-manifest.json", "README.md", "LICENSE", "NOTICE"}
    payload = [p for p in folder.rglob("*") if p.is_file() and p.name not in ignored]
    if not payload:
        raise ValueError(f"{archive_name}: no resource files found")
    return data


def process(path: Path, extract: bool) -> None:
    with TemporaryDirectory(prefix="22store-zip-") as temp:
        temp_root = Path(temp)
        with zipfile.ZipFile(path) as archive:
            # Re-run all archive checks before extracting.
            _, entries = inspect_archive(path)
            archive.extractall(temp_root)
        folder = locate_package(temp_root)
        manifest = validate_package(folder, path.name)
        package_id = manifest["id"]
        print(f"VALID: {path.name} -> {package_id}")
        if extract:
            target = DESTINATION / package_id
            if target.exists():
                raise ValueError(f"{path.name}: destination already exists: {target.relative_to(ROOT)}")
            target.mkdir(parents=True)
            for child in folder.iterdir():
                dest = target / child.name
                if child.is_dir():
                    import shutil
                    shutil.copytree(child, dest)
                else:
                    import shutil
                    shutil.copy2(child, dest)
            print(f"STAGED: {target.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", action="store_true",
                        help="stage validated ZIPs into contributions (main-branch publisher only)")
    args = parser.parse_args()
    archives = sorted(INBOX.glob("*.zip"))
    if not archives:
        print("No ZIP contributions found.")
        return 0
    errors = []
    ids = set()
    for path in archives:
        try:
            with TemporaryDirectory(prefix="22store-id-") as temp:
                with zipfile.ZipFile(path) as archive:
                    inspect_archive(path)
                    archive.extractall(temp)
                folder = locate_package(Path(temp))
                data = validate_package(folder, path.name)
                if data["id"] in ids:
                    raise ValueError(f"duplicate package ID in ZIP inbox: {data['id']}")
                ids.add(data["id"])
            if args.extract:
                process(path, True)
            else:
                print(f"VALID: {path.name}")
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
    if errors:
        print("ZIP contribution validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"ZIP contribution validation passed: {len(archives)} archive(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
