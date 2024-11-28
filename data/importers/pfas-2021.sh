#!/usr/bin/env bash

source importers/utils.sh

function add_pfas(){
	local database=$1
	shift

	rm -rf build/pfa-21
	mkdir -p build/pfa-21
	unzip "downloads/Police_Force_Areas_Dec_2021_EW_BGC_2022.zip" -d build/pfa-21

	local converted=$(reproject_shp "build/pfa-21/PFA_DEC_2021_EW_BGC.shp" "EPSG:4326")
	spatialite_tool -i -shp "${converted}" -d "$database" \
		-t "pfa_21" -g geometry -c utf-8 -s 4326

	add_indexes "$database" "pfa_21" | spatialite $database
}

add_pfas $1
