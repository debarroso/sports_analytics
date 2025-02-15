import psycopg2
import pathlib
import logging
import glob
import csv


class BaseDatabaseHandler:
    def __init__(self, handler_path, db_name, schema, db_config=None):
        if db_config is None:
            db_config = {
                "dbname": db_name,
                "host": "localhost",
                "port": 5432,
            }

        self.handler_path = handler_path
        self.handler_name = handler_path.parts[-1]

        self.db_name = db_name
        self.schema = schema
        self.db_config = db_config
        self.db_connection = self.connect_to_database()
        self.base_path = pathlib.Path(__file__).parents[2].resolve()
        self.datalake_parsed_path = (
            self.base_path
            / "datalake"
            / "parsed"
            / self.handler_path.parts[-2]
            / self.handler_name
        )

        self.table_name = None
        self.logger = self.get_logger()

    def get_logger(self):
        file_path = self.base_path / "logs" / f"{self.handler_name}_pipeline.log"
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()

        logging.basicConfig(
            filename=str(file_path),
            filemode="a",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        return logging.getLogger(self.handler_name)

    def connect_to_database(self):
        return psycopg2.connect(**self.db_config)

    def get_parsed_csv_files(self):
        return glob.glob(str(self.datalake_parsed_path / "*"))

    def upload_csv_files(self, csv_list):
        cursor = self.db_connection.cursor()
        for csv_file in csv_list:
            self.upload_single_csv_file(cursor, csv_file)
            self.db_connection.commit()

        cursor.close()
        self.db_connection.close()

    def upload_single_csv_file(self, cursor, csv_file):
        # if not explicitly set, infer from file name
        if self.table_name is None:
            self.table_name = pathlib.Path(csv_file).stem

        with open(csv_file) as f:
            reader = csv.DictReader(f)
            columns = [f'"{column}"' for column in reader.fieldnames]  # type: ignore
            f.seek(0)
            cursor.copy_expert(
                f"COPY {self.schema}.{self.table_name} ({', '.join(columns)}) FROM STDIN WITH CSV HEADER",
                f,
            )

        self.logger.info(
            f"CSV for {self.table_name} has been inserted into the database."
        )

    def upload_parsed_data(self, csv_list=None):
        if csv_list is None:
            csv_list = self.get_parsed_csv_files()

        if len(csv_list) == 0:
            self.logger.info("No new files found in datalake")
            return

        self.upload_csv_files(csv_list)

        # making it here assumes successful upload, delete these files now
        for csv_file in csv_list:
            pathlib.Path(csv_file).unlink()
