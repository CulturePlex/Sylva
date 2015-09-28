#!/bin/bash
set -e
cd titan/
./bin/gremlin-server.sh  > /dev/null 2>&1 &
