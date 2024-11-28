import os
import police_stats_tools.db as db

def test_SpatialiteConnection_in_memory():
    # GIVEN an in-memory Spatialite database
    with db.SpatialiteConnection() as in_memory:
        # WHEN initialised
        cur = in_memory.execute('SELECT ref_sys_name from spatial_ref_sys limit 1;')
        ret = cur.fetchall()
        # THEN there should be spatial_ref_sys metadata tables
        assert ret == [{'ref_sys_name': 'Undefined - Cartesian'}]

def test_SpatialiteConnection_in_file():
    # GIVEN an in-file Spatialite database
    with db.SpatialiteConnection('/tmp/test.spatialite') as in_file:
        # WHEN initialised
        cur = in_file.execute('SELECT ref_sys_name from spatial_ref_sys limit 1;')
        ret = cur.fetchall()
        # THEN there should be spatial_ref_sys metadata tables
        assert ret == [{'ref_sys_name': 'Undefined - Cartesian'}]

    # THEN the database is persisted to storage afterwards
    assert os.path.isfile('/tmp/test.spatialite')
    os.remove('/tmp/test.spatialite')

def test_SQLiteConnection_in_memory():
    # GIVEN an in-memory SQLite database
    with db.SQLiteConnection() as in_memory:
        # WHEN selecting
        cur = in_memory.execute('select 1 as "test";')
        ret = cur.fetchall()
        # THEN the result should be put into a List of Dicts
        assert ret == [{'test': 1}]

def test_SQLiteConnection_in_file():
    # Given an in-file SQLite database
    with db.SQLiteConnection('/tmp/test.sqlite3') as in_file:
        # When selecting
        cur = in_file.execute('select 2 as "test";')
        ret = cur.fetchall()
        # THEN the result should be put into a List of Dicts
        assert ret == [{'test': 2}]

    # THEN the database is persisted to storage afterwards
    assert os.path.isfile('/tmp/test.sqlite3')
    os.remove('/tmp/test.sqlite3')
