%define major 1
%define libname %mklibname audit %{major}
%define devname %mklibname -d audit
%define staticdevname %mklibname -d -s audit

%define auparsemajor 0
%define auparselibname %mklibname auparse %{auparsemajor}
%define auparsedevname %mklibname -d auparse
%define auparsestaticdevname %mklibname -d -s auparse

Summary:	User-space tools for Linux 2.6 kernel auditing
Name:		audit
Version:	2.3.2
Release:	5
License:	LGPLv2+
Group:		System/Base
Url:		http://people.redhat.com/sgrubb/audit/
Source0:	http://people.redhat.com/sgrubb/audit/%{name}-%{version}.tar.gz
Source100:	%{name}.rpmlintrc
Patch0:		audit-for-cross-compiling.patch

BuildRequires:	intltool
BuildRequires:	libtool
BuildRequires:	swig
BuildRequires:	gettext-devel
BuildRequires:	glibc-devel >= 2.6
BuildRequires:	openldap-devel
BuildRequires:	tcp_wrappers-devel
BuildRequires:	pkgconfig(libcap-ng)
BuildRequires:	pkgconfig(libprelude)
BuildRequires:	pkgconfig(python)
BuildRequires:	systemd-units
Requires(preun,post):	rpm-helper
# has the mandriva-simple-auth pam config file we link to
Requires:	usermode-consoleonly >= 1.92-4
Requires:	tcp_wrappers
Conflicts:	audispd-plugins < 1.7.11

%description
The audit package contains the user space utilities for storing and searching
the audit records generate by the audit subsystem in the Linux 2.6 kernel.

%package -n	%{libname}
Summary:	Main libraries for %{name}
Group:		System/Libraries
Conflicts:	audit < 2.0

%description -n	%{libname}
This package contains the main libraries for %{name}.

%package -n	%{devname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
This package contains development files for %{name}.

%package -n	%{staticdevname}
Summary:	Static libraries for %{name}
Group:		Development/C
Requires:	%{devname} = %{version}
Provides:	audit-static-devel = %{version}-%{release}

%description -n	%{staticdevname}
This package contains static libraries for %{name} used for
development.

%package -n	%{auparselibname}
Summary:	Main libraries for %{name}
Group:		System/Libraries
Conflicts:	%{mklibname audit 0} <= 1.7.13

%description -n	%{auparselibname}
This package contains the main auparse libraries for %{name}.

%package -n	%{auparsedevname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{auparselibname} = %{version}
Provides:	auparse-devel = %{version}-%{release}
Conflicts:	%{mklibname audit 0 -d} <= 1.7.13

%description -n	%{auparsedevname}
This package contains development files for %{name}.

%package -n	%{auparsestaticdevname}
Summary:	Static libraries for %{name}
Requires:	%{auparsedevname} = %{version}
Group:		Development/C
Provides:	auparse-static-devel = %{version}-%{release}
Conflicts:	%{mklibname audit 0 -d -s} <= 1.7.13

%description -n	%{auparsestaticdevname}
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
Requires:	openldap

%description -n	audispd-plugins
The audispd-plugins package provides plugins for the real-time interface to the
audit system, audispd. These plugins can do things like relay events to remote
machines or analyze events for suspicious behavior.

%prep

%setup -q
%apply_patches

find -type d -name ".libs" | xargs rm -rf


%build
#fix build with new automake
sed -i -e 's,AM_CONFIG_HEADER,AC_CONFIG_HEADERS,g' configure.* 
libtoolize --copy --force
autoreconf -f -v --install
%serverbuild

%configure2_5x \
	--sbindir=/sbin \
	--libdir=/%{_lib} \
	--enable-systemd \
	--with-prelude \
	--enable-static \
	--with-libwrap \
	--enable-gssapi-krb5=no \
%ifarch aarch64
	--with-aarch64 \
%endif
	--with-libcap-ng=yes \
	--libexecdir=%{_sbindir}

%make

%install
install -d %{buildroot}%{_var}/log/audit
install -d %{buildroot}%{_libdir}/audit
install -d %{buildroot}%{_var}/spool/audit

%makeinstall_std
install -d %{buildroot}/%{_libdir}
# This winds up in the wrong place when libtool is involved
mv %{buildroot}/%{_lib}/libaudit.a %{buildroot}%{_libdir}/
mv %{buildroot}/%{_lib}/libauparse.a %{buildroot}%{_libdir}/
curdir=`pwd`
cd %{buildroot}/%{_libdir}
LIBNAME=`basename \`ls %{buildroot}/%{_lib}/libaudit.so.%{major}.*.*\``
ln -s ../../%{_lib}/$LIBNAME libaudit.so
LIBNAME=`basename \`ls %{buildroot}/%{_lib}/libauparse.so.%{auparsemajor}.*.*\``
ln -s ../../%{_lib}/$LIBNAME libauparse.so
cd $curdir

mkdir -p %{buildroot}%{_unitdir}
mv %{buildroot}/%{_prefix}/lib/systemd/system/auditd.service %{buildroot}%{_unitdir}

# uneeded files
rm -f %{buildroot}/%{_lib}/*.so
rm -f %{buildroot}/%{_lib}/*.la
rm -f %{buildroot}%{py_platsitedir}/*.{a,la}

%post
# Copy default rules into place on new installation
if [ ! -e /etc/audit/audit.rules ] ; then
	cp /etc/audit/rules.d/audit.rules /etc/audit/audit.rules
fi
%_post_service auditd

%preun
%_preun_service auditd

%files
%doc README COPYING contrib/capp.rules contrib/nispom.rules contrib/lspp.rules contrib/stig.rules init.d/auditd.cron
%{_unitdir}/auditd.service
%attr(0750,root,root) %dir %{_sysconfdir}/audit
%attr(0750,root,root) %dir %{_sysconfdir}/audisp
%attr(0750,root,root) %dir %{_sysconfdir}/audisp/plugins.d
%attr(0750,root,root) %dir %{_libdir}/audit
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audit/auditd.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audit/rules.d/audit.rules
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/audispd.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/af_unix.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/syslog.conf
%attr(0750,root,root) /sbin/audispd
%attr(0750,root,root) /sbin/auditctl
%attr(0750,root,root) /sbin/auditd
%attr(0750,root,root) /sbin/autrace
%attr(0755,root,root) /sbin/aureport
%attr(0755,root,root) /sbin/ausearch
%attr(0755,root,root) /sbin/augenrules
%attr(0755,root,root) %{_sbindir}/initscripts/legacy-actions/auditd/*
%attr(0755,root,root) %{_bindir}/aulastlog
%attr(0755,root,root) %{_bindir}/aulast
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
%attr(6444,root,root) %{_mandir}/man8/augenrules.8*
%attr(0700,root,root) %dir %{_var}/log/audit

%files -n %{libname}
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/libaudit.conf
/%{_lib}/libaudit.so.%{major}*
%attr(0644,root,root) %{_mandir}/man5/libaudit.conf.5*

%files -n %{devname}
%doc ChangeLog contrib/skeleton.c contrib/plugin
%{_libdir}/libaudit.so
%{_includedir}/libaudit.h
%{_mandir}/man3/audit_*
%{_mandir}/man3/ausearch_*
%{_mandir}/man3/get_auditfail_action.3*
%{_mandir}/man3/set_aumessage_mode.3*

%files -n %{staticdevname}
%{_libdir}/libaudit.a

%files -n %{auparselibname}
/%{_lib}/libauparse.so.%{auparsemajor}*

%files -n %{auparsedevname}
%doc ChangeLog contrib/skeleton.c contrib/plugin
%{_libdir}/libauparse.so
%{_includedir}/auparse-defs.h
%{_includedir}/auparse.h
%{_mandir}/man3/auparse_*

%files -n %{auparsestaticdevname}
%{_libdir}/libauparse.a

%files -n python-audit
%{py_platsitedir}/*.so
%{py_platsitedir}/audit.p*

%files -n audispd-plugins
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
%attr(0750,root,root) %dir %{_var}/spool/audit

