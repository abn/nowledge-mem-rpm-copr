# Nowledge Mem RPM & COPR Build Repository

This repository packages **Nowledge Mem** (v0.10.56) into Fedora/RHEL RPM packages using [Tito](https://github.com/rpm-software-management/tito) and dispatches builds to [Fedora COPR](https://copr.fedorainfracloud.org/).

## Package Architecture

The build produces 3 modular RPM packages:

1. **`nowledge-mem`** (Virtual Metapackage):
   - Dependencies: `nowledge-mem-desktop` & `nowledge-mem-server`
   - Purpose: Top-level convenience package for users installing the full local experience (`dnf install nowledge-mem`).

2. **`nowledge-mem-desktop`** (Desktop GUI Client):
   - Dependencies: `gtk3`, `webkit2gtk4.1`, `libayatana-appindicator3`, `libsoup3`
   - Recommends: `nowledge-mem-server`
   - Purpose: Lightweight GUI client. Connects to either a local server or a remote Nowledge Mem server.

3. **`nowledge-mem-server`** (Headless Server & CLI Tools):
   - Dependencies: Standard Linux system libraries (no GTK/desktop dependencies)
   - Contents: `nmem-server` daemon, `nmem-tui`, `nmem` CLI, `browse-now` CLI
   - Purpose: Headless server and CLI suite for deployment on servers, VMs, or remote hosts.

## Automated Daily CI Updates & Tito Tagging

A GitHub Actions workflow ([`.github/workflows/check-updates.yml`](file:///.github/workflows/check-updates.yml)) runs inside the `quay.io/abn/rpmbuilder:fedora-latest` container on a daily schedule (`cron: '0 2 * * *'`) and via `workflow_dispatch`:

1. Runs directly in the native Fedora build container (`quay.io/abn/rpmbuilder:fedora-latest`) with `copr-cli` installed via DNF.
2. Queries `https://nowled.ge/download-mem-rpm` to resolve the latest online version.
3. If a new version is detected:
   - Updates `nowledge-mem.spec` with the new version.
   - Commits the spec update to Git.
   - Executes `tito tag --use-version <version> --use-release '1%{?dist}' --accept-auto-changelog`.
   - Pushes the new commit and release tag (`git push origin main --follow-tags`), triggering COPR automatically via webhook.

## Quick Start

### 1. View Available Targets
```bash
make help
```

### 2. Fetch Version & Build SRPM
```bash
make srpm
```
This fetches the latest version, updates `nowledge-mem.spec`, downloads the binary RPM, and generates the Source RPM (`.src.rpm`) in `build/`.

### 3. Containerized Test Build
To test the build inside the `quay.io/abn/rpmbuilder:fedora-latest` container:
```bash
make build-container
```

### 4. Tag a New Release with Tito
```bash
make tag-release
```

### 5. Dispatch Build to COPR
1. Ensure your COPR API token is saved at `~/.config/copr` (get it from [COPR API](https://copr.fedorainfracloud.org/api/)).
2. Run:
```bash
make copr-build COPR_REPO=abn/nowledge-mem
```

## Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── check-updates.yml
├── .gitignore
├── .tito/
│   ├── packages/
│   │   └── nowledge-mem
│   └── tito.props
├── Makefile
├── README.md
├── dispatch_copr.py
├── nowledge-mem.spec
└── update_version.py
```
