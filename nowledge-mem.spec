Name:           nowledge-mem
Version:        0.10.56
Release:        1%{?dist}
Summary:        Personal memory and context management system (Metapackage)

License:        Proprietary
URL:            https://download-mem.nowledge.co
Source0:        https://download-mem.nowledge.co/app/%{version}/x86_64-unknown-linux-gnu.rpm

ExclusiveArch:  x86_64
AutoReqProv:    no
%global debug_package %{nil}

BuildRequires:  cpio
BuildRequires:  rpm

Requires:       nowledge-mem-desktop = %{version}-%{release}
Requires:       nowledge-mem-server = %{version}-%{release}

%description
Meta-package for Nowledge Mem that installs both the desktop GUI client
(nowledge-mem-desktop) and the local backend server (nowledge-mem-server).

%package desktop
Summary:        Nowledge Mem Desktop GUI client
AutoReqProv:    no
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
Recommends:     nowledge-mem-server = %{version}-%{release}

%description desktop
Desktop GUI client for Nowledge Mem. Connects to a local or remote Nowledge Mem server
for AI-powered memory and context management workflows. Supports Fedora, RHEL, CentOS Stream,
Rocky Linux, and openSUSE (Leap / Tumbleweed).

%package server
Summary:        Nowledge Mem backend server and CLI tools
AutoReqProv:    no

%description server
Headless server daemon (nmem-server), TUI interface (nmem-tui), and CLI tools
(nmem, browse-now) for Nowledge Mem. Can be installed standalone on headless
servers or remote hosts (Fedora, RHEL, CentOS Stream, Rocky Linux, openSUSE) without desktop GUI dependencies.

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

cp -a usr/bin/* %{buildroot}/usr/bin/ 2>/dev/null || true
cp -a "usr/lib/Nowledge Mem" %{buildroot}/usr/lib/
cp -a usr/share/applications/* %{buildroot}/usr/share/applications/ 2>/dev/null || true
cp -a usr/share/icons/* %{buildroot}/usr/share/icons/ 2>/dev/null || true
if [ -d usr/share/nowledge-mem ]; then
    cp -a usr/share/nowledge-mem %{buildroot}/usr/share/ 2>/dev/null || true
fi

# Symlink CLI binaries into /usr/bin if present in rust-backend
if [ -f "%{buildroot}/usr/lib/Nowledge Mem/_up_/rust-backend/nmem" ]; then
    ln -sf "/usr/lib/Nowledge Mem/_up_/rust-backend/nmem" %{buildroot}/usr/bin/nmem
fi
if [ -f "%{buildroot}/usr/lib/Nowledge Mem/_up_/rust-backend/browse-now" ]; then
    ln -sf "/usr/lib/Nowledge Mem/_up_/rust-backend/browse-now" %{buildroot}/usr/bin/browse-now
fi

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

%files
# Metapackage contains no files directly

%files desktop
/usr/bin/nowledge-mem
"/usr/share/applications/Nowledge Mem.desktop"
/usr/share/icons/hicolor/*/*/*

%files server
/usr/bin/nmem
/usr/bin/browse-now
"/usr/lib/Nowledge Mem"
%{_datadir}/nowledge-mem

%changelog
