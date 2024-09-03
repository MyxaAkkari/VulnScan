from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config.config import Config

# Create the database engine
engine = create_engine(Config.DATABASE_URL)

# Create a declarative base class
Base = declarative_base()

# Define the session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Example of a many-to-many relationship table for grouping targets
target_groups = Table('target_groups', Base.metadata,
    Column('target_id', Integer, ForeignKey('targets.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)

# Define the Target model
class Target(Base):
    __tablename__ = 'targets'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group", back_populates="targets")

# Define the Group model
class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    targets = relationship("Target", back_populates="group")

# Initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
