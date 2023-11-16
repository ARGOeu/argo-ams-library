pipeline {
    agent any
    options {
        checkoutToSubdirectory('argo-ams-library')
    }
    environment {
        PROJECT_DIR="argo-ams-library"
        GIT_COMMIT=sh(script: "cd ${WORKSPACE}/$PROJECT_DIR && git log -1 --format=\"%H\"",returnStdout: true).trim()
        GIT_COMMIT_HASH=sh(script: "cd ${WORKSPACE}/$PROJECT_DIR && git log -1 --format=\"%H\" | cut -c1-7",returnStdout: true).trim()
        GIT_COMMIT_DATE=sh(script: "date -d \"\$(cd ${WORKSPACE}/$PROJECT_DIR && git show -s --format=%ci ${GIT_COMMIT_HASH})\" \"+%Y%m%d%H%M%S\"",returnStdout: true).trim()

    }
    stages {
        stage ('Execute tests for RockyLinux'){
            parallel {
                stage ('Test Rocky 8') {
                    agent {
                        docker {
                            image 'localhost:5000/rocky-8:latest'
                            args '-u jenkins:jenkins'
                        }
                    }
                    steps {
                        echo 'Building Rpm...'
                        sh '''
                            cd ${WORKSPACE}/$PROJECT_DIR
                            cp argo-ams-library-r8.spec argo-ams-library.spec
                            rm -f .python-version &>/dev/null
                            pyenv local 3.7.15 3.8.15 3.9.15 3.10.13 3.11.6
                            tox
                            coverage xml --omit=*usr* --omit=*.tox*
                        '''
                        cobertura coberturaReportFile: '**/coverage.xml'
                    }
                }
                stage ('Test Rocky 9') {
                    agent {
                        docker {
                            image 'localhost:5000/rocky-9:latest'
                            args '-u jenkins:jenkins'
                        }
                    }
                    steps {
                        echo 'Building Rpm...'
                        sh '''
                            cd ${WORKSPACE}/$PROJECT_DIR
                            cp argo-ams-library-r9.spec argo-ams-library.spec
                            rm -f .python-version &>/dev/null
                            pyenv local 3.7.15 3.8.15 3.9.15 3.10.13 3.11.6
                            for version in 37 38 39 310 311; do tox -e py${version}-requests0; done
                            coverage xml --omit=*usr* --omit=*.tox*
                        '''
                        cobertura coberturaReportFile: '**/coverage.xml'
                    }
                }
            }
        }
        stage ('Build RPM packages for Rocky 8 and Rocky 9'){
            parallel {
                stage ('Build Rocky 8') {
                    agent {
                        docker {
                            image 'localhost:5000/rocky-8:latest'
                            args '-u jenkins:jenkins'
                        }
                    }
                    steps {
                        echo 'Building Rpm...'
                        withCredentials(bindings: [sshUserPrivateKey(credentialsId: 'jenkins-rpm-repo', usernameVariable: 'REPOUSER', \
                                                                    keyFileVariable: 'SSH_PRIVATE_KEY')]) {
                            sh '''
                                cd ${WORKSPACE}/$PROJECT_DIR
                                make clean
                                make git_commit_date=${GIT_COMMIT_DATE} git_commit_hash=${GIT_COMMIT_HASH} workspace=${WORKSPACE}/$PROJECT_DIR branch_name=${GIT_BRANCH} rpm
                                make git_commit_date=${GIT_COMMIT_DATE} git_commit_hash=${GIT_COMMIT_HASH} secretkey=${SSH_PRIVATE_KEY} workspace=${WORKSPACE}/$PROJECT_DIR branch_name=${GIT_BRANCH} upload
                            '''
                        }
                        archiveArtifacts artifacts: '**/*.rpm', fingerprint: true
                    }
                    post {
                        always {
                            cleanWs()
                        }
                    }
                }
                stage ('Build Rocky 9') {
                    agent {
                        docker {
                            image 'localhost:5000/rocky-9:latest'
                            args '-u jenkins:jenkins'
                        }
                    }
                    steps {
                        echo 'Building Rpm...'
                        withCredentials(bindings: [sshUserPrivateKey(credentialsId: 'jenkins-rpm-repo', usernameVariable: 'REPOUSER', \
                                                                    keyFileVariable: 'SSH_PRIVATE_KEY')]) {
                            sh '''
                                cd ${WORKSPACE}/$PROJECT_DIR
                                make clean
                                make git_commit_date=${GIT_COMMIT_DATE} git_commit_hash=${GIT_COMMIT_HASH} workspace=${WORKSPACE}/$PROJECT_DIR branch_name=${GIT_BRANCH} rpm
                                make git_commit_date=${GIT_COMMIT_DATE} git_commit_hash=${GIT_COMMIT_HASH} secretkey=${SSH_PRIVATE_KEY} workspace=${WORKSPACE}/$PROJECT_DIR branch_name=${GIT_BRANCH} upload
                            '''
                        }
                        archiveArtifacts artifacts: '**/*.rpm', fingerprint: true
                    }
                    post {
                        always {
                            cleanWs()
                        }
                    }
                }
            }
        }
        // stage ('Upload to PyPI'){
        //     when {
        //         branch 'master'
        //     }
        //     agent {
        //         docker {
        //             image 'argo.registry:5000/python3'
        //         }
        //     }
        //     steps {
        //         echo 'Build python package'
        //         withCredentials(bindings: [usernamePassword(credentialsId: 'pypi-token', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
        //             sh '''
        //                 cd ${WORKSPACE}/$PROJECT_DIR
        //                 pipenv install --dev
        //                 pipenv run python setup.py sdist bdist_wheel
        //                 pipenv run python -m twine upload -u $USERNAME -p $PASSWORD dist/*
        //             '''
        //         }
        //     }
        //     post {
        //         always {
        //             cleanWs()
        //         }
        //     }
        // }
    }
    // post {
    //     always {
    //         cleanWs()
    //     }
    //     success {
    //         script{
    //             if ( env.BRANCH_NAME == 'devel' ) {
    //                 build job: '/ARGO/argodoc/devel', propagate: false
    //             } else if ( env.BRANCH_NAME == 'master' ) {
    //                 build job: '/ARGO/argodoc/master', propagate: false
    //             }
    //             if ( env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'devel' ) {
    //                 slackSend( message: ":rocket: New version for <$BUILD_URL|$PROJECT_DIR>:$BRANCH_NAME Job: $JOB_NAME !")
    //             }
    //         }
    //     }
    //     failure {
    //         script{
    //             if ( env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'devel' ) {
    //                 slackSend( message: ":rain_cloud: Build Failed for <$BUILD_URL|$PROJECT_DIR>:$BRANCH_NAME Job: $JOB_NAME")
    //             }
    //         }
    //     }
    // }
}