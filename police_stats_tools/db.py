"""
Database connections.
"""

import os
import sqlite3
from typing import Optional

class SpatialiteConnection():
    """
    Helper class for connecting to Spatialite datastores,
    for use in a with statement.
    """
    def __init__(self, location: Optional[str] = None) -> None:
        if location:
            self.conn = sqlite3.connect(os.path.join(location))
        else:
            self.conn = sqlite3.connect(':memory:')
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

class SQLiteConnection():
    """
    Helper class for connecting to SQLite datastores,
    for use in a with statement.
    """
    def __init__(self, location: Optional[str] = None) -> None:
        if location:
            self.conn = sqlite3.connect(os.path.join(location))
        else:
            self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = lambda cursor, result: \
            dict(zip([column[0] for column in cursor.description], result))

    def __enter__(self) -> sqlite3.Connection:
        return self.conn

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.conn.close()
