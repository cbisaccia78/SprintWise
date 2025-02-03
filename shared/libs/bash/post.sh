#!/bin/bash

# Check if the JSON file and URL arguments are provided
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <url> <path_to_json_file>"
  exit 1
fi

URL=$1
JSON_FILE=$2


# Check if the JSON file exists
if [ ! -f "$JSON_FILE" ]; then
  echo "File not found: $JSON_FILE"
  exit 1
fi

# Execute the curl command with the provided JSON file and URL
curl -X POST "$URL" \
     -H "Content-Type: application/json" \
     -d @"$JSON_FILE"