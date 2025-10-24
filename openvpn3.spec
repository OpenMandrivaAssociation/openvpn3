%define debug_package %{nil}

Name:           openvpn3
Version:        26
Release:        2%{?dist}
Summary:        OpenVPN 3 Linux client

License:        AGPL-3.0-only
Url:            https://codeberg.org/OpenVPN/openvpn3-linux
Conflicts:      openvpn
Source0:        https://swupdate.openvpn.net/community/releases/openvpn3-linux-%{version}.tar.xz
Source1:        openvpn3.rule
Source2:        sysusers-openvpn3.conf
Source3:        openvpn3-subprojects.tar.gz

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

Requires:       gdbuspp

Recommends:     openssl
Recommends:     mbedtls
Recommends:     polkit >= 0.112

%description
OpenVPN 3 Linux client, providing a D-Bus service for managing OpenVPN connections.

# -------------------------------------------------------------------------
%prep
%autosetup -n openvpn3-linux-%{version}
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
    -Dbash-completion=enabled \
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
install -Dm644 %{SOURCE2} %{buildroot}%{_prefix}/lib/sysusers.d/%{name}.conf
install -Dm644 COPYRIGHT.md %{buildroot}%{_datadir}/licenses/%{name}/COPYRIGHT.md

# -------------------------------------------------------------------------
%check
meson test --num-processes $(nproc) --print-errorlogs -C %{_builddir}/build

# -------------------------------------------------------------------------
%post
openvpn3-admin init-config --write-configs --force || :
systemctl reload dbus || :

# -------------------------------------------------------------------------
%files
%exclude %{_prefix}/lib/meson-private
%exclude %{_prefix}/share/meson
%exclude /usr/local

%license COPYRIGHT.md

# ---------- Binaries (all in /usr/bin) ----------
%{_bindir}/openvpn3
%{_bindir}/openvpn3-as
%{_bindir}/openvpn2
%{_bindir}/openvpn3-admin
%{_bindir}/openvpn3-autoload

# ---------- libexec ----------
%{_libexecdir}/openvpn3-linux/

# ---------- Bash completion ----------
%{_datadir}/bash-completion/completions/openvpn2
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

# ---------- Misc config ----------
%{_sysconfdir}/repkg/rules/system/%{name}.rule
%{_prefix}/lib/sysusers.d/%{name}.conf

# ---------- Man pages ----------
%{_mandir}/man1/*.1*
%{_mandir}/man7/*.7*
%{_mandir}/man8/*.8*

# ---------- Documentation (only once) ----------
%doc /usr/share/doc/openvpn3/*

# ---------- Development header ----------
%{_includedir}/openvpn3/constants.h

# ---------- Python bindings (single wildcard – includes __pycache__) ----------
%{_prefix}/lib/python3.11/site-packages/openvpn3/

# ---------- Runtime directories ----------
%dir %{_localstatedir}/lib/openvpn3/
%dir %{_localstatedir}/lib/openvpn3/configs/

# -------------------------------------------------------------------------
%changelog