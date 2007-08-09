%define major 0
%define libname %mklibname audit %{major}
%define devellibname %mklibname -d %name %major

Name: audit
Summary: User-space tools for Linux 2.6 kernel auditing
Version: 1.5.4
Release: %mkrel 1
License: GPL
Group: System/Base
Source0: http://people.redhat.com/sgrubb/audit/audit-%{version}.tar.gz
URL: http://people.redhat.com/sgrubb/audit/index.html
BuildRoot: %{_tmppath}/%{name}-%{version}-root-%(id -u -n)
# need proper kernel headers
BuildRequires: glibc-devel >= 2.6
%py_requires -d
Requires(preun): rpm-helper
Requires(post): rpm-helper

%description
The audit package contains the user space utilities for storing and
searching the audit records generate by the audit subsystem in the
Linux 2.6 kernel.

%package -n %{libname}
Summary: Main libraries for %{name}
Group: System/Libraries

%description -n %{libname}
This package contains the main libraries for %{name}.

%package -n %devellibname
Summary: Development files for %{name}
Group: Development/C
Requires: %{libname} = %{version}
Provides: libaudit-devel = %{version}-%{release}

%description -n %devellibname
This package contains development files for %{name}.

%package -n %{libname}-static-devel
Summary: Static libraries for %{name}
Requires: %devellibname = %{version}
Group: Development/C

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

%build
autoreconf -fv --install
%configure --sbindir=/sbin --libdir=/%{_lib} --with-apparmor
%make

%install
rm -rf %{buildroot}
mkdir -p -m 0700 %{buildroot}%{_var}/log/audit
%{makeinstall_std}

# uneeded files
rm -f %{buildroot}%py_platsitedir/*.{a,la}

%clean
rm -rf %{buildroot}

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%post
%_post_service auditd

%preun
%_preun_service auditd

%files
%defattr(-,root,root)
%doc README COPYING
%config(noreplace) %{_sysconfdir}/sysconfig/auditd
%config(noreplace) %{_sysconfdir}/audit/auditd.conf
/sbin/*
%{_initrddir}/auditd
%{_mandir}/man5/auditd.conf.5*
%{_mandir}/man8/*
%attr(0700,root,root) %{_var}/log/audit

%files -n %{libname}
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
