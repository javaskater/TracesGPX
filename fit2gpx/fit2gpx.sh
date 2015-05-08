#!/bin/sh
#export INSTALL_HOME="/home/jpmena/AtelierSODA"
export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-amd64"
export CLASSPATH="lib/fit.jar:lib/fit2gpx_nosdk.jar"
${JAVA_HOME}/bin/java -classpath $CLASSPATH fit2gpx $@
