from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://collecthor_clearlybee:36ce5163b5b3b7d82ec578b256477eed7f01289e@wq1.h.filess.io:3305/collecthor_clearlybee?charset=utf8"
#DATABASE_URL = "mysql+pymysql://root:%40Danganronpa47@91.199.227.99:10965/ccgapi?charset=utf8"

engine = create_engine(
    DATABASE_URL,
    connect_args={"connect_timeout": 10},
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
