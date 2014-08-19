%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name:           beaker-system-scan
Version:        1.3
Release:        1%{?dist}
Summary:        Collect and upload hardware information to Beaker
Group:          Applications/System
License:        GPLv2+
URL:            http://beaker-project.org/
Source0:        http://beaker-project.org/releases/%{name}-%{version}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  python2-devel
BuildRequires:  python-setuptools

Requires:       smolt
%if 0%{?rhel} < 6  && !(0%{?fedora} > 0)
%ifarch x86_64
Requires:       kmod-kvm
%endif
%endif
%ifarch x86_64
Requires:       iasl
%endif
Requires:       device-mapper-multipath
Requires:       python-ctypes
Requires:       python-linux-procfs

%description
beaker-system-scan is a small script to collect details about the hardware of 
the system it is run on, and upload those details to a Beaker server.

%prep
%setup -q

%build
make %{?_smp_mflags} CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

%files
%doc COPYING
%{python_sitelib}/systemscan
%{python_sitelib}/bkr.systemscan*.egg-info
%{_libexecdir}/%{name}
%{_bindir}/%{name}

%changelog
* Thu May 08 2014 Amit Saha <asaha@redhat.com> 1.3-1
- s390x 'identification' should be converted to an integer (asaha@redhat.com)
- s390x and ppc: Fill in CPU model field (asaha@redhat.com)
- Make iasl a conditional dependency for x86_64 (asaha@redhat.com)

* Tue Jul 30 2013 Dan Callaghan <dcallagh@redhat.com> 1.2-3
- kmod-kvm is for x86_64 only (dcallagh@redhat.com)

* Fri Jul 26 2013 Dan Callaghan <dcallagh@redhat.com> 1.2-2
- %%{python_sitelib} is not defined on RHEL5 (dcallagh@redhat.com)

* Fri Jul 26 2013 Dan Callaghan <dcallagh@redhat.com> 1.2-1
- initial version, based on /distribution/inventory task from Beaker
