%define keepstatic 1

Name:       lua
Summary:    Powerful light-weight programming language
Version:    5.3.5
Release:    4
License:    MIT
URL:        https://www.lua.org/
Source0:    https://www.lua.org/ftp/lua-%{version}.tar.gz
Source1:    mit.txt
Patch0:     lua-5.3.0-autotoolize.patch
Patch1:     CVE-2019-6706-use-after-free-lua_upvaluejoin.patch
Patch2:     lua-5.3.0-configure-compat-module.patch


%description
Lua is a powerful light-weight programming language designed for
extending applications. Lua is also frequently used as a
general-purpose, stand-alone language. Lua is free software.
Lua combines simple procedural syntax with powerful data description
constructs based on associative arrays and extensible semantics. Lua
is dynamically typed, interpreted from bytecodes, and has automatic
memory management with garbage collection, making it ideal for
configuration, scripting, and rapid prototyping.



%package -n liblua
Summary:    The Lua library
# Older rpm is still depends on older lua, and will break if this replacement is done before it is upgraded
Conflicts: rpm < 4.14.1+git11
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

%description -n liblua
This package contains the shared version of liblua for %{name}.
%package static
Summary:    Static library for %{name}
Requires:   lua-devel = %{version}-%{release}

%description static
This package contains the static version of liblua for %{name}.

%package devel
Summary:    Development files for %{name}
Requires:   liblua = %{version}-%{release}

%description devel
This package contains development files for %{name}.


%prep
%setup -q -n %{name}-%{version}

cp %{SOURCE1} .
mv src/luaconf.h src/luaconf.h.template.in
# lua-5.3.0-autotoolize.patch
%patch0 -p1
# CVE-2019-6706-use-after-free-lua_upvaluejoin.patch
%patch1 -p1
# lua-5.3.0-configure-compat-module.patch
%patch2 -p1
# Put proper version in configure.ac, patch0 hardcodes 5.3.0
sed -i 's|5.3.0|%{version}|g' configure.ac
autoreconf -ifv

%build

# We enable the compat module because rpm 4.14 still needs this.
# From rpm 4.15 onwards, this is not needed anymore.
%configure  \
    --without-readline --with-compat-module

sed -i 's|@pkgdatadir@|%{_datadir}|g' src/luaconf.h.template

make %{?_smp_mflags}

# >> build post
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
# hack so that only /usr/bin/lua gets linked with readline as it is the
# only one which needs this and otherwise we get License troubles
make %{?_smp_mflags} LIBS="-ldl" luac_LDADD="liblua.la -lm -ldl"


%install
rm -rf %{buildroot}
%make_install
# We need to make sure we package liblua-5.1.so too, so that
# the dependencies for rpm, rpm-python and rpmlint remain present.
# NOTE: this can be only removed after next stop release, previous was Sailfish OS 3.0.0
[ -f %{_libdir}/liblua-5.1.so ] && cp %{_libdir}/liblua-5.1.so %{buildroot}%{_libdir}

%post -n liblua -p /sbin/ldconfig

%postun -n liblua -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc mit.txt
%doc README
%{_bindir}/lua*
%doc %{_mandir}/man1/lua*.1*


%files -n liblua
%defattr(-,root,root,-)
%{_libdir}/liblua-*.so

%files static
%defattr(-,root,root,-)
%{_libdir}/*.a

%files devel
%defattr(-,root,root,-)
%doc doc/*.css doc/*.gif doc/*.html doc/*.png
%{_includedir}/l*.h
%{_includedir}/l*.hpp
%{_libdir}/liblua.so
%{_libdir}/pkgconfig/*.pc
