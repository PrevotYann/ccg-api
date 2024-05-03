from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://prya2699:65EH-8MbE-qVu$@plume.o2switch.net:3306/prya2699_ccgapi"

engine = create_engine(
    DATABASE_URL,
    connect_args={"connect_timeout": 10},
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
