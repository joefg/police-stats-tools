#!/usr/bin/env bash

function all_crime_stats(){
    local database=$1
    python3 ./importers/crime_stats_all.py "$database"
}

all_crime_stats "$1"