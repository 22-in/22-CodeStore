# 22 Code Store 🚀

### Open-Source Library & Script Store

**22 Code Store** is a free, community-driven collection of reusable libraries and ready-to-use scripts for developers.

It is built to make code easier to **find, download, reuse, and share** across different projects and languages.

---

## 📦 What's in 22 Code Store?

### Libraries

Reusable packages or modules that can be added to a project and used by other code.

Libraries are suitable for:

- APIs and SDKs
- utilities and helper modules
- AI or automation libraries
- reusable application logic
- language-specific packages

A published library includes documentation explaining installation, usage, and examples.

### Scripts

Ready-to-use programs or tools that can be downloaded and used directly.

Scripts are suitable for:

- utilities
- automation tools
- small developer tools
- examples and standalone programs

---

## 💻 QuickCode

22 Code Store is integrated with **QuickCode**, where Store resources can be accessed through QuickCode's own command system.

### Install a Library

Inside QuickCode:

```bash
22 install <name>
```

Example:

```bash
22 install google_generativeai
```

QuickCode resolves the requested package through the Store registry and selects the appropriate distribution.

### Install an Exact Version

A specific version can be requested when reproducibility matters:

```bash
22 install <name>@<version>
```

Example:

```bash
22 install google_generativeai@1.0.0
```

When an exact version is requested, the client must install that version or fail rather than silently selecting another version.

### Get a Script

Inside QuickCode:

```bash
22 get <name>
```

Example:

```bash
22 get calculator
```

QuickCode downloads the requested script resource into the active project according to the package metadata.

> **Important:** `22 install` and `22 get` are QuickCode commands. They are not commands provided by GitHub or by this repository itself.
>
> Other developers and applications can use the 22 Code Store registry with their own commands, interfaces, installers, or workflows.

---

## 🌍 Multi-Language Support

22 Code Store is designed to support resources written in different languages.

Current structure:

```text
libraries/
├── python/
├── java/
├── cpp/
└── web/

scripts/
├── python/
├── java/
├── cpp/
└── web/
```

Additional languages can be added as the Store grows.

---

## 🧭 How the Store Works

The repository contains the resources and a machine-readable registry.

```text
Developer / App
      ↓
registry/index.json
      ↓
resolve package ID or alias
      ↓
package metadata
      ↓
select compatible distribution
      ↓
verify integrity
      ↓
download / install
```

The registry describes:

- stable package ID
- human-facing name
- version and version history
- type and language
- release/status
- license and attribution
- dependencies
- supported architectures
- distribution files
- SHA-256 checksums for published artifacts

See `docs/INTEGRATION.md` for the integration contract.

---

## 🔐 Package Integrity & Versions

Published artifacts use **SHA-256 checksums** so a client can verify that the downloaded file matches the artifact published by the Store.

Clients should verify the checksum **before extracting or installing** an artifact. A checksum mismatch should stop the installation.

Packages use versioned artifacts, allowing clients to request an exact version instead of depending only on the latest release.

SHA-256 verifies artifact integrity, but does not by itself prove who published the artifact. Stronger publisher-signing mechanisms may be added in the future.

---

## 🏗️ Architecture Support

Some resources are architecture-independent, while others contain native or compiled components.

### Architecture-independent

A pure-source or architecture-independent package may declare:

```json
"architectures": ["any"]
```

### Native / compiled resources

If a resource contains architecture-dependent native binaries, it must declare the architectures it actually supports.

Example:

```json
"architectures": ["armv7", "arm64"]
```

A package is **not** automatically `any` just because its primary language is Python. Native components determine the required architecture support.

Current architecture identifiers include:

- `any`
- `source`
- `armv7`
- `arm64`
- `x86`
- `x86_64`

---

## 🔎 Finding Resources

The registry is organized as:

```text
registry/
├── index.json
├── aliases.json
├── schema.json
└── packages/
    ├── <package-id>.json
    └── ...
```

A package ID is the stable identity of a resource. A package's version belongs to that ID; a different package has its own independent version history.

Aliases provide alternate names but must resolve to exactly one package ID.

---

## 🤝 Contributing

New resources enter through the `contributions/` directory rather than being placed directly into the published Store directories.

```text
Prepare resource
      ↓
22-manifest.json
      ↓
Pull request
      ↓
Automated validation
      ↓
Human + security + license review
      ↓
Merge
      ↓
Trusted publication workflow
      ↓
Archive + metadata + registry
```

See `CONTRIBUTING.md` for the exact contributor requirements.

The contributor supplies the resource and basic metadata. **22 generates/maintains the published registry metadata**, so contributors do not have to manually maintain the backend registry.

---

## 🛡️ Review & Security

Contributions are reviewed before publication.

The process may include:

1. Automated structure and metadata validation
2. Static/basic language validation where safe
3. Malware and security checks
4. Manual functionality testing
5. License and attribution verification
6. Publication after approval

Submitted code is not automatically imported or executed during the untrusted pull-request validation workflow.

Small, obvious bugs may be fixed during review when practical. Major unresolved functionality or dependency problems can be rejected with a reason and resubmitted later.

Malicious or unsafe resources can be quarantined or unpublished without removing unrelated resources.

---

## 📜 Licensing

The 22 Code Store repository is licensed under the **MIT License**.

For individual resources, contributors must have the right to submit the code under the license declared for that resource.

If a contributor chooses MIT for their own eligible code, the publication workflow can generate the standard MIT `LICENSE` file when one is not already present.

Third-party code must retain its applicable copyright notices, attribution, and license requirements.

Hosting code in 22 Code Store does not automatically change its original license.

---

## 📁 Repository Structure

```text
22-CodeStore/
├── contributions/
├── libraries/
├── scripts/
├── registry/
├── tools/
├── .github/workflows/
├── libs.json
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

`libs.json` is retained for compatibility with older QuickCode integrations. New integrations should use the registry.

---

## 🌱 Built for Developers

Whether you are:

- **Exploring** the Store
- **Downloading** a resource
- **Integrating** the registry into your own application
- **Contributing** a library or script

22 Code Store is designed to keep the process simple and machine-readable.

---

### Happy Coding 💻

**22 Code Store — Harvesting Potential Everywhere.**
