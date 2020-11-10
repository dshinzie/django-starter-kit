#!/bin/bash

if [ $# -ne 1 ]
then
    echo "$(basename $0) env"
    exit 1
fi

env=$1

gsutil -m cp -r -a public-read $(dirname $0)/../static/** gs://${env}-static
