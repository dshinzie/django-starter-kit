#!/bin/bash
#
# Used by docker-compose to prevent the web container
# from starting before the database is ready.

max_tries=18
tries=0
success=0

while [ $tries -lt $max_tries ]
do
    if ./manage.py showmigrations > /dev/null 2>&1
    then
        success=1
        break
    else
        echo "database check failed"
        sleep 5
        tries=$(( $tries + 1 ))
    fi
done

if [ $success -ne 1 ]
then
    exit 1
fi

echo "database ready"
echo "running: $@"
$@
