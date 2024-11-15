AutoReqProv: no
%global pybasever 2.7

Name:       python27
Version:    2.7.18
Release:    1.buildroot%{?dist}
Summary:    Interpreter of the Python programming language

License:    Python
URL:        https://www.python.org/
Source:     https://www.python.org/ftp/python/%{version}/Python-%{version}.tar.xz
%global debug_package %{nil}
%global ABIFLAGS_optimized m
%global ABIFLAGS_debug     dm
%global LDVERSION_optimized %{pybasever}%{ABIFLAGS_optimized}
%global LDVERSION_debug     %{pybasever}%{ABIFLAGS_debug}
BuildRequires: autoconf
BuildRequires: bluez-libs-devel
BuildRequires: bzip2
BuildRequires: bzip2-devel
BuildRequires: expat-devel
BuildRequires: findutils
BuildRequires: gcc-c++
BuildRequires: glibc-all-langpacks
BuildRequires: glibc-devel
BuildRequires: gmp-devel
BuildRequires: libGL-devel
BuildRequires: libX11-devel
BuildRequires: libdb-devel
BuildRequires: libffi-devel
BuildRequires: libnsl2-devel
BuildRequires: libtirpc-devel
BuildRequires: make
BuildRequires: ncurses-devel
BuildRequires: openssl-devel
BuildRequires: pkgconf-pkg-config
BuildRequires: readline-devel
BuildRequires: sqlite-devel
BuildRequires: tar
BuildRequires: tcl-devel
BuildRequires: tix-devel
BuildRequires: tk-devel
BuildRequires: zlib-devel
BuildRequires: gnupg2
BuildRequires: git-core

BuildRequires: gdbm-devel >= 1:1.13


BuildRequires: systemtap-sdt-devel
BuildRequires: /usr/bin/dtrace

BuildRequires: valgrind-devel

%global _description \
Python is an accessible, high-level, dynamically typed, interpreted programming\
language, designed with an emphasis on code readibility.\
It includes an extensive standard library, and has a vast ecosystem of\
third-party libraries.\
\
The python37 package provides the "python3.7" executable: the reference\
interpreter for the Python language, version 3.\
\
The python37-devel package contains files for dovelopment of Python application\
and the python36-debug is helpful for debugging.\
\
Packages containing additional libraries for Python 3.7 are generally named\
with the "python3-" prefix. Documentation for Python is provided in the\
python3-docs package.

%description %_description

%package devel
Summary:    Libraries and header files needed for Python development
Requires:   python311

%description devel
This package contains the header files and configuration needed to compile
Python extension modules (typically written in C or C++), to embed Python
into other programs, and to make binary distributions for Python libraries.

It also contains the necessary macros to build RPM packages with Python modules.

%prep
%autosetup -n Python-%{version}

%build
%configure
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_bindir}
make altinstall DESTDIR=$RPM_BUILD_ROOT
#ln -s /usr/bin/python%{pybasever} $RPM_BUILD_ROOT/%{_bindir}/python3

%files
%{_bindir}/python%{pybasever}
#%{_bindir}/python3
/usr/lib/python%{pybasever}/
/usr/lib/python%{pybasever}/*
/usr/lib64/python%{pybasever}/
/usr/lib64/python%{pybasever}/*
/usr/share/man/man1/python%{pybasever}.1.gz
#/usr/bin/2to3-%{pybasever}
#/usr/bin/easy_install-%{pybasever}
/usr/bin/idle%{pybasever}
/usr/bin/pip%{pybasever}
/usr/bin/pydoc%{pybasever}
#/usr/bin/python%{pybasever}m
/usr/bin/python%{pybasever}-config
#/usr/bin/pyvenv-%{pybasever}
/usr/include/python%{pybasever}/
/usr/include/python%{pybasever}/*
/usr/lib64/libpython%{pybasever}.a

%files devel
/usr/lib64/pkgconfig/python-%{pybasever}.pc
/usr/lib64/pkgconfig/python-%{pybasever}-embed.pc

%changelog
* Sat Sep 29 2018 Tomas Orsava <torsava@redhat.com> - 3.6.6-13.buildroot
- Merged `stream-3.6` branch into the `rhel-8.0` branch for the buildroot
- Differences:
  - Don't provide `python3-devel` from the `python36-devel` package because
    `python3-devel` itself is actually available in the buildroot
  - Instead of using the `alternatives`, simply simplink the main executables
    (python3, python3-config,...)
- Resolves: rhbz#1619153
