#!/bin/bash

curl -s -I -H "Api-Key: $API_KEY" localhost:8080/healthz/ | grep 'HTTP/1.1 200 OK' > /dev/null 2>&1

exit $?
