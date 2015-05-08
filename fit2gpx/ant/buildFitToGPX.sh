#!/bin/bash

export INSTALL_HOME="/home/jpmena/AtelierSODA"
export ANT_HOME="${INSTALL_HOME}/OUTILS/CONSTRUCTION/ANT/apache-ant-1.8.4"
export ANT_OPTS="-Xms256M -Xmx512M -Dhttp.proxyHost=dgproxy.appli.dgi -Dhttp.proxyPort=8080  -Dhttp.nonProxyHosts='*.dgfip|*.impots|*.dgi|localhost'"
#export JAVA_HOME="${INSTALL_HOME}/JDK/jdk1.5.0_19_DGFiP_1"
export JAVA_HOME="${INSTALL_HOME}/JDK/jdk7"

$ANT_HOME/bin/ant -f buildFitoGPX.xml