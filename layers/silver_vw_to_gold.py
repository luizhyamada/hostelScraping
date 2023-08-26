import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

db_params = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT")
}
db_url = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
engine = create_engine(db_url)

create_gold_table = '''
create table if not exists test_db.gold.hostels (
    id serial primary key,
    name text,
    rating float,
    review int,
    distance float,
    dorm_prices int,
    private_prices int,
    created_at timestamp,
    updated_at timestamp
)
'''

insert_into_gold = '''
insert into gold.hostels (
    id,
    name,
    rating,
    review,
    distance,
    dorm_prices,
    private_prices,
    created_at,
    updated_at
)
select
    id,
    name,
    rating,
    review,
    distance,
    dorm_prices,
    private_prices,
    now() as created_at,
    now() as updated_at
from 
    test_db.silver.vw_silver_hostels
'''

with engine.connect() as connection:
    try:
        trans = connection.begin()

        connection.execute(text(create_gold_table))

        trans.commit()
        print("Table created successfully.")
    except Exception as e:
        trans.rollback()
        print("Error:", str(e))

with engine.connect() as connection:
    try:
        trans = connection.begin()

        connection.execute(text(insert_into_gold))

        trans.commit()
        print("View created successfully.")
    except Exception as e:
        trans.rollback()
        print("Error:", str(e))
