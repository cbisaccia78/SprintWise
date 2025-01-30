#!/bin/bash

KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"

bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/kraft/reconfig-server.properties

bin/kafka-server-start.sh config/kraft/reconfig-server.properties

bin/kafka-topics.sh --create --topic task-created --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --topic estimate-complete --bootstrap-server localhost:9092