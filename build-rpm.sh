#!/bin/bash

#title           :build-rpm.sh
#usage		     :./build-rpm.sh [-w] [-b] [-p] [-d] [-s] [-e]
#description     :This script will run the compilation of a project and will
#                 build an rpm to copy it to a remote repo specified. The 
#                 purpose of this script is to be used inside a container at 
#                 the stage of packaging executed from a Jenkinsfile
#==============================================================================

set -ex

# Get Arguments 
while getopts "hw:b:p:d:s:e:" opt; do
  case ${opt} in
    h )
        echo "Usage: build-rpm.sh"
        echo "Required arguments:"
        echo "   -w  Workspace path"
        echo "   -b  Checkedout branch"
        echo "   -p  Project name"
        echo "   -d  OS distribution ex. centos7"
        echo "Optional arguments:"
        echo "   -s  SecretKey for rpm-repo"
        echo "   -e  Rpmbuild --with cmd switch"
        exit 0
      ;;
    b ) branch_name=${OPTARG};;
    w ) workspace=${OPTARG};;
    p ) project=${OPTARG};;
    d ) distribution=${OPTARG} ;;
    s ) secretkey=${OPTARG} ;;
    e ) withswitch=${OPTARG} ;;
    \? ) echo "Usage: build-rpm.sh [-w] Workspace [-b] Branch [-p] Project [-d] Distribution [-s] SecretKey [-e] --with Switch"
         exit 1
      ;;
  esac
done

# Check if required variables values are not empty
if [[ -z "${workspace}" || -z "${project}" || -z "${branch_name}" || -z "${distribution}" ]]; then
    echo "Please specify all 4 required arguments to execute script"
    echo "Run build-rpm.sh -h for more"
    exit 1
fi

# Set up Release env (devel|prod) for rpm-repo upload
if [[ "${branch_name}" == "master" || "${branch_name}" == "main" ]]; then
    release_env="prod"
elif  [[ "${branch_name}" == "devel" || "${branch_name}" == "develop" ]]; then
    release_env="devel"
fi

echo 'Building rpm ...'
cd ${workspace}/${project} && make sources
cp ${workspace}/${project}/${project}*.tar.gz /home/jenkins/rpmbuild/SOURCES/
if [[ "${branch_name}" != "master"  && "${branch_name}" != "main" ]]; then
    sed -i 's/^Release.*/Release: %(echo $GIT_COMMIT_DATE).%(echo $GIT_COMMIT_HASH)%{?dist}/' ${workspace}/${project}/${project}.spec
fi
cd /home/jenkins/rpmbuild/SOURCES && tar -xzvf ${project}*.tar.gz
cp ${workspace}/${project}/${project}.spec /home/jenkins/rpmbuild/SPECS/
if [[ -z "${withswitch}" ]]; then
  rpmbuild -bb /home/jenkins/rpmbuild/SPECS/*.spec
else
  rpmbuild -bb /home/jenkins/rpmbuild/SPECS/*.spec --with ${withswitch}
fi
rm -f ${workspace}/*.rpm
cp /home/jenkins/rpmbuild/RPMS/**/*.rpm ${workspace}/

# Upload artifacts to rpm-repo if branch is master or devel
if [[ "${branch_name}" == "master" || "${branch_name}" == "main" || "${branch_name}" == "devel" || "${branch_name}" == "develop" ]]; then
    echo "Uploading rpm for ${release_env} ..."
    if [[ -z "${secretkey}" ]]; then
        scp -o StrictHostKeyChecking=no ${workspace}/*.rpm jenkins@rpm-repo.argo.grnet.gr:/repos/ARGO/${release_env}/${distribution}/
        ssh -o StrictHostKeyChecking=no jenkins@rpm-repo.argo.grnet.gr createrepo --update /repos/ARGO/${release_env}/${distribution}/
    else
        scp -i ${secretkey} -o StrictHostKeyChecking=no ${workspace}/*.rpm jenkins@rpm-repo.argo.grnet.gr:/repos/ARGO/${release_env}/${distribution}/
        ssh -i ${secretkey} -o StrictHostKeyChecking=no jenkins@rpm-repo.argo.grnet.gr createrepo --update /repos/ARGO/${release_env}/${distribution}/
    fi
fi
