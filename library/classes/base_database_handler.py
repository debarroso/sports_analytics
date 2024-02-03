import psycopg2
import pathlib
import logging
import glob
import csv


class BaseDatabaseHandler:
    def __init__(
            self,
            datalake_path = pathlib.Path(__file__).resolve().parents[2],
            db_config={},
            schema="",
            table_name=""
        ):
        self.db_config = db_config
        self.schema = schema
        self.table_name = table_name
        self.logger = self.get_logger()

        self.datalake_path = datalake_path

    def get_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(self.crawler_name)
    
    def get_files(self, glob_string="*"):
        glob_path = self.datalake_path / "unprocessed" / glob_string
        return glob.glob(str(glob_path))

    def get_postgres_connection(self):
        return psycopg2.connect(**self.db_config)
    
    def copy_csv_to_postgres(self, csv_file, cursor):
        with open(csv_file, "r") as fp:
            reader = csv.DictReader(fp)
            columns = [f"'{column}'" for column in reader.fieldnames]
            fp.seek(0)
            copy_query = f"COPY {self.schema}.{self.table_name} ({', '.join(columns)}) FROM STDIN WITH CSV HEADER"
            self.logger.info(f"Executing: {copy_query}")
            cursor.copy_expert(copy_query, fp)
