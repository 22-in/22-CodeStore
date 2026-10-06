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

Contributors submit the resource and basic metadata. Do not manually edit generated registry files.

## Manifest

Example:

```json
{
  "id": "my-library",
  "name": "My Library",
  "type": "library",
  "language": "python",
  "license": "MIT",
  "author": {
    "name": "Your Name"
  },
  "description": "A short description.",
  "aliases": ["my-lib"],
  "dependencies": [
    {
      "id": "requests",
      "version": ">=2.30.0"
    }
  ],
  "architectures": ["any"]
}
```

### Field rules

- `id`: stable package identifier. It must be unique in the Store.
- `name`: human-facing resource name.
- `type`: `library` or `script`.
- `language`: supported language such as `python`, `java`, `cpp`, or `web`.
- `version`: optional. A new package defaults to `1.0.0`. An update without an explicit version receives a patch bump. Contributors can explicitly choose a higher version when a minor/major release is appropriate.
- `license`: the license the contributor has the right to grant. Use `NO-LICENSE` when no license is granted; this does not mean the code is free to use.
- `author`: original author name. `username` is optional; the publishing workflow can preserve the GitHub account that submitted the contribution.
- `description`: short explanation of what the resource does.
- `aliases`: optional alternate names. They must not conflict with an existing package or alias.
- `dependencies`: optional list of dependency objects. Each dependency must contain a package `id` and a `version` constraint, such as `>=2.30.0`, `^1.4.0`, or `1.2.3`. Dependency IDs refer to 22 Store package IDs, not display names or aliases.
- `architectures`: use `any` for architecture-independent resources, `source` for source-only distribution where appropriate, and actual architecture values for native/compiled resources. For native resources, add `architecture_artifacts` mapping each architecture to the contributor-supplied binary/artifact.

The Store defines dependency declarations, but does not currently perform dependency resolution or conflict resolution. Clients/package managers are responsible for resolving the declared constraints.

## Library requirements

A library must include:

- library/package files
- `README.md` with installation, usage, and at least one working example
- `22-manifest.json`
- declared license information
- third-party copyright/license notices where applicable
- dependency information when applicable

Complex libraries should include automated tests.

## Script requirements

A script must include:

- runnable/source files
- `22-manifest.json`
- enough documentation to explain how to run it and what it does
- dependency information when applicable
- declared license information

A source header may contain concise attribution, but 22 Store will not rewrite source code merely to add metadata. Source changes are only made when an actual fix or approved modification is required.

## License and attribution

22 Store preserves original authorship and applicable third-party licenses.

If 22 fixes or modifies a contribution, the published metadata may record both the original author and 22 as maintainer/modifier. This does not transfer original authorship to 22.

22 Store must not silently change a contributor's license choice.

## Review and rejection

Automated checks are not final approval. A maintainer reviews functionality, security, licensing, documentation, and compatibility.

Small, obvious fixes may be made during review when practical. Contributions with major errors, unresolved dependency problems, broken functionality, or unclear licensing may be rejected with a reason and can be resubmitted after correction.

Malicious or clearly abusive submissions may be quarantined and can lead to contributor restrictions under the Store's security policy.
