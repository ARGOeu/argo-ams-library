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
        stage ('Testing and building...') {
            parallel {
                stage('Centos 7') {
                    agent {
                        docker {
                            image 'argo.registry:5000/epel-7-ams'
                            args '-u jenkins:jenkins'
                        }
                    }
                    stages {
                        stage ('Test Centos 7') {
                            steps {
                                echo 'Executing unit tests @ Centos 7...'
                                sh '''
                                    cd ${WORKSPACE}/$PROJECT_DIR
                                    rm -f .python-version &>/dev/null
                                    rm -rf .coverage* .tox/ coverage.xml &> /dev/null
                                    source $HOME/pyenv.sh
                                    ALLPYVERS=$(pyenv versions | grep '^[ ]*[0-9]' | tr '\n' ' ')
                                    PY310V=$(pyenv versions | grep ams-py310)
                                    echo Found Python versions $ALLPYVERS $PY310V
                                    pyenv local $ALLPYVERS ${PY310V// /}
                                    export TOX_SKIP_ENV="py3[7,8,9,10,11].*"
                                    tox -p all
                                    coverage xml --omit=*usr* --omit=*.tox*
                                '''
                                cobertura coberturaReportFile: '**/coverage.xml'
                            }
                        }
                        stage ('Build Centos 7') {
                            steps {
                                echo 'Building Centos 7 RPM...'
                                withCredentials(bindings: [sshUserPrivateKey(credentialsId: 'jenkins-rpm-repo', usernameVariable: 'REPOUSER', \
                                                                            keyFileVariable: 'REPOKEY')]) {
                                    sh "/home/jenkins/build-rpm.sh -w ${WORKSPACE} -b ${BRANCH_NAME} -d centos7 -p ${PROJECT_DIR} -s ${REPOKEY}"
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
                stage('Rocky 8') {
                    agent {
                        docker {
                            image 'argo.registry:5000/epel-8-ams'
                            args '-u jenkins:jenkins'
                        }
                    }
                    stages {
                        stage ('Test Rocky 8') {
                            steps {
                                echo 'Executing unit tests @ Rocky 8...'
                                sh '''
                                    cd ${WORKSPACE}/$PROJECT_DIR
                                    rm -f .python-version &>/dev/null
                                    rm -rf .coverage* .tox/ coverage.xml &> /dev/null
                                    source $HOME/pyenv.sh
                                    ALLPYVERS=$(pyenv versions | grep '^[ ]*[0-9]' | tr '\n' ' ')
                                    echo Found Python versions $ALLPYVERS
                                    pyenv local $ALLPYVERS
                                    export TOX_SKIP_ENV="py27.*|py311.*"
                                    tox -p 4
                                    coverage xml --omit=*usr* --omit=*.tox*
                                '''
                                cobertura coberturaReportFile: '**/coverage.xml'
                            }
                        }
                        stage ('Build Rocky 8') {
                            steps {
                                echo 'Building Rocky 8 RPM...'
                                withCredentials(bindings: [sshUserPrivateKey(credentialsId: 'jenkins-rpm-repo', usernameVariable: 'REPOUSER', \
                                                                            keyFileVariable: 'REPOKEY')]) {
                                    sh "/home/jenkins/build-rpm.sh -w ${WORKSPACE} -b ${BRANCH_NAME} -d rocky8 -p ${PROJECT_DIR} -s ${REPOKEY}"
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
                stage('Rocky 9') {
                    agent {
                        docker {
                            image 'argo.registry:5000/epel-9-ams'
                            args '-u jenkins:jenkins'
                        }
                    }
                    stages {
                        stage ('Test Rocky 9') {
                            steps {
                                echo 'Executing unit tests @ Rocky 9...'
                                sh '''
                                    cd ${WORKSPACE}/$PROJECT_DIR
                                    rm -f .python-version &>/dev/null
                                    rm -rf .coverage* .tox/ coverage.xml &> /dev/null
                                    source $HOME/pyenv.sh
                                    ALLPYVERS=$(pyenv versions | grep '^[ ]*[0-9]' | tr '\n' ' ')
                                    echo Found Python versions $ALLPYVERS
                                    pyenv local $ALLPYVERS
                                    export TOX_SKIP_ENV="py27.*|py36.*"
                                    tox -p all
                                    coverage xml --omit=*usr* --omit=*.tox*
                                '''
                                cobertura coberturaReportFile: '**/coverage.xml'
                            }
                        }
                        stage ('Build Rocky 9') {
                            steps {
                                echo 'Building Rocky 9 RPM...'
                                withCredentials(bindings: [sshUserPrivateKey(credentialsId: 'jenkins-rpm-repo', usernameVariable: 'REPOUSER', \
                                                                            keyFileVariable: 'REPOKEY')]) {
                                    sh "/home/jenkins/build-rpm.sh -w ${WORKSPACE} -b ${BRANCH_NAME} -d rocky9 -p ${PROJECT_DIR} -s ${REPOKEY}"
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
            }
        }
        stage ('Upload to PyPI'){
            when {
                branch 'master'
            }
            agent {
                docker {
                    image 'argo.registry:5000/python3'
                }
            }
            steps {
                echo 'Build python package'
                withCredentials(bindings: [usernamePassword(credentialsId: 'pypi-token', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
                    sh '''
                        cd ${WORKSPACE}/$PROJECT_DIR
                        pipenv install --dev
                        pipenv run python setup.py sdist bdist_wheel
                        pipenv run python -m twine upload -u $USERNAME -p $PASSWORD dist/*
                    '''
                }
            }
            post {
                always {
                    cleanWs()
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
