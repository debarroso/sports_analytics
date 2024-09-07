import psycopg2
import platform
import glob
import csv


class BaseDatabaseHandler:
    def __init__(self, dbname, schema, table_name, datalake_path, db_config=None):
        if db_config is None:
            db_config = {
                "dbname": dbname,
                "host": "localhost",
                "port": 5432,
            }

        self.db_config = db_config
        self.schema = schema
        self.table_name = table_name
        self.delimiter = "\\" if platform.system() == "Windows" else "/"
        self.datalake_path = datalake_path
        self.csv_list = self.get_csv_files()

    def get_csv_files(self):
        csv_list = glob.glob(f"{self.datalake_path}{self.delimiter}*")
        if len(csv_list) == 0:
            print("No CSV files found.")
            exit()
        return csv_list

    def connect_to_database(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            exit()

    def process_csv_files(self):
        conn = self.connect_to_database()
        cursor = conn.cursor()

        for csv_file in self.csv_list:
            self.process_single_file(cursor, csv_file)
            conn.commit()

        cursor.close()
        conn.close()

    def process_single_file(self, cursor, csv_file):
        # Open the CSV file
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            columns = [f'"{column}"' for column in reader.fieldnames]  # type: ignore
            f.seek(0)
            cursor.copy_expert(
                f"COPY {self.schema}.{self.table_name} ({', '.join(columns)}) FROM STDIN WITH CSV HEADER",
                f,
            )
        print(f"CSV for {self.table_name} has been inserted into the database.")
