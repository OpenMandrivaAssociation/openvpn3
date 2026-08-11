%define debug_package %{nil}

Name:           openvpn3
Version:        27.1
Release:        1
Summary:        OpenVPN 3 Linux client

License:        AGPL-3.0-only
Group:          Networking/Other
Url:            https://codeberg.org/OpenVPN/openvpn3-linux
Conflicts:      openvpn
Source100:      openvpn3.rpmlintrc
Source0:        https://swupdate.openvpn.net/community/releases/openvpn3-linux-%{version}.tar.xz
Source1:        openvpn3.rule
Source2:        sysusers-openvpn3.conf
Source3:        openvpn3-subprojects.tar.gz
Patch0:         openvpn3-27.1-openssl4-const.patch

ExcludeArch:    armv7hl i686

# ---------- Build requirements (Clang + OpenMandriva) ----------
BuildRequires:  gdbuspp-devel
BuildRequires:  meson
BuildRequires:  clang >= 10
BuildRequires:  lib64stdc++-devel
BuildRequires:  lib64dbus-1-devel
BuildRequires:  lib64glib2.0-devel
BuildRequires:  gdbuspp-devel >= 3
BuildRequires:  lib64jsoncpp-devel
BuildRequires:  lib64cap-ng-devel
BuildRequires:  lib64uuid-devel
BuildRequires:  lib64lz4-devel
BuildRequires:  lib64openssl-devel
BuildRequires:  systemd
BuildRequires:  lib64systemd-devel
BuildRequires:  lib64z-devel
BuildRequires:  python-dbus
BuildRequires:  lib64python-devel
BuildRequires:  python-docutils
BuildRequires:  python-jinja2
BuildRequires:  ninja
BuildRequires:  pkgconf
BuildRequires:  lib64mbedtls-devel
BuildRequires:  lib64polkit1-devel >= 0.112
BuildRequires:  lib64tinyxml2-devel
BuildRequires:  lib64nl3-devel
BuildRequires:  lib64protobuf-devel

Requires:       gdbuspp

Recommends:     openssl
Recommends:     mbedtls
Recommends:     polkit >= 0.112

%description
OpenVPN 3 Linux client, providing a D-Bus service for managing OpenVPN connections.

# -------------------------------------------------------------------------
%prep
%autosetup -p1 -n openvpn3-linux-%{version}
tar -xzf %{SOURCE3} -C .

# -------------------------------------------------------------------------
%build
rm -rf %{_builddir}/build
mkdir -p %{_builddir}/build

# Force Clang
export CXX="clang++"

meson setup %{_builddir}/build \
    --prefix=/usr \
    --libdir=/usr/lib64 \
    --libexecdir=/usr/libexec \
    --bindir=/usr/bin \
    --sbindir=/usr/bin \
    --sysconfdir=/etc \
    --datadir=/usr/share \
    --mandir=/usr/share/man \
    -Dc_args='-Wno-error=non-virtual-dtor -Wno-vla-cxx-extension -Wno-deprecated-enum-enum-conversion' \
    -Dcpp_args='-Wno-error=non-virtual-dtor -Wno-vla-cxx-extension -Wno-deprecated-enum-enum-conversion' \
    -Dcpp_std=c++20 \
    -Dselinux=disabled \
    -Dselinux_policy=disabled \
    -Dbash-completion=disabled \
    -Dtest_programs=enabled \
    -Dunit_tests=disabled \
    --reconfigure

ninja -C %{_builddir}/build -v -j$(nproc)

# -------------------------------------------------------------------------
%install
rm -rf %{buildroot}
DESTDIR=%{buildroot} meson install --no-rebuild -C %{_builddir}/build

# Remove Meson artefacts (kept for %exclude later)
rm -rf %{buildroot}%{_prefix}/lib/meson-private
rm -rf %{buildroot}%{_prefix}/share/meson
rm -rf %{buildroot}/usr/local

# Extra files not installed by meson
install -Dm644 %{SOURCE1} %{buildroot}%{_sysconfdir}/repkg/rules/system/%{name}.rule
install -Dm644 %{SOURCE2} %{buildroot}%{_sysusersdir}/%{name}.conf
install -Dm644 COPYRIGHT.md %{buildroot}%{_datadir}/licenses/%{name}/COPYRIGHT.md
# openvpn2 completion is generated from the in-tree python module and
# fails in an out-of-tree meson build. Ship the static openvpn3 helper.
install -Dm644 src/shell/bash-completion/openvpn3 %{buildroot}%{_datadir}/bash-completion/completions/openvpn3
ln -sf openvpn3 %{buildroot}%{_datadir}/bash-completion/completions/openvpn3-admin

# -------------------------------------------------------------------------
%post
openvpn3-admin init-config --write-configs --force || :
systemctl reload dbus || :

# -------------------------------------------------------------------------
%files
%license COPYRIGHT.md

# ---------- Binaries (all in /usr/bin) ----------
%{_bindir}/openvpn3
%{_bindir}/openvpn3-as
%{_bindir}/openvpn2
%{_bindir}/openvpn3-admin
%{_bindir}/openvpn3-autoload
%{_bindir}/openvpn3-desktop-session-watcher

# ---------- libexec ----------
%{_libexecdir}/openvpn3-linux/

# ---------- Bash completion ----------
%{_datadir}/bash-completion/completions/openvpn3
%{_datadir}/bash-completion/completions/openvpn3-admin

# ---------- D-Bus ----------
%{_datadir}/dbus-1/system-services/net.openvpn.v3.*
%{_datadir}/dbus-1/system.d/net.openvpn.v3.*

# ---------- Polkit ----------
%{_datadir}/polkit-1/rules.d/net.openvpn.v3.rules

# ---------- Systemd ----------
%{_unitdir}/openvpn3-session@.service
%{_unitdir}/openvpn3-autoload.service
%{_userunitdir}/openvpn3-desktop-session-watcher.service

# ---------- Misc config ----------
%{_sysconfdir}/repkg/rules/system/%{name}.rule
%{_sysusersdir}/%{name}.conf

# ---------- Man pages ----------
%{_mandir}/man1/*.1*
%{_mandir}/man7/*.7*
%{_mandir}/man8/*.8*

# ---------- Documentation (only once) ----------
%doc /usr/share/doc/openvpn3/*

# ---------- Development header ----------
%{_includedir}/openvpn3/constants.h

# ---------- Python bindings (single wildcard – includes __pycache__) ----------
%{python_sitelib}/openvpn3/

# ---------- Runtime directories ----------
%dir %{_localstatedir}/lib/openvpn3/
%dir %{_localstatedir}/lib/openvpn3/configs/

# -------------------------------------------------------------------------
%changelog