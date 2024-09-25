from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table, Enum  # Import necessary SQLAlchemy classes and functions
from sqlalchemy.ext.declarative import declarative_base  # Import declarative_base for creating model classes
from sqlalchemy.orm import sessionmaker, relationship  # Import sessionmaker for creating sessions and relationship for defining relationships
from config.config import Config  # Import configuration settings
import enum  # Import enum for defining enumerations
from werkzeug.security import generate_password_hash, check_password_hash  # Import functions for password hashing

# Create the database engine
engine = create_engine(Config.DATABASE_URL)  # Create a SQLAlchemy engine using the database URL from config

# Create a declarative base class
Base = declarative_base()  # Create a base class for model definitions

# Define the session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Define a session factory for interacting with the database

# Example of a many-to-many relationship table for grouping targets
target_groups = Table('target_groups', Base.metadata,
    Column('target_id', Integer, ForeignKey('targets.id'), primary_key=True),  # Define target_id as a primary key referencing targets
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)  # Define group_id as a primary key referencing groups
)

# Define an Enum for user roles
class UserRole(enum.Enum):
    ADMIN = "admin"  # User role for administrators
    USER = "user"    # User role for standard users

# Define the User model
class User(Base):
    __tablename__ = 'users'  # Define the name of the table in the database

    id = Column(Integer, primary_key=True, index=True)  # Define the primary key
    username = Column(String, nullable=False, unique=True, index=True)  # Define a unique username column
    email = Column(String, nullable=False, unique=True, index=True)  # Define a unique email column
    hashed_password = Column(String, nullable=False)  # Define a column for storing hashed passwords
    role = Column(Enum(UserRole), nullable=False)  # Restrict role to an enumeration of 'admin' or 'user'
    comment = Column(String)  # Optional comment column

    # Method to set password
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)  # Hash the password and store it

    # Method to check password
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)  # Check if the provided password matches the hashed password

# Define the Target model
class Target(Base):
    __tablename__ = 'targets'  # Define the name of the table in the database

    id = Column(Integer, primary_key=True, index=True)  # Define the primary key
    name = Column(String, nullable=False)  # Define a column for the target name
    ip_address = Column(String, nullable=False)  # Define a column for the target IP address
    group_id = Column(Integer, ForeignKey('groups.id'))  # Define a foreign key relationship to the groups table
    group = relationship("Group", back_populates="targets")  # Set up the relationship to the Group model

# Define the Group model
class Group(Base):
    __tablename__ = 'groups'  # Define the name of the table in the database

    id = Column(Integer, primary_key=True, index=True)  # Define the primary key
    name = Column(String, nullable=False, unique=True)  # Define a unique column for the group name
    targets = relationship("Target", back_populates="group")  # Set up the relationship to the Target model

# Initialize the database
def init_db():
    Base.metadata.create_all(bind=engine)  # Create all tables in the database based on the defined models

# Dependency to get DB session
def get_db():
    db = SessionLocal()  # Create a new database session
    try:
        yield db  # Yield the session for use in requests
    finally:
        db.close()  # Ensure the session is closed after use
