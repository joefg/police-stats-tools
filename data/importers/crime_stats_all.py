#!/usr/bin/env python3

import logging
import csv
import os
import re
import sys
import sqlite3
from zipfile import ZipFile

class SpatialiteConnection():
    """
    Helper class for connecting to Spatialite datastores,
    for use in a with statement.
    """
    def __init__(self, location, debug=False) -> None:
        if location:
            self.conn = sqlite3.connect(os.path.join(location))
        else:
            self.conn = sqlite3.connect(':memory:')
        if debug:
            self.conn.set_trace_callback(print)
        self.conn.row_factory = lambda cursor, result: \
            dict(zip([column[0] for column in cursor.description], result))
        self.conn.enable_load_extension(True)
        self.conn.execute('SELECT load_extension("mod_spatialite")')
        if not self.is_spatial():
            self.conn.execute('SELECT InitSpatialMetaData(1);')

    def is_spatial(self) -> bool:
        """
        Helper function for determining if the currently open database is
        a Spatial database (i. e. has the Spatial Reference metadata tables
        in there).
        """
        try:
            cur = self.conn.execute('SELECT * FROM spatial_ref_sys LIMIT 1;')
            ret = cur.fetchall()
            if ret:
                return True
            return False
        except sqlite3.OperationalError:
            return False

    def __enter__(self) -> sqlite3.Connection:
        return self.conn

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.conn.close()

def snake_case(string):
    return '_'.join(
        re.sub(r"(\s|-|_)+"," ",
        re.sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
        lambda mo: ' ' + mo.group(0).lower(), string)).split()
    )

#PFAS = (
#    'avon-and-somerset', 'bedfordshire', 'btp', 'cambridgeshire',
#    'cheshire', 'city-of-london', 'cleveland', 'cumbria',
#    'derbyshire', 'devon-and-cornwall', 'dorset', 'durham',
#    'dyfed-powys', 'essex', 'gloucestershire', 'gwent',
#    'hampshire', 'hertfordshire', 'kent', 'lancashire',
#    'leicestershire', 'lincolnshire', 'merseyside', 'metropolitan',
#    'norfolk', 'northamptonshire', 'northumbria', 'north-wales',
#    'north-yorkshire', 'nottinghamshire', 'south-wales', 'south-yorkshire',
#    'staffordshire', 'suffolk', 'surrey', 'sussex', 'thames-valley',
#    'warwickshire', 'west-mercia', 'west-midlands', 'west-yorkshire',
#    'wiltshire'
#)
PFAS = ('metropolitan',)

PERIODS = (
    '2024-10', '2024-09', '2024-08', '2024-07', '2024-06',
    '2024-05', '2024-04'
)

SOURCES = ('outcomes', 'stop-and-search', 'street')

sql = {
    'outcomes': {
        'STRUCT': '''
            CREATE TABLE IF NOT EXISTS {force}_outcomes (
                crime_id text,
                month text,
                reported_by text,
                falls_within text,
                location text,
                lsoa_code text,
                lsoa_name text,
                outcome_type text
            );
            SELECT AddGeometryColumn('{force}_outcomes', 'geom', 4326, 'POINT', 'XY', 0);
            SELECT CreateSpatialIndex('{force}_outcomes', 'geom');
        ''',
        'INSERT': '''
            INSERT INTO {force}_outcomes (
                crime_id,
                month,
                reported_by,
                falls_within,
                location,
                lsoa_code,
                lsoa_name,
                outcome_type,
                geom
            ) values (
                :crime_id,
                :month,
                :reported_by,
                :falls_within,
                :location,
                :lsoa_code,
                :lsoa_name,
                :outcome_type,
                MakePoint(CAST(:longitude as real), CAST(:latitude as real), 4326)
            );
        '''
    },
    'stop-and-search': {
        'STRUCT': '''
            CREATE TABLE IF NOT EXISTS {force}_stop_search (
            type text,
            date text,
            part_of_a_policing_operation bool,
            policing_operation text,
            gender text,
            age_range text,
            self_defined_ethnicity text,
            officer_defined_ethnicity text,
            legislation text,
            object_of_search,
            outcome text,
            outcome_linked_to_object_of_search bool
        );
        SELECT AddGeometryColumn('{force}_stop_search', 'geom', 4326, 'POINT', 'XY', 0);
        SELECT CreateSpatialIndex('{force}_stop_search', 'geom');

        ''',
        'INSERT': '''
            INSERT INTO {force}_stop_search (
            type,
            date,
            part_of_a_policing_operation,
            policing_operation,
            gender,
            age_range,
            self_defined_ethnicity,
            officer_defined_ethnicity,
            legislation,
            object_of_search,
            outcome,
            outcome_linked_to_object_of_search,
            geom
        ) values (
            :type,
            :date,
            :part_of_a_policing_operation,
            :policing_operation,
            :gender,
            :age_range,
            :self_defined_ethnicity,
            :officer_defined_ethnicity,
            :legislation,
            :object_of_search,
            :outcome,
            :outcome_linked_to_object_of_search,
            MakePoint(CAST(:longitude as real), CAST(:latitude as real), 4326)
        );
        '''
    },
    'street': {
        'STRUCT': '''
            CREATE TABLE IF NOT EXISTS {force}_street (
                crime_id text,
                month text,
                reported_by text,
                falls_within text,
                location text
                falls_within text,
                lsoa_code text,
                lsoa_name text,
                crime_type text,
                last_outcome_category text,
                context text
            );
            SELECT AddGeometryColumn('{force}_street', 'geom', 4326, 'POINT');
            SELECT CreateSpatialIndex('{force}_street', 'geom');
        ''',
        'INSERT': '''
            INSERT INTO {force}_street (
                crime_id,
                month,
                reported_by,
                falls_within,
                location,
                falls_within,
                lsoa_code,
                lsoa_name,
                crime_type,
                last_outcome_category,
                context,
                geom
            ) VALUES (
                :crime_id,
                :month,
                :reported_by,
                :falls_within,
                :location,
                :falls_within,
                :lsoa_code,
                :lsoa_name,
                :crime_type,
                :last_outcome_category,
                :context,
                MakePoint(CAST(:longitude as real), CAST(:latitude as real), 4326)
            );
        '''
    }
}

    
def extract_files():
    if not os.path.isdir('build/crime-data/'):
        with ZipFile('./downloads/2024-10.zip') as z:
            z.extractall('build/crime-data/')
        logging.info('Crime data extracted to build/crime-data')
    else:
        logging.info('Crime data already extracted, skipped')

def create_tables(database):
    with SpatialiteConnection(database) as db:
        for force in [snake_case(force) for force in PFAS]:
            for source in SOURCES:
                db.executescript(sql[source]['STRUCT'].format(force=force))
                db.commit()

def load_data(database):
    for period in PERIODS:
        for force in [snake_case(force) for force in PFAS]:
            for source in SOURCES:
                location = f'./build/crime-data/{period}/{period}-{force}-{source}.csv'
                if os.path.exists(location):
                    logging.info(f'Loading {source} for {force} in {period}...')
                    with open(location) as data:
                        dict_row = csv.DictReader(data)
                        to_db = [{snake_case(key): value for key, value in row.items()} for row in dict_row]
                        with SpatialiteConnection(database, debug=False) as db:
                            db.executemany(sql[source]['INSERT'].format(force=force), to_db)
                            db.commit()
                else:
                    logging.warning(f'No {source} present for {force} in {period}. Skipped.')

def main(database):
    extract_files()
    create_tables(database)
    load_data(database)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    database = sys.argv[1]
    main(database)