%global underscore() %(echo %1 | sed 's/-/_/g')

%global sum A simple python library for interacting with the ARGO Messaging Service
%global desc A simple python library for interacting with the ARGO Messaging Service


Name:           argo-ams-library
Summary:        %{sum}
Version:        0.5.6
Release:        1%{?dist}

Group:          Development/Libraries
License:        ASL 2.0
URL:            https://github.com/ARGOeu/argo-ams-library
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch


%description
%{desc}


%if 0%{?el6}

%package -n python2-%{name}
Obsoletes:     argo-ams-library
Provides:      argo-ams-library
Summary:       %{sum}
BuildRequires: python2-devel    python2-setuptools
Requires:      python2-requests
AutoReq: no
%description -n python2-%{name}
%{desc}
%{?python_provide:%python_provide python2-%{name}}

%else

%package -n python-%{name}
Obsoletes:     argo-ams-library
Provides:      argo-ams-library
Summary:       %{sum}
BuildRequires: python-devel     python-setuptools
Requires:      python-requests
AutoReq: no
%description -n python-%{name}
%{desc}
%{?python_provide:%python_provide python-%{name}}

%endif

%package -n python%{python3_pkgversion}-%{name}
Summary: %{sum}
%if 0%{?el6}
BuildRequires: python34-devel    python34-setuptools
Requires:      python34-requests
AutoReq: no
%else
BuildRequires: python36-devel    python36-setuptools
Requires:      python36-requests
AutoReq: no
%endif
%description -n python%{python3_pkgversion}-%{name}
%{desc}
%{?python_provide:%python_provide python3-%{name}}


%prep
%setup -q


%build
%{py_build}
%{py3_build}


%install
rm -rf %{buildroot}
%{py_install "--record=INSTALLED_FILES_PY2" }
%{py3_install "--record=INSTALLED_FILES_PY3" }


%files -n python%{python3_pkgversion}-%{name} -f INSTALLED_FILES_PY3
%doc examples/ README.md
%defattr(-,root,root,-)
%{python3_sitelib}/*
%if 0%{?el7}
%files -n python-%{name} -f INSTALLED_FILES_PY2
%else
%files -n python2-%{name} -f INSTALLED_FILES_PY2
%endif
%doc examples/ README.md
%defattr(-,root,root,-)
%{python_sitelib}/*


%changelog
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
