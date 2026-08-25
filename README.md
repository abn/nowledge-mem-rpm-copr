# Nowledge Mem RPM & COPR Build Repository

This repository packages **Nowledge Mem** into modular RPM packages using [Tito](https://github.com/rpm-software-management/tito) and dispatches builds to [Fedora COPR: abn/nowledge-mem](https://copr.fedorainfracloud.org/coprs/abn/nowledge-mem/).

## Installation from Fedora COPR

Pre-built RPM packages are available on Fedora COPR: [**`abn/nowledge-mem`**](https://copr.fedorainfracloud.org/coprs/abn/nowledge-mem/).

### 1. Enable the COPR Repository

On Fedora, RHEL, CentOS Stream, or Rocky Linux:
```bash
sudo dnf copr enable abn/nowledge-mem
```

### 2. Install Packages

- **Full Package (GUI + CLI + Server)**:
  ```bash
  sudo dnf install nowledge-mem
  # Or via shorthand alias
  sudo dnf install nmem
  ```

- **CLI & Terminal UI Tools Only**:
  ```bash
  sudo dnf install nowledge-mem-cli
  ```

- **Headless Server Daemon Only**:
  ```bash
  sudo dnf install nowledge-mem-server
  ```

- **Desktop GUI Client Only**:
  ```bash
  sudo dnf install nowledge-mem-desktop
  ```

## Package Architecture

The build produces 4 modular RPM packages:

1. **`nowledge-mem`** (Virtual Metapackage):
   - **Dependencies**: `nowledge-mem-desktop`, `nowledge-mem-cli`, & `nowledge-mem-server`
   - **Provides**: `nmem`
   - **Purpose**: Top-level convenience package for users installing the full local experience (`dnf install nowledge-mem` or `dnf install nmem`).

2. **`nowledge-mem-cli`** (Command Line & TUI Tools):
   - **Dependencies**: Standard system libraries (no GTK/GUI dependencies)
   - **Provides**: `nmem-cli`, `nmem-tui`
   - **Contents**: `/usr/bin/nmem`, `/usr/bin/nmem-tui`
   - **Purpose**: Command-line tool and terminal UI client for managing memories, search, and configuration.

3. **`nowledge-mem-desktop`** (Desktop GUI Client):
   - **Dependencies**: `nowledge-mem-cli`, `gtk3`, `webkit2gtk`, `libayatana-appindicator3`, `libsoup`
   - **Provides**: `browse-now`, `nmem-desktop`
   - **Suggests**: `nowledge-mem-server`
   - **Contents**: `/usr/bin/nowledge-mem`, `/usr/bin/browse-now`, `.desktop` launcher, and high-resolution application icons.
   - **Purpose**: GUI client and browser integration helper. Connects to a local or remote Nowledge Mem server.

4. **`nowledge-mem-server`** (Headless Server Daemon & Systemd Units):
   - **Dependencies**: Standard system libraries (no GTK/desktop dependencies)
   - **Provides**: `nmem-server`
   - **Contents**: `/usr/bin/nmem-server`, `libpdfium.so`, `cloudflared`, embedded Web UI (`web-dist`), and systemd unit files.
   - **Purpose**: Headless server daemon for deployment on servers, VMs, or remote hosts.

## Systemd Service Management

The `nowledge-mem-server` package installs both **system** and **user** systemd service units:

### System Service
```bash
# Enable and start system daemon
sudo systemctl enable --now nowledge-mem.service
# Environment variables can be configured in /etc/default/nowledge-mem
```

### User Service
```bash
# Enable and start user daemon
systemctl --user enable --now nowledge-mem.service
```

## Distribution Compatibility

The RPM spec file ([`nowledge-mem.spec`](file:///nowledge-mem.spec)) includes macro conditionals and boolean dependencies supporting:
- **Fedora**: 40, 41, 42, Rawhide
- **Enterprise Linux / RHEL / CentOS Stream / Rocky Linux**: EPEL 8, 9, 10
- **openSUSE**: Leap 15.x & Tumbleweed

## Automated CI Updates & Tito Tagging

A GitHub Actions workflow ([`.github/workflows/check-updates.yml`](file:///.github/workflows/check-updates.yml)) runs inside the standard `fedora:latest` container on a 4-hour schedule (`cron: '0 */4 * * *'`) and via `workflow_dispatch`:

1. Runs in a standard `fedora:latest` container with `git` and `tito` installed via DNF.
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

### 3. Containerized Test Build
To test the build inside the `quay.io/abn/rpmbuilder:fedora-latest` container (auto-detecting Podman or Docker CLI):
```bash
make build-container
```


### 4. Tag a New Release with Tito
```bash
make tag-release
```

### 5. Dispatch Build to COPR
1. Ensure your COPR API token is saved at `~/.config/copr`.
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
