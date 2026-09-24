%global debug_package %{nil}
%global __os_install_post %{nil}
%global _build_id_links none

Name:           qcom-sensors-ship
Version:        2.0.1
Release:        %autorelease
Summary:        Prebuilt Qualcomm Sensors-ship libraries and services
License:        Proprietary
URL:            http://support.cdmatech.com
Source0:        qcom-sensors-ship-2.0.1_1.el10.aarch64.tar.gz
ExclusiveArch:  aarch64

%description
Prebuilt Qualcomm Sensors-ship libraries, services, configuration files, and
 test components. This package-only spec repackages the binary payload from
Source0 and does not compile source code.

%package -n qcom-sensors-registry
Summary:        Qualcomm Sensors-registry runtime files
%description -n qcom-sensors-registry
Runtime configuration and registry pkg-config files for Sensors.

%package -n qcom-sensors-api
Summary:        Qualcomm Sensors-api runtime libraries
Requires:       qcom-sensing-hub%{?_isa}
Requires:       fastrpc%{?_isa}
%description -n qcom-sensors-api
Runtime Sensors API libraries and protocol files.

%package -n qcom-sensors-api-devel
Summary:        Qualcomm Sensors-api development files
Requires:       qcom-sensors-api%{?_isa} = %{version}-%{release}
Requires:       qcom-sensing-hub-devel%{?_isa}
Requires:       fastrpc-devel%{?_isa}
%description -n qcom-sensors-api-devel
Development files for the Sensors API.

%package -n qcom-sensors-core
Summary:        Qualcomm Sensors-core runtime libraries
Requires:       qmi-framework%{?_isa}
Requires:       qcom-sensing-hub%{?_isa}
Requires:       qcom-sensors-api%{?_isa} = %{version}-%{release}
%description -n qcom-sensors-core
Runtime Sensors core libraries.

%package -n qcom-sensors-core-devel
Summary:        Qualcomm Sensors-core development files
Requires:       qcom-sensors-core%{?_isa} = %{version}-%{release}
Requires:       qcom-sensors-api-devel%{?_isa} = %{version}-%{release}
Requires:       qmi-framework-devel%{?_isa}
Requires:       qcom-sensing-hub-devel%{?_isa}
%description -n qcom-sensors-core-devel
Development files for the Sensors core libraries.

%package -n qcom-sensors-services
Summary:        Qualcomm Sensors services and sscrpcd
Requires:       fastrpc%{?_isa}
Requires:       qcom-sensors-registry%{?_isa} = %{version}-%{release}
%description -n qcom-sensors-services
Runtime Sensors services, libraries, and sscrpcd service files.

%package -n qcom-sensors-services-devel
Summary:        Qualcomm Sensors services development files
Requires:       qcom-sensors-services%{?_isa} = %{version}-%{release}
Requires:       fastrpc-devel%{?_isa}
%description -n qcom-sensors-services-devel
Development files for the Sensors services libraries.

%package -n qcom-sensors-test-core
Summary:        Qualcomm Sensors test-core runtime libraries
Requires:       qcom-sensors-api%{?_isa} = %{version}-%{release}
Requires:       qcom-sensors-core%{?_isa} = %{version}-%{release}
%description -n qcom-sensors-test-core
Runtime Sensors test-core libraries.

%package -n qcom-sensors-test-core-devel
Summary:        Qualcomm Sensors test-core development files
Requires:       qcom-sensors-test-core%{?_isa} = %{version}-%{release}
Requires:       qcom-sensors-api-devel%{?_isa} = %{version}-%{release}
Requires:       qcom-sensors-core-devel%{?_isa} = %{version}-%{release}
%description -n qcom-sensors-test-core-devel
Development files for Sensors test-core.

%package -n qcom-sensors-test-apps
Summary:        Qualcomm Sensors test applications
Requires:       qcom-sensors-api%{?_isa} = %{version}-%{release}
Requires:       qcom-sensors-core%{?_isa} = %{version}-%{release}
Requires:       qcom-sensors-test-core%{?_isa} = %{version}-%{release}
%description -n qcom-sensors-test-apps
Prebuilt Sensors test applications.

%package -n qcom-sensors-test-apps-devel
Summary:        Qualcomm Sensors test applications development files
Requires:       qcom-sensors-test-apps%{?_isa} = %{version}-%{release}
Requires:       qcom-sensors-test-core-devel%{?_isa} = %{version}-%{release}
%description -n qcom-sensors-test-apps-devel
Development files for Sensors test applications.

%prep
%setup -q -n qcom-sensors-ship-2.0.1

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a etc usr %{buildroot}/

# These payloads belong to separate packages and are not duplicated here.
rm -rf %{buildroot}%{_includedir}/nanopb
rm -rf %{buildroot}%{_includedir}/nanopb_gen
rm -rf %{buildroot}%{_includedir}/proto_gen
rm -f %{buildroot}%{_libdir}/libprotobuf*.so*
rm -f %{buildroot}%{_libdir}/libprotobuf*.a
find %{buildroot} -type f -name '*.la' -delete
# Build-ID links came from the original binary RPM build and are regenerated
# by the target RPM build if needed; do not leave stale links in this payload.
rm -rf %{buildroot}%{_prefix}/lib/.build-id

manifest_dir=%{_builddir}/qcom-sensors-prebuilt-manifests
rm -rf "$manifest_dir"
mkdir -p "$manifest_dir"

add_matches() {
    local out="$1"
    shift
    local pattern path
    for pattern in "$@"; do
        while IFS= read -r path; do
            path="${path#%{buildroot}}"
            printf '%s\n' "$path" >> "$out"
        done < <(find %{buildroot} -type f -o -type l | while IFS= read -r path; do
            case "$path" in
                %{buildroot}/$pattern) printf '%s\n' "$path" ;;
            esac
        done)
    done
}

sort_unique() {
    local f="$1"
    sed -i '/\.la$/d' "$f"
    sort -u "$f" -o "$f"
}

require_nonempty() {
    local f="$1"
    if [ ! -s "$f" ]; then
        echo "ERROR: empty RPM file manifest: $f" >&2
        exit 1
    fi
}

: > "$manifest_dir/registry"
add_matches "$manifest_dir/registry" 'etc/sensors/*'
printf '%s\n' \
    '/usr/lib64/pkgconfig/sensors-registry.pc' \
    '/usr/share/licenses/qcom-sensors-registry/copyright' >> "$manifest_dir/registry"
sort_unique "$manifest_dir/registry"

: > "$manifest_dir/api.runtime"
: > "$manifest_dir/api.devel"
add_matches "$manifest_dir/api.runtime" \
    'usr/lib64/libsensinghubapiprop.so.*' \
    'usr/lib64/libsensinghubapipropc.so.*' \
    'etc/sensors/proto/*'
printf '%s\n' '/usr/share/licenses/qcom-sensors-api/copyright' >> "$manifest_dir/api.runtime"
add_matches "$manifest_dir/api.devel" \
    'usr/lib64/libsensinghubapiprop.so' \
    'usr/lib64/libsensinghubapipropc.so' \
    'usr/lib64/pkgconfig/sensors-api*.pc' \
    'usr/include/*'
sort_unique "$manifest_dir/api.runtime"
sort_unique "$manifest_dir/api.devel"

: > "$manifest_dir/core.runtime"
: > "$manifest_dir/core.devel"
add_matches "$manifest_dir/core.runtime" \
    'usr/lib64/libQshSession.so.*' \
    'usr/lib64/libQshQmiIDL.so.*'
printf '%s\n' '/usr/share/licenses/qcom-sensors-core/copyright' >> "$manifest_dir/core.runtime"
add_matches "$manifest_dir/core.devel" \
    'usr/lib64/libQshSession.so' \
    'usr/lib64/libQshQmiIDL.so' \
    'usr/lib64/pkgconfig/sensors-core*.pc'
sort_unique "$manifest_dir/core.runtime"
sort_unique "$manifest_dir/core.devel"

: > "$manifest_dir/services.runtime"
: > "$manifest_dir/services.devel"
add_matches "$manifest_dir/services.runtime" \
    'usr/bin/sscrpcd' \
    'usr/lib/systemd/system/sscrpcd.service' \
    'usr/lib64/libsns_direct_channel_stub.so.*' \
    'usr/lib64/libsns_remote_proc_state_stub.so.*'
printf '%s\n' '/usr/share/licenses/qcom-sensors-services/copyright' >> "$manifest_dir/services.runtime"
add_matches "$manifest_dir/services.devel" \
    'usr/lib64/libsns_direct_channel_stub.so' \
    'usr/lib64/libsns_remote_proc_state_stub.so' \
    'usr/lib64/pkgconfig/sensors-services*.pc'
sort_unique "$manifest_dir/services.runtime"
sort_unique "$manifest_dir/services.devel"

: > "$manifest_dir/test-core.runtime"
: > "$manifest_dir/test-core.devel"
add_matches "$manifest_dir/test-core.runtime" \
    'usr/lib64/libsnsdiaglog.so.*' \
    'usr/lib64/libsnsdiaglog-c.so.*' \
    'usr/lib64/libSEESalt.so.*' \
    'usr/lib64/libUSTANative.so.*'
printf '%s\n' '/usr/share/licenses/qcom-sensors-test-core/copyright' >> "$manifest_dir/test-core.runtime"
add_matches "$manifest_dir/test-core.devel" \
    'usr/lib64/libsnsdiaglog.so' \
    'usr/lib64/libsnsdiaglog-c.so' \
    'usr/lib64/libSEESalt.so' \
    'usr/lib64/libUSTANative.so' \
    'usr/lib64/pkgconfig/sensors-test-core*.pc' \
    'usr/include/test/core/*'
sort_unique "$manifest_dir/test-core.runtime"
sort_unique "$manifest_dir/test-core.devel"

: > "$manifest_dir/test-apps.runtime"
: > "$manifest_dir/test-apps.devel"
find %{buildroot}%{_bindir} -maxdepth 1 \( -type f -o -type l \) -print 2>/dev/null | \
    sed "s#^%{buildroot}##" | grep -v '^/usr/bin/sscrpcd$' >> "$manifest_dir/test-apps.runtime" || :
printf '%s\n' '/usr/share/licenses/qcom-sensors-test-apps/copyright' >> "$manifest_dir/test-apps.runtime"
add_matches "$manifest_dir/test-apps.devel" \
    'usr/lib64/pkgconfig/sensors-test-apps*.pc'
sort_unique "$manifest_dir/test-apps.runtime"
sort_unique "$manifest_dir/test-apps.devel"

for f in "$manifest_dir"/*; do
    require_nonempty "$f"
done

echo '===== GENERATED RPM FILE LISTS ====='
for f in "$manifest_dir"/*; do
    echo "--- $(basename "$f")"
    cat "$f"
done
echo '===== END GENERATED RPM FILE LISTS ====='

%files -n qcom-sensors-registry -f %{_builddir}/qcom-sensors-prebuilt-manifests/registry
%files -n qcom-sensors-api -f %{_builddir}/qcom-sensors-prebuilt-manifests/api.runtime
%files -n qcom-sensors-api-devel -f %{_builddir}/qcom-sensors-prebuilt-manifests/api.devel
%files -n qcom-sensors-core -f %{_builddir}/qcom-sensors-prebuilt-manifests/core.runtime
%files -n qcom-sensors-core-devel -f %{_builddir}/qcom-sensors-prebuilt-manifests/core.devel
%files -n qcom-sensors-services -f %{_builddir}/qcom-sensors-prebuilt-manifests/services.runtime
%files -n qcom-sensors-services-devel -f %{_builddir}/qcom-sensors-prebuilt-manifests/services.devel
%files -n qcom-sensors-test-core -f %{_builddir}/qcom-sensors-prebuilt-manifests/test-core.runtime
%files -n qcom-sensors-test-core-devel -f %{_builddir}/qcom-sensors-prebuilt-manifests/test-core.devel
%files -n qcom-sensors-test-apps -f %{_builddir}/qcom-sensors-prebuilt-manifests/test-apps.runtime
%files -n qcom-sensors-test-apps-devel -f %{_builddir}/qcom-sensors-prebuilt-manifests/test-apps.devel

%changelog
* Wed Sep 23 2026 QGenie <qgenie@qti.qualcomm.com> - 2.0.1-1.nodiag
- Repackage the prebuilt Sensors-ship payload.
- Remove stale build-ID links and include generated license files.
- Include sensors-registry.pc in the registry runtime package.
- Exclude protobuf, NanoPB, and libtool archive payloads.
