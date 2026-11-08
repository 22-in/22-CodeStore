# Contributing to 22 Code Store

22 Code Store accepts reusable libraries and ready-to-use scripts from the community.

## Choose how to contribute

**Option A — Upload one ZIP (recommended for new contributors)**

1. Prepare a ZIP containing your package and its `22-manifest.json`.
2. The manifest must be at the ZIP root or inside one top-level package folder.
3. For a library, include `README.md` with installation, usage, and a working example.
4. Upload the ZIP to `contributions/inbox/` in a pull request. Use a clear filename such as `my-library.zip`.
5. Automated checks validate the archive. A maintainer reviews it before merge and publication.

The ZIP must be no larger than 50 MiB, expand to no more than 150 MiB, and contain no more than 1,000 entries. ZIP paths, duplicate entries, symlinks, encrypted entries, and suspicious compression ratios are rejected. Submitted code is never executed during validation.

**Option B — Contribute an extracted folder**

Create `contributions/<package-id>/`, put `22-manifest.json` and resource files inside it, then open a pull request as described below.

## Manifest

Example:

```json
{
  "id": "my-library",
  "name": "My Library",
  "type": "library",
  "language": "python",
  "license": "MIT",
  "author": { "name": "Your Name" },
  "description": "A short description.",
  "aliases": [],
  "dependencies": [],
  "architectures": ["any"]
}
```

### Field rules

- `id`: unique stable package identifier; use lowercase letters, numbers, dots, underscores or hyphens.
- `name`: human-facing resource name.
- `type`: `library` or `script`.
- `language`: `python`, `java`, `cpp`, or `web`.
- `version`: optional; a new package defaults to `1.0.0`. Updates without an explicit version receive a patch bump.
- `license`: license you have the right to grant. Use `NO-LICENSE` when no license is granted; this does not mean the code is free to use.
- `author.name`: original author name. `author.username` is optional.
- `description`: short explanation of the resource.
- `aliases`: optional alternate names; they must not conflict with an existing package or alias.
- `dependencies`: optional list of objects with Store package `id` and `version` constraint.
- `architectures`: use `any` for architecture-independent resources, `source` for source-only resources, or actual supported architecture values. Native resources require `architecture_artifacts` mappings.

## Review and publication

Automated validation checks structure and metadata; it does not prove code is safe or functional. A maintainer reviews functionality, security, licensing, attribution, and compatibility before merging. Only the trusted workflow on `main` stages ZIPs and publishes generated archives and registry metadata.

Do not manually edit generated registry files.
