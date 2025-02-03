#!/bin/bash

bin/kafka-topics.sh --create --topic task-created --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --topic estimate-complete --bootstrap-server localhost:9092