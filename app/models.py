from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# class MediaType(Base):
#     __tablename__ = "mediatype"

#     id: int = Column(Integer, primary_key=True, index=True)
#     name : str = Column(String(100), nullable = False)
