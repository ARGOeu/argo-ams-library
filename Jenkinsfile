pipeline {
    agent any
    environment {
        PROJECT_DIR=""
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