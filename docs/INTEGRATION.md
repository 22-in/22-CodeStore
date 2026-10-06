# 22 Store Integration

This is the stable machine-readable flow for applications such as QuickCode.

## 1. Read the registry

Fetch `registry/index.json`.

The `packages` object maps a stable package ID to its package metadata file.

## 2. Resolve a package

A client may receive a package ID or an alias.

- Check `registry/index.json` for a package ID.
- If it is not found, check `registry/aliases.json`.
- Resolve the alias to exactly one package ID.
- Fetch that package's metadata file.

Do not hardcode individual package download URLs.

## 3. Select a version

Package requests should support:

```text
22 install <package>
22 install <package>@<version>
```

These are example client commands; they are not Store or GitHub commands.

- Without `@version`, a client may install the package's current version.
- With `@version`, the client must resolve that exact version from the package metadata's `versions` map.
- If the requested version is unavailable, installation must fail rather than silently installing another version.
- Versioned artifacts are retained so an installed project can reproduce the same package version later.

A future lockfile can additionally pin exact versions and checksums for an entire project.

## 4. Read metadata

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
- `versions` when exact historical versions are needed

Optional metadata may include aliases, dependencies, description, and author username.

## 5. Select a distribution

For architecture-independent resources:

```json
"architectures": ["any"]
```

For source resources:

```json
"architectures": ["source"]
```

Native resources may expose architecture-specific entries such as `armv7`, `arm64`, `x86`, or `x86_64`.

## 6. Verify before install

The selected distribution may provide:

```json
"checksums": {
  "sha256": "..."
}
```

A client should calculate SHA-256 after download and compare it with the registry value **before extracting or installing the artifact**.

A checksum mismatch must stop installation.

Checksums protect integrity. They do not by themselves prove that the publisher is trustworthy; signature-based verification can be added later.

## 7. Download and install

Only install the verified selected distribution.

Clients should cache downloaded artifacts by package ID and exact version where practical.

## 8. Show attribution

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

## 9. Dependencies

Dependencies are declared in the manifest as package ID + version constraint objects:

```json
"dependencies": [
  {
    "id": "requests",
    "version": ">=2.30.0"
  }
]
```

The `id` must refer to a 22 Store package ID. A dependency version is a constraint, so clients may support exact versions or ranges according to their package-manager implementation.

The Store validates the dependency declaration format but does not currently resolve dependencies or handle conflicts. Clients/package managers are responsible for selecting compatible versions and deciding how to handle conflicts.

## 10. Compatibility

The registry is the discovery layer. The client decides how to present, download, cache, install, and update resources.

This allows QuickCode and third-party applications to use the same Store without sharing the same command syntax.
