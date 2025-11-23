# ngtcp2 can be used by curl, curl is used by libsystemd,
# libsystemd is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%define major 16
%define libname %mklibname ngtcp2
%define develname %mklibname -d ngtcp2
%define lib32name libngtcp2
%define devel32name libngtcp2-devel

Summary:	An implementation of the RFC9000 QUIC protocol
Name:		ngtcp2
Version:	1.18.0
Release:	1
License:	MIT
Group:		System/Libraries
URL:		https://github.com/ngtcp2/ngtcp2
Source0:	https://github.com/ngtcp2/ngtcp2/releases/download/v%{version}/ngtcp2-%{version}.tar.xz
BuildRequires:	cmake ninja
BuildRequires:	pkgconfig(gnutls)
%if %{with compat32}
BuildRequires:	libc6
BuildRequires:	devel(libgnutls)
%endif

%description
An implementation of the RFC9000 QUIC protocol

%package -n %{libname}
Summary: An implementation of the RFC9000 QUIC protocol
Group: System/Libraries

%description -n %{libname}
An implementation of the RFC9000 QUIC protocol

%package -n %{develname}
Summary: Files needed for building applications with libngtcp2
Group: Development/C
Provides: %{name}-devel = %{version}-%{release}
Requires: %{libname} >= %{version}-%{release}

%description -n %{develname}
The libngtcp2-devel package includes libraries and header files needed
for building applications with libngtcp2.

%package -n %{lib32name}
Summary: An implementation of the RFC9000 QUIC protocol (32-bit)
Group: System/Libraries

%description -n %{lib32name}
An implementation of the RFC9000 QUIC protocol

%package -n %{devel32name}
Summary: Files needed for building applications with libngtcp2 (32-bit)
Group: Development/C
Requires: %{lib32name} = %{EVRD}
Requires: %{develname} = %{EVRD}

%description -n %{devel32name}
The libngtcp2-devel package includes libraries and header files needed
for building applications with libngtcp2.

%prep
%autosetup -p1 -n %{name}-%{version}
if [ -e crypto/includes/ngtcp2/ngtcp2_crypto__openssl.h ]; then
	echo "OpenSSL support is there again, remove the workaround"
	exit 1
fi
ln -s ngtcp2_crypto_quictls.h crypto/includes/ngtcp2/ngtcp2_crypto_openssl.h

%if %{with compat32}
#define build_ldflags -O2 -fno-lto
%cmake32 -G Ninja \
	-DENABLE_STATIC_LIB=OFF \
	-DENABLE_OPENSSL:BOOL=OFF \
	-DENABLE_GNUTLS:BOOL=ON
cd ..
%endif
%cmake -G Ninja \
	-DENABLE_STATIC_LIB=OFF \
	-DENABLE_OPENSSL:BOOL=OFF \
	-DENABLE_GNUTLS:BOOL=ON

%build
%if %{with compat32}
%ninja_build -C build32
%endif
%ninja_build -C build

%check
# test the just built library instead of the system one, without using rpath
export "LD_LIBRARY_PATH=$RPM_BUILD_ROOT%{_libdir}"
%ninja -C build check || :

%install
%if %{with compat32}
%ninja_install -C build32
%endif
%ninja_install -C build

#libpackage ngtcp2_crypto_quictls 1
%libpackage ngtcp2_crypto_gnutls 8

%files

%files -n %{libname}
%{_libdir}/libngtcp2.so.%{major}*

%files -n %{develname}
%{_includedir}/ngtcp2
%{_libdir}/pkgconfig/*.pc
%{_libdir}/*.so
%{_prefix}/lib/cmake/ngtcp2
%doc %{_docdir}/ngtcp2

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libngtcp2.so.%{major}*

%files -n %{devel32name}
%{_prefix}/lib/pkgconfig/*.pc
%{_prefix}/lib/*.so

#lib32package ngtcp2_crypto_quictls 1
%lib32package ngtcp2_crypto_gnutls 8
%endif
