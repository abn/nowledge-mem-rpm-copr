Name:           nowledge-mem
Version:        0.10.68
Release:        1%{?dist}
Summary:        Personal memory and context management system (Metapackage)

License:        Proprietary
URL:            https://download-mem.nowledge.co
Source0:        https://download-mem.nowledge.co/app/%{version}/x86_64-unknown-linux-gnu.rpm

ExclusiveArch:  x86_64
AutoReqProv:    no
%global debug_package %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_strip %{nil}
%global __brp_strip_lto %{nil}

BuildRequires:  cpio
BuildRequires:  rpm
BuildRequires:  systemd-rpm-macros

Provides:       nmem = %{version}-%{release}

Requires:       nowledge-mem-desktop = %{version}-%{release}
Requires:       nowledge-mem-server = %{version}-%{release}
Requires:       nowledge-mem-cli = %{version}-%{release}

%description
Meta-package for Nowledge Mem that installs the desktop GUI client (nowledge-mem-desktop),
CLI tools (nowledge-mem-cli), and local backend server (nowledge-mem-server).

%package cli
Summary:        Nowledge Mem CLI and TUI tools
AutoReqProv:    no
Provides:       nmem-cli = %{version}-%{release}
Provides:       nmem-tui = %{version}-%{release}

%description cli
Command-line interface (nmem) and Terminal UI (nmem-tui) for Nowledge Mem.

%package desktop
Summary:        Nowledge Mem Desktop GUI client
AutoReqProv:    no
Provides:       browse-now = %{version}-%{release}
Provides:       nmem-desktop = %{version}-%{release}
Requires:       nowledge-mem-cli = %{version}-%{release}
%if 0%{?suse_version}
Requires:       (libgtk-3-0 or gtk3)
Requires:       (libwebkit2gtk-4_1-0 or libwebkit2gtk-4_0-0 or webkit2gtk4.1)
Requires:       (libayatana-appindicator3-1 or libappindicator3-1 or libayatana-appindicator3)
Requires:       (libsoup-3_0-0 or libsoup3)
%elif 0%{?rhel} && 0%{?rhel} < 9
Requires:       gtk3
Requires:       webkit2gtk3
Requires:       libappindicator-gtk3
Requires:       libsoup
%else
Requires:       gtk3
Requires:       (webkit2gtk4.1 or webkit2gtk4.0 or webkit2gtk3)
Requires:       (libayatana-appindicator3 or libappindicator-gtk3)
Requires:       (libsoup3 or libsoup)
%endif
Suggests:       nowledge-mem-server = %{version}-%{release}

%description desktop
Desktop GUI client for Nowledge Mem and browser integration helper (browse-now).
Connects to a local or remote Nowledge Mem server.

%package server
Summary:        Nowledge Mem backend server daemon
AutoReqProv:    no
Provides:       nmem-server = %{version}-%{release}
%if 0%{?suse_version}
Requires:       (libgomp1 or libgomp)
%else
Requires:       libgomp
%endif
%{?systemd_requires}

%description server
Headless server daemon (nmem-server) for Nowledge Mem. Includes systemd system and user unit files.
Can be installed standalone on headless servers or remote hosts without desktop GUI dependencies.

%prep
%setup -q -c -T
RPM_FILE=""
for f in \
    "/sources/build/x86_64-unknown-linux-gnu.rpm" \
    "/sources/x86_64-unknown-linux-gnu.rpm" \
    "%{_sourcedir}/x86_64-unknown-linux-gnu.rpm" \
    "%{SOURCE0}"; do
    if [ -f "$f" ] && rpm2cpio "$f" >/dev/null 2>&1; then
        RPM_FILE="$f"
        break
    fi
done

if [ -n "$RPM_FILE" ]; then
    echo "Extracting RPM from: $RPM_FILE"
    rpm2cpio "$RPM_FILE" | cpio -idmv
else
    echo "Downloading upstream binary RPM..."
    curl -L -o upstream.rpm https://download-mem.nowledge.co/app/%{version}/x86_64-unknown-linux-gnu.rpm
    rpm2cpio upstream.rpm | cpio -idmv
fi

%build
# Pre-compiled binary package; no build step required.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/lib
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_userunitdir}

cp -a usr/bin/* %{buildroot}/usr/bin/ 2>/dev/null || true
cp -a "usr/lib/Nowledge Mem" %{buildroot}/usr/lib/
cp -a usr/share/applications/* %{buildroot}/usr/share/applications/ 2>/dev/null || true
cp -a usr/share/icons/* %{buildroot}/usr/share/icons/ 2>/dev/null || true

# Symlink binaries into /usr/bin
if [ -f "%{buildroot}/usr/lib/Nowledge Mem/_up_/rust-backend/nmem" ]; then
    ln -sf "/usr/lib/Nowledge Mem/_up_/rust-backend/nmem" %{buildroot}/usr/bin/nmem
fi
if [ -f "%{buildroot}/usr/lib/Nowledge Mem/_up_/rust-backend/nmem-tui" ]; then
    ln -sf "/usr/lib/Nowledge Mem/_up_/rust-backend/nmem-tui" %{buildroot}/usr/bin/nmem-tui
fi
if [ -f "%{buildroot}/usr/lib/Nowledge Mem/_up_/rust-backend/browse-now" ]; then
    ln -sf "/usr/lib/Nowledge Mem/_up_/rust-backend/browse-now" %{buildroot}/usr/bin/browse-now
fi
if [ -f "%{buildroot}/usr/lib/Nowledge Mem/_up_/rust-backend/nmem-server" ]; then
    ln -sf "/usr/lib/Nowledge Mem/_up_/rust-backend/nmem-server" %{buildroot}/usr/bin/nmem-server
fi

# Remove redundant /usr/share/nowledge-mem script folder if present
rm -rf %{buildroot}/usr/share/nowledge-mem

# Install systemd System Service Unit
cat << 'EOF' > %{buildroot}%{_unitdir}/nowledge-mem.service
[Unit]
Description=Nowledge Mem Server Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/nmem-server
Restart=always
RestartSec=5
EnvironmentFile=-/etc/default/nowledge-mem

[Install]
WantedBy=multi-user.target
EOF
ln -sf nowledge-mem.service %{buildroot}%{_unitdir}/nmem-server.service

# Install systemd User Service Unit
cat << 'EOF' > %{buildroot}%{_userunitdir}/nowledge-mem.service
[Unit]
Description=Nowledge Mem Server Daemon (User Service)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/nmem-server
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF
ln -sf nowledge-mem.service %{buildroot}%{_userunitdir}/nmem-server.service

%post desktop
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor 2>/dev/null || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q 2>/dev/null || true
fi

%postun desktop
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor 2>/dev/null || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q 2>/dev/null || true
fi

%post server
%systemd_post nowledge-mem.service

%preun server
%systemd_preun nowledge-mem.service

%postun server
%systemd_postun_with_restart nowledge-mem.service

%files
# Metapackage contains no files directly

%files cli
/usr/bin/nmem
/usr/bin/nmem-tui
%dir "/usr/lib/Nowledge Mem"
%dir "/usr/lib/Nowledge Mem/_up_"
%dir "/usr/lib/Nowledge Mem/_up_/rust-backend"
"/usr/lib/Nowledge Mem/_up_/rust-backend/nmem"
"/usr/lib/Nowledge Mem/_up_/rust-backend/nmem-tui"

%files desktop
/usr/bin/nowledge-mem
/usr/bin/browse-now
%dir "/usr/lib/Nowledge Mem"
%dir "/usr/lib/Nowledge Mem/_up_"
%dir "/usr/lib/Nowledge Mem/_up_/rust-backend"
"/usr/lib/Nowledge Mem/_up_/rust-backend/browse-now"
"/usr/share/applications/Nowledge Mem.desktop"
/usr/share/icons/hicolor/*/*/*

%files server
/usr/bin/nmem-server
%{_unitdir}/nowledge-mem.service
%{_unitdir}/nmem-server.service
%{_userunitdir}/nowledge-mem.service
%{_userunitdir}/nmem-server.service
%dir "/usr/lib/Nowledge Mem"
%dir "/usr/lib/Nowledge Mem/_up_"
%dir "/usr/lib/Nowledge Mem/_up_/rust-backend"
"/usr/lib/Nowledge Mem/_up_/rust-backend/nmem-server"
"/usr/lib/Nowledge Mem/_up_/rust-backend/libpdfium.so"
"/usr/lib/Nowledge Mem/_up_/rust-backend/cloudflared"
"/usr/lib/Nowledge Mem/_up_/rust-backend/web-dist"
"/usr/lib/Nowledge Mem/_up_/rust-backend/.gitkeep"

%changelog
* Tue Aug 25 2026 github-actions[bot] <github-actions[bot]@users.noreply.github.com>
- chore: bump version to 0.10.68 (github-actions[bot]@users.noreply.github.com)

* Fri Aug 21 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 0.10.67-2
- fix(spec): add libpdfium back to server files section
  (arun.neelicattu@gmail.com)

* Fri Aug 21 2026 github-actions[bot] <github-actions[bot]@users.noreply.github.com>
- chore: bump version to 0.10.67 (github-actions[bot]@users.noreply.github.com)

* Thu Aug 20 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 0.10.66-2
- fix(spec): remove libpdfium and disable brp-strip hooks for paths with spaces
  (arun.neelicattu@gmail.com)
- docs: remove libpdfium reference from server package descriptions
  (arun.neelicattu@gmail.com)

* Thu Aug 20 2026 github-actions[bot] <github-actions[bot]@users.noreply.github.com>
- chore: bump version to 0.10.66 (github-actions[bot]@users.noreply.github.com)

* Wed Aug 19 2026 github-actions[bot] <github-actions[bot]@users.noreply.github.com>
- chore: bump version to 0.10.65 (github-actions[bot]@users.noreply.github.com)

* Sun Aug 16 2026 github-actions[bot] <github-actions[bot]@users.noreply.github.com>
- chore: bump version to 0.10.64 (github-actions[bot]@users.noreply.github.com)

* Sat Aug 15 2026 github-actions[bot] <github-actions[bot]@users.noreply.github.com>
- chore: bump version to 0.10.63 (github-actions[bot]@users.noreply.github.com)

* Thu Aug 13 2026 github-actions[bot] <github-actions[bot]@users.noreply.github.com>
- chore: bump version to 0.10.62 (github-actions[bot]@users.noreply.github.com)

* Thu Aug 13 2026 github-actions[bot] <github-actions[bot]@users.noreply.github.com>
- chore: bump version to 0.10.61 (github-actions[bot]@users.noreply.github.com)
- fix(ci): split workflow into check-update and release-tag jobs to resolve
  missing python3 in raw container (arun.neelicattu@gmail.com)
- ci: check version before dnf install, run every 4 hours, and add COPR
  installation docs (arun.neelicattu@gmail.com)

* Wed Aug 12 2026 github-actions[bot] <github-actions[bot]@users.noreply.github.com>
- chore: bump version to 0.10.59 (github-actions[bot]@users.noreply.github.com)
- docs: add AGENTS.md, manage-rpm-packaging skill, and auto-detect container
  engine in Makefile (arun.neelicattu@gmail.com)
- Bump actions/checkout from 4 to 7 in the github-actions group
  (49699333+dependabot[bot]@users.noreply.github.com)
- ci: configure git safe directory and identity prior to checkout step
  (arun.neelicattu@gmail.com)
- ci: add dependabot configuration for weekly grouped actions updates
  (arun.neelicattu@gmail.com)
- ci: use fedora:latest container and install git and tito prior to checkout
  (arun.neelicattu@gmail.com)
- Update README with 4-subpackage layout, Provides aliases, systemd service
  management, and distro support (arun.neelicattu@gmail.com)

* Wed Aug 12 2026 Arun Babu Neelicattu <arun.neelicattu@gmail.com> 0.10.56-5
- Add systemd system and user unit files

