# data

This contains data acquisition steps and processing scripts for shoving
this data into databases.

To build/rebuild/migrate the database, run `./run build/rebuild/migrate`.

## Prerequisites

Tools required:

* sqlite3;
* spatialite;
* ogr2ogr

## Sources

Shapefiles are sourced from [geoportal](https://geoportal.statistics.gov.uk)
unless stated otherwise.

## Importers

Each importer should be written as a `shell` script, with a particular emphasis
on using `ogr2ogr` for conversions, `spatialite_tool` for importing Shapefiles
into the database, and `sqlite3` for importing CSVs into the database.

## Schema

Each schema should be written as a `shell` script, calling out to the database,
loading database definitions via stdin to `sqlite3`.
