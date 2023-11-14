// pipeline {
//     agent any
//     options {
//         checkoutToSubdirectory('argo-ams-library')
//     }
//     environment {
//         PROJECT_DIR="argo-ams-library"
//         GIT_COMMIT=sh(script: "cd ${WORKSPACE}/$PROJECT_DIR && git log -1 --format=\"%H\"",returnStdout: true).trim()
//         GIT_COMMIT_HASH=sh(script: "cd ${WORKSPACE}/$PROJECT_DIR && git log -1 --format=\"%H\" | cut -c1-7",returnStdout: true).trim()
//         GIT_COMMIT_DATE=sh(script: "date -d \"\$(cd ${WORKSPACE}/$PROJECT_DIR && git show -s --format=%ci ${GIT_COMMIT_HASH})\" \"+%Y%m%d%H%M%S\"",returnStdout: true).trim()

//     }
//     stages {
//         stage ('Test'){
//             parallel {
//                 stage ('Test Centos 7') {
//                     agent {
//                         docker {
//                             image 'argo.registry:5000/epel-7-ams'
//                             args '-u jenkins:jenkins'
//                         }
//                     }
//                     steps {
//                         echo 'Building Rpm...'
//                         sh '''
//                             cd ${WORKSPACE}/$PROJECT_DIR
//                             rm -f .python-version &>/dev/null
//                             source $HOME/pyenv.sh
//                             PY310V=$(pyenv versions | grep ams-py310)
//                             pyenv local 3.7.15 3.8.15 3.9.15 ${PY310V// /}
//                             tox
//                             coverage xml --omit=*usr* --omit=*.tox*
//                         '''
//                         cobertura coberturaReportFile: '**/coverage.xml'
//                     }
//                 }
//             }
//         }
//         stage ('Build'){
//             parallel {
//                 stage ('Build Centos 7') {
//                     agent {
//                         docker {
//                             image 'argo.registry:5000/epel-7-ams'
//                             args '-u jenkins:jenkins'
//                         }
//                     }
//                     steps {
//                         echo 'Building Rpm...'
//                         withCredentials(bindings: [sshUserPrivateKey(credentialsId: 'jenkins-rpm-repo', usernameVariable: 'REPOUSER', \
//                                                                     keyFileVariable: 'REPOKEY')]) {
//                             sh "/home/jenkins/build-rpm.sh -w ${WORKSPACE} -b ${BRANCH_NAME} -d centos7 -p ${PROJECT_DIR} -s ${REPOKEY}"
//                         }
//                         archiveArtifacts artifacts: '**/*.rpm', fingerprint: true
//                     }
//                     post {
//                         always {
//                             cleanWs()
//                         }
//                     }
//                 }
//             }
//         }
//         stage ('Upload to PyPI'){
//             when {
//                 branch 'master'
//             }
//             agent {
//                 docker {
//                     image 'argo.registry:5000/python3'
//                 }
//             }
//             steps {
//                 echo 'Build python package'
//                 withCredentials(bindings: [usernamePassword(credentialsId: 'pypi-token', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
//                     sh '''
//                         cd ${WORKSPACE}/$PROJECT_DIR
//                         pipenv install --dev
//                         pipenv run python setup.py sdist bdist_wheel
//                         pipenv run python -m twine upload -u $USERNAME -p $PASSWORD dist/*
//                     '''
//                 }
//             }
//             post {
//                 always {
//                     cleanWs()
//                 }
//             }
//         }
//     }
//     post {
//         always {
//             cleanWs()
//         }
//         success {
//             script{
//                 if ( env.BRANCH_NAME == 'devel' ) {
//                     build job: '/ARGO/argodoc/devel', propagate: false
//                 } else if ( env.BRANCH_NAME == 'master' ) {
//                     build job: '/ARGO/argodoc/master', propagate: false
//                 }
//                 if ( env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'devel' ) {
//                     slackSend( message: ":rocket: New version for <$BUILD_URL|$PROJECT_DIR>:$BRANCH_NAME Job: $JOB_NAME !")
//                 }
//             }
//         }
//         failure {
//             script{
//                 if ( env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'devel' ) {
//                     slackSend( message: ":rain_cloud: Build Failed for <$BUILD_URL|$PROJECT_DIR>:$BRANCH_NAME Job: $JOB_NAME")
//                 }
//             }
//         }
//     }
// }


pipeline {
    agent any
    environment {
        PROJECT_DIR=""
    }
    stages {
        stage('Check Docker') {
            steps {
                echo 'provjeravam da li docker postoji'
                sh 'docker --version'
            }
        }
        stage ('NodeJS'){
            parallel {
                stage ('Test NodeJS') {
                    agent {
                        docker {
                            image 'node:18.18.0-alpine3.18'
                        }
                    }
                    steps {
                        echo 'Checking Node...'
                        sh 'node --version'
                    }
                }
            }
        }
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
                            cd ${WORKSPACE}
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
                            cd ${WORKSPACE}
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
        // stage ('Build'){
        //     parallel {
        //         stage ('Build Rocky 9') {
        //             agent {
        //                 docker {
        //                     image 'localhost:5000/rocky83:latest'
        //                     args '-u jenkins:jenkins'
        //                 }
        //             }
        //             steps {
        //                 echo 'Building Rpm...'
        //                 cp argo-ams-library-r9.spec argo-ams-library.spec
        //                 sh "/home/jenkins/build-rpm.sh -w ${WORKSPACE} -b ${BRANCH_NAME} -d centos7 -p ${PROJECT_DIR}"
        //                 archiveArtifacts artifacts: '**/*.rpm', fingerprint: true
        //             }
        //             post {
        //                 always {
        //                     cleanWs()
        //                 }
        //             }
        //         }
        //     }
        // }
        stage("deploy") {
            steps {
                echo 'Hello World'
                echo "deploying the aplication... wooooow!!!"
            }
        }
    }
}