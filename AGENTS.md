# AGENTS.md

Welcome! This repository packages **Nowledge Mem** into modular RPM packages (`nowledge-mem`, `nowledge-mem-cli`, `nowledge-mem-desktop`, `nowledge-mem-server`) using [Tito](https://github.com/rpm-software-management/tito) and dispatches builds to [Fedora COPR](https://copr.fedorainfracloud.org/).

## Core Architecture & Package Roles

1. **[`nowledge-mem.spec`](file:///nowledge-mem.spec)**: The single spec file that defines 4 RPM sub-packages:
   - `nowledge-mem` (Metapackage): Top-level convenience package requiring `nowledge-mem-cli`, `nowledge-mem-desktop`, and `nowledge-mem-server`.
   - `nowledge-mem-cli`: CLI binary (`nmem`), TUI client (`nmem-tui`), no GUI dependencies.
   - `nowledge-mem-desktop`: GUI launcher (`nowledge-mem`), browser helper (`browse-now`), desktop icons, `.desktop` files.
   - `nowledge-mem-server`: Headless server daemon (`nmem-server`), `cloudflared`, web UI, systemd system & user units.

2. **Python Helpers**:
   - [`update_version.py`](file:///update_version.py): Resolves latest version from `https://nowled.ge/download-mem-rpm`, updates spec file version/release, downloads upstream binary RPM to `build/x86_64-unknown-linux-gnu.rpm`.
   - [`dispatch_copr.py`](file:///dispatch_copr.py): Dispatches SRPM build to Fedora COPR (`abn/nowledge-mem`) using `copr-cli`.

3. **Automation**:
   - [`.github/workflows/check-updates.yml`](file:///.github/workflows/check-updates.yml): Cron workflow running every 4 hours in `fedora:latest` container to check, update spec, run `tito tag`, and push release tags.

## Standard Agent Workflows & Commands

All common tasks are wrapped in the [`Makefile`](file:///Makefile). Run `make help` for target listing:

- **Check/Download upstream version**: `make download-upstream`
- **Build SRPM**: `make srpm`
- **Containerized Test Build**: `make build-container` (Uses `quay.io/abn/rpmbuilder:fedora-latest` via Podman or Docker)

- **Local Tito Test Build**: `make build-test`
- **Tag Release**: `make tag-release` (Automates Git commit & `tito tag`)
- **COPR Dispatch**: `make copr-build`

## Critical RPM Packaging Rules for AI Agents

1. **Commit Before Tito Testing**: Tito builds (`tito build --test`) ignore uncommitted git working tree changes. Always commit spec or script edits before testing.
2. **No Manual Spec Changelogs**: Never edit `%changelog` manually in `nowledge-mem.spec`. `tito tag` generates changelogs automatically.
3. **Clean Git State**: Keep `.gitignore` updated so temporary files (e.g. `.cover`, `.mbx`, `build/`) do not cause dirty tree errors during `tito tag`.

## Project Agent Skills (`.agents/skills/`)

- [`manage-rpm-packaging`](file:///.agents/skills/manage-rpm-packaging/SKILL.md): Complete lifecycle management (upstream sync, containerized testing, Tito tagging, COPR dispatch).
