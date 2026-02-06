# RIFT Package Manager Plan (RIFT-PKG)

Goal: design a comprehensive package manager ecosystem for the RIFT programming language, including:
- multiple package file types with a custom markup syntax (pkg.json alternative)
- a program to read those files, resolve dependencies, and deploy projects
- executable command files with custom CLI syntax
- extensive feature set covering registry, security, build, deploy, workspace, and tooling

This is a PLAN ONLY. No implementation details or code.

---

## 1) Core Vision & Principles

- First-class RIFT-native packaging: files readable/writable by RIFT tooling, expressive syntax, human-friendly.
- Safety by default: reproducible installs, signed packages, strict integrity checks.
- Deterministic builds: lockfiles, content-addressed storage, version constraints.
- Multi-environment deployments: local, container, serverless, edge.
- Extensible: custom file types, plugins, hooks, and CLI commands.
- Offline-first: local cache and mirror support.

---

## 2) Product Surface

- `riftpkg` (primary package manager CLI)
- `riftpkgd` (optional background daemon for caching, build queues, downloads)
- `riftpkgc` (config compiler/validator for package files)
- `riftpkg-exec` (CLI command file runner)
- `riftpkg-deploy` (deployment orchestrator)

---

## 3) File Type Strategy (Custom Markup Syntax)

We will define a custom markup format called **RIFT Package Markup (RPM)**.
- Syntax goals: readable, comment-friendly, deterministic parsing, minimal ambiguity.
- Structure: blocks, attributes, lists, optional inline tables.
- Supports schema declarations for validation.

Example naming:
- `*.rpm` for general RIFT package markup
- Specialized file types for different domains

### 3.1 Core Package Files (Multiple Types)

1. `package.rpm` (primary package manifest)
   - Purpose: package metadata, dependencies, entrypoints, scripts
   - Features: version constraints, optional flags, platform selectors

2. `deps.rpm` (dependency override/augmentation)
   - Purpose: add/override dependencies without touching main manifest
   - Features: environment-specific overrides

3. `build.rpm` (build plan)
   - Purpose: build steps, asset pipeline, caching policy
   - Features: artifact signatures, output mapping

4. `deploy.rpm` (deployment plan)
   - Purpose: environment targets, secrets mapping, runtime flags
   - Features: multi-target (cloud, edge, bare metal)

5. `workspace.rpm` (monorepo/workspace config)
   - Purpose: package graph, shared settings, workspace-level scripts
   - Features: selective builds, scoped dependencies

6. `lock.rpm` (dependency lockfile)
   - Purpose: deterministic dependency graph with checksums
   - Features: platform fingerprints, optional source mirrors

7. `registry.rpm` (registry config)
   - Purpose: registry URLs, auth policy, trust settings
   - Features: multiple registries, tiered trust levels

8. `profiles.rpm` (env profiles)
   - Purpose: configuration profiles (dev, ci, prod)
   - Features: variable interpolation, conditional blocks

9. `scripts.rpm` (script registry)
   - Purpose: named scripts and task chains
   - Features: includes, dependencies between scripts

10. `runtime.rpm` (runtime constraints)
    - Purpose: language/runtime version, platform support
    - Features: optional ABI targets, CPU features

### 3.2 Extended / Optional File Types

11. `license.rpm` (license constraints)
    - Purpose: SPDX mapping, dual-licensing rules

12. `security.rpm` (security policy)
    - Purpose: signing keys, allowed ciphers, audit rules

13. `metrics.rpm` (metrics/telemetry config)
    - Purpose: metrics sinks, sampling, observability settings

14. `cli.rpm` (custom CLI commands)
    - Purpose: CLI command definitions with custom syntax
    - Features: help strings, argument schema

15. `compat.rpm` (compatibility shims)
    - Purpose: RIFT version compat, legacy mapping

---

## 4) RPM (RIFT Package Markup) Syntax Ideas

### 4.1 Syntax Features

- Block syntax:
  - `block_name { key = value }`
- Lists:
  - `dependencies = [ pkg("name", "^1.2"), pkg("foo", "~3.0") ]`
- Comments:
  - `# single line` and `/* multiline */`
- Type hints:
  - `version: semver = "1.2.3"`
- Tags/annotations:
  - `@optional`, `@platform("linux")`, `@dev_only`
- Env variables:
  - `path = env("HOME") + "/.rift"`

### 4.2 Modularity

- `include` directive for shared config:
  - `include "common/profiles.rpm"`
- Conditional blocks:
  - `if platform("linux") { ... }`
- Merge rules:
  - `merge dependencies += [ ... ]`

### 4.3 Security & Integrity

- Built-in checksum blocks:
  - `integrity { sha256 = "..." }`
- Signed blocks:
  - `signed_by "KEYID"`

---

## 5) CLI Command File Type (Executable Commands)

We will define **RIFT Command Scripts (RCS)**:
- File extension: `*.rcs`
- Run with `riftpkg exec <command>` or `riftpkg-exec <file.rcs>`
- Custom CLI syntax for arguments, options, and pipelines

### 5.1 RCS Syntax Ideas

- Command blocks:
  - `command build { ... }`
- Arg schema:
  - `arg name: string required`
- Option schema:
  - `option --release: bool default=false`
- Pipelines:
  - `run "rift build" | run "rift test"`
- Environment injection:
  - `env { RIFT_ENV = "prod" }`

### 5.2 RCS Features

- Namespaced commands
- Argument validation
- Built-in help/usage generation
- Dependency on manifest scripts
- Integration with `scripts.rpm`

---

## 6) Package Manager Feature Set (Extensive)

### 6.1 Package Discovery & Registry

- Central registry + private registries
- Multiple registry fallback order
- Namespaces and scopes
- Package search by tags, dependencies, or license
- Mirror support and caching proxies

### 6.2 Dependency Resolution

- Semantic versioning support
- Overrides via `deps.rpm`
- Conflict resolution policies
- Optional dependencies, platform constraints
- Feature flags (like optional modules)
- Dependency graph visualization

### 6.3 Installation & Caching

- Content-addressed store
- Global cache shared across projects
- Offline install mode
- Partial install with lazy downloads
- Verification on install

### 6.4 Builds & Artifacts

- `build.rpm` steps
- Build caching
- Artifact signing
- Build profiles (debug/release)
- Multi-target builds

### 6.5 Deployment

- `deploy.rpm` with multi-environment targets
- Secret injection (vault, env, file)
- Rollbacks
- Blue/green deploy
- Deployment logs

### 6.6 Security

- Package signing and verification
- SBOM generation
- Audit dependencies for CVEs
- `security.rpm` policy enforcement

### 6.7 Workspaces & Monorepos

- `workspace.rpm` to define packages
- Shared dependency resolution
- Package-level overrides
- Workspace-level scripts

### 6.8 CLI & UX

- Rich help output
- Config validation warnings
- `riftpkg doctor` diagnostics
- `riftpkg graph` dependency graph
- `riftpkg audit` security scanning

### 6.9 Extensibility

- Plugin system
- Custom file type parsers
- CLI command extensions
- Hook system (pre/post install, build, deploy)

### 6.10 Observability

- Structured logging
- Metrics hooks
- Debug verbosity levels

---

## 7) Program Components

### 7.1 Parser & Validator

- Parse RPM files into AST
- Validate against schemas
- Provide linting and formatting

### 7.2 Resolver

- Build dependency graph
- Handle overrides, features, and constraints

### 7.3 Installer

- Fetch package artifacts
- Verify signatures and checksums
- Store in cache

### 7.4 Builder

- Execute `build.rpm` steps
- Manage build cache

### 7.5 Deployer

- Execute `deploy.rpm` pipeline
- Log and rollback support

### 7.6 Executor

- Parse and run `*.rcs` files
- Integrate with `scripts.rpm`

---

## 8) CLI Command Set (Planned)

- `riftpkg init`
- `riftpkg add <pkg>`
- `riftpkg remove <pkg>`
- `riftpkg install`
- `riftpkg update`
- `riftpkg build`
- `riftpkg run <script>`
- `riftpkg exec <command.rcs>`
- `riftpkg deploy`
- `riftpkg audit`
- `riftpkg graph`
- `riftpkg doctor`
- `riftpkg clean`

---

## 9) Deployment & Distribution

- Package publishing to registries
- Artifact signing with keys
- Support for private registries
- Version promotion workflow

---

## 10) Next Steps (Planning Phase)

1. Finalize RPM syntax grammar
2. Define file schemas for each `*.rpm` type
3. Draft CLI UX spec and help output
4. Design registry API and package format
5. Build parser prototype
6. Validate with sample projects

