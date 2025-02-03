#!/bin/bash

KAFKA_CLUSTER_ID="$(${KAFKA_LOCATION}/bin/kafka-storage.sh random-uuid)"

# Remove existing storage directory and temporary files
rm -rf /tmp/kraft-combined-logs
rm -rf /tmp/kafka-logs

${KAFKA_LOCATION}/bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c ${KAFKA_LOCATION}/config/kraft/reconfig-server.properties

${KAFKA_LOCATION}/bin/kafka-server-start.sh ${KAFKA_LOCATION}/config/kraft/reconfig-server.properties