%define keepstatic 1

Name:       lua
Summary:    Powerful light-weight programming language
Version:    5.4.6
Release:    1
License:    MIT
URL:        https://github.com/sailfishos/lua
Source0:    %{name}-%{version}.tar.gz
Source1:    mit.txt
Patch0:     lua-5.4.0-autotoolize.patch

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
# lua-5.4.0-autotoolize.patch
%patch0 -p1

# Put proper version in configure.ac, patch0 hardcodes 5.4.0
sed -i 's|5.4.0|%{version}|g' configure.ac
autoreconf -ifv

%build

%configure  \
    --without-readline

sed -i 's|@pkgdatadir@|%{_datadir}|g' src/luaconf.h.template

make %{?_smp_mflags}

sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
# hack so that only /usr/bin/lua gets linked with readline as it is the
# only one which needs this and otherwise we get License troubles
make %{?_smp_mflags} LIBS="-ldl" luac_LDADD="liblua.la -lm -ldl"


%install
%make_install
# We need to make sure we package liblua-5.3.so too, so that
# the dependencies for rpm, rpm-python and rpmlint remain present.
# NOTE: this can be only removed after next stop release
[ -f %{_libdir}/liblua-5.3.so ] && cp %{_libdir}/liblua-5.3.so %{buildroot}%{_libdir}

%post -n liblua -p /sbin/ldconfig

%postun -n liblua -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%license mit.txt
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
