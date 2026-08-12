---
name: manage-rpm-packaging
description: "Streamlined purpose-built workflow for building, testing, tagging, and dispatching Nowledge Mem RPM packages using Tito, rpmbuilder containers, and COPR."
---

# Nowledge Mem RPM Packaging Workflow

Use this skill when modifying `nowledge-mem.spec`, testing builds in containerized environments with `rpmbuilder`, tagging releases with Tito, or dispatching builds to Fedora COPR.

## Key Project Files
- [`nowledge-mem.spec`](file:///nowledge-mem.spec) - RPM Spec file defining the 4 modular sub-packages (`nowledge-mem`, `cli`, `desktop`, `server`).
- [`Makefile`](file:///Makefile) - Primary build automation interface (`build-container`, `tag-release`, `copr-build`).
- [`update_version.py`](file:///update_version.py) - Resolves latest version from `https://nowled.ge/download-mem-rpm` and downloads upstream binary.
- [`dispatch_copr.py`](file:///dispatch_copr.py) - Submits SRPMs to Fedora COPR (`abn/nowledge-mem`).

---

## Containerized Testing with `rpmbuilder`

To test `nowledge-mem.spec` locally without installing DNF build dependencies on the host, use the `quay.io/abn/rpmbuilder:fedora-latest` container image.

### How `rpmbuilder` Operates
The `quay.io/abn/rpmbuilder:fedora-latest` container image features a custom entrypoint script (`rpmbuilder`) that automatically:
1. Mounts the local working tree at `/sources` and output path at `/output` (`build/`).
2. Copies source files to `/root/rpmbuild/SOURCES`.
3. Invokes `dnf builddep -y /sources/nowledge-mem.spec` to install required build dependencies inside the container.
4. Executes `rpmbuild` on `nowledge-mem.spec`.
5. If `build/x86_64-unknown-linux-gnu.rpm` is missing, `%prep` in `nowledge-mem.spec` automatically fetches `Source0` via `curl`.
6. Places generated RPM and SRPM packages into `/output` (`build/`).

### How to Run Containerized Build Tests
Run via Makefile:
```bash
make build-container
```

Or run directly with Podman or Docker (auto-detected by `CONTAINER_ENGINE` in Makefile):
```bash
mkdir -p build
# Uses podman by default, falls back to docker, or respects CONTAINER_ENGINE
${CONTAINER_ENGINE:-podman} run --rm \
  -v $(pwd):/sources:z \
  -v $(pwd)/build:/output:z \
  quay.io/abn/rpmbuilder:fedora-latest
```

*CRITICAL CONTAINER RULE*: Do NOT append command overrides (such as `tito build` or `rpmbuild`) to `podman`/`docker run`. The image's native entrypoint handles dependency installation and `rpmbuild` execution automatically. Appending commands overrides the entrypoint script and causes build failures.


---

## Full Release Lifecycle Steps

### 1. (Optional) Check Version & Pre-fetch Upstream Source
To check `nowled.ge` for a new release version and pre-download the ~400MB binary RPM to avoid repeated network downloads during local iteration:
```bash
make download-upstream
```

### 2. Test Container Build
Run the containerized build test to verify `nowledge-mem.spec` compiles cleanly:
```bash
make build-container
```

### 3. Tagging Release with Tito
When ready to tag a release:
- **DO NOT** edit `%changelog` manually in `nowledge-mem.spec`. `tito tag` auto-generates changelogs.
- Host `tito` requirement: If using host `tito build --test`, commit spec edits first as Tito ignores uncommitted working tree changes.
- Execute:
  ```bash
  make tag-release
  ```
  This automatically commits spec version changes and runs `tito tag --use-version <VERSION> --use-release '1%{?dist}' --accept-auto-changelog`.

### 4. Dispatching to Fedora COPR
To submit the built SRPM to COPR:
```bash
make copr-build COPR_REPO=abn/nowledge-mem
```
*(Requires API token at `~/.config/copr`).*

---

## Critical Rules Summary
1. **Container Execution**: Always use `quay.io/abn/rpmbuilder:fedora-latest` without command overrides so the container's built-in `rpmbuilder` script executes `dnf builddep` and `rpmbuild`.
2. **Spec %Prep Download**: `%prep` automatically downloads `Source0` if no local source RPM is mounted in `/sources/build/`.
3. **No Manual Changelogs**: Never manually write `%changelog` entries in `nowledge-mem.spec`. Tito manages changelogs on tag.
