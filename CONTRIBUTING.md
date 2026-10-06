# Contributing to 22 Store

22 Store accepts reusable libraries and ready-to-use scripts from the community.

## Contribution flow

1. Prepare and test your resource.
2. Create a contribution folder under `contributions/`.
3. Add the resource and a `22-manifest.json`.
4. Add documentation required for the resource type.
5. Open a pull request.
6. Automated checks validate structure and metadata.
7. 22 reviews the contribution, including security, licensing, and functionality.
8. Approved contributions are published into the Store registry.

Contributors should submit the resource itself and its basic metadata. Do not manually edit the generated registry files unless a maintainer specifically asks you to.

## Manifest

Each contribution uses `22-manifest.json`.

Example:

```json
{
  "id": "my-library",
  "name": "My Library",
  "type": "library",
  "language": "python",
  "version": "1.0.0",
  "license": "MIT",
  "author": {
    "name": "Your Name",
    "username": "your-github-username"
  },
  "description": "A short description.",
  "aliases": ["my-lib"],
  "dependencies": [],
  "architectures": ["any"]
}
```

### Field rules

- `id`: stable package identifier. It must be unique in the Store.
- `name`: human-facing resource name.
- `type`: `library` or `script`.
- `language`: supported language such as `python`, `java`, `cpp`, or `web`.
- `version`: version of this package. A new package normally starts at `1.0.0`; later releases update the version of the same package.
- `license`: the license the contributor has the right to grant for their submitted code. Do not claim MIT for code you do not own or have permission to relicense.
- `author`: the original author identity. The GitHub username identifies the submitting account; it does not by itself determine legal copyright ownership.
- `description`: short explanation of what the resource does.
- `aliases`: optional alternate names. They must not conflict with an existing package or alias.
- `dependencies`: optional dependency declarations. Keep them in metadata rather than inserting them into source headers.
- `architectures`: use `any` for architecture-independent source where appropriate; use `source` for source distributions when that is the correct representation; native/compiled resources must declare their actual supported architectures.

## Library requirements

A library must include:

- the library/package files
- `README.md` with installation, usage, and at least one working example
- `22-manifest.json`
- its declared license information
- third-party copyright/license notices where applicable
- dependency information when applicable

Complex libraries should include automated tests.

## Script requirements

A script must include:

- the runnable/source files
- `22-manifest.json`
- enough documentation to explain how to run it and what it does
- dependency information when applicable
- its declared license information

A source header may contain concise attribution, but 22 Store will not rewrite source code merely to add metadata. Source changes are only made when an actual fix or approved modification is required.

## License and attribution

22 Store preserves original authorship and applicable third-party licenses.

If 22 fixes or modifies a contribution, the published metadata may record both the original author and 22 as maintainer/modifier. This does not transfer original authorship to 22.

22 Store must not silently change a contributor's license choice.

## Review and rejection

Automated checks are not final approval. A maintainer reviews the resource for functionality, security, licensing, documentation, and compatibility.

Small, obvious fixes may be made during review when practical. Contributions with major errors, unresolved dependency problems, broken functionality, or unclear licensing may be rejected with a reason and can be resubmitted after correction.

Malicious or clearly abusive submissions may be quarantined and can lead to contributor restrictions under the Store's security policy.
