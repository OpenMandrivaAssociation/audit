%define major 0
%define libname %mklibname audit
%define devellibname %mklibname -d %name

Name: audit
Summary: User-space tools for Linux 2.6 kernel auditing
Version: 1.6.1
Release: %mkrel 2
License: GPL
Group: System/Base
Source0: http://people.redhat.com/sgrubb/audit/audit-%{version}.tar.gz
Patch: audit-1.6.1-desktopfile.patch
URL: http://people.redhat.com/sgrubb/audit/index.html
BuildRoot: %{_tmppath}/%{name}-%{version}-root-%(id -u -n)
# need proper kernel headers
BuildRequires: glibc-devel >= 2.6
BuildRequires: gettext-devel intltool libtool swig python-devel
%py_requires -d
Requires(preun): rpm-helper
Requires(post): rpm-helper
# has the mandriva-simple-auth pam config file we link to
Requires: usermode-consoleonly >= 1.92-4mdv2008.0

%description
The audit package contains the user space utilities for storing and
searching the audit records generate by the audit subsystem in the
Linux 2.6 kernel.

%package -n %{libname}%{major}
Summary: Main libraries for %{name}
Group: System/Libraries

%description -n %{libname}%{major}
This package contains the main libraries for %{name}.

%package -n system-config-audit
Summary: Audit GUI configuration tool
Group: System/Base
Obsoletes: %{libname}-common < 1.6.1
# moved some files from there to here
Conflicts: %{name} < 1.6.1
Requires: python-audit

%description -n system-config-audit
This package contains a GUI for configuring the Audit system.

%package -n %devellibname
Summary: Development files for %{name}
Group: Development/C
Requires: %{libname}%{major} = %{version}
Provides: libaudit-devel = %{version}-%{release}
Provides: audit-devel = %{version}-%{release}
Provides: audit-libs-devel = %{version}-%{release}
Obsoletes: %{libname}0-devel

%description -n %devellibname
This package contains development files for %{name}.

%package -n %{libname}-static-devel
Summary: Static libraries for %{name}
Requires: %devellibname = %{version}
Group: Development/C
Provides: audit-static-devel = %{version}-%{release}
Provides: audit-libs-static-devel = %{version}-%{release}
Obsoletes: %{libname}0-static-devel

%description -n %{libname}-static-devel
This package contains static libraries for %{name} used for
development.

%package -n python-audit
Summary: Python bindings for %{name}
Group: Development/Python

%description -n python-audit
This package contains python bindings for %{name}.

%prep
%setup -q
%patch -p1

%build
./autogen.sh
%{configure2_5x} --sbindir=/sbin --libdir=/%{_lib} --with-apparmor --libexecdir=%{_sbindir}
%{make}

%install
rm -rf %{buildroot}
mkdir -p -m 0700 %{buildroot}%{_var}/log/audit
%{makeinstall_std}
pushd system-config-audit
%{makeinstall_std} install-fedora
popd
%find_lang system-config-audit

# uneeded files
rm -f %{buildroot}%py_platsitedir/*.{a,la}

# let's use our own pam config
rm -f %{buildroot}%{_sysconfdir}/pam.d/system-config-audit-server
ln -s %{_sysconfdir}/pam.d/mandriva-simple-auth \
        %{buildroot}%{_sysconfdir}/pam.d/system-config-audit-server

%clean
rm -rf %{buildroot}

%post -n %{libname}%{major} -p /sbin/ldconfig

%postun -n %{libname}%{major} -p /sbin/ldconfig

%post
%_post_service auditd

%preun
%_preun_service auditd

%files
%defattr(-,root,root)
%doc README COPYING
%config(noreplace) %{_sysconfdir}/sysconfig/auditd
%config(noreplace) %{_sysconfdir}/audit/auditd.conf
%dir %{_sysconfdir}/audisp
%dir %{_sysconfdir}/audisp/plugins.d
%config(noreplace) %{_sysconfdir}/audisp/audispd.conf
%config(noreplace) %{_sysconfdir}/audisp/plugins.d/af_unix.conf
%config(noreplace) %{_sysconfdir}/audisp/plugins.d/syslog.conf
/sbin/*
%{_initrddir}/auditd
%{_mandir}/man5/auditd.conf.5*
%{_mandir}/man5/audispd.conf.5*
%{_mandir}/man8/*
%attr(0700,root,root) %{_var}/log/audit

%files -n system-config-audit -f system-config-audit.lang
%defattr(-,root,root)
%doc system-config-audit/README system-config-audit/NEWS
%doc system-config-audit/COPYING system-config-audit/AUTHORS
%config(noreplace) %{_sysconfdir}/pam.d/system-config-audit-server
%config(noreplace) %{_sysconfdir}/security/console.apps/system-config-audit-server
%_datadir/applications/system-config-audit.desktop
%_datadir/system-config-audit/
%_bindir/system-config-audit
%_sbindir/system-config-audit-server-real
%_sbindir/system-config-audit-server

%files -n %{libname}%{major}
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/libaudit.conf
%dir %{_sysconfdir}/audit
# XXX - here or in the bin package?
%config(noreplace) %{_sysconfdir}/audit/audit.rules
/%{_lib}/lib*.so.*

%files -n %devellibname
%defattr(-,root,root)
%doc ChangeLog
/%{_lib}/lib*.so
/%{_lib}/lib*.la
%{_includedir}/*
%{_mandir}/man3/*

%files -n %{libname}-static-devel
%defattr(-,root,root)
/%{_lib}/lib*.a

%files -n python-audit
%defattr(-,root,root)
%py_platsitedir/*
%py_purelibdir/*
