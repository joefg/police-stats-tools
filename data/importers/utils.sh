#!/usr/bin/env bash

function reproject_shp(){
	local shapefile=$1
	local new_projection=$2
	local base_shape="$(dirname $shapefile)/$(basename $shapefile .shp)"
	local new_shape="${base_shape}_Projected.shp"

	ogr2ogr -overwrite -t_srs "$new_projection" -unsetFieldWidth -lco ENCODING=UTF-8 \
			"$new_shape" "$shapefile"

	echo "$(dirname $new_shape)/$(basename $new_shape .shp)"
}

function add_indexes(){
	local database=$1
	local table=$2

	echo "SELECT CreateSpatialIndex('${table}', 'geometry');"

}
