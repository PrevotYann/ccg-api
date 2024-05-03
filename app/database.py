from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


DATABASE = 'mysql+pymysql://prya2699:65EH-8MbE-qVu$@plume.o2switch.net:3306/prya2699_ccgapi'

engine = create_engine(
    DATABASE,
    encoding='utf-8',
    echo=True
)

SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

Base = declarative_base()
Base.query = SessionLocal.query_property()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()