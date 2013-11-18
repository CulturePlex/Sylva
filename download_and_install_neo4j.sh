#!/bin/bash

DEFAULT_VERSION="1.9.2"
VERSION=${1-$DEFAULT_VERSION}
OLD_DIR="neo4j-community-$VERSION"
NEW_DIR="neo4j"
FILE="$OLD_DIR-unix.tar.gz"
DOWNLOAD_SERVER="http://dist.neo4j.org/"
DOWNLOAD_URL="$DOWNLOAD_SERVER$FILE"
SERVER_PROPERTIES_FILE="neo4j/conf/neo4j-server.properties"
OLD_URL="\/db\/data\/"
NEW_URL="\/db\/sylva\/"
OLD_PORT="7474"
NEW_PORT="7373"

wget $DOWNLOAD_URL
tar -zxvf $FILE > /dev/null
rm $FILE
mv $OLD_DIR $NEW_DIR

if grep $OLD_PORT $SERVER_PROPERTIES_FILE > /dev/null; then
    sed -i s/$OLD_PORT/$NEW_PORT/g  $SERVER_PROPERTIES_FILE
fi

if grep $OLD_URL $SERVER_PROPERTIES_FILE > /dev/null; then
    sed -i s/$OLD_URL/$NEW_URL/g  $SERVER_PROPERTIES_FILE
fi
