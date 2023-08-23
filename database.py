import os
import psycopg2
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db_params = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT")
}


# Directory containing the JSON files
json_dir = "data"

# Schema and table names
schema_name = "raw"
table_name = "hostels"

# Queries
create_schema_query = f"CREATE SCHEMA IF NOT EXISTS {schema_name}"
create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
        id SERIAL PRIMARY KEY,
        name TEXT,
        rating TEXT,
        review TEXT,
        distance TEXT,
        link TEXT,
        dorm_prices TEXT,
        private_prices TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
"""
insert_query = f"""
    INSERT INTO {schema_name}.{table_name} (
        name, rating, review, distance, link, dorm_prices, private_prices, created_at, updated_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

def get_json(file_path):
    with open(file_path, "r") as json_file:
        lines = json_file.readlines()
    return lines

def write_table(connection, json_data):
    with connection.cursor() as cursor:
        for line in json_data:
            try:
                json_obj = json.loads(line)
                prices = json_obj['prices']
                dorm_prices = prices.get('dorms from', None)
                private_prices = prices.get('privates from', None)

                dorm_price = dorm_prices[0] if dorm_prices else None
                private_price = private_prices[0] if private_prices else None

                cursor.execute(insert_query, (
                    json_obj.get('name', None),
                    json_obj.get('rating', None),
                    json_obj.get('review', None),
                    json_obj.get('distance', None),
                    json_obj.get('link', None),
                    dorm_price,
                    private_price,
                    json_obj.get('created_at', None),
                    json_obj.get('updated_at', None)
                ))
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                continue

    connection.commit()

def load_json_content_into_db(directory, connection):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            json_data = get_json(file_path)
            write_table(connection, json_data)

def main():
    try:
        connection = psycopg2.connect(**db_params)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(create_schema_query)
                cursor.execute(create_table_query)
        load_json_content_into_db(json_dir, connection)
    except psycopg2.Error as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
