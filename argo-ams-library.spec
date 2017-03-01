%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%define underscore() %(echo %1 | sed 's/-/_/g')

Name:           argo-ams-library
Version:        0.1.0
Release:        1%{?dist}
Summary:        A simple python library for interacting with the ARGO Messaging Service

Group:          Development/Libraries
License:        ASL 2.0  
URL:            https://github.com/ARGOeu/argo-ams-library
Source0:        %{name}-%{version}.tar.gz 

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch 
BuildRequires:  python2-devel
Requires:       python-requests 

%description
A simple python library for interacting with the ARGO Messaging Service

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT --record=INSTALLED_FILES

%files -f INSTALLED_FILES
%defattr(-,root,root,-)
%dir %{python_sitelib}/%{underscore %{name}}
%{python_sitelib}/%{underscore %{name}}/*.py[co]

%changelog
* Fri Feb 24 2017 Daniel Vrcic <dvrcic@srce.hr> - 0.1.0-1%{?dist}
- first version 
