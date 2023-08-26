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

create_vw_raw = '''
create or replace view test_db.raw.vw_raw_hostels as
with base as (
	select 
		*,
		row_number () over (partition by id order by created_at desc) as rb
	from 
		test_db.raw.hostels 
),
hostel_filter as(
    select
        id,
        name,
        cast(rating as float) as rating,
        cast(review as int) as review,
        distance,
        dorm_prices,
        private_prices,
        created_at,
        updated_at
    from 
        base
    where 
        rb = 1
)
select
    *
from
    hostel_filter
'''

with engine.connect() as connection:
    try:
        trans = connection.begin()

        connection.execute(text(create_vw_raw))

        trans.commit()
        print("View created successfully.")
    except Exception as e:
        trans.rollback()
        print("Error:", str(e))
