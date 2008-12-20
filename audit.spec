%define major 0
%define libname %mklibname audit %{major}
%define develname %mklibname -d audit
%define staticdevelname %mklibname -d -s audit

Summary:	User-space tools for Linux 2.6 kernel auditing
Name:		audit
Version:	1.7.10
Release:	%mkrel 1
License:	LGPLv2+
Group:		System/Base
URL:		http://people.redhat.com/sgrubb/audit/
Source0:	http://people.redhat.com/sgrubb/audit/audit-%{version}.tar.gz
Patch0:		audit-1.6.1-desktopfile.patch
Patch1:		audit-1.6.1-sendmail.patch
Patch2:		audit-1.7.10-format_not_a_string_literal_and_no_format_arguments.diff
# need proper kernel headers
BuildRequires:	gettext-devel
BuildRequires:	glibc-devel >= 2.6
BuildRequires:	intltool
BuildRequires:	krb5-devel
BuildRequires:	libtool
BuildRequires:	openldap-devel
BuildRequires:	prelude-devel >= 0.9.16
BuildRequires:	python-devel
BuildRequires:	swig
BuildRequires:	tcp_wrappers-devel
%py_requires -d
Requires(preun): rpm-helper
Requires(post): rpm-helper
# has the mandriva-simple-auth pam config file we link to
Requires:	usermode-consoleonly >= 1.92-4
Requires:	tcp_wrappers
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The audit package contains the user space utilities for storing and searching
the audit records generate by the audit subsystem in the Linux 2.6 kernel.

%package -n	%{libname}
Summary:	Main libraries for %{name}
Group:		System/Libraries

%description -n	%{libname}
This package contains the main libraries for %{name}.

%package -n	system-config-audit
Summary:	Audit GUI configuration tool
Group:		System/Base
Obsoletes:	lib%{name}-common < 1.6.1
# moved some files from there to here
Conflicts:	%{name} < 1.6.1
Requires:	python-audit
Requires:	pygtk2.0-libglade
Requires:	audit
Requires:	usermode-consoleonly >= 1.92-4

%description -n	system-config-audit
This package contains a GUI for configuring the Audit system.

%package -n	%{develname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	libaudit-devel = %{version}-%{release}
Provides:	audit-devel = %{version}-%{release}
Provides:	audit-libs-devel = %{version}-%{release}
Obsoletes:	%{mklibname audit 0 -d}

%description -n	%{develname}
This package contains development files for %{name}.

%package -n	%{staticdevelname}
Summary:	Static libraries for %{name}
Requires:	%{develname} = %{version}
Group:		Development/C
Provides:	audit-static-devel = %{version}-%{release}
Provides:	audit-libs-static-devel = %{version}-%{release}
Obsoletes:	%{mklibname audit 0 -d -s}

%description -n	%{staticdevelname}
This package contains static libraries for %{name} used for
development.

%package -n	python-audit
Summary:	Python bindings for %{name}
Group:		Development/Python

%description -n	python-audit
This package contains python bindings for %{name}.

%package -n	audispd-plugins
Summary:	Plugins for the audit event dispatcher
Group:		System/Base
Requires:	%{name} = %{version}
Requires:	%{libname} = %{version}
Requires:	openldap

%description -n	audispd-plugins
The audispd-plugins package provides plugins for the real-time interface to the
audit system, audispd. These plugins can do things like relay events to remote
machines or analyze events for suspicious behavior.

%prep

%setup -q
%patch0 -p1 -b .misc
%patch1 -p1
%patch2 -p1 -b .format_not_a_string_literal_and_no_format_arguments

find -type d -name ".libs" | xargs rm -rf

%build
%serverbuild

%configure2_5x \
    --sbindir=/sbin \
    --libdir=/%{_lib} \
    --with-apparmor \
    --with-prelude \
    --with-libwrap \
    --enable-gssapi-krb5 \
    --libexecdir=%{_sbindir}

%make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_var}/log/audit
install -d %{buildroot}%{_libdir}/audit

%makeinstall_std

pushd system-config-audit
    %makeinstall_std install-fedora
popd

%find_lang system-config-audit

# uneeded files
rm -f %{buildroot}%{py_platsitedir}/*.{a,la}

# let's use our own pam config
rm -f %{buildroot}%{_sysconfdir}/pam.d/system-config-audit-server
ln -s %{_sysconfdir}/pam.d/mandriva-simple-auth \
        %{buildroot}%{_sysconfdir}/pam.d/system-config-audit-server

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%post
%_post_service auditd

%preun
%_preun_service auditd

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README COPYING contrib/capp.rules contrib/nispom.rules contrib/lspp.rules contrib/stig.rules init.d/auditd.cron
%{_initrddir}/auditd
%attr(0750,root,root) %dir %{_sysconfdir}/audit
%attr(0750,root,root) %dir %{_sysconfdir}/audisp
%attr(0750,root,root) %dir %{_sysconfdir}/audisp/plugins.d
%attr(0750,root,root) %dir %{_libdir}/audit
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audit/auditd.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audit/audit.rules
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/sysconfig/auditd
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/audispd.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/af_unix.conf
%attr(0750,root,root) /sbin/audispd
%attr(0750,root,root) /sbin/auditctl
%attr(0750,root,root) /sbin/auditd
%attr(0750,root,root) /sbin/autrace
%attr(0755,root,root) /sbin/aureport
%attr(0755,root,root) /sbin/ausearch
%attr(0750,root,root) %{_bindir}/aulastlog
%attr(0755,root,root) %{_bindir}/aulast
%attr(0755,root,root) %{_bindir}/ausyscall
%attr(0644,root,root) %{_mandir}/man5/audispd.conf.5*
%attr(0644,root,root) %{_mandir}/man5/auditd.conf.5*
%attr(0644,root,root) %{_mandir}/man5/ausearch-expression.5*
%attr(0644,root,root) %{_mandir}/man8/audispd.8*
%attr(0644,root,root) %{_mandir}/man8/auditctl.8*
%attr(0644,root,root) %{_mandir}/man8/auditd.8*
%attr(0644,root,root) %{_mandir}/man8/aulast.8*
%attr(0644,root,root) %{_mandir}/man8/aulastlog.8*
%attr(0644,root,root) %{_mandir}/man8/aureport.8*
%attr(0644,root,root) %{_mandir}/man8/ausearch.8*
%attr(0644,root,root) %{_mandir}/man8/ausyscall.8*
%attr(0644,root,root) %{_mandir}/man8/autrace.8*
%attr(0700,root,root) %dir %{_var}/log/audit

%files -n system-config-audit -f system-config-audit.lang
%defattr(-,root,root)
%doc system-config-audit/README system-config-audit/NEWS
%doc system-config-audit/COPYING system-config-audit/AUTHORS
%config(noreplace) %{_sysconfdir}/pam.d/system-config-audit-server
%config(noreplace) %{_sysconfdir}/security/console.apps/system-config-audit-server
%{_datadir}/applications/system-config-audit.desktop
%{_datadir}/system-config-audit/
%{_bindir}/system-config-audit
%{_sbindir}/system-config-audit-server-real
%{_sbindir}/system-config-audit-server

%files -n %{libname}
%defattr(-,root,root)
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/libaudit.conf
/%{_lib}/lib*.so.*

%files -n %{develname}
%defattr(-,root,root)
%doc ChangeLog contrib/skeleton.c contrib/plugin
/%{_lib}/lib*.so
/%{_lib}/lib*.la
%{_includedir}/*
%{_mandir}/man3/*

%files -n %{staticdevelname}
%defattr(-,root,root)
/%{_lib}/lib*.a

%files -n python-audit
%defattr(-,root,root)
%{py_platsitedir}/*.so
%{py_purelibdir}/site-packages/audit.p*

%files -n audispd-plugins
%defattr(-,root,root,-)
%attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/syslog.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/audisp-prelude.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/audisp-remote.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/audispd-zos-remote.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/au-prelude.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/au-remote.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/zos-remote.conf
%attr(0750,root,root) /sbin/audispd-zos-remote
%attr(0750,root,root) /sbin/audisp-prelude
%attr(0750,root,root) /sbin/audisp-remote
%attr(0644,root,root) %{_mandir}/man5/audisp-prelude.conf.5*
%attr(0644,root,root) %{_mandir}/man5/audisp-remote.conf.5*
%attr(0644,root,root) %{_mandir}/man5/zos-remote.conf.5*
%attr(0644,root,root) %{_mandir}/man8/audispd-zos-remote.8*
%attr(0644,root,root) %{_mandir}/man8/audisp-prelude.8*
%attr(0644,root,root) %{_mandir}/man8/audisp-remote.8*
