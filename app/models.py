from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://prya2699:65EH-8MbE-qVu$@plume.o2switch.net:3306/prya2699_ccgapi"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(250), unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String(250))

class Cardset(Base):
    __tablename__ = "cardsets"

    id = Column(Integer, primary_key=True, index=True)
    gameId = Column(Integer)
    name = Column(String(250))
    prefix = Column(String(250), nullable=True)
    language = Column(String(250))
    official_card_count_pokemon = Column(Integer, nullable=True)
    total_card_count_pokemon = Column(Integer, nullable=True)
    symbol_pokemon = Column(String(250), nullable=True)
    logo_pokemon = Column(String(250), nullable=True)