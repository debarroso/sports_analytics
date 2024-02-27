import psycopg2
import pathlib
import logging
import glob


class BaseDatabaseHandler:
    def __init__(
            self,
            datalake_path,
            db_config={}
        ):
        self.datalake_path = datalake_path
        self.db_config = db_config

    def get_logger(self, name):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(name)
    
    def get_files(self, glob_string="*"):
        glob_path = self.datalake_path / glob_string
        return glob.glob(str(glob_path))

    def get_postgres_connection(self):
        return psycopg2.connect(**self.db_config)
