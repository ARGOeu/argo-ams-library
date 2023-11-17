PKGNAME=argo-ams-library

branch_name ?= default
workspace ?= default
secretkey ?= default
git_commit_date ?= default
git_commit_hash ?= default
ID := $(shell grep '^ID=' /etc/os-release | awk -F= '{print $$2}' | tr -d '"')
OS_VERSION := $(shell grep VERSION_ID /etc/os-release | cut -d= -f2 | cut -d. -f1 | tr -d '"')
distribution := $(ID)$(OS_VERSION)


# Check rockylinux os version and uses .spec file adjusted for that version 
ifeq ($(shell echo "$(OS_VERSION) >= 9.0" | bc),1)
	specfile=${PKGNAME}-r9.spec
	dist = el9
else
	specfile=${PKGNAME}-r8.spec
	dist = el8
endif

PKGVERSION=$(shell grep -s '^Version:' $(specfile) | sed -e 's/Version: *//')


# Set up Release env (devel|prod) for rpm-repo upload
ifeq ($(branch_name),master)
	release_env = prod
else ifeq ($(branch_name),main)
	release_env = prod
else ifeq ($(branch_name),devel)
	release_env = devel
else ifeq ($(branch_name),develop)
	release_env = devel
endif


srpm: dist
	rpmbuild -ts --define='dist .el6' ${PKGNAME}-${PKGVERSION}.tar.gz


# Build rpm package
rpm: dist
	rpmbuild -ta ${PKGNAME}-${PKGVERSION}.tar.gz
	rm -f ${workspace}/*.rpm
	cp /home/jenkins/rpmbuild/RPMS/**/*.rpm ${workspace}/
	rm -f /home/jenkins/rpmbuild/RPMS/noarch/*.rpm

# Upload artifacts to rpm-repo if branch is master or devel
upload:
ifeq ($(filter $(branch_name),master main devel develop),$(branch_name))
	echo "Uploading rpm for $(release_env) ..."
	scp -i $(secretkey) -o StrictHostKeyChecking=no $(workspace)/*.rpm jenkins@rpm-repo.argo.grnet.gr:./repos/ARGO/$(release_env)/$(distribution)/
	ssh -i $(secretkey) -o StrictHostKeyChecking=no jenkins@rpm-repo.argo.grnet.gr createrepo --update ./repos/ARGO/${release_env}/${distribution}/
endif


dist:
ifneq ($(filter $(branch_name),master main),$(branch_name))
	sed -i 's/^Release.*/Release:        $(git_commit_date).$(git_commit_hash).$(dist)/' ${workspace}/${specfile}
endif 
	rm -rf dist
	cp ${specfile} argo-ams-library.spec
	python3 setup.py sdist
	mv -f dist/${PKGNAME}-${PKGVERSION}.tar.gz .
	rm -rf dist
	rm -rf argo-ams-library.spec

sources: dist

clean:
	rm -rf ${PKGNAME}-${PKGVERSION}.tar.gz
	rm -f MANIFEST
	rm -rf dist
	rm -rf argo-ams-library.spec