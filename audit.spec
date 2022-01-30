%define major 1
%define libname %mklibname audit %{major}
%define devname %mklibname -d audit
%define staticdevname %mklibname -d -s audit

%define _disable_ld_no_undefined 1
%define _disable_lto 1

%define auparsemajor 0
%define auparselibname %mklibname auparse %{auparsemajor}
%define auparsedevname %mklibname -d auparse
%define auparsestaticdevname %mklibname -d -s auparse

%bcond_with systemd

Summary:	User-space tools for Linux 2.6 kernel auditing
Name:		audit
Version:	3.0.7
Release:	1
License:	LGPLv2+
Group:		System/Base
Url:		http://people.redhat.com/sgrubb/audit/
Source0:	http://people.redhat.com/sgrubb/audit/%{name}-%{version}.tar.gz
Source1:	%{name}-tmpfiles.conf
Source100:	%{name}.rpmlintrc
BuildRequires:	intltool
BuildRequires:	libtool
BuildRequires:	swig
BuildRequires:	gettext-devel
BuildRequires:	glibc-devel >= 2.6
BuildRequires:	openldap-devel
BuildRequires:	tcp_wrappers-devel
BuildRequires:	pkgconfig(libcap-ng)
BuildRequires:	pkgconfig(python3)
%if %{with systemd}
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	systemd-rpm-macros
%systemd_requires
%endif
Requires(preun,post):	rpm-helper
# has the mandriva-simple-auth pam config file we link to
Requires:	usermode-consoleonly >= 1.92-4
Requires:	tcp_wrappers
Conflicts:	audispd-plugins < 1.7.11

%description
The audit package contains the user space utilities for storing and searching
the audit records generate by the audit subsystem in the Linux 2.6 kernel.

%package -n %{libname}
Summary:	Main libraries for %{name}
Group:		System/Libraries
Conflicts:	audit < 2.0

%description -n %{libname}
This package contains the main libraries for %{name}.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
This package contains development files for %{name}.

%package -n %{staticdevname}
Summary:	Static libraries for %{name}
Group:		Development/C
Requires:	%{devname} = %{version}
Provides:	audit-static-devel = %{version}-%{release}

%description -n %{staticdevname}
This package contains static libraries for %{name} used for
development.

%package -n %{auparselibname}
Summary:	Main libraries for %{name}
Group:		System/Libraries
Conflicts:	%{mklibname audit 0} <= 1.7.13

%description -n %{auparselibname}
This package contains the main auparse libraries for %{name}.

%package -n %{auparsedevname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{auparselibname} = %{version}
Provides:	auparse-devel = %{version}-%{release}
Conflicts:	%{mklibname audit 0 -d} <= 1.7.13

%description -n %{auparsedevname}
This package contains development files for %{name}.

%package -n %{auparsestaticdevname}
Summary:	Static libraries for %{name}
Requires:	%{auparsedevname} = %{version}
Group:		Development/C
Provides:	auparse-static-devel = %{version}-%{release}
Conflicts:	%{mklibname audit 0 -d -s} <= 1.7.13

%description -n %{auparsestaticdevname}
This package contains static libraries for %{name} used for
development.

%package -n python-audit
Summary:	Python bindings for %{name}
Group:		Development/Python

%description -n python-audit
This package contains python3 bindings for %{name}.

%package -n audispd-plugins
Summary:	Plugins for the audit event dispatcher
Group:		System/Base
Requires:	%{name} = %{version}
Requires:	openldap

%description -n audispd-plugins
The audispd-plugins package provides plugins for the real-time interface to the
audit system, audispd. These plugins can do things like relay events to remote
machines or analyze events for suspicious behavior.

%prep
%autosetup -p1

# Remove the ids code, its not ready
sed -i 's/ ids / /' audisp/plugins/Makefile.in
find -type d -name ".libs" | xargs rm -rf

%build
%configure \
	--sbindir=/sbin \
	--libdir=/%{_lib} \
	--with-python=no \
	--with-python3=yes \
%if %{with systemd}
	--enable-systemd \
%else
	--disable-systemd \
%endif
	--enable-static \
	--with-libwrap \
	--enable-gssapi-krb5=no \
%ifarch aarch64
	--with-aarch64 \
%endif
%ifarch armv7hl armv7hnl
	--with-arm \
%endif
	--with-libcap-ng=yes \
	--libexecdir=%{_sbindir}

%make_build

%install
install -d %{buildroot}%{_var}/log/audit
install -d %{buildroot}%{_libdir}/audit
install -d %{buildroot}%{_var}/spool/audit

%make_install
install -d %{buildroot}/%{_libdir}
# This winds up in the wrong place when libtool is involved
mv %{buildroot}/%{_lib}/libaudit.a %{buildroot}%{_libdir}/
mv %{buildroot}/%{_lib}/libauparse.a %{buildroot}%{_libdir}/
curdir=$(pwd)
cd %{buildroot}/%{_libdir}
LIBNAME="$(basename $(ls %{buildroot}/%{_lib}/libaudit.so.%{major}.*.*))"
ln -s ../../%{_lib}/$LIBNAME libaudit.so
LIBNAME="$(basename $(ls %{buildroot}/%{_lib}/libauparse.so.%{auparsemajor}.*.*))"
ln -s ../../%{_lib}/$LIBNAME libauparse.so
cd $curdir

%if %{with systemd}
mkdir -p %{buildroot}%{_systemunitdir}
mv %{buildroot}/%{_prefix}/lib/systemd/system/auditd.service %{buildroot}%{_systemunitdir}/auditd.service
install -D -p -m 644 %{SOURCE1} %{buildroot}%{_tmpfilesdir}/%{name}.conf
%else
rm -rf %{buildroot}%{_sysconfdir}/rc.d/init.d/auditd
rm -rf %{buildroot}%{_sysconfdir}/sysconfig/auditd
%endif

# Move the pkgconfig file
mv %{buildroot}/%{_lib}/pkgconfig %{buildroot}%{_libdir}

# uneeded files
rm -f %{buildroot}/%{_lib}/*.so
rm -f %{buildroot}/%{_lib}/*.la
rm -f %{buildroot}%{py_platsitedir}/*.{a,la}
rm -rf %{buildroot}/%{_libdir}/%{name}

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-audit.preset << EOF
disable auditd.service
EOF

%post
# Copy default rules into place on new installation
files=$(ls /etc/audit/rules.d/ 2>/dev/null | wc -w)
if [ "$files" -eq 0 ] ; then
# FESCO asked for audit to be off by default. #1117953
    if [ -e /usr/share/doc/audit/rules/10-no-audit.rules ]; then
	cp /usr/share/doc/audit/rules/10-no-audit.rules /etc/audit/rules.d/audit.rules
    else
	touch /etc/audit/rules.d/audit.rules
    fi
    chmod 0600 /etc/audit/rules.d/audit.rules
fi

%if %{with systemd}
%systemd_post auditd.service

%preun
%systemd_preun auditd.service
%endif

%files
%doc README rules init.d/auditd.cron
%attr(0750,root,root) %dir %{_sysconfdir}/%{name}
%attr(0750,root,root) %dir %{_datadir}/%{name}
%attr(0750,root,root) %dir %{_datadir}/%{name}/sample-rules
%attr(0750,root,root) %ghost %dir  %{_sysconfdir}/%{name}/rules.d
%attr(0750,root,root) %dir  %{_sysconfdir}/%{name}/plugins.d
%ghost %config(noreplace) %attr(0640,root,root)  %{_sysconfdir}/%{name}/rules.d/audit.rules
%ghost %config(noreplace) %attr(0640,root,root)  %{_sysconfdir}/%{name}/audit.rules
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/%{name}/auditd.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/%{name}/audit-stop.rules
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/%{name}/plugins.d/af_unix.conf
%attr(0750,root,root) /sbin/auditctl
%attr(0750,root,root) /sbin/auditd
%attr(0750,root,root) /sbin/autrace
%attr(0755,root,root) /sbin/aureport
%attr(0755,root,root) /sbin/ausearch
%attr(0755,root,root) /sbin/augenrules
%if %{with systemd}
%{_tmpfilesdir}/%{name}.conf
%{_systemunitdir}/auditd.service
%attr(0755,root,root) %{_sbindir}/initscripts/legacy-actions/auditd/*
%endif
%{_presetdir}/86-audit.preset
%attr(0755,root,root) %{_bindir}/aulastlog
%attr(0755,root,root) %{_bindir}/aulast
%attr(0755,root,root) %{_bindir}/ausyscall
%attr(0755,root,root) %{_bindir}/auvirt
%attr(0644,root,root) %{_datadir}/%{name}/sample-rules/*
%attr(0644,root,root) %{_mandir}/man5/auditd.conf.5*
%attr(0644,root,root) %{_mandir}/man5/ausearch-expression.5*
%attr(0644,root,root) %{_mandir}/man5/auditd-plugins.5*
%attr(0644,root,root) %{_mandir}/man7/audit.rules.7*
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
%{_libdir}/libaudit.so
%{_includedir}/libaudit.h
%{_datadir}/aclocal/audit.m4
%{_libdir}/pkgconfig/audit.pc
%{_libdir}/pkgconfig/auparse.pc
%{_mandir}/man3/audit_*
%{_mandir}/man3/ausearch_*
%{_mandir}/man3/get_auditfail_action.3*
%{_mandir}/man3/set_aumessage_mode.3*

%files -n %{staticdevname}
%{_libdir}/libaudit.a

%files -n %{auparselibname}
/%{_lib}/libauparse.so.%{auparsemajor}*

%files -n %{auparsedevname}
%{_libdir}/libauparse.so
%{_includedir}/auparse-defs.h
%{_includedir}/auparse.h
%{_mandir}/man3/auparse_*

%files -n %{auparsestaticdevname}
%{_libdir}/libauparse.a

%files -n python-audit
%{py3_platsitedir}/__pycache__/*.py*
%{py3_platsitedir}/*.so
%{py3_platsitedir}/audit.p*

%files -n audispd-plugins
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/%{name}/audisp-remote.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/%{name}/plugins.d/au-remote.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/%{name}/plugins.d/audispd-zos-remote.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/%{name}/plugins.d/syslog.conf
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/%{name}/zos-remote.conf
%attr(0750,root,root) /sbin/audisp-syslog
%attr(0750,root,root) /sbin/audispd-zos-remote
%attr(0750,root,root) /sbin/audisp-remote
%attr(0644,root,root) %{_mandir}/man5/audisp-remote.conf.5*
%attr(0644,root,root) %{_mandir}/man5/zos-remote.conf.5*
%attr(0644,root,root) %{_mandir}/man8/audisp-syslog.8*
%attr(0644,root,root) %{_mandir}/man8/audispd-zos-remote.8*
%attr(0644,root,root) %{_mandir}/man8/audisp-remote.8*
%attr(0750,root,root) %dir %{_var}/spool/audit
