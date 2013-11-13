#!/bin/bash

wget dist.neo4j.org/neo4j-community-1.9.2-unix.tar.gz
tar -zxvf neo4j-community-1.9.2-unix.tar.gz
mv neo4j-community-1.9.2 neo4j
cp ./server.properties neo4j/conf/
rm -rf neo4j/conf/neo4j-server.properties
mv neo4j/conf/server.properties neo4j/conf/neo4j-server.properties
./neo4j/bin/neo4j start
