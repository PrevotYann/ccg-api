from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://prya2699:65EH-8MbE-qVu$@plume.o2switch.net:3306/prya2699_ccgapi"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
