# police-stats-tools

Tooling for wrangling [British Police data](https://data.police.uk/).

## Prerequisites

### Programs

Requires:

- [Spatialite](https://www.gaia-gis.it/fossil/libspatialite/index)
- [jq](https://jqlang.github.io/jq/)
- Python and [Pipenv](https://pipenv.pypa.io/en/latest/)

Make sure these are installed and working before using these tools.

### Data

Go to `data/`, then read the README in `downloads/`. Make sure you download
the files specified in the README. Then run `./run build` to create your
Spatialite database containing police data.

### Running

A `./run restore` builds your Python envitonment.

A `./run dev` spawns a JupyterLab notebook.

### Using the data

You can use JupyterLab.

You can also use QGIS: just open the Spatialite files generated in
`data/databases` in QGIS as a source, and you can treat it like any other
database.
