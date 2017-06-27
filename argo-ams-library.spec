%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%define underscore() %(echo %1 | sed 's/-/_/g')

Name:           argo-ams-library
Version:        0.3.0
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
%doc examples/ README.md
%defattr(-,root,root,-)
%dir %{python_sitelib}/%{underscore %{name}}
%{python_sitelib}/%{underscore %{name}}/*.py[co]

%changelog
* Mon Jun 5 2017 Daniel Vrcic <dvrcic@srce.hr> - 0.2.0-1%{?dist}
- ARGO-782 Iterate over subscriptions and topics methods
- ARGO-789 Topic and subscription creation/deletion that mimic Google implementation
- ARGO-791 Methods for settings acls on topics and subscriptions
- ARGO-804 Has topic/sub methods should have ability to pass kwargs to python-requests library
- ARGO-812 Mimicked topic and subcription methods will always return corresponding objects
- ARGO-814 Publish method accepts directly list of AmsMessage objects
* Fri Mar 17 2017 Daniel Vrcic <dvrcic@srce.hr>, Themis Zamani <themiszamani@gmail.com>, Konstantinos Kagkelidis <kaggis@gmail.com> - 0.1.1-1%{?dist}
- ARGO-760 Has topic and subscription methods
- ARGO-770 AMS Library tests
* Thu Mar 2 2017 Daniel Vrcic <dvrcic@srce.hr> - 0.1.0-2%{?dist}
- ARGO-710 Provide examples of simple publishing and consuming
* Fri Feb 24 2017 Daniel Vrcic <dvrcic@srce.hr> - 0.1.0-1%{?dist}
- first version 
