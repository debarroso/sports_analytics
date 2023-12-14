import pandas as pd
from sqlalchemy import create_engine, text
import platform, glob, pathlib, json

# Database connection parameters
db_config = {
    "dbname": "nfl_statistics",
    "host": "localhost",  # or your database host
    "port": 5432  # default port for PostgreSQL
}
file_delimiter = "\\" if platform.system() == "Windows" else "/"
datalake_path = str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("database", "datalake")
csv_list = glob.glob(f"{datalake_path}{file_delimiter}parsed{file_delimiter}football{file_delimiter}pro_football_ref{file_delimiter}*")

if len(csv_list) == 0:
    exit()

engine = create_engine(f"postgresql://{db_config['host']}:{db_config['port']}/{db_config['dbname']}")

for csv_file in csv_list:
    df = pd.read_csv(csv_file)
    table_name = csv_file.split(file_delimiter)[-1].replace(".csv", "")
    df.to_sql(f"{table_name}", engine, schema="pro_football_ref_parsed", if_exists='append', index=False)
