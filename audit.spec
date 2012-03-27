%define major 1
%define libname %mklibname audit %{major}
%define develname %mklibname -d audit

%define auparsemajor 0
%define auparselibname %mklibname auparse %{auparsemajor}
%define auparsedevelname %mklibname -d auparse

Summary:	User-space tools for Linux 2.6 kernel auditing
Name:		audit
Version:	2.2.1
Release:	1
License:	LGPLv2+
Group:		System/Base
URL:		http://people.redhat.com/sgrubb/audit/
Source0:	http://people.redhat.com/sgrubb/audit/audit-%{version}.tar.gz
Patch0:		audit-1.7.12-lsb-headers.patch
# need proper kernel headers
BuildRequires:	gettext-devel
BuildRequires:	glibc-devel >= 2.6
BuildRequires:	intltool
BuildRequires:	libcap-ng-devel
BuildRequires:	autoconf automake libtool
BuildRequires:	openldap-devel
#BuildRequires:	prelude-devel >= 0.9.16
BuildRequires:	python-devel
BuildRequires:	swig
BuildRequires:	tcp_wrappers-devel
Requires(preun): rpm-helper
Requires(post): rpm-helper
# has the mandriva-simple-auth pam config file we link to
Requires:	usermode-consoleonly >= 1.92-4
Requires:	tcp_wrappers
Conflicts:	audispd-plugins < 1.7.11
Requires:	%{auparselibname} >= %{version}

%description
The audit package contains the user space utilities for storing and searching
the audit records generate by the audit subsystem in the Linux 2.6 kernel.

%package -n	%{libname}
Summary:	Main libraries for %{name}
Group:		System/Libraries
Conflicts:	audit < 2.0

%description -n	%{libname}
This package contains the main libraries for %{name}.

%package -n	%{develname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} >= %{version}-%{release}
Provides:	libaudit-devel = %{version}-%{release}
Provides:	audit-devel = %{version}-%{release}
Provides:	audit-libs-devel = %{version}-%{release}
Obsoletes:	%{mklibname audit 0 -d}

%description -n	%{develname}
This package contains development files for %{name}.

%package -n	%{auparselibname}
Summary:	Main libraries for %{name}
Group:		System/Libraries
Conflicts:	%{mklibname audit 0} <= 1.7.13

%description -n	%{auparselibname}
This package contains the main auparse libraries for %{name}.

%package -n	%{auparsedevelname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{auparselibname} >= %{version}-%{release}
Provides:	auparse-devel = %{version}-%{release}
Conflicts:	%{mklibname audit 0 -d} <= 1.7.13

%description -n	%{auparsedevelname}
This package contains development files for %{name}.

%package -n	python-audit
Summary:	Python bindings for %{name}
Group:		Development/Python

%description -n	python-audit
This package contains python bindings for %{name}.

%package -n	audispd-plugins
Summary:	Plugins for the audit event dispatcher
Group:		System/Base
Requires:	%{name} >= %{version}-%{release}
Requires:	%{libname} >= %{version}-%{release}
Requires:	openldap

%description -n	audispd-plugins
The audispd-plugins package provides plugins for the real-time interface to the
audit system, audispd. These plugins can do things like relay events to remote
machines or analyze events for suspicious behavior.

%prep

%setup -q
%patch0 -p1

find -type d -name ".libs" | xargs rm -rf

%build
%serverbuild
autoreconf -f -v --install

%configure2_5x \
    --disable-static \
    --sbindir=/sbin \
    --libdir=/%{_lib} \
    --with-libwrap \
    --enable-gssapi-krb5=no \
    --with-libcap-ng=yes \
    --libexecdir=%{_sbindir}

#    --with-prelude \

%make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_var}/log/audit
install -d %{buildroot}%{_libdir}/audit
install -d %{buildroot}%{_var}/spool/audit

%makeinstall_std

install -d %{buildroot}/%{_libdir}
# This winds up in the wrong place when libtool is involved
curdir=`pwd`
cd %{buildroot}/%{_libdir}
LIBNAME=`basename \`ls %{buildroot}/%{_lib}/libaudit.so.%{major}.*.*\``
ln -s ../../%{_lib}/$LIBNAME libaudit.so
LIBNAME=`basename \`ls %{buildroot}/%{_lib}/libauparse.so.%{auparsemajor}.*.*\``
ln -s ../../%{_lib}/$LIBNAME libauparse.so
cd $curdir

# uneeded files
rm -f %{buildroot}/%{_lib}/*.so
rm -f %{buildroot}/%{_lib}/*.*a
rm -f %{buildroot}%{py_platsitedir}/*.{a,la}

%post
%_post_service auditd

%preun
%_preun_service auditd

%files
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
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/syslog.conf
%attr(0750,root,root) /sbin/audispd
%attr(0750,root,root) /sbin/auditctl
%attr(0750,root,root) /sbin/auditd
%attr(0750,root,root) /sbin/autrace
%attr(0755,root,root) /sbin/aureport
%attr(0755,root,root) /sbin/ausearch
%attr(0755,root,root) %{_bindir}/aulast
%attr(0755,root,root) %{_bindir}/aulastlog
%attr(0755,root,root) %{_bindir}/ausyscall
%attr(0755,root,root) %{_bindir}/auvirt
%attr(0644,root,root) %{_mandir}/man5/audispd.conf.5*
%attr(0644,root,root) %{_mandir}/man5/auditd.conf.5*
%attr(0644,root,root) %{_mandir}/man5/ausearch-expression.5*
%attr(0644,root,root) %{_mandir}/man7/audit.rules.7*
%attr(0644,root,root) %{_mandir}/man8/audispd.8*
%attr(0644,root,root) %{_mandir}/man8/auditctl.8*
%attr(0644,root,root) %{_mandir}/man8/auditd.8*
%attr(0644,root,root) %{_mandir}/man8/aulast.8*
%attr(0644,root,root) %{_mandir}/man8/aulastlog.8*
%attr(0644,root,root) %{_mandir}/man8/aureport.8*
%attr(0644,root,root) %{_mandir}/man8/ausearch.8*
%attr(0644,root,root) %{_mandir}/man8/ausyscall.8*
%attr(0644,root,root) %{_mandir}/man8/autrace.8*
%attr(0644,root,root) %{_mandir}/man8/auvirt.8*
%attr(0700,root,root) %dir %{_var}/log/audit

%files -n %{libname}
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/libaudit.conf
/%{_lib}/libaudit.so.%{major}*
%attr(0644,root,root) %{_mandir}/man5/libaudit.conf.5*

%files -n %{develname}
%doc ChangeLog contrib/skeleton.c contrib/plugin
%{_libdir}/libaudit.so
%{_includedir}/libaudit.h
%{_mandir}/man3/audit_*
%{_mandir}/man3/ausearch_*
%{_mandir}/man3/get_auditfail_action.3*
%{_mandir}/man3/set_aumessage_mode.3*

%files -n %{auparselibname}
/%{_lib}/libauparse.so.%{auparsemajor}*

%files -n %{auparsedevelname}
%doc ChangeLog contrib/skeleton.c contrib/plugin
%{_libdir}/libauparse.so
%{_includedir}/auparse-defs.h
%{_includedir}/auparse.h
%{_mandir}/man3/auparse_*

%files -n python-audit
%{py_platsitedir}/*.so
%{py_platsitedir}/audit.p*

%files -n audispd-plugins
#config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/audisp-prelude.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/audisp-remote.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/audispd-zos-remote.conf
#config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/au-prelude.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/au-remote.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/zos-remote.conf
%attr(0750,root,root) /sbin/audispd-zos-remote
#%attr(0750,root,root) /sbin/audisp-prelude
%attr(0750,root,root) /sbin/audisp-remote
#attr(0644,root,root) %{_mandir}/man5/audisp-prelude.conf.5*
%attr(0644,root,root) %{_mandir}/man5/audisp-remote.conf.5*
%attr(0644,root,root) %{_mandir}/man5/zos-remote.conf.5*
%attr(0644,root,root) %{_mandir}/man8/audispd-zos-remote.8*
#attr(0644,root,root) %{_mandir}/man8/audisp-prelude.8*
%attr(0644,root,root) %{_mandir}/man8/audisp-remote.8*
%attr(0750,root,root) %dir %{_var}/spool/audit

