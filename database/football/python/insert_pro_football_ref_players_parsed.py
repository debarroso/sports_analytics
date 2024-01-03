import psycopg2
import platform
import glob
import pathlib
import csv

# Database connection parameters
db_config = {
    "dbname": "nfl_statistics",
    "host": "localhost",  # or your database host
    "port": 5432  # default port for PostgreSQL
}
delimiter = "\\" if platform.system() == "Windows" else "/"
schema = "dimensions"
datalake_path = str(pathlib.Path(__file__).parent.parent.parent.resolve()).replace("database", "datalake")
csv_list = glob.glob(f"{datalake_path}{delimiter}parsed{delimiter}football{delimiter}pro_football_ref_players{delimiter}*")

if len(csv_list) == 0:
    exit()

# Connect to the database
conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

# Process each CSV file
for csv_file in csv_list:
    # Extract table name from the file name
    table_name = "players"

    # Open the CSV file
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        columns = [f'"{column}"' for column in reader.fieldnames]
        f.seek(0)
        cursor.copy_expert(f"COPY {schema}.{table_name} ({', '.join(columns)}) FROM STDIN WITH CSV HEADER", f)

    conn.commit()
    print(f"CSV for {table_name} has been inserted into the database.")

cursor.close()
conn.close()
