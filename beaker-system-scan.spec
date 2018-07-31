%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

# Python 3 on Fedora 29+ / RHEL8+, Python 2 otherwise.
%if 0%{?fedora} >= 29 || 0%{?rhel} >= 8
%bcond_without python3
%else
%bcond_with python3
%endif

# Can't run tests on older RHELs, we are missing pytest.
%if 0%{?fedora} || 0%{?rhel} >= 7
# Also can't run tests on non-x86 platforms because of
# the mess with conditionally compiling hvm_detect.
%ifarch x86_64
%bcond_without tests
%else
%bcond_with tests
%endif
%else
%bcond_with tests
%endif

# x86_64 is the only arch with compiled code (hvm_detect), all other arches are 
# pure Python and hence debuginfo is empty.
%ifnarch x86_64
%global debug_package %{nil}
%endif

Name:           beaker-system-scan
Version:        2.3
Release:        3%{?dist}
Summary:        Collect and upload hardware information to Beaker
Group:          Applications/System
License:        GPLv2+
URL:            http://beaker-project.org/
Source0:        http://beaker-project.org/releases/%{name}-%{version}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  gcc
%if %{with python3}
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
Requires:       python3-linux-procfs
Requires:       python3-setuptools
Requires:       python3-lxml
%if %{with tests}
BuildRequires:  python3-pytest
# runtime requirements also needed for tests
BuildRequires:  python3-linux-procfs
BuildRequires:  python3-lxml
%endif
%else
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
Requires:       python-linux-procfs
Requires:       python-setuptools
Requires:       python-lxml
%if %{with tests}
BuildRequires:  pytest
# runtime requirements also needed for tests
BuildRequires:  python-linux-procfs
BuildRequires:  python-lxml
%endif
%endif
Requires:       lshw
%if 0%{?rhel} < 6  && !(0%{?fedora} > 0)
Requires:       python-simplejson
%ifarch x86_64
Requires:       kmod-kvm
%endif
%endif
%ifarch x86_64
Requires:       /usr/bin/iasl
%endif
Requires:       device-mapper-multipath

%description
beaker-system-scan is a small script to collect details about the hardware of 
the system it is run on, and upload those details to a Beaker server.

%prep
%setup -q
%if 0%{?rhel} == 5
sed -r -i -e 's/except (.*) as (.*):/except \1, \2:/' systemscan/*.py
%endif

%build
%if %{with python3}
make %{?_smp_mflags} PYTHON="%{__python3}" CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
%else
make %{?_smp_mflags} PYTHON="%{__python}" CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
%endif

%install
rm -rf %{buildroot}
%if %{with python3}
make install PYTHON="%{__python3}" DESTDIR=%{buildroot}
%else
make install PYTHON="%{__python}" DESTDIR=%{buildroot}
%endif

%if %{with tests}
%check
%if %{with python3}
PYTHONPATH=. py.test-3 -vv tests/
%else
PYTHONPATH=. py.test -vv tests/
%endif
%endif

%files
%doc COPYING
%if %{with python3}
%{python3_sitelib}/systemscan
%{python3_sitelib}/bkr.systemscan*.egg-info
%else
%{python_sitelib}/systemscan
%{python_sitelib}/bkr.systemscan*.egg-info
%endif
%{_libexecdir}/%{name}
%{_bindir}/%{name}

%changelog
* Tue Jul 31 2018 Dan Callaghan <dcallagh@redhat.com> 2.3-3
- tests: can't check the value of 'Numa' (dcallagh@redhat.com)

* Tue Jul 31 2018 Dan Callaghan <dcallagh@redhat.com> 2.3-2
- disable tests on non-x86 platforms (dcallagh@redhat.com)

* Tue Jul 31 2018 Dan Callaghan <dcallagh@redhat.com> 2.3-1
- collect firmware information (sdoherty@redhat.com)
- Python 3 support (dcallagh@redhat.com)
- tests: refactor to make it easier to add new samples (dcallagh@redhat.com)
- tests: add missing /proc/cpuinfo sample for APM Mustang (dcallagh@redhat.com)
- tests: better assertion messages (dcallagh@redhat.com)
- run tests in rpmbuild (dcallagh@redhat.com)

* Wed Jun 15 2016 Dan Callaghan <dcallagh@redhat.com> 2.2-1
- KVM module is called kvm_hv on POWER (dcallagh@redhat.com)

* Thu Aug 27 2015 Dan Callaghan <dcallagh@redhat.com> 2.1-1
- fix DISKSPACE cumulative rounding error (dcallagh@redhat.com)
- identify PnP devices by looking for <capability id="pnp">
  (dcallagh@redhat.com)
- omit 0000:0000 from USBID key-values (dcallagh@redhat.com)
- work around wrong PCI class for virtio memory balloon (dcallagh@redhat.com)

* Thu Aug 13 2015 Dan Callaghan <dcallagh@redhat.com> 2.0-4
- ensure disk sector sizes are always populated (dcallagh@redhat.com)

* Wed Aug 12 2015 Dan Callaghan <dcallagh@redhat.com> 2.0-3
- CPUFAMILY and CPUMODELNUMBER are numeric (dcallagh@redhat.com)

* Tue Aug 11 2015 Dan Callaghan <dcallagh@redhat.com> 2.0-2
- convert DISK_CONTROLLER value to a real unicode object (dcallagh@redhat.com)

* Fri Aug 07 2015 Dan Callaghan <dcallagh@redhat.com> 2.0-1
- use 'lshw' instead of 'smolt'
- new regression test suite

* Wed Jan 28 2015 Amit Saha <asaha@redhat.com> 1.6-1
- Make the code Python 2.4 compatible (asaha@redhat.com)
- iasl => /usr/bin/iasl (asaha@redhat.com)
- Add runtime dependencies on parted and python-setuptools (asaha@redhat.com)

* Thu Oct 16 2014 Amit Saha <asaha@redhat.com> 1.5-1
- Redirect stdout of "service multipathd restart" to /dev/null
  (asaha@redhat.com)
- Ignore failures from getdriver.sh when finding the bootdisk
  (asaha@redhat.com)

* Fri Aug 29 2014 Amit Saha <asaha@redhat.com> 1.4-1
- Try a more recent version of libparted for Fedora 20+ and RHEL 7+
  (asaha@redhat.com)
- Always return 0 from hvm_detect (asaha@redhat.com)
- Couple of random changes: (asaha@redhat.com)
- Add Fedora checking for kmod-kvm (asaha@redhat.com)
- Add a new switch to output JSON data when run in debug mode
  (asaha@redhat.com)

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
