#!/bin/bash

DEFAULT_VERSION="31.0esr"
VERSION=${1-$DEFAULT_VERSION}
DIR="firefox"
FILE="firefox-$VERSION.tar.bz2"
DOWNLOAD_SERVER="http://releases.mozilla.org/"
DOWNLOAD_PATH="pub/firefox/releases/$VERSION/linux-x86_64/en-US/"
DOWNLOAD_URL="$DOWNLOAD_SERVER$DOWNLOAD_PATH$FILE"

if [ ! -d "$DIR" ]; then
  wget $DOWNLOAD_URL
  tar -jxvf $FILE > /dev/null
  rm $FILE
else
  echo "Using cached directory '$DIR'."
fi
