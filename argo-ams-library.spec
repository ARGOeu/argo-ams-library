%global underscore() %(echo %1 | sed 's/-/_/g')

%global python3_pkgversion_39 3.9
%global python3_pkgversion_311 3.11

%global sum A simple python library for interacting with the ARGO Messaging Service
%global desc A simple python library for interacting with the ARGO Messaging Service


Name:           argo-ams-library
Summary:        %{sum}
Version:        1.0.0
Release:        1%{?dist}

Group:          Development/Libraries
License:        ASL 2.0
URL:            https://github.com/ARGOeu/argo-ams-library
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch


%description
%{desc}


%if 0%{?el8}
%package -n python%{python3_pkgversion}-%{name}
Summary: %{sum}
BuildRequires: python3-devel    python3-setuptools
Requires:      python3-requests
AutoReq: no
%description -n python%{python3_pkgversion}-%{name}
%{desc}
%{?python_provide:%python_provide python3-%{name}}

%package -n python%{python3_pkgversion_39}-%{name}
Summary: %{sum}
BuildRequires: python39-devel    python39-setuptools
Requires:      python39-requests
AutoReq: no
%description -n python%{python3_pkgversion_39}-%{name}
%{desc}
%{?python_provide:%python_provide python%{python3_pkgversion_39}-%{name}}

%prep
%setup -q

%build
%{py3_build}
python3.9 setup.py build

%install
rm -rf %{buildroot}
%{py3_install "--record=INSTALLED_FILES_PY3" }
python3.9 setup.py install --root=%{buildroot} --record=INSTALLED_FILES_PY3_39

%files -n python%{python3_pkgversion}-%{name} -f INSTALLED_FILES_PY3
%doc examples/ README.md
%defattr(-,root,root,-)
%{python3_sitelib}/*
%doc examples/ README.md

%files -n python%{python3_pkgversion_39}-%{name} -f INSTALLED_FILES_PY3_39
%doc examples/ README.md
%defattr(-,root,root,-)
/usr/lib/python3.9/site-packages/*
%doc examples/ README.md
%endif


%if 0%{?el9}
%package -n python%{python3_pkgversion}-%{name}
Summary: %{sum}
BuildRequires: python3-devel    python3-setuptools
Requires:      python3-requests
AutoReq: no
%description -n python%{python3_pkgversion}-%{name}
%{desc}
%{?python_provide:%python_provide python3-%{name}}

%package -n python%{python3_pkgversion_311}-%{name}
Summary: %{sum}
BuildRequires: python3.11-devel    python3.11-setuptools
Requires:      python3.11-requests
AutoReq: no
%description -n python%{python3_pkgversion_311}-%{name}
%{desc}
%{?python_provide:%python_provide python%{python3_pkgversion_311}-%{name}}

%prep
%setup -q

%build
%{py3_build}
python3.11 setup.py build

%install
rm -rf %{buildroot}
%{py3_install "--record=INSTALLED_FILES_PY3" }
python3.11 setup.py install --root=%{buildroot} --record=INSTALLED_FILES_PY3_311

%files -n python%{python3_pkgversion}-%{name} -f INSTALLED_FILES_PY3
%doc examples/ README.md
%defattr(-,root,root,-)
%{python3_sitelib}/*
%doc examples/ README.md

%files -n python%{python3_pkgversion_311}-%{name} -f INSTALLED_FILES_PY3_311
%doc examples/ README.md
%defattr(-,root,root,-)
/usr/lib/python3.11/site-packages/*
%doc examples/ README.md
%endif


%changelog
* Thu Jul 3 2025 Daniel Vrcic <dvrcic@srce.hr> - 0.6.3-1%{?dist}
- remove Centos 7 RPM building steps
* Thu Mar 7 2024 Daniel Vrcic <dvrcic@srce.hr> - 0.6.2-1%{?dist}
- refine spec for Rocky 8 and Rocky 9 python3 package build
* Mon Feb 6 2023 agelostsal <agelos.tsal@gmail.com> - 0.6.1-1%{?dist}
- AM-314 Add projects:createUser functionality to ams library
* Thu Nov 3 2022 Daniel Vrcic <dvrcic@srce.hr>, agelostsal <agelos.tsal@gmail.com> - 0.6.0-1%{?dist}
- AM-143 Add support for requests ReadTimeOut exception
- AM-228 Add user management fuctionality to AMS-library
- AM-227 ams-library: add support for miscellaneous api calls
- AM-225 AMS Library Support for more API Calls
- ARGO-4050 Update tox to run unit tests against recent Python versions
- ARGO-4088 Fix ams-library test execute with local pyenv load
- remove Centos 6 RPM build from spec
* Tue Aug 2 2022 agelostsal <agelos.tsal@gmail.com> - 0.5.9-1%{?dist}
- Different requests version for various  python versions
* Tue Jul 26 2022 agelostsal <agelos.tsal@gmail.com> - 0.5.8-1%{?dist}
- AM-264 argo-ams-library: Delete topic and sub doesn't use the x-api-key token
* Wed Jun 22 2022 agelostsal <agelos.tsal@gmail.com> - 0.5.7-1%{?dist}
- AM-249 ams-library: bug fix regarding sub and topic acl methods
* Tue Jun 21 2022 agelostsal <agelos.tsal@gmail.com> - 0.5.6-1%{?dist}
- AM-233 ams-library: support for project_member_get api call
- AM-230 ams-library: support for project_member_add api call
- AM-229 ams-library: support for user_get api call
- AM-226 ams-library: support for user_create api call
* Thu Apr 15 2021 agelostsal <agelos.tsal@gmail.com> - 0.5.5-1%{?dist}
- ARGO-2768 ams-library: support for AMS authorization header
* Thu Oct 8 2020 Daniel Vrcic <dvrcic@srce.hr> - 0.5.4-1%{?dist}
- ARGO-2592 ams-library py2 RPM also packages py3 specific modules
* Tue Sep 8 2020 Daniel Vrcic <dvrcic@srce.hr> - 0.5.3-1%{?dist}
- ARGO-2530 bytes handling in Py3
* Wed Jul 8 2020 Daniel Vrcic <dvrcic@srce.hr> - 0.5.2-1%{?dist}
- ARGO-2479 Modify subscription offset method fails
- ARGO-2360 Fix ack_sub retry loop
* Mon Feb 10 2020 Daniel Vrcic <dvrcic@srce.hr> - 0.5.1-1%{?dist}
- ARGO-2182 ams-lib does not retry on topic publish
* Wed Dec 4 2019 Daniel Vrcic <dvrcic@srce.hr> - 0.5.0-1%{?dist}
- ARGO-1481 Connection retry logic in ams-library
* Fri Nov 8 2019 Daniel Vrcic <dvrcic@srce.hr>, agelostsal <agelos.tsal@gmail.com> - 0.4.3-1%{?dist}
- ARGO-1990 Fix runtime dependencies
- ARGO-1862 Make argo-ams-library Python 3 ready
- ARGO-1841 Update the ams library to include the new timeToOffset functionality
* Thu Jul 26 2018 agelostsal <agelos.tsal@gmail.com> - 0.4.2-1%{?dist}
- ARGO-1479 Subscription create methods don't delegate **reqkwargs where needed
- Error handling bug during list_topic route
* Tue Jun 19 2018 Daniel Vrcic <dvrcic@srce.hr>, Konstantinos Kagkelidis <kaggis@gmail.com>, agelostsal <agelos.tsal@gmail.com> - 0.4.1-1%{?dist}
- ARGO-1120 Extend AMS client to support X509 method via the authentication server
* Mon May 14 2018 Daniel Vrcic <dvrcic@srce.hr>, Konstantinos Kagkelidis <kaggis@gmail.com>, agelostsal <agelos.tsal@gmail.com> - 0.4.0-1%{?dist}
- ARGO-1103 Handle non-JSON AMS responses
- ARGO-1105 Extend ams library to support offset manipulation
- ARGO-1118 Fix returnImmediately parameter in sub pull request
- ARGO-1127 Wrap offsets low level methods into one
- ARGO-1153 Extract JSON error messages propagated through AMS
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
