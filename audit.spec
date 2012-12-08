%define major 1
%define libname %mklibname audit %{major}
%define develname %mklibname -d audit
%define staticdevelname %mklibname -d -s audit

%define auparsemajor 0
%define auparselibname %mklibname auparse %{auparsemajor}
%define auparsedevelname %mklibname -d auparse
%define auparsestaticdevelname %mklibname -d -s auparse

Summary:	User-space tools for Linux 2.6 kernel auditing
Name:		audit
Version:	2.1.2
Release:	4
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
BuildRequires:	libtool
BuildRequires:	openldap-devel
BuildRequires:	prelude-devel >= 0.9.16
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
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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

%package -n	%{auparselibname}
Summary:	Main libraries for %{name}
Group:		System/Libraries
Conflicts:	%{mklibname audit 0} <= 1.7.13

%description -n	%{auparselibname}
This package contains the main auparse libraries for %{name}.

%package -n	%{auparsedevelname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{auparselibname} = %{version}
Provides:	auparse-devel = %{version}-%{release}
Conflicts:	%{mklibname audit 0 -d} <= 1.7.13

%description -n	%{auparsedevelname}
This package contains development files for %{name}.

%package -n	%{auparsestaticdevelname}
Summary:	Static libraries for %{name}
Requires:	%{auparsedevelname} = %{version}
Group:		Development/C
Provides:	auparse-static-devel = %{version}-%{release}
Conflicts:	%{mklibname audit 0 -d -s} <= 1.7.13

%description -n	%{auparsestaticdevelname}
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
%patch0 -p1

find -type d -name ".libs" | xargs rm -rf

%build
%serverbuild
autoreconf -f -v --install

%configure2_5x \
    --sbindir=/sbin \
    --libdir=/%{_lib} \
    --with-prelude \
    --with-libwrap \
    --enable-gssapi-krb5=no \
    --with-libcap-ng=yes \
    --libexecdir=%{_sbindir}

%make

%install
rm -rf %{buildroot}

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

# uneeded files
rm -f %{buildroot}/%{_lib}/*.so
rm -f %{buildroot}/%{_lib}/*.la
rm -f %{buildroot}%{py_platsitedir}/*.{a,la}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig

%post -n %{auparselibname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%postun -n %{auparselibname} -p /sbin/ldconfig
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
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/audisp/plugins.d/syslog.conf
%attr(0750,root,root) /sbin/audispd
%attr(0750,root,root) /sbin/auditctl
%attr(0750,root,root) /sbin/auditd
%attr(0750,root,root) /sbin/autrace
%attr(0755,root,root) /sbin/aureport
%attr(0755,root,root) /sbin/ausearch
%attr(0755,root,root) %{_bindir}/aulastlog
%attr(0755,root,root) %{_bindir}/aulast
%attr(0755,root,root) %{_bindir}/ausyscall
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
%attr(0700,root,root) %dir %{_var}/log/audit

%files -n %{libname}
%defattr(-,root,root)
%config(noreplace) %attr(0640,root,root) %{_sysconfdir}/libaudit.conf
/%{_lib}/libaudit.so.%{major}*
%attr(0644,root,root) %{_mandir}/man5/libaudit.conf.5*

%files -n %{develname}
%defattr(-,root,root)
%doc ChangeLog contrib/skeleton.c contrib/plugin
%{_libdir}/libaudit.so
%{_includedir}/libaudit.h
%{_mandir}/man3/audit_*
%{_mandir}/man3/ausearch_*
%{_mandir}/man3/get_auditfail_action.3*
%{_mandir}/man3/set_aumessage_mode.3*

%files -n %{staticdevelname}
%defattr(-,root,root)
%{_libdir}/libaudit.a

%files -n %{auparselibname}
%defattr(-,root,root)
/%{_lib}/libauparse.so.%{auparsemajor}*

%files -n %{auparsedevelname}
%defattr(-,root,root)
%doc ChangeLog contrib/skeleton.c contrib/plugin
%{_libdir}/libauparse.so
%{_includedir}/auparse-defs.h
%{_includedir}/auparse.h
%{_mandir}/man3/auparse_*

%files -n %{auparsestaticdevelname}
%defattr(-,root,root)
%{_libdir}/libauparse.a

%files -n python-audit
%defattr(-,root,root)
%{py_platsitedir}/*.so
%{py_platsitedir}/audit.p*

%files -n audispd-plugins
%defattr(-,root,root,-)
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


%changelog
* Mon Jun 13 2011 Oden Eriksson <oeriksson@mandriva.com> 2.1.2-1mdv2011.0
+ Revision: 684386
- 2.1.2

* Fri Apr 22 2011 Oden Eriksson <oeriksson@mandriva.com> 2.1.1-1
+ Revision: 656627
- 2.1.1

* Sun Feb 06 2011 Oden Eriksson <oeriksson@mandriva.com> 2.0.6-1
+ Revision: 636365
- 2.0.6

* Thu Nov 04 2010 Götz Waschk <waschk@mandriva.org> 2.0.5-2mdv2011.0
+ Revision: 593331
- rebuild for new python 2.7

* Sun Oct 10 2010 Oden Eriksson <oeriksson@mandriva.com> 2.0.5-1mdv2011.0
+ Revision: 584586
- 2.0.5
- drop upstream added patches

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 2.0.4-5mdv2010.1
+ Revision: 523828
- more split and deps fixes

* Tue Mar 16 2010 Oden Eriksson <oeriksson@mandriva.com> 2.0.4-4mdv2010.1
+ Revision: 521483
- fix deps

* Mon Mar 15 2010 Oden Eriksson <oeriksson@mandriva.com> 2.0.4-3mdv2010.1
+ Revision: 519924
- refine the split

* Mon Mar 15 2010 Oden Eriksson <oeriksson@mandriva.com> 2.0.4-2mdv2010.1
+ Revision: 519883
- fix build
- revert the lib split

* Sun Mar 14 2010 Oden Eriksson <oeriksson@mandriva.com> 2.0.4-1mdv2010.1
+ Revision: 519090
- 2.0.4 (sync with audit-2.0.4-3.fc13.src.rpm)
- rebuild
- bump release
- disable gssapi support (bogdano)

* Mon Jul 27 2009 Emmanuel Andry <eandry@mandriva.org> 1.7.13-1mdv2010.0
+ Revision: 400832
- New version 1.7.13
- drop p101 and p103 (merged upstream)
- check major

* Mon Apr 06 2009 Frederik Himpe <fhimpe@mandriva.org> 1.7.12-3mdv2009.1
+ Revision: 364560
- Add LSB headers to init script (bug #49587)
- Add Fedora patches:
  * Handle audit=0 boot option for 2.6.29 kernel (RH Bug 487541)
  * Drop some debug code in libev
  * Move audit.py file to arch specific python dir

* Thu Feb 26 2009 Oden Eriksson <oeriksson@mandriva.com> 1.7.12-1mdv2009.1
+ Revision: 345019
- 1.7.12
- sync with the bundled spec file

* Sun Jan 11 2009 Oden Eriksson <oeriksson@mandriva.com> 1.7.11-1mdv2009.1
+ Revision: 328322
- 1.7.11
- drop P2, it's fixed upstream

* Fri Dec 26 2008 Funda Wang <fwang@mandriva.org> 1.7.10-2mdv2009.1
+ Revision: 319212
- rebuild for new python

* Sat Dec 20 2008 Oden Eriksson <oeriksson@mandriva.com> 1.7.10-1mdv2009.1
+ Revision: 316500
- 1.7.10
- drop one redundant patch
- fix build with -Werror=format-security (P2)

* Thu Nov 06 2008 Oden Eriksson <oeriksson@mandriva.com> 1.7.9-1mdv2009.1
+ Revision: 300182
- 1.7.9

* Thu Oct 23 2008 Oden Eriksson <oeriksson@mandriva.com> 1.7.8-1mdv2009.1
+ Revision: 296652
- 1.7.8

* Thu Sep 18 2008 Oden Eriksson <oeriksson@mandriva.com> 1.7.7-1mdv2009.0
+ Revision: 285646
- 1.7.7 (Major bugfixes)
- drop upstream implemented patches

* Sat Sep 13 2008 Oden Eriksson <oeriksson@mandriva.com> 1.7.6-2mdv2009.0
+ Revision: 284587
- remove the _disable_ld_as_needed workaround, it's fixed in P5

* Sat Sep 13 2008 Oden Eriksson <oeriksson@mandriva.com> 1.7.6-1mdv2009.0
+ Revision: 284451
- use _disable_ld_as_needed because auditd won't link
  against -lwrap otherwise
- added one security fix from svn (P4)

* Fri Sep 12 2008 Oden Eriksson <oeriksson@mandriva.com> 1.7.6-0.1mdv2009.0
+ Revision: 284213
- 1.7.6, enables tcp_wrappers support but don't
  link it in for some reason...
- misc spec file fixes

* Tue Aug 26 2008 Oden Eriksson <oeriksson@mandriva.com> 1.7.5-1mdv2009.0
+ Revision: 276119
- 1.7.5

* Fri Aug 08 2008 Thierry Vignaud <tv@mandriva.org> 1.7.3-3mdv2009.0
+ Revision: 267862
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Mon May 19 2008 Oden Eriksson <oeriksson@mandriva.com> 1.7.3-1mdv2009.0
+ Revision: 209147
- 1.7.3
- drop upstream applied patches
- 1.7.2
- sync with fedora (audit-1.7.2-6.fc9.src.rpm)

* Sat Apr 12 2008 Oden Eriksson <oeriksson@mandriva.com> 1.6.8-1mdv2009.0
+ Revision: 192614
- P2: security fix for CVE-2008-1628

* Thu Feb 14 2008 Oden Eriksson <oeriksson@mandriva.com> 1.6.8-1mdv2008.1
+ Revision: 168666
- 1.6.8

* Fri Feb 01 2008 Oden Eriksson <oeriksson@mandriva.com> 1.6.7-1mdv2008.1
+ Revision: 161092
- 1.6.7
- dropped P2, it's implemented upstream
- added the prelude support (plugins should be broken out)

* Fri Jan 11 2008 Andreas Hasenack <andreas@mandriva.com> 1.6.5-2mdv2008.1
+ Revision: 148491
- rebuild to force re-upload

* Tue Jan 08 2008 Andreas Hasenack <andreas@mandriva.com> 1.6.5-1mdv2008.1
+ Revision: 146739
- updated to version 1.6.5

* Thu Jan 03 2008 Andreas Hasenack <andreas@mandriva.com> 2mdv2008.1-current
+ Revision: 142635
- fix log file permissions check

* Thu Jan 03 2008 Andreas Hasenack <andreas@mandriva.com> 1.6.4-1mdv2008.1
+ Revision: 142477
- updated to version 1.6.4
- imported Oden's changes:
  - new plugin package
  - am_cflags patch
  - spec cleanup
  - openldap-devel buildrequires

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Sep 25 2007 Andreas Hasenack <andreas@mandriva.com> 1.6.1-5mdv2008.0
+ Revision: 92698
- fixed "config file too large" on x86_64 (#33891)
- added some missing requires for system-config-audit

* Mon Sep 24 2007 Andreas Hasenack <andreas@mandriva.com> 1.6.1-4mdv2008.0
+ Revision: 92509
- change menu icon (#33920)
- fix sendmail check (#33891)

* Fri Sep 21 2007 Andreas Hasenack <andreas@mandriva.com> 1.6.1-3mdv2008.0
+ Revision: 92101
- fixed menu (#33868)
- fixed duplicated lang entry (#33874)

* Fri Sep 21 2007 David Walluck <walluck@mandriva.org> 1.6.1-2mdv2008.0
+ Revision: 92084
- add some devel provides for fc compat
- use %%{configure2_5x} and %%{makeinstall_std}

* Tue Sep 18 2007 Andreas Hasenack <andreas@mandriva.com> 1.6.1-1mdv2008.0
+ Revision: 89849
- updated to version 1.6.1
- obey new library policy (unversioned devel)
- properly package system-config-audit GUI

* Sun Sep 16 2007 Thierry Vignaud <tv@mandriva.org> 1.5.6-4mdv2008.0
+ Revision: 87792
- fix system-config-audit starting (#33354)

* Mon Aug 13 2007 Thierry Vignaud <tv@mandriva.org> 1.5.6-3mdv2008.0
+ Revision: 62632
- add missing requires for python module (#32503)

* Fri Aug 10 2007 Thierry Vignaud <tv@mandriva.org> 1.5.6-2mdv2008.0
+ Revision: 61460
- run %%find_lang in %%install
- package missing files
- create libaudit-common sub package
- add missing buildrequires
- new release
- fix build
- new devel policy

  + Andreas Hasenack <andreas@mandriva.com>
    - buildrequires glibc-devel which has the needed headers
    - updated to version 1.5.4
    - fixed group
    - fixed requires
    - fixer provides
    - Import audit

