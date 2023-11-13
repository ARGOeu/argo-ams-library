%global underscore() %(echo %1 | sed 's/-/_/g')

%global python3_pkgversion_1 3.9
%global python3_pkgversion_2 3.11

%global sum A simple python library for interacting with the ARGO Messaging Service
%global desc A simple python library for interacting with the ARGO Messaging Service

Name:           argo-ams-library
Summary:        %{sum}
Version:        0.6.1
Release:        1%{?dist}

Group:          Development/Libraries
License:        ASL 2.0
URL:            https://github.com/ARGOeu/argo-ams-library
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

%description
%{desc}

%package -n python3-%{python3_pkgversion_1}-%{name}
Summary:       %{sum}
BuildRequires: python3-devel    python3-setuptools
Requires:      python3-requests
AutoReq: no
%description -n python3-%{python3_pkgversion_1}-%{name}
%{desc}
%{?python_provide:%python_provide python3-%{python3_pkgversion_1}-%{name}}

%package -n python3-%{python3_pkgversion_2}-%{name}
Summary:       %{sum}
BuildRequires: python3.11-devel    python3.11-setuptools
Requires:      python3.11-requests
AutoReq: no
%description -n python3-%{python3_pkgversion_2}-%{name}
%{desc}
%{?python_provide:%python_provide python3-%{python3_pkgversion_2}-%{name}}

%prep
%setup -q

%build
python3.9 setup.py build
python3.11 setup.py build

%install
rm -rf %{buildroot}
python3.9 setup.py install --root=%{buildroot} --record=INSTALLED_FILES_PY3_3.9
python3.11 setup.py install --root=%{buildroot} --record=INSTALLED_FILES_PY3_3.11

%files -n python3-%{python3_pkgversion_1}-%{name} -f INSTALLED_FILES_PY3_3.9
%doc examples/ README.md
%defattr(-,root,root,-)
/usr/lib/python3.9/site-packages/*

%files -n python3-%{python3_pkgversion_2}-%{name} -f INSTALLED_FILES_PY3_3.11
%doc examples/ README.md
%defattr(-,root,root,-)
/usr/lib/python3.11/site-packages/*