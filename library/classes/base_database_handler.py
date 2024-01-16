import psycopg2
import pathlib
import glob
import csv


class BaseDatabaseHandler:
    def __init__(
            self,
            db_config={},
            schema=""
        ):
        pass
