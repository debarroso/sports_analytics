import argparse
import pathlib
import sys
import csv


project_path = pathlib.Path(__file__).resolve().parents[4]
sys.path.append(f"{project_path}/")
from library.classes.base_database_handler import BaseDatabaseHandler


def parse_args():
    parser = argparse.ArgumentParser(
        description="Copies files from a directory to postgres"
    )

    parser.add_argument(
        "--datalake_path", type=str, required=True, help="Path to datalake files"
    )
    parser.add_argument(
        "--dbname", type=str, required=True, help="Name of the database"
    )
    parser.add_argument("--host", type=str, required=True, help="Database host")
    parser.add_argument("--port", type=int, required=True, help="Database port")
    parser.add_argument("--schema", type=str, required=True, help="Database schema")
    parser.add_argument("--table", type=str, required=True, help="Database table")

    args = parser.parse_args()
    return args


class CopyDatalakeFilesToDatabase(BaseDatabaseHandler):

    def __init__(self):
        super().__init__(datalake_path="", db_config={})

    def copy_csv_to_postgres(self, csv_file, cursor):
        with open(csv_file) as fp:
            reader = csv.DictReader(fp)
            columns = [f"'{column}'" for column in reader.fieldnames]
            fp.seek(0)
            query = f"COPY {self.schema}.{self.table_name} ({', '.join(columns)}) FROM STDIN WITH CSV HEADER"
            self.logger.info(f"Executing: {query}")
            cursor.copy_expert(query, fp)


if __name__ == "__main__":
    args = parse_args()
    db_operation = CopyDatalakeFilesToDatabase()
