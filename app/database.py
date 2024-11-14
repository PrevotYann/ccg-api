import os
from sqlalchemy import URL, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


database_username = os.environ.get('DATABASE_USERNAME', 'collecthor_clearlybee')
database_password = os.environ.get('DATABASE_PASSWORD', '36ce5163b5b3b7d82ec578b256477eed7f01289e')
database_url = os.environ.get('DATABASE_URL', 'wq1.h.filess.io')
database_name = os.environ.get('DATABASE_NAME', 'collecthor_clearlybee')

print('DB URL:', database_url)
print('DB:', database_name)

url_object = URL.create(
    "mysql+pymysql",
    username=database_username,
    password=database_password,
    host=database_url,
    port=3305,
    database=database_name
)

engine = create_engine(
    url=url_object,
    pool_size=5,           # Set the maximum number of connections in the pool
    max_overflow=10,        # Allow up to this many overflow connections (over pool_size)
    pool_recycle=1800,      # Recycle connections after 30 minutes
    pool_timeout=30,        # Timeout after 30 seconds if a connection cannot be obtained
    pool_pre_ping=True      # Checks connection health before using it
)

engine = create_engine(url_object)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
meta = MetaData()
conn = engine.connect()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
