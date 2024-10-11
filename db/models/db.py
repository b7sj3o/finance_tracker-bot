from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model that includes common columns.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True)


class User(BaseModel):
    """
    Represents a user in the system.

    Attributes:
        username (str): The user's username, must be unique.
        email (str): The user's email address, must be unique.

    Relationships:
        finances (list of Finance): List of financial records associated with the user.
    """

    __tablename__ = "users"

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    finances = relationship("Finance", order_by="Finance.id", back_populates="user")


class Finance(BaseModel):
    """
    Represents a financial record associated with a user.

    Attributes:
        user_id (int): The ID of the user this record belongs to.
        balance (float): The balance amount.
        currency (str): The currency of the balance.

    Relationships:
        user (User): The user associated with this financial record.
    """

    __tablename__ = "finances"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Float, nullable=False)
    currency = Column(String, nullable=False)

    user = relationship("User", back_populates="finances")


engine = create_engine("sqlite:///finance.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
