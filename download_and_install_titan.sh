#!/bin/bash

DEFAULT_VERSION="1.0.0-hadoop1"
VERSION=${1-$DEFAULT_VERSION}
OLD_DIR="titan-$VERSION"
NEW_DIR="titan"
FILE="$OLD_DIR.zip"
DOWNLOAD_SERVER="http://s3.thinkaurelius.com/downloads/titan/"
DOWNLOAD_URL="$DOWNLOAD_SERVER$FILE"

wget $DOWNLOAD_URL
unzip $FILE > /dev/null
rm $FILE
mv $OLD_DIR $NEW_DIR

SERVER_PROPERTIES_FILE="titan/conf/gremlin-server/gremlin-server.yaml"
OLD_CHANNELIZER="org.apache.tinkerpop.gremlin.server.channel.WebSocketChannelizer"
NEW_CHANNELIZER="org.apache.tinkerpop.gremlin.server.channel.HttpChannelizer"

if grep $OLD_CHANNELIZER $SERVER_PROPERTIES_FILE > /dev/null; then
    sed -i s/$OLD_CHANNELIZER/$NEW_CHANNELIZER/g $SERVER_PROPERTIES_FILE
fi
