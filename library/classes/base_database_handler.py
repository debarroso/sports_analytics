import psycopg2
import pathlib
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

        self.datalake_path = datalake_path

    def get_postgres_connection(self):
        return psycopg2.connect(**self.db_config)
    
    def copy_csv_to_postgres(self, csv_file, cursor):
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            columns = [f"'{column}'" for column in reader.fieldnames]
            f.seek(0)
            cursor.copy_expert(f"COPY {self.schema}.{self.table_name} ({', '.join(columns)}) FROM STDIN WITH CSV HEADER", f)
