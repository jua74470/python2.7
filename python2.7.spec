# ======================================================
# Conditionals and other variables controlling the build
# ======================================================

# Note that the bcond macros are named for the CLI option they create.
# "%%bcond_without" means "ENABLE by default and create a --without option"

# Whether to use RPM build wheels from the python-{pip,setuptools}-wheel package
# Uses upstream bundled prebuilt wheels otherwise
# setuptools >= 45.0 no longer support Python 2.7, hence disabled
%bcond_with rpmwheels

# Run the test suite in %%check
%bcond_without tests

# Simplify dependencis for Flatpaks that include Python-2.7
%if 0%{?flatpak}
%bcond_with tkinter
%else
%bcond_without tkinter
%endif

%global unicode ucs4
%global pybasever 2.7
%global pyshortver 27
%global pylibdir %{_libdir}/python%{pybasever}
%global tools_dir %{pylibdir}/Tools
%global demo_dir %{pylibdir}/Demo
%global doc_tools_dir %{pylibdir}/Doc/tools
%global dynload_dir %{pylibdir}/lib-dynload
%global site_packages %{pylibdir}/site-packages

# Python's configure script defines SOVERSION, and this is used in the Makefile
# to determine INSTSONAME, the name of the libpython DSO:
#   LDLIBRARY='libpython$(VERSION).so'
#   INSTSONAME="$LDLIBRARY".$SOVERSION
# We mirror this here in order to make it easier to add the -gdb.py hooks.
# (if these get out of sync, the payload of the libs subpackage will fail
# and halt the build)
%global py_SOVERSION 1.0
%global py_INSTSONAME_optimized libpython%{pybasever}.so.%{py_SOVERSION}
%global py_INSTSONAME_debug     libpython%{pybasever}_d.so.%{py_SOVERSION}

%global with_huntrleaks 0
%global with_gdb_hooks 1
%global with_systemtap 1
%global with_valgrind 0
%global with_gdbm 1

# Disable automatic bytecompilation. The python2.7 binary is not yet
# available in /usr/bin when Python is built. Also, the bytecompilation fails
# on files that test invalid syntax.
%global __brp_python_bytecompile %{nil}
%global regenerate_autotooling_patch 0

# https://fedoraproject.org/wiki/Changes/Package_information_on_ELF_objects
# https://bugzilla.redhat.com/2043092
# The default %%build_ldflags macro contains a reference to a file that only
# exists in the builddir of this very package.
# The flag is stored in distutils/sysconfig and is used to build extension modules.
# As a result, 3rd party extension modules cannot be built,
# because the file does not exist when this package is installed.
# Python 3 solves this by using %%extension_ldflags in LDFLAGS_NODIST,
# however Python 2 does not support LDFLAGS_NODIST, so we opt-out completely.
# The exact opt-out mechanism is still not finalized, so we use all of them:
%undefine _package_note_flags
%undefine _package_note_file
%undefine _generate_package_note_file

# ==================
# Top-level metadata
# ==================
Summary: Version %{pybasever} of the Python interpreter
Name: python%{pybasever}
URL: https://www.python.org/

%global general_version %{pybasever}.18
#global prerel ...
%global upstream_version %{general_version}%{?prerel}
Version: %{general_version}%{?prerel:~%{prerel}}
Release: %autorelease
%if %{with rpmwheels}
License: Python
%else
# Python is Python
# setuptools is MIT and bundles:
#   packaging: BSD or ASL 2.0
#   pyparsing: MIT
#   six: MIT
# pip is MIT and bundles:
#   appdirs: MIT
#   distlib: Python
#   distro: ASL 2.0
#   html5lib: MIT
#   six: MIT
#   colorama: BSD
#   CacheControl: ASL 2.0
#   msgpack-python: ASL 2.0
#   lockfile: MIT
#   progress: ISC
#   ipaddress: Python
#   packaging: ASL 2.0 or BSD
#   pep517: MIT
#   pyparsing: MIT
#   pytoml: MIT
#   retrying: ASL 2.0
#   requests: ASL 2.0
#   chardet: LGPLv2
#   idna: BSD
#   urllib3: MIT
#   certifi: MPLv2.0
#   setuptools: MIT
#   webencodings: BSD
License: Python and MIT and ASL 2.0 and BSD and ISC and LGPLv2 and MPLv2.0 and (ASL 2.0 or BSD)
%endif

# Python 2 is deprecated in Fedora 30+, see:
#   https://fedoraproject.org/wiki/Changes/Mass_Python_2_Package_Removal
# This means that new packages MUST NOT depend on python2, even transitively
#   see: https://fedoraproject.org/wiki/Packaging:Deprecating_Packages
# Python 2 will not be supported after 2019. Use the python3 package instead
# if possible.
Provides: deprecated()

# This package was renamed from python27 in Fedora 33
Provides:  python%{pyshortver} = %{version}-%{release}
Obsoletes: python%{pyshortver} < %{version}-%{release}

# People might want to dnf install python2 instead of pythonXY
Provides: python2 = %{version}-%{release}

# We want to be nice for the packages that still remain, so we keep providing this
# TODO stop doing this in undefined future
Provides: python(abi) = %{pybasever}

# To test the python27 without disrupting everything, we keep providing the devel part until mid September 2019
Provides: python2-devel = %{version}-%{release}
%if %{with tkinter}
Provides: python2-tkinter = %{version}-%{release}
%endif


# =======================
# Build-time requirements
# =======================

# (keep this list alphabetized)

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
%if %{with tkinter}
BuildRequires: tcl-devel
BuildRequires: tix-devel
BuildRequires: tk-devel
%endif
BuildRequires: zlib-devel
BuildRequires: gnupg2
BuildRequires: git-core

%if %{with_gdbm}
# ABI change without soname bump, reverted
BuildRequires: gdbm-devel >= 1:1.13
%endif

%if 0%{?with_systemtap}
BuildRequires: systemtap-sdt-devel
# (this introduces a circular dependency, in that systemtap-sdt-devel's
# /usr/bin/dtrace is a python script)
%global tapsetdir      /usr/share/systemtap/tapset
%endif # with_systemtap

%if 0%{?with_valgrind}
BuildRequires: valgrind-devel
%endif

%if %{with rpmwheels}
BuildRequires: python-setuptools-wheel < 45
BuildRequires: python-pip-wheel
Requires: python-setuptools-wheel < 45
Requires: python-pip-wheel
%else
Provides: bundled(python2dist(setuptools)) = 41.2.0
Provides: bundled(python2dist(packaging)) = 16.8
Provides: bundled(python2dist(pyparsing)) = 2.2.1
Provides: bundled(python2dist(six)) = 1.10.0

Provides: bundled(python2dist(pip)) = 19.2.3
Provides: bundled(python2dist(appdirs)) = 1.4.3
Provides: bundled(python2dist(CacheControl)) = 0.12.5
Provides: bundled(python2dist(certifi)) = 2019.6.16
Provides: bundled(python2dist(chardet)) = 3.0.4
Provides: bundled(python2dist(colorama)) = 0.4.1
Provides: bundled(python2dist(distlib)) = 0.2.9.post0
Provides: bundled(python2dist(distro)) = 1.4.0
Provides: bundled(python2dist(html5lib)) = 1.0.1
Provides: bundled(python2dist(idna)) = 2.8
Provides: bundled(python2dist(ipaddress)) = 1.0.22
Provides: bundled(python2dist(lockfile)) = 0.12.2
Provides: bundled(python2dist(msgpack)) = 0.6.1
Provides: bundled(python2dist(packaging)) = 19.0
Provides: bundled(python2dist(pep517)) = 0.5.0
Provides: bundled(python2dist(progress)) = 1.5
Provides: bundled(python2dist(pyparsing)) = 2.4.0
Provides: bundled(python2dist(pytoml)) = 0.1.20
Provides: bundled(python2dist(requests)) = 2.22.0
Provides: bundled(python2dist(retrying)) = 1.3.3
Provides: bundled(python2dist(setuptools)) = 41.0.1
Provides: bundled(python2dist(six)) = 1.12.0
Provides: bundled(python2dist(urllib3)) = 1.25.3
Provides: bundled(python2dist(webencodings)) = 0.5.1
%endif

# For /usr/lib64/pkgconfig/
Requires: pkgconf-pkg-config

# The RPM related dependencies bring nothing to a non-RPM Python developer
# But we want them when packages BuildRequire python2-devel
Requires: (python-rpm-macros if rpm-build)
Requires: (python-srpm-macros if rpm-build)
# Remove this no sooner than Fedora 36:
Provides: python2-rpm-macros = 3.9-34
Obsoletes: python2-rpm-macros < 3.9-34

# https://bugzilla.redhat.com/show_bug.cgi?id=1217376
# https://bugzilla.redhat.com/show_bug.cgi?id=1496757
# https://bugzilla.redhat.com/show_bug.cgi?id=1218294
# TODO change to a specific subpackage once available (#1218294)
Requires: (redhat-rpm-config if gcc)

Obsoletes: python2 < %{version}-%{release}
Obsoletes: python2-debug < %{version}-%{release}
Obsoletes: python2-devel < %{version}-%{release}
Obsoletes: python2-libs < %{version}-%{release}
Obsoletes: python2-test < %{version}-%{release}
Obsoletes: python2-tkinter < %{version}-%{release}
Obsoletes: python2-tools < %{version}-%{release}


# =======================
# Source code and patches
# =======================

Source0: %{url}ftp/python/%{general_version}/Python-%{upstream_version}.tar.xz
Source1: %{url}ftp/python/%{general_version}/Python-%{upstream_version}.tar.xz.asc
Source2: %{url}static/files/pubkeys.txt

# Systemtap tapset to make it easier to use the systemtap static probes
# (actually a template; LIBRARY_PATH will get fixed up during install)
# Written by dmalcolm; not yet sent upstream
Source3: libpython.stp

# Example systemtap script using the tapset
# Written by wcohen, mjw, dmalcolm; not yet sent upstream
Source4: systemtap-example.stp

# Another example systemtap script that uses the tapset
# Written by dmalcolm; not yet sent upstream
Source5: pyfuntop.stp

Source6: macros.python2

# (Patches taken from github.com/fedora-python/cpython)

# 00000 # eb41a89085f19eab30c9e1f22d09102f3dcab7f0
# Modules/Setup.dist is ultimately used by the "makesetup" script to construct
# the Makefile and config.c
#
# Upstream leaves many things disabled by default, to try to make it easy as
# possible to build the code on as many platforms as possible.
#
# TODO: many modules can also now be built by setup.py after the python binary
# has been built; need to assess if we should instead build things there
#
# We patch it downstream as follows:
#   - various modules are built by default by upstream as static libraries;
#   we built them as shared libraries
#   - build the "readline" module (appears to also be handled by setup.py now)
#   - build the nis module (which needs the tirpc library since glibc 2.26)
#   - enable the build of the following modules:
#     - array arraymodule.c     # array objects
#     - cmath cmathmodule.c # -lm # complex math library functions
#     - math mathmodule.c # -lm # math library functions, e.g. sin()
#     - _struct _struct.c       # binary structure packing/unpacking
#     - time timemodule.c # -lm # time operations and variables
#     - operator operator.c     # operator.add() and similar goodies
#     - _weakref _weakref.c     # basic weak reference support
#     - _testcapi _testcapimodule.c    # Python C API test module
#     - _random _randommodule.c # Random number generator
#     - _collections _collectionsmodule.c # Container types
#     - itertools itertoolsmodule.c
#     - strop stropmodule.c
#     - _functools _functoolsmodule.c
#     - _bisect _bisectmodule.c # Bisection algorithms
#     - unicodedata unicodedata.c    # static Unicode character database
#     - _locale _localemodule.c
#     - fcntl fcntlmodule.c     # fcntl(2) and ioctl(2)
#     - spwd spwdmodule.c               # spwd(3)
#     - grp grpmodule.c         # grp(3)
#     - select selectmodule.c   # select(2); not on ancient System V
#     - mmap mmapmodule.c  # Memory-mapped files
#     - _csv _csv.c  # CSV file helper
#     - _socket socketmodule.c  # Socket module helper for socket(2)
#     - _ssl _ssl.c
#     - crypt cryptmodule.c -lcrypt     # crypt(3)
#     - termios termios.c       # Steen Lumholt's termios module
#     - resource resource.c     # Jeremy Hylton's rlimit interface
#     - audioop audioop.c       # Operations on audio samples
#     - imageop imageop.c       # Operations on images
#     - _md5 md5module.c md5.c
#     - _sha shamodule.c
#     - _sha256 sha256module.c
#     - _sha512 sha512module.c
#     - linuxaudiodev linuxaudiodev.c
#     - timing timingmodule.c
#     - _tkinter _tkinter.c tkappinit.c
#     - dl dlmodule.c
#     - gdbm gdbmmodule.c
#     - _bsddb _bsddb.c
#     - binascii binascii.c
#     - parser parsermodule.c
#     - cStringIO cStringIO.c
#     - cPickle cPickle.c
#     - zlib zlibmodule.c
#     - _multibytecodec cjkcodecs/multibytecodec.c
#     - _codecs_cn cjkcodecs/_codecs_cn.c
#     - _codecs_hk cjkcodecs/_codecs_hk.c
#     - _codecs_iso2022 cjkcodecs/_codecs_iso2022.c
#     - _codecs_jp cjkcodecs/_codecs_jp.c
#     - _codecs_kr cjkcodecs/_codecs_kr.c
#     - _codecs_tw cjkcodecs/_codecs_tw.c
Patch0: python-2.7.1-config.patch

# 00001 # 4cc17cbeaa6c5320d44494c14fe4abe479bf186b
# Removes the "-g" option from "pydoc", for some reason; I believe
# (dmalcolm 2010-01-29) that this was introduced in this change:
# - fix pydoc (#68082)
# in 2.2.1-12 as a response to the -g option needing TkInter installed
# (Red Hat Linux 8)
Patch1: 00001-pydocnogui.patch

# 00004 # 81b93bf369d9d67c71beb5449ff0870f8ac15c7d
# Add $(CFLAGS) to the linker arguments when linking the "python" binary
# since some architectures (sparc64) need this (rhbz:199373).
# Not yet filed upstream
Patch4: python-2.5-cflags.patch

# 00006 # bebaf146393db2eb55ea494243a4095ae32eb50d
# Work around a bug in Python' gettext module relating to the "Plural-Forms"
# header (rhbz:252136)
# Related to upstream issues:
#   http://bugs.python.org/issue1448060 and http://bugs.python.org/issue1475523
# though the proposed upstream patches are, alas, different
Patch6: python-2.5.1-plural-fix.patch

# 00007 # 824c01cf0f2ee2f66cdd8373295431c16b809c5c
# This patch was listed in the changelog as:
#  * Fri Sep 14 2007 Jeremy Katz <katzj@redhat.com> - 2.5.1-11
#  - fix encoding of sqlite .py files to work around weird encoding problem
#  in Turkish (#283331)
# A traceback attached to rhbz 244016 shows the problem most clearly: a
# traceback on attempting to import the sqlite module, with:
#   "SyntaxError: encoding problem: with BOM (__init__.py, line 1)"
# This seems to come from Parser/tokenizer.c:check_coding_spec
# Our patch changes two source files within sqlite3, removing the
# "coding: ISO-8859-1" specs and character E4 = U+00E4 =
# LATIN SMALL LETTER A WITH DIAERESIS from in ghaering's surname.
#
# It may be that the conversion of "ISO-8859-1" to "iso-8859-1" is thwarted
# by the implementation of "tolower" in the Turkish locale; see:
#   https://bugzilla.redhat.com/show_bug.cgi?id=191096#c9
#
# TODO: Not yet sent upstream, and appears to me (dmalcolm 2010-01-29) that
# it may be papering over a symptom
Patch7: python-2.5.1-sqlite-encoding.patch

# 00010 # 4a21749202ce4e7b8ea716d38c194a997bcf5baa
# FIXME: Lib/ctypes/util.py posix implementation defines a function
# _get_soname(f).  Upstreams's implementation of this uses objdump to read the
# SONAME from a library; we avoid this, apparently to minimize space
# requirements on the live CD:
# (rhbz:307221)
Patch10: 00010-2.7.13-binutils-no-dep.patch

# 00013 # 4f2f7b3152a8c3d28441877567051384f23b3e4b
# Add various constants to the socketmodule (rhbz#436560):
# TODO: these patches were added in 2.5.1-22 and 2.5.1-24 but appear not to
# have been sent upstream yet:
Patch13: python-2.7rc1-socketmodule-constants.patch

# 00014 # 250d635a8481bc3bf729567e135d6d9cb4698199
# Add various constants to the socketmodule (rhbz#436560):
# TODO: these patches were added in 2.5.1-22 and 2.5.1-24 but appear not to
# have been sent upstream yet:
Patch14: python-2.7rc1-socketmodule-constants2.patch

# 00016 # 7ac402c3d2d7f6cd9b98deb0b7138765d31d105a
# Remove an "-rpath $(LIBDIR)" argument from the linkage args in configure.in:
# FIXME: is this for OSF, not Linux?
Patch16: python-2.6-rpath.patch

# 00017 # c30c4e768942a54dd3a5020c820935f9e2e9fa80
# Fixup distutils/unixccompiler.py to remove standard library path from rpath:
# Adapted from Patch0 in ivazquez' python3000 specfile, removing usage of
# super() as it's an old-style class
Patch17: python-2.6.4-distutils-rpath.patch

# 00055 # 4cde34923ef71a8c32f8fae50630c90645170500
# Systemtap support: add statically-defined probe points
# Patch based on upstream bug: http://bugs.python.org/issue4111
# fixed up by mjw and wcohen for 2.6.2, then fixed up by dmalcolm for 2.6.4
# then rewritten by mjw (attachment 390110 of rhbz 545179), then reformatted
# for 2.7rc1 by dmalcolm:
Patch55: 00055-systemtap.patch

# 00102 # 2242f5aa671eb490b5487dc46dcb05266decfe02
# Only used when "%%%%{_lib}" == "lib64"
# Fixup various paths throughout the build and in distutils from "lib" to "lib64",
# and add the /usr/lib64/pythonMAJOR.MINOR/site-packages to sitedirs, in front of
# /usr/lib/pythonMAJOR.MINOR/site-packages
# Not upstream
Patch102: 00102-2.7.13-lib64.patch

# 00103 # ccade12a68954f5bac4d00153ac92e7eee9c2b34
# Python 2.7 split out much of the path-handling from distutils/sysconfig.py to
# a new sysconfig.py (in r77704).
# We need to make equivalent changes to that new file to ensure that the stdlib
# and platform-specific code go to /usr/lib64 not /usr/lib, on 64-bit archs:
Patch103: python-2.7-lib64-sysconfig.patch

# 00104 # dc327f751c4f4ad6c2e7ad338e97a8a1e0650b60
# Only used when "%%%%{_lib}" == "lib64"
# Another lib64 fix, for distutils/tests/test_install.py; not upstream:
Patch104: 00104-lib64-fix-for-test_install.patch

# 00111 # 3dd8cb916b10ea83c0c7d690cf3c7512394a7f66
# Patch the Makefile.pre.in so that the generated Makefile doesn't try to build
# a libpythonMAJOR.MINOR.a (bug 550692):
# Downstream only: not appropriate for upstream
Patch111: 00111-no-static-lib.patch

# 00112 # 1676b155da8dcacc21fd20006105e3c164a6c5de
# Patch to support building both optimized vs debug stacks DSO ABIs, sharing
# the same .py and .pyc files, using "_d.so" to signify a debug build of an
# extension module.
#
# Based on Debian's patch for the same,
#  http://patch-tracker.debian.org/patch/series/view/python2.6/2.6.5-2/debug-build.dpatch
#
# (which was itself based on the upstream Windows build), but with some
# changes:
#
#   * Debian's patch to dynload_shlib.c looks for module_d.so, then module.so,
# but this can potentially find a module built against the wrong DSO ABI.  We
# instead search for just module_d.so in a debug build
#
#   * We remove this change from configure.in's build of the Makefile:
#   SO=$DEBUG_EXT.so
# so that sysconfig.py:customize_compiler stays with shared_lib_extension='.so'
# on debug builds, so that UnixCCompiler.find_library_file can find system
# libraries (otherwise "make sharedlibs" fails to find system libraries,
# erroneously looking e.g. for "libffi_d.so" rather than "libffi.so")
#
#   * We change Lib/distutils/command/build_ext.py:build_ext.get_ext_filename
# to add the _d there, when building an extension.  This way, "make sharedlibs"
# can build ctypes, by finding the sysmtem libffi.so (rather than failing to
# find "libffi_d.so"), and builds the module as _ctypes_d.so
#
#   * Similarly, update build_ext:get_libraries handling of Py_ENABLE_SHARED by
# appending "_d" to the python library's name for the debug configuration
#
#   * We modify Modules/makesetup to add the "_d" to the generated Makefile
# rules for the various Modules/*.so targets
#
# This may introduce issues when building an extension that links directly
# against another extension (e.g. users of NumPy?), but seems more robust when
# searching for external libraries
#
#   * We don't change Lib/distutils/command/build.py: build.build_purelib to
# embed plat_specifier, leaving it as is, as pure python builds should be
# unaffected by these differences (we'll be sharing the .py and .pyc files)
#
#   * We introduce DEBUG_SUFFIX as well as DEBUG_EXT:
#     - DEBUG_EXT is used by ELF files (names and SONAMEs); it will be "_d" for
# a debug build
#     - DEBUG_SUFFIX is used by filesystem paths; it will be "-debug" for a
# debug build
#
#   Both will be empty in an optimized build.  "_d" contains characters that
# are valid ELF metadata, but this leads to various ugly filesystem paths (such
# as the include path), and DEBUG_SUFFIX allows these paths to have more natural
# names.  Changing this requires changes elsewhere in the distutils code.
#
#   * We add DEBUG_SUFFIX to PYTHON in the Makefile, so that the two
# configurations build parallel-installable binaries with different names
# ("python-debug" vs "python").
#
#   * Similarly, we add DEBUG_SUFFIX within python-config and
#  python$(VERSION)-config, so that the two configuration get different paths
#  for these.
#
#  See also patch 130 below
Patch112: 00112-2.7.13-debug-build.patch

# 00113 # 9dd9dbc52d40c76002245bdc718f2d09590615bf
# Add configure-time support for the COUNT_ALLOCS and CALL_PROFILE options
# described at http://svn.python.org/projects/python/trunk/Misc/SpecialBuilds.txt
# so that if they are enabled, they will be in that build's pyconfig.h, so that
# extension modules will reliably use them
# Not yet sent upstream
Patch113: 00113-more-configuration-flags.patch

# 00114 # 3cfc26f24a13732fe602a47e389152714b757fd7
# Add flags for statvfs.f_flag to the constant list in posixmodule (i.e. "os")
# (rhbz:553020); partially upstream as http://bugs.python.org/issue7647
# Not yet sent upstream
Patch114: 00114-statvfs-f_flag-constants.patch

# 00121 # 15d7dd7ccf99e88ddc9d858cef57b1c91f6871b2
# Upstream r79310 removed the "Modules" directory from sys.path when Python is
# running from the build directory on POSIX to fix a unit test (issue #8205).
# This seems to have broken the compileall.py done in "make install": it cannot
# find shared library extension modules at this point in the build (sys.path
# does not contain DESTDIR/usr/lib(64)/python-2.7/lib-dynload for some reason),
# leading to the build failing with:
# Traceback (most recent call last):
#   File "/home/david/rpmbuild/BUILDROOT/python-2.7-0.1.rc2.fc14.x86_64/usr/lib64/python2.7/compileall.py", line 17, in <module>
#     import struct
#   File "/home/david/rpmbuild/BUILDROOT/python-2.7-0.1.rc2.fc14.x86_64/usr/lib64/python2.7/struct.py", line 1, in <module>
#    from _struct import *
# ImportError: No module named _struct
# This patch adds the build Modules directory to build path.
Patch121: 00121-add-Modules-to-build-path.patch

# 00128 # cf4b30b7664a016ba6ee399aad8f65588a7efd79
# 2.7.1 (in r84230) added a test to test_abc which fails if python is
# configured with COUNT_ALLOCS, which is the case for our debug build
# (the COUNT_ALLOCS instrumentation keeps "C" alive).
# Not yet sent upstream
Patch128: python-2.7.1-fix_test_abc_with_COUNT_ALLOCS.patch

# 00130 # a1595a504aa3fc712856b20bd0850a13b5755762
# Add "--extension-suffix" option to python-config and python-debug-config
# (rhbz#732808)
#
# This is adapted from 3.2's PEP-3149 support.
#
# Fedora's debug build has some non-standard features (see also patch 112
# above), though largely shared with Debian/Ubuntu and Windows
#
# In particular, SO in the Makefile is currently always just ".so" for our
# python 2 optimized builds, but for python 2 debug it should be '_d.so', to
# distinguish the debug vs optimized ABI, following the pattern in the above
# patch.
#
# Not yet sent upstream
Patch130: python-2.7.2-add-extension-suffix-to-python-config.patch

# 00131 # aa81f736a8d7cc4315e920bcec3cb5883c67034b
# The four tests in test_io built on top of check_interrupted_write_retry
# fail when built in Koji, for ppc and ppc64; for some reason, the SIGALRM
# handlers are never called, and the call to write runs to completion
# (rhbz#732998)
Patch131: 00131-disable-tests-in-test_io.patch

# 00132 # 1ec40c78e547fc449ee22a4dbc52562b89115f40
# Add non-standard hooks to unittest for use in the "check" phase below, when
# running selftests within the build:
#   @unittest._skipInRpmBuild(reason)
# for tests that hang or fail intermittently within the build environment, and:
#   @unittest._expectedFailureInRpmBuild
# for tests that always fail within the build environment
#
# The hooks only take effect if WITHIN_PYTHON_RPM_BUILD is set in the
# environment, which we set manually in the appropriate portion of the "check"
# phase below (and which potentially other python-* rpms could set, to reuse
# these unittest hooks in their own "check" phases)
Patch132: 00132-add-rpmbuild-hooks-to-unittest.patch

# 00133 # 434fef9eec3c579fd1ecc956136c1b7cc0b2ea3f
# "dl" is deprecated, and test_dl doesn't work on 64-bit builds:
Patch133: 00133-skip-test_dl.patch

# 00136 # 2f7c096e92687ca4ab771802f866588242ba9184
# Some tests try to seek on sys.stdin, but don't work as expected when run
# within Koji/mock; skip them within the rpm build:
Patch136: 00136-skip-tests-of-seeking-stdin-in-rpmbuild.patch

# 00137 # ddb14da3b15a1f6cfda5ab94919f624c91294e00
# Some tests within distutils fail when run in an rpmbuild:
Patch137: 00137-skip-distutils-tests-that-fail-in-rpmbuild.patch

# 00138 # c955cda1742fcfc632c8eaf0b50e4bffb199d33a
# Fixup some tests within distutils to work with how debug builds are set up:
Patch138: 00138-fix-distutils-tests-in-debug-build.patch

# 00139 # 38a2e2222cf61623fa5519a652a28537b5cd005d
# ARM-specific: skip known failure in test_float:
#  http://bugs.python.org/issue8265 (rhbz#706253)
Patch139: 00139-skip-test_float-known-failure-on-arm.patch

# 00140 # e5095acfe56937839f02013f9c46cb188784a5b2
# Sparc-specific: skip known failure in test_ctypes:
#  http://bugs.python.org/issue8314 (rhbz#711584)
# which appears to be a libffi bug
Patch140: 00140-skip-test_ctypes-known-failure-on-sparc.patch

# 00142 # bcd487be7de5823edd0017bf6778d5e2a0b06c8d
# Some pty tests fail when run in mock (rhbz#714627):
Patch142: 00142-skip-failing-pty-tests-in-rpmbuild.patch

# 00143 # 87bf5bbe4f0c89ec249ee9707bc03ccc9103406c
# Fix the --with-tsc option on ppc64, and rework it on 32-bit ppc to avoid
# aliasing violations (rhbz#698726)
# Sent upstream as http://bugs.python.org/issue12872
Patch143: 00143-tsc-on-ppc.patch

# 00144 # 7a99684f18ea9fc4c00cd2235c623658af36fc97
# (Optionally) disable the gdbm module:
Patch144: 00144-no-gdbm.patch

# 00147 # c77e8f43adbfb44f0a843f06869a36a37415d389
# Add a sys._debugmallocstats() function
# Based on patch 202 from RHEL 5's python.spec, with updates from rhbz#737198
# Sent upstream as http://bugs.python.org/issue14785
Patch147: 00147-add-debug-malloc-stats.patch

# 00155 # a154c44f2dfb60419cecaa193ef13e7613dbd488
# Avoid allocating thunks in ctypes unless absolutely necessary, to avoid
# generating SELinux denials on "import ctypes" and "import uuid" when
# embedding Python within httpd (rhbz#814391)
Patch155: 00155-avoid-ctypes-thunks.patch

# 00156 # a8d1c46e2ab627c493fdcea6d6ba752d9a7bfa2e
# Recent builds of gdb will only auto-load scripts from certain safe
# locations.  Turn off this protection when running test_gdb in the selftest
# suite to ensure that it can load our -gdb.py script (rhbz#817072):
# Not yet sent upstream
Patch156: 00156-gdb-autoload-safepath.patch

# 00165 # 38fdabaaa8c5d1576a372a22cdae1f17b65a215f
# Backport to Python 2 from Python 3.3 of improvements to the "crypt" module
# adding precanned ways of salting a password (rhbz#835021)
# Based on r88500 patch to py3k from Python 3.3
# plus 6482dd1c11ed, 0586c699d467, 62994662676a, 74a1110a3b50, plus edits
# to docstrings to note that this additional functionality is not standard
# within 2.7
Patch165: 00165-crypt-module-salt-backport.patch

# 00167 # 76aea104d5c20527ea08936fb6f2edbb52a07a46
# Don't run any of the stack navigation tests in test_gdb when Python is
# optimized, since there appear to be many different ways in which gdb can
# fail to read the PyFrameObject* for arbitrary places in the callstack,
# presumably due to compiler optimization (rhbz#912025)
#
# Not yet sent upstream
Patch167: 00167-disable-stack-navigation-tests-when-optimized-in-test_gdb.patch

# 00169 # 8d99c73e801c185674c7aee473d3466a118b566a
# Use SHA-256 rather than implicitly using MD5 within the challenge handling
# in multiprocessing.connection
#
# Sent upstream as http://bugs.python.org/issue17258
# (rhbz#879695)
Patch169: 00169-avoid-implicit-usage-of-md5-in-multiprocessing.patch

# 00170 # 029de09ec004fb47f8cbd978f68759e7b4267a38
# In debug builds, try to print repr() when a C-level assert fails in the
# garbage collector (typically indicating a reference-counting error
# somewhere else e.g in an extension module)
# Backported to 2.7 from a patch I sent upstream for py3k
#   http://bugs.python.org/issue9263  (rhbz#614680)
# hiding the proposed new macros/functions within gcmodule.c to avoid exposing
# them within the extension API.
# (rhbz#850013)
Patch170: 00170-gc-assertions.patch

# 00174 # 149dca2c7ba69102e681d9834ac13c153ca53afc
# Workaround for failure to set up prefix/exec_prefix when running
# an embededed libpython that sets Py_SetProgramName() to a name not
# on $PATH when run from the root directory due to
#   https://fedoraproject.org/wiki/Features/UsrMove
# e.g. cmpi-bindings under systemd (rhbz#817554):
Patch174: 00174-fix-for-usr-move.patch

# 00180 # 7199dba788cff67117e091f6ea84a8e7a98d39fe
# Enable building on ppc64p7
# Not appropriate for upstream, Fedora-specific naming
Patch180: 00180-python-add-support-for-ppc64p7.patch

# 00181 # 4034653bd9e53ead4d73f263d12acf20497b6155
# Allow arbitrary timeout for Condition.wait, as reported in
# https://bugzilla.redhat.com/show_bug.cgi?id=917709
# Upstream doesn't want this: http://bugs.python.org/issue17748
# But we have no better solution downstream yet, and since there is
# no API breakage, we apply this patch.
# Doesn't apply to Python 3, where this is fixed otherwise and works.
Patch181: 00181-allow-arbitrary-timeout-in-condition-wait.patch

# 00185 # b104ec8a02f122cfc5c1bdfe923dfe94a6b5079e
# Makes urllib2 honor "no_proxy" enviroment variable for "ftp:" URLs
# when ftp_proxy is set
Patch185: 00185-urllib2-honors-noproxy-for-ftp.patch

# 00189 # 038b390c478fe336a8ea350972785d317bdbbd53
# Instead of bundled wheels, use our RPM packaged wheels from
# /usr/share/python-wheels
Patch189: 00189-use-rpm-wheels.patch

# 00191 # d6f8cb42773c48c480e0639cc8a57aebbf3a4c76
# Disabling NOOP test as it fails without internet connection
Patch191: 00191-disable-NOOP.patch

# 00193 # 31a84748ead0945648369d3520369cdd508815e8
# Enable loading sqlite extensions. This patch isn't needed for
# python3.spec, since Python 3 has a configuration option for this.
# rhbz#1066708
# Patch provided by John C. Peterson
Patch193: 00193-enable-loading-sqlite-extensions.patch

# 00289 # a923413277ad6331772a93b9daeb85a842ddfc00
# Disable automatic detection for the nis module
# (we handle it it in Setup.dist, see Patch0)
Patch289: 00289-disable-nis-detection.patch

# 00351 # 2ee72df6cc70c914e55da3017244c59c5d2c872c
# Avoid infinite loop when reading specially crafted TAR files using the tarfile module
# (CVE-2019-20907).
# See: https://bugs.python.org/issue39017
Patch351: 00351-cve-2019-20907-fix-infinite-loop-in-tarfile.patch

# 00354 # 73d8baef9f57f26ba97232d116f7220d1801452c
# Reject control chars in HTTP method in httplib.putrequest to prevent
# HTTP header injection
#
# Backported from Python 3.5-3.10 (and adjusted for py2's single-module httplib):
# - https://bugs.python.org/issue39603
# - https://github.com/python/cpython/pull/18485 (3.10)
# - https://github.com/python/cpython/pull/21946 (3.5)
Patch354: 00354-cve-2020-26116-http-request-method-crlf-injection-in-httplib.patch

# 00355 # fde656e7116767a761720970ee750ecda6774e71
# No longer call eval() on content received via HTTP in the CJK codec tests
# Backported from the python3 branches upstream: https://bugs.python.org/issue41944
# Resolves: https://bugzilla.redhat.com/show_bug.cgi?id=1889886
Patch355: 00355-CVE-2020-27619.patch

# 00357 # c4b8cabe4e772e4b8eea3e4dab5de12a3e9b5bc2
# CVE-2021-3177: Replace snprintf with Python unicode formatting in ctypes param reprs
#
# Backport of Python3 commit 916610ef90a0d0761f08747f7b0905541f0977c7:
# https://bugs.python.org/issue42938
# https://github.com/python/cpython/pull/24239
Patch357: 00357-CVE-2021-3177.patch

# 00359 # 0d63bea395d9ba5e281dfbddddd6843cdfc609e5
# CVE-2021-23336: Add `separator` argument to parse_qs; warn with default
#
# Partially backports https://bugs.python.org/issue42967 : [security] Address a web cache-poisoning issue reported in urllib.parse.parse_qsl().
#
# Backported from the python3 branch.
# However, this solution is different than the upstream solution in Python 3.
#
# Based on the downstream solution for python 3.6.13 by Petr Viktorin.
#
# An optional argument seperator is added to specify the separator.
# It is recommended to set it to '&' or ';' to match the application or proxy in use.
# The default can be set with an env variable of a config file.
# If neither the argument, env var or config file specifies a separator, "&" is used
# but a warning is raised if parse_qs is used on input that contains ';'.
Patch359: 00359-CVE-2021-23336.patch

# 00361 # 67d6979a90e1dddf902dd1dc42fef34b80ca325b
# Make python2.7 compatible with OpenSSL 3.0.0
#
# Backported from python3.
#
# Based on https://github.com/tiran/cpython/tree/2.7.18-openssl3
Patch361: 00361-openssl-3-compat.patch

# 00366 # e76b05ea3313854adf80e290c07d5b38fef606bb
# CVE-2021-3733: Fix ReDoS in urllib AbstractBasicAuthHandler
#
# Fix Regular Expression Denial of Service (ReDoS) vulnerability in
# urllib2.AbstractBasicAuthHandler. The ReDoS-vulnerable regex
# has quadratic worst-case complexity and it allows cause a denial of
# service when identifying crafted invalid RFCs. This ReDoS issue is on
# the client side and needs remote attackers to control the HTTP server.
#
# Backported from Python 3 together with another backward-compatible
# improvement of the regex from fix for CVE-2020-8492.
Patch366: 00366-CVE-2021-3733.patch

# 00368 # 10dcf6732fb101ce89ad506a89365c6b1ff8c4e4
# CVE-2021-3737: http client infinite line reading (DoS) after a HTTP 100 Continue
#
# Fixes http.client potential denial of service where it could get stuck reading
# lines from a malicious server after a 100 Continue response.
#
# Backported from Python 3.
Patch368: 00368-CVE-2021-3737.patch

# 00372 # 0039a5762ac21255d6e4c2421a2159cbecfc95bd
# CVE-2021-4189: ftplib should not use the host from the PASV response
#
# Upstream: https://bugs.python.org/issue43285
#
# Backported from the python3 branch.
Patch372: 00372-CVE-2021-4189.patch

# 00375 # 5488ab84d2447aa8df8b3502e76f151ac2488947
# Fix precision in test_distance (test.test_turtle.TestVec2D).
# See: https://bugzilla.redhat.com/show_bug.cgi?id=2038843
Patch375: 00375-fix-test_distance-to-enable-Python-build-on-i686.patch

# 00377 # 53940f806f5e3451c9b77b44e2fc4d18b243156b
# CVE-2022-0391: urlparse does not sanitize URLs containing ASCII newline and tabs
#
# ASCII newline and tab characters are stripped from the URL.
#
# Upstream: https://bugs.python.org/issue43882
#
# Backported from Python 3.
Patch377: 00377-CVE-2022-0391.patch

# 00378 # 32b7f6200303fb36d104ac8d2afa3afba1789c1b
# Support expat 2.4.5
#
# Curly brackets were never allowed in namespace URIs
# according to RFC 3986, and so-called namespace-validating
# XML parsers have the right to reject them a invalid URIs.
#
# libexpat >=2.4.5 has become strcter in that regard due to
# related security issues; with ET.XML instantiating a
# namespace-aware parser under the hood, this test has no
# future in CPython.
#
# References:
# - https://datatracker.ietf.org/doc/html/rfc3968
# - https://www.w3.org/TR/xml-names/
#
# Also, test_minidom.py: Support Expat >=2.4.5
#
# Upstream: https://bugs.python.org/issue46811
#
# Backported from Python 3.
Patch378: 00378-support-expat-2-4-5.patch

# 00382 # 65796028be4b28aaf027963d6fb2ef4c219e73dc
# Make mailcap refuse to match unsafe filenames/types/params (GH-91993)
#
# Upstream: https://github.com/python/cpython/issues/68966
#
# Tracker bug: https://bugzilla.redhat.com/show_bug.cgi?id=2075390
#
# Backported from python3.
Patch382: 00382-cve-2015-20107.patch

# 00394 # 32a7810526fb88b82f6e2dee6d8367d1264e8fad
# gh-98433: Fix quadratic time idna decoding.
#
# There was an unnecessary quadratic loop in idna decoding. This restores
# the behavior to linear.
#
# Backported from python3.
Patch394: 00394-cve-2022-45061-cpu-denial-of-service-via-inefficient-idna-decoder.patch

# 00399 # 70e14c5e59a39bf5fae54c040d0e1d8b5c06d92c
# * gh-102153: Start stripping C0 control and space chars in `urlsplit` (GH-102508)
#
# `urllib.parse.urlsplit` has already been respecting the WHATWG spec a bit GH-25595.
#
# This adds more sanitizing to respect the "Remove any leading C0 control or space from input" [rule](https://url.spec.whatwg.org/GH-url-parsing:~:text=Remove%%20any%%20leading%%20and%%20trailing%%20C0%%20control%%20or%%20space%%20from%%20input.) in response to [CVE-2023-24329](https://nvd.nist.gov/vuln/detail/CVE-2023-24329).
#
# Backported to Python 2 from Python 3.12.
Patch399: 00399-cve-2023-24329.patch

# 00403 # 1cbe589d7b18cb74b205b9e9d48087c12fa2f6c1
# Fix test suite failure with openssl >= 3.1.0
#
# https://www.openssl.org/news/openssl-3.1-notes.html
#
# > SSL 3, TLS 1.0, TLS 1.1, and DTLS 1.0 only work at security level 0.
#
# This causes a FTBFS in one of the members of the test suite -
# it dies with a SSL internal error rather than the expected error - in detail:
#
# In test_subclass(), SSL_do_handshake() is called with SSL.version unmodified
# from version passed to SSLContext() - but that's an impossible version
# from the config (Fedora's default security level is 2),
# and an internal error is returned.
#
# The assumption of the code is probably that earlier steps will have negotiated
# a version that's allowed by the config, but this test skips them.
# This is fixed by simply using TLSv1_2 to start with.
Patch403: 00403-no-tls-10.patch

# 00405 # 0be039ad8332dded8b1336346a8fa59b84630cbf
# Fix C99 build error: declare functions explicitly
Patch405: 00405-fix-c99-build-error.patch

# 00406 # 33d46d8ceb68210f6234f26f3465c8556c0b6ccb
# Reject XML entity declarations in plist files
# CVE-2022-48565: XML External Entity in XML processing plistlib module
# Backported from https://github.com/python/cpython/commit/a158fb9c5138
# Tracking bug: https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2022-48565
Patch406: 00406-cve-2022-48565.patch

# 00407 # f562db9763f424318fd311e3267d2aed0afadbbe
# gh-99086: Fix implicit int compiler warning in configure check for PTHREAD_SCOPE_SYSTEM
Patch407: 00407-gh-99086-fix-implicit-int-compiler-warning-in-configure-check-for-pthread_scope_system.patch

# 00408 # 7cfb7e151bb64b384c47bfe0dddf5c2d6837772f
# Security fix for CVE-2022-48560: python3: use after free in heappushpop()
# of heapq module
# Resolved upstream: https://github.com/python/cpython/issues/83602
#
# Backported from Python 3.6.11.
Patch408: 00408-cve-2022-48560.patch

# 00410 # ea9f02d63dc0f772362f520967bce90e4f4d3abd
# bpo-42598: Fix implicit function declarations in configure
#
# This is invalid in C99 and later and is an error with some compilers
# (e.g. clang in Xcode 12), and can thus cause configure checks to
# produce incorrect results.
Patch410: 00410-bpo-42598-fix-implicit-function-declarations-in-configure.patch

# 00415 # eb2d53e3e9bd2c708e9387044e8a84f0acda5830
# [CVE-2023-27043] gh-102988: Reject malformed addresses in email.parseaddr() (#111116)
#
# Detect email address parsing errors and return empty tuple to
# indicate the parsing error (old API). Add an optional 'strict'
# parameter to getaddresses() and parseaddr() functions. Patch by
# Thomas Dwyer.
#
#
# Changes for Python 2:
# - Define encoding for test_email
# - Adjust import so we don't need change the tests
# - Do not use f-strings
# - Do not use SubTest
# - KW only function arguments are not supported
Patch415: 00415-cve-2023-27043-gh-102988-reject-malformed-addresses-in-email-parseaddr-111116.patch

# 00417 # 48af248abeac52b6f26f056405170d366ea132ef
# Avoid passing incompatible pointer type in _tkinter
#
# Modules/_tkinter.c:1178:38: error: passing argument 1 of ‘Tcl_NewUnicodeObj’
# from incompatible pointer type [-Wincompatible-pointer-types]
Patch417: 00417-avoid-passing-incompatible-pointer-type-in-_tkinter.patch

# (New patches go here ^^^)
#
# When adding new patches to "python2" and "python3" in Fedora, EL, etc.,
# please try to keep the patch numbers in-sync between all specfiles.
#
# More information, and a patch number catalog, is at:
#
#     https://fedoraproject.org/wiki/SIGs/Python/PythonPatches

# Disable tk, applied conditionally if %%{without tkinter}
Patch4000: 04000-disable-tk.patch

# This is the generated patch to "configure"; see the description of
#   %%{regenerate_autotooling_patch}
# above:

Patch5000: 05000-autotool-intermediates.patch

# ======================================================
# Additional metadata
# ======================================================

%description
Python 2 is an old version of the language that is incompatible with the 3.x
line of releases. The language is mostly the same, but many details, especially
how built-in objects like dictionaries and strings work, have changed
considerably, and a lot of deprecated features have finally been removed in the
3.x line.

Note that Python 2 is not supported upstream after 2020-01-01, please use the
python3 package instead if you can.

This package also provides the "python2" executable.

# ======================================================
# The prep phase of the build:
# ======================================================

%prep
%gpgverify -k2 -s1 -d0
%setup -q -n Python-%{upstream_version}

%if 0%{?with_systemtap}
# Provide an example of usage of the tapset:
cp -a %{SOURCE4} .
cp -a %{SOURCE5} .
%endif # with_systemtap

# Ensure that we're using the system copy of various libraries, rather than
# copies shipped by upstream in the tarball:
#   Remove embedded copy of expat:
rm -r Modules/expat || exit 1

#   Remove embedded copy of libffi:
for SUBDIR in darwin libffi libffi_arm_wince libffi_msvc libffi_osx ; do
  rm -r Modules/_ctypes/$SUBDIR || exit 1 ;
done

#   Remove embedded copy of zlib:
rm -r Modules/zlib || exit 1

## Disabling hashlib patch for now as it needs to be reimplemented
## for OpenSSL 1.1.0.
# Don't build upstream Python's implementation of these crypto algorithms;
# instead rely on _hashlib and OpenSSL.
#
# For example, in our builds md5.py uses always uses hashlib.md5 (rather than
# falling back to _md5 when hashlib.md5 is not available); hashlib.md5 is
# implemented within _hashlib via OpenSSL (and thus respects FIPS mode)
#for f in md5module.c md5.c shamodule.c sha256module.c sha512module.c; do
#    rm Modules/$f
#done

#
# Apply patches:
#
%patch -P0 -p1 -b .rhconfig
%patch -P1 -p1 -b .no_gui
%patch -P4 -p1 -b .cflags
%patch -P6 -p1 -b .plural
%patch -P7 -p1

%if "%{_lib}" == "lib64"
%patch -P102 -p1 -b .lib64
%patch -P103 -p1 -b .lib64-sysconfig
%patch -P104 -p1
%endif

%patch -P10 -p1 -b .binutils-no-dep
%patch -P13 -p1 -b .socketmodule
%patch -P14 -p1 -b .socketmodule2
%patch -P16 -p1 -b .rpath
%patch -P17 -p1 -b .distutils-rpath

%if 0%{?with_systemtap}
%patch -P55 -p1 -b .systemtap
%endif

%patch -P111 -p1 -b .no-static-lib

%patch -P112 -p1 -b .debug-build

%patch -P113 -p1 -b .more-configuration-flags

%patch -P114 -p1 -b .statvfs-f-flag-constants


%patch -P121 -p1
%patch -P128 -p1

%patch -P130 -p1

%ifarch ppc %{power64}
%patch -P131 -p1
%endif

%patch -P132 -p1
%patch -P133 -p1
%patch -P136 -p1 -b .stdin-test
%patch -P137 -p1
%patch -P138 -p1
%ifarch %{arm}
%patch -P139 -p1
%endif
%ifarch %{sparc}
%patch -P140 -p1
%endif
%patch -P142 -p1 -b .tty-fail
%patch -P143 -p1 -b .tsc-on-ppc
%if !%{with_gdbm}
%patch -P144 -p1
%endif
%patch -P147 -p1
%patch -P155 -p1
%patch -P156 -p1
%patch -P165 -p1
mv Modules/cryptmodule.c Modules/_cryptmodule.c
%patch -P167 -p1
%patch -P169 -p1
%patch -P170 -p1
%patch -P174 -p1 -b .fix-for-usr-move
%patch -P180 -p1
%patch -P181 -p1
%patch -P185 -p1

%if %{with rpmwheels}
%patch -P189 -p1
rm Lib/ensurepip/_bundled/*.whl
%endif

%patch -P191 -p1
%patch -P193 -p1
%patch -P289 -p1

# Patch 351 adds binary file for testing. We need to apply it using Git.
git apply %{PATCH351}

%patch -P354 -p1
%patch -P355 -p1
%patch -P357 -p1
%patch -P359 -p1
%patch -P361 -p1
%patch -P366 -p1
%patch -P368 -p1
%patch -P375 -p1
%patch -P377 -p1
%patch -P378 -p1
%patch -P382 -p1
%patch -P394 -p1
%patch -P399 -p1
%patch -P403 -p1
%patch -P405 -p1
%patch -P406 -p1
%patch -P407 -p1
%patch -P408 -p1
%patch -P410 -p1
%patch -P417 -p1

%if %{without tkinter}
%patch -P4000 -p1
%endif

# This shouldn't be necesarry, but is right now (2.2a3)
find -name "*~" |xargs rm -f

%if ! 0%{regenerate_autotooling_patch}
# Normally we apply the patch to "configure"
# We don't apply the patch if we're working towards regenerating it
%patch -P5000 -p0 -b .autotool-intermediates
%endif


# ======================================================
# Configuring and building the code:
# ======================================================

%build
topdir=$(pwd)
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CPPFLAGS="$(pkg-config --cflags-only-I libffi)"
export OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export LINKCC="gcc"
export LDFLAGS="$RPM_LD_FLAGS"
if pkg-config openssl ; then
  export CFLAGS="$CFLAGS $(pkg-config --cflags openssl)"
  export LDFLAGS="$LDFLAGS $(pkg-config --libs-only-L openssl)"
fi
# Force CC
export CC=gcc

%if 0%{regenerate_autotooling_patch}
# If enabled, this code regenerates the patch to "configure", using a
# local copy of autoconf-2.65, then exits the build
#
# The following assumes that the copy is installed to ~/autoconf-2.65/bin
# as per these instructions:
#   http://bugs.python.org/issue7997

for f in pyconfig.h.in configure ; do
    cp $f $f.autotool-intermediates ;
done

# Rerun the autotools:
PATH=~/autoconf-2.65/bin:$PATH autoconf
autoheader

# Regenerate the patch:
gendiff . .autotool-intermediates > %{PATCH5000}


# Exit the build
exit 1
%endif

# Define a function, for how to perform a "build" of python for a given
# configuration:
BuildPython() {
  ConfName=$1
  BinaryName=$2
  SymlinkName=$3
  ExtraConfigArgs=$4
  PathFixWithThisBinary=$5

  ConfDir=build/$ConfName

  echo STARTING: BUILD OF PYTHON FOR CONFIGURATION: $ConfName - %{_bindir}/$BinaryName
  mkdir -p $ConfDir

  pushd $ConfDir

  # Use the freshly created "configure" script, but in the directory two above:
  %global _configure $topdir/configure

%configure \
  --enable-ipv6 \
  --enable-shared \
  --enable-unicode=%{unicode} \
  --with-dbmliborder=gdbm:ndbm:bdb \
  --with-system-expat \
  --with-system-ffi \
%if 0%{?with_systemtap}
  --with-dtrace \
  --with-tapset-install-dir=%{tapsetdir} \
%endif
%if 0%{?with_valgrind}
  --with-valgrind \
%endif
  $ExtraConfigArgs \
  %{nil}

%make_build EXTRA_CFLAGS="$CFLAGS"

# We need to fix shebang lines across the full source tree.
#
# We do this using the pathfix.py script, which requires one of the
# freshly-built Python binaries.
#
# We use the optimized python binary, and make the shebangs point at that same
# optimized python binary:
if $PathFixWithThisBinary
then
  # pathfix.py currently only works with files matching ^[a-zA-Z0-9_]+\.py$
  # when crawling through directories, so we handle the special cases manually
  LD_LIBRARY_PATH="$topdir/$ConfDir" ./$BinaryName \
    $topdir/Tools/scripts/pathfix.py \
      -i "%{_bindir}/python%{pybasever}" \
      $topdir \
      $topdir/Tools/pynche/pynche \
      $topdir/Demo/pdist/{rcvs,rcsbump,rrcs} \
      $topdir/Demo/scripts/find-uname.py \
      $topdir/Tools/scripts/reindent-rst.py
fi

# Rebuild with new python
# We need a link to a versioned python in the build directory
ln -s $BinaryName $SymlinkName
LD_LIBRARY_PATH="$topdir/$ConfDir" PATH=$PATH:$topdir/$ConfDir make -s EXTRA_CFLAGS="$CFLAGS" %{?_smp_mflags}

  popd
  echo FINISHED: BUILD OF PYTHON FOR CONFIGURATION: $ConfDir
}

# Use "BuildPython" to support building with different configurations:

BuildPython optimized \
  python \
  python%{pybasever} \
  "" \
  true


# ======================================================
# Installing the built code:
# ======================================================

%install
topdir=$(pwd)
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_prefix} %{buildroot}%{_mandir}

# Clean up patched .py files that are saved as .lib64
for f in distutils/command/install distutils/sysconfig; do
    rm -f Lib/$f.py.lib64
done

InstallPython() {

  ConfName=$1
  BinaryName=$2
  PyInstSoName=$3

  ConfDir=build/$ConfName

  echo STARTING: INSTALL OF PYTHON FOR CONFIGURATION: $ConfName - %{_bindir}/$BinaryName
  mkdir -p $ConfDir

  pushd $ConfDir

%make_install

# We install a collection of hooks for gdb that make it easier to debug
# executables linked against libpython (such as /usr/lib/python itself)
#
# These hooks are implemented in Python itself
#
# gdb-archer looks for them in the same path as the ELF file, with a -gdb.py suffix.
# We put them in the debuginfo package by installing them to e.g.:
#  /usr/lib/debug/usr/lib/libpython2.6.so.1.0.debug-gdb.py
# (note that the debug path is /usr/lib/debug for both 32/64 bit)
#
# See https://fedoraproject.org/wiki/Features/EasierPythonDebugging for more
# information
#
# Initially I tried:
#  /usr/lib/libpython2.6.so.1.0-gdb.py
# but doing so generated noise when ldconfig was rerun (rhbz:562980)
#
%if 0%{?with_gdb_hooks}
DirHoldingGdbPy=%{_usr}/lib/debug/%{_libdir}
PathOfGdbPy=$DirHoldingGdbPy/$PyInstSoName-%{version}-%{release}.%{_arch}.debug-gdb.py

mkdir -p %{buildroot}$DirHoldingGdbPy
cp $topdir/Tools/gdb/libpython.py %{buildroot}$PathOfGdbPy

# Manually byte-compile the file, in case find-debuginfo.sh is run before
# brp-python-bytecompile, so that the .pyc/.pyo files are properly listed in
# the debuginfo manifest:
# Clamp the source mtime first, see https://fedoraproject.org/wiki/Changes/ReproducibleBuildsClampMtimes
# The clamp_source_mtime module is only guaranteed to exist on Fedoras that enabled this option:
%if 0%{?clamp_mtime_to_source_date_epoch}
LD_LIBRARY_PATH="%{buildroot}%{dynload_dir}/:%{buildroot}%{_libdir}" \
PYTHONPATH="%{_rpmconfigdir}/redhat" \
%{buildroot}%{_bindir}/python%{pybasever} -s -B -m clamp_source_mtime %{buildroot}$DirHoldingGdbPy
%endif
LD_LIBRARY_PATH="$topdir/$ConfDir" $topdir/$ConfDir/$BinaryName \
  -c "import compileall; import sys; compileall.compile_dir('%{buildroot}$DirHoldingGdbPy', ddir='$DirHoldingGdbPy')"

LD_LIBRARY_PATH="$topdir/$ConfDir" $topdir/$ConfDir/$BinaryName -O \
  -c "import compileall; import sys; compileall.compile_dir('%{buildroot}$DirHoldingGdbPy', ddir='$DirHoldingGdbPy')"
%endif # with_gdb_hooks

  popd

  echo FINISHED: INSTALL OF PYTHON FOR CONFIGURATION: $ConfName
}

# Use "InstallPython" to support building with different configurations:

# Now the optimized build:
InstallPython optimized \
  python%{pybasever} \
  %{py_INSTSONAME_optimized}


# Fix the interpreter path in binaries installed by distutils
# (which changes them by itself)
# Make sure we preserve the file permissions
for fixed in %{buildroot}%{_bindir}/pydoc; do
    sed 's,#!.*/python$,#!/usr/bin/env python%{pybasever},' $fixed > $fixed- \
        && cat $fixed- > $fixed && rm -f $fixed-
done

# Junk, no point in putting in -test sub-pkg
rm -f %{buildroot}/%{pylibdir}/idlelib/testcode.py*

# don't include tests that are run at build time in the package
# This is documented, and used: rhbz#387401
if /bin/false; then
 # Move this to -test subpackage.
mkdir save_bits_of_test
for i in test_support.py __init__.py; do
  cp -a %{buildroot}/%{pylibdir}/test/$i save_bits_of_test
done
rm -rf %{buildroot}/%{pylibdir}/test
mkdir %{buildroot}/%{pylibdir}/test
cp -a save_bits_of_test/* %{buildroot}/%{pylibdir}/test
fi

# tools

mkdir -p ${RPM_BUILD_ROOT}%{site_packages}

#pynche
rm -f Tools/pynche/*.pyw
cp -rp Tools/pynche \
  ${RPM_BUILD_ROOT}%{site_packages}/

mv Tools/pynche/README Tools/pynche/README.pynche

#gettext
install -m755  Tools/i18n/pygettext.py %{buildroot}%{_bindir}/
install -m755  Tools/i18n/msgfmt.py %{buildroot}%{_bindir}/

# Useful development tools
install -m755 -d %{buildroot}%{tools_dir}/scripts
install Tools/README %{buildroot}%{tools_dir}/
install Tools/scripts/*py %{buildroot}%{tools_dir}/scripts/

# Documentation tools
install -m755 -d %{buildroot}%{doc_tools_dir}
#install -m755 Doc/tools/mkhowto %{buildroot}%{doc_tools_dir}

# Useful demo scripts
install -m755 -d %{buildroot}%{demo_dir}
cp -ar Demo/* %{buildroot}%{demo_dir}

# Get rid of crap
find %{buildroot}/ -name "*~"|xargs rm -f
find %{buildroot}/ -name ".cvsignore"|xargs rm -f
find %{buildroot}/ -name "*.bat"|xargs rm -f
find . -name "*~"|xargs rm -f
find . -name ".cvsignore"|xargs rm -f


# Provide binaries in the form of bin2 and bin2.7, thus implementing
# (and expanding) the recommendations of PEP 394.
# Do NOT provide unversioned binaries
# https://fedoraproject.org/wiki/Changes/Python_means_Python3
mv %{buildroot}%{_bindir}/idle %{buildroot}%{_bindir}/idle%{pybasever}
ln -s ./idle%{pybasever} %{buildroot}%{_bindir}/idle2

mv %{buildroot}%{_bindir}/pydoc %{buildroot}%{_bindir}/pydoc%{pybasever}
ln -s ./pydoc%{pybasever} %{buildroot}%{_bindir}/pydoc2

mv %{buildroot}%{_bindir}/pygettext.py %{buildroot}%{_bindir}/pygettext%{pybasever}.py
ln -s ./pygettext%{pybasever}.py %{buildroot}%{_bindir}/pygettext2.py

mv %{buildroot}%{_bindir}/msgfmt.py %{buildroot}%{_bindir}/msgfmt%{pybasever}.py
ln -s ./msgfmt%{pybasever}.py %{buildroot}%{_bindir}/msgfmt2.py

mv %{buildroot}%{_bindir}/smtpd.py %{buildroot}%{_bindir}/smtpd%{pybasever}.py
ln -s ./smtpd%{pybasever}.py %{buildroot}%{_bindir}/smtpd2.py

# Fix for bug #136654
rm -f %{buildroot}%{pylibdir}/email/test/data/audiotest.au %{buildroot}%{pylibdir}/test/audiotest.au

# Fix bug #143667: python should own /usr/lib/python2.x on 64-bit machines
%if "%{_lib}" == "lib64"
install -d %{buildroot}/%{_prefix}/lib/python%{pybasever}/site-packages
%endif

# Make python-devel multilib-ready (bug #192747, #139911)
%global _pyconfig32_h pyconfig-32.h
%global _pyconfig64_h pyconfig-64.h

%ifarch %{power64} s390x x86_64 ia64 alpha sparc64 aarch64 %{mips64} riscv64
%global _pyconfig_h %{_pyconfig64_h}
%else
%global _pyconfig_h %{_pyconfig32_h}
%endif

%global PyIncludeDirs python%{pybasever}

for PyIncludeDir in %{PyIncludeDirs} ; do
  mv %{buildroot}%{_includedir}/$PyIncludeDir/pyconfig.h \
     %{buildroot}%{_includedir}/$PyIncludeDir/%{_pyconfig_h}
  cat > %{buildroot}%{_includedir}/$PyIncludeDir/pyconfig.h << EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "%{_pyconfig32_h}"
#elif __WORDSIZE == 64
#include "%{_pyconfig64_h}"
#else
#error "Unknown word size"
#endif
EOF
done
ln -s ../../libpython%{pybasever}.so %{buildroot}%{pylibdir}/config/libpython%{pybasever}.so

# Fix for bug 201434: make sure distutils looks at the right pyconfig.h file
# Similar for sysconfig: sysconfig.get_config_h_filename tries to locate
# pyconfig.h so it can be parsed, and needs to do this at runtime in site.py
# when python starts up.
#
# Split this out so it goes directly to the pyconfig-32.h/pyconfig-64.h
# variants:
sed -i -e "s/'pyconfig.h'/'%{_pyconfig_h}'/" \
  %{buildroot}%{pylibdir}/distutils/sysconfig.py \
  %{buildroot}%{pylibdir}/sysconfig.py

# Ensure that the curses module was linked against libncursesw.so, rather than
# libncurses.so (bug 539917)
ldd %{buildroot}/%{dynload_dir}/_curses*.so \
    | grep curses \
    | grep libncurses.so && (echo "_curses.so linked against libncurses.so" ; exit 1)

# Ensure that the debug modules are linked against the debug libpython, and
# likewise for the optimized modules and libpython:
for Module in %{buildroot}/%{dynload_dir}/*.so ; do
    case $Module in
    *_d.so)
        ldd $Module | grep %{py_INSTSONAME_optimized} &&
            (echo Debug module $Module linked against optimized %{py_INSTSONAME_optimized} ; exit 1)

        ;;
    *)
        ldd $Module | grep %{py_INSTSONAME_debug} &&
            (echo Optimized module $Module linked against debug %{py_INSTSONAME_optimized} ; exit 1)
        ;;
    esac
done

#
# Systemtap hooks:
#
%if 0%{?with_systemtap}
# Install a tapset for this libpython into tapsetdir, fixing up the path to the
# library:
mkdir -p %{buildroot}%{tapsetdir}
%ifarch %{power64} s390x x86_64 ia64 alpha sparc64 aarch64 %{mips64}
%global libpython_stp_optimized libpython%{pybasever}-64.stp
%global libpython_stp_debug     libpython%{pybasever}-debug-64.stp
%else
%global libpython_stp_optimized libpython%{pybasever}-32.stp
%global libpython_stp_debug     libpython%{pybasever}-debug-32.stp
%endif

sed \
   -e "s|LIBRARY_PATH|%{_libdir}/%{py_INSTSONAME_optimized}|" \
   %{SOURCE3} \
   > %{buildroot}%{tapsetdir}/%{libpython_stp_optimized}

%endif # with_systemtap

# Do bytecompilation with the newly installed interpreter.
# Clamp the source mtime first, see https://fedoraproject.org/wiki/Changes/ReproducibleBuildsClampMtimes
# The clamp_source_mtime module is only guaranteed to exist on Fedoras that enabled this option:
%if 0%{?clamp_mtime_to_source_date_epoch}
LD_LIBRARY_PATH="%{buildroot}%{dynload_dir}/:%{buildroot}%{_libdir}" \
PYTHONPATH="%{_rpmconfigdir}/redhat" \
%{buildroot}%{_bindir}/python%{pybasever} -s -B -m clamp_source_mtime %{buildroot}%{pylibdir}
%endif
# compile *.pyo
find %{buildroot} -type f -a -name "*.py" -print0 | \
    LD_LIBRARY_PATH="%{buildroot}%{dynload_dir}/:%{buildroot}%{_libdir}" \
    PYTHONPATH="%{buildroot}%{_libdir}/python%{pybasever} %{buildroot}%{_libdir}/python%{pybasever}/site-packages" \
    xargs -0 %{buildroot}%{_bindir}/python%{pybasever} -O -c 'import py_compile, sys; [py_compile.compile(f, dfile=f.partition("%{buildroot}")[2]) for f in sys.argv[1:]]' || :
# compile *.pyc
find %{buildroot} -type f -a -name "*.py" -print0 | \
    LD_LIBRARY_PATH="%{buildroot}%{dynload_dir}/:%{buildroot}%{_libdir}" \
    PYTHONPATH="%{buildroot}%{_libdir}/python%{pybasever} %{buildroot}%{_libdir}/python%{pybasever}/site-packages" \
    xargs -0 %{buildroot}%{_bindir}/python%{pybasever} -c 'import py_compile, sys; [py_compile.compile(f, dfile=f.partition("%{buildroot}")[2]) for f in sys.argv[1:]]' || :


# Make library-files user writable
/usr/bin/chmod 755 %{buildroot}%{dynload_dir}/*.so
/usr/bin/chmod 755 %{buildroot}%{_libdir}/libpython%{pybasever}.so.1.0

# Remove pyc/pyo files from /usr/bin
# They are not needed, and due to them, the resulting RPM is not multilib-clean
# https://bugzilla.redhat.com/show_bug.cgi?id=1703575
rm %{buildroot}%{_bindir}/*.py{c,o}

# Remove all remaining unversioned commands
# https://fedoraproject.org/wiki/Changes/Python_means_Python3
rm %{buildroot}%{_bindir}/python
rm %{buildroot}%{_bindir}/python-config
rm %{buildroot}%{_mandir}/*/python.1*
rm %{buildroot}%{_libdir}/pkgconfig/python.pc

# RPM macros
mkdir -p %{buildroot}%{rpmmacrodir}
cp -a %{SOURCE6} %{buildroot}%{rpmmacrodir}

# ======================================================
# Running the upstream test suite
# ======================================================

%check
topdir=$(pwd)
CheckPython() {
  ConfName=$1
  BinaryName=$2
  ConfDir=$(pwd)/build/$ConfName

  export OPENSSL_CONF=/non-existing-file

  echo STARTING: CHECKING OF PYTHON FOR CONFIGURATION: $ConfName

  # Note that we're running the tests using the version of the code in the
  # builddir, not in the buildroot.

  pushd $ConfDir

  EXTRATESTOPTS="--verbose"

%ifarch s390 s390x %{power64} %{arm} aarch64 %{mips}
    EXTRATESTOPTS="$EXTRATESTOPTS -x test_gdb"
%endif
%ifarch %{mips64}
    EXTRATESTOPTS="$EXTRATESTOPTS -x test_ctypes"
%endif

%if 0%{?with_huntrleaks}
  # Try to detect reference leaks on debug builds.  By default this means
  # running every test 10 times (6 to stabilize, then 4 to watch):
  if [ "$ConfName" = "debug"  ] ; then
    EXTRATESTOPTS="$EXTRATESTOPTS --huntrleaks : "
  fi
%endif

  # Run the upstream test suite, setting "WITHIN_PYTHON_RPM_BUILD" so that the
  # our non-standard decorators take effect on the relevant tests:
  #   @unittest._skipInRpmBuild(reason)
  #   @unittest._expectedFailureInRpmBuild
  WITHIN_PYTHON_RPM_BUILD= EXTRATESTOPTS="$EXTRATESTOPTS" make test

  popd

  echo FINISHED: CHECKING OF PYTHON FOR CONFIGURATION: $ConfName

}

%if %{with tests}

# no locale coercion in python2
# test_ssl:test_load_dh_params shutil.copies into unicode filename
export LC_ALL=C.utf-8

# Check each of the configurations:
CheckPython \
  optimized \
  python%{pybasever}

%endif # with tests


# ======================================================
# Cleaning up
# ======================================================


%files
%doc README
%license %{pylibdir}/LICENSE.txt
%{_bindir}/pydoc2*
%{_bindir}/python2
%{_bindir}/python%{pybasever}
%{_mandir}/*/python2*

%dir %{pylibdir}
%dir %{dynload_dir}

%{dynload_dir}/_md5module.so
%{dynload_dir}/_sha256module.so
%{dynload_dir}/_sha512module.so
%{dynload_dir}/_shamodule.so

%{dynload_dir}/Python-%{upstream_version}-py%{pybasever}.egg-info
%{dynload_dir}/_bisectmodule.so
%{dynload_dir}/_bsddb.so
%{dynload_dir}/_codecs_cn.so
%{dynload_dir}/_codecs_hk.so
%{dynload_dir}/_codecs_iso2022.so
%{dynload_dir}/_codecs_jp.so
%{dynload_dir}/_codecs_kr.so
%{dynload_dir}/_codecs_tw.so
%{dynload_dir}/_collectionsmodule.so
%{dynload_dir}/_csv.so
%{dynload_dir}/_ctypes.so
%{dynload_dir}/_curses.so
%{dynload_dir}/_curses_panel.so
%{dynload_dir}/_elementtree.so
%{dynload_dir}/_functoolsmodule.so
%{dynload_dir}/_hashlib.so
%{dynload_dir}/_heapq.so
%{dynload_dir}/_hotshot.so
%{dynload_dir}/_io.so
%{dynload_dir}/_json.so
%{dynload_dir}/_localemodule.so
%{dynload_dir}/_lsprof.so
%{dynload_dir}/_multibytecodecmodule.so
%{dynload_dir}/_multiprocessing.so
%{dynload_dir}/_randommodule.so
%{dynload_dir}/_socketmodule.so
%{dynload_dir}/_sqlite3.so
%{dynload_dir}/_ssl.so
%{dynload_dir}/_struct.so
%{dynload_dir}/arraymodule.so
%{dynload_dir}/audioop.so
%{dynload_dir}/binascii.so
%{dynload_dir}/bz2.so
%{dynload_dir}/cPickle.so
%{dynload_dir}/cStringIO.so
%{dynload_dir}/cmathmodule.so
%{dynload_dir}/_cryptmodule.so
%{dynload_dir}/datetime.so
%{dynload_dir}/dbm.so
%{dynload_dir}/dlmodule.so
%{dynload_dir}/fcntlmodule.so
%{dynload_dir}/future_builtins.so
%if %{with_gdbm}
%{dynload_dir}/gdbmmodule.so
%endif
%{dynload_dir}/grpmodule.so
%{dynload_dir}/imageop.so
%{dynload_dir}/itertoolsmodule.so
%{dynload_dir}/linuxaudiodev.so
%{dynload_dir}/math.so
%{dynload_dir}/mmapmodule.so
%{dynload_dir}/nismodule.so
%{dynload_dir}/operator.so
%{dynload_dir}/ossaudiodev.so
%{dynload_dir}/parsermodule.so
%{dynload_dir}/pyexpat.so
%{dynload_dir}/readline.so
%{dynload_dir}/resource.so
%{dynload_dir}/selectmodule.so
%{dynload_dir}/spwdmodule.so
%{dynload_dir}/stropmodule.so
%{dynload_dir}/syslog.so
%{dynload_dir}/termios.so
%{dynload_dir}/timemodule.so
%{dynload_dir}/timingmodule.so
%{dynload_dir}/unicodedata.so
%{dynload_dir}/xxsubtype.so
%{dynload_dir}/zlibmodule.so

%dir %{site_packages}
%{site_packages}/README
%{pylibdir}/*.py*
%{pylibdir}/*.doc
%{pylibdir}/wsgiref.egg-info
%dir %{pylibdir}/bsddb
%{pylibdir}/bsddb/*.py*
%{pylibdir}/compiler
%dir %{pylibdir}/ctypes
%{pylibdir}/ctypes/*.py*
%{pylibdir}/ctypes/macholib
%{pylibdir}/curses
%dir %{pylibdir}/distutils
%{pylibdir}/distutils/*.py*
%{pylibdir}/distutils/README
%{pylibdir}/distutils/command
%exclude %{pylibdir}/distutils/command/wininst-*.exe
%dir %{pylibdir}/email
%{pylibdir}/email/*.py*
%{pylibdir}/email/mime
%{pylibdir}/encodings
%{pylibdir}/hotshot
%{pylibdir}/idlelib
%{pylibdir}/importlib
%dir %{pylibdir}/json
%{pylibdir}/json/*.py*
%{pylibdir}/lib2to3
%{pylibdir}/logging
%{pylibdir}/multiprocessing
%{pylibdir}/plat-linux2
%{pylibdir}/pydoc_data
%dir %{pylibdir}/sqlite3
%{pylibdir}/sqlite3/*.py*

%{pylibdir}/unittest
%{pylibdir}/wsgiref
%{pylibdir}/xml
%if "%{_lib}" == "lib64"
%attr(0755,root,root) %dir %{_prefix}/lib/python%{pybasever}
%attr(0755,root,root) %dir %{_prefix}/lib/python%{pybasever}/site-packages
%endif

%{_libdir}/%{py_INSTSONAME_optimized}
%if 0%{?with_systemtap}
%dir %(dirname %{tapsetdir})
%dir %{tapsetdir}
%{tapsetdir}/%{libpython_stp_optimized}
%doc systemtap-example.stp pyfuntop.stp
%endif

%dir %{pylibdir}/ensurepip/
%{pylibdir}/ensurepip/*.py*
%if %{with rpmwheels}
%exclude %{pylibdir}/ensurepip/_bundled
%else
%dir %{pylibdir}/ensurepip/_bundled
%{pylibdir}/ensurepip/_bundled/*.whl
%endif


#files devel
%{_libdir}/pkgconfig/python-%{pybasever}.pc
%{_libdir}/pkgconfig/python2.pc
%{pylibdir}/config/
%{pylibdir}/distutils/command/wininst-*.exe
%dir %{_includedir}/python%{pybasever}/
%{_includedir}/python%{pybasever}/*.h

%doc Misc/README.valgrind Misc/valgrind-python.supp Misc/gdbinit
%{_bindir}/python2-config
%{_bindir}/python%{pybasever}-config
%{_libdir}/libpython%{pybasever}.so

#files tools
%doc Tools/pynche/README.pynche
%{site_packages}/pynche
%{_bindir}/smtpd2*.py

# https://bugzilla.redhat.com/show_bug.cgi?id=1111275
%exclude %{_bindir}/2to3*

%{_bindir}/idle2*
%{_bindir}/pygettext2*.py
%{_bindir}/msgfmt2*.py
%{tools_dir}
%{demo_dir}
%{pylibdir}/Doc

#files tkinter
%{pylibdir}/lib-tk
%if %{with tkinter}
%{dynload_dir}/_tkinter.so
%endif

#files test
%{pylibdir}/bsddb/test
%{pylibdir}/ctypes/test
%{pylibdir}/distutils/tests
%{pylibdir}/email/test
%{pylibdir}/json/tests
%{pylibdir}/sqlite3/test
%{pylibdir}/test/

%{dynload_dir}/_ctypes_test.so
%{dynload_dir}/_testcapimodule.so

# RPM macros, dir co-owned to avoid the dependency
%dir %{rpmmacrodir}
%{rpmmacrodir}/macros.python2

# Workaround for rhbz#1476593
%undefine _debuginfo_subpackages

# ======================================================
# Finally, the changelog:
# ======================================================

%changelog
%autochangelog
