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

create_vw_silver = '''
create or replace view test_db.silver.vw_silver_hostels as
with base as (
select
	id,
	name,
	rating,
	review,
    case
        when distance like '%km from city centre' then
            cast(substring(distance from 1 for position('km from city centre' in distance) - 1) as float)
        else
            cast(distance as float)
    end as distance,
    case
        when dorm_prices like 'R$%' then
            cast(substring(dorm_prices from 3) as int)
        else
            cast(dorm_prices as int)
    end as dorm_prices,
	case
        when private_prices like 'R$%' then
            cast(substring(private_prices from 3) as int)
        else
            cast(private_prices as int)
    end as private_prices,
	created_at,
	updated_at
from
	silver.hostels
)
select
    *
from
    base
'''

with engine.connect() as connection:
    try:
        trans = connection.begin()

        connection.execute(text(create_vw_silver))

        trans.commit()
        print("View created successfully.")
    except Exception as e:
        trans.rollback()
        print("Error:", str(e))
