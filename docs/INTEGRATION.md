# 22 Store Integration

This is the stable machine-readable flow for applications such as QuickCode.

## 1. Read the registry

Fetch `registry/index.json`.

The `packages` object maps a stable package ID to its metadata file.

## 2. Resolve a package

A client may receive a package ID or an alias.

- Check `registry/index.json` for a package ID.
- If it is not found, check `registry/aliases.json`.
- Resolve the alias to exactly one package ID.
- Fetch that package's metadata file.

Do not hardcode individual package download URLs.

## 3. Read metadata

Important fields include:

- `id`
- `name`
- `type`
- `language`
- `version`
- `license`
- `author`
- `maintainer`
- `architectures`
- `source`
- `distribution`

Optional metadata may include aliases, dependencies, description, and author username.

## 4. Select a distribution

For architecture-independent resources:

```json
"architectures": ["any"]
```

For source resources:

```json
"architectures": ["source"]
```

Native resources may expose architecture-specific entries such as `armv7`, `arm64`, `x86`, or `x86_64`.

## 5. Download and install

Download the selected `distribution.path` or architecture-specific distribution entry.

A client should verify a trusted checksum or signature when the registry provides one. Checksum/signature support can be added later without changing package identity.

## 6. Show attribution

Published archives contain `22-METADATA.json`, generated from the contributor manifest.

A client can display:

```text
Installing My Library 1.0.0
Author: Example Author
License: MIT
Maintainer: 22
Source: 22 Store
```

This keeps the UI/terminal layer independent from source-code formatting.

## 7. Dependencies

Dependencies are metadata, not source headers.

A client can inspect the dependency list before installation and decide whether to resolve, warn about, or install those dependencies.

## 8. Compatibility

The registry is the discovery layer. The client decides how to present, download, cache, install, and update resources.

This allows QuickCode and third-party applications to use the same Store without sharing the same command syntax.
