from sqlalchemy import Integer,Column,DateTime,ForeignKey,Text,Enum,String,Boolean
import enum
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine



engine = create_engine("sqlite:///fastPizza.db")

SessionLocal = sessionmaker(bind=engine,autocommit=False,autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

Base = declarative_base()

"""
def save(self):
    db.add(self)
    db.commit()
"""

class Sizes(enum.Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRA_LARGE = 'extra_large'

class OrderStatus(enum.Enum):
    PENDING = 'pending'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'

class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), primary_key=True)
    email = Column(String(200), unique=True,nullable=False)
    username = Column(String(100),unique=True,nullable=False)
    password = Column(String(100),nullable=False)
    is_staff = Column(Boolean(),default=False)
    is_active = Column(Boolean(),default=False)
    orders = relationship('Order',back_populates="creator")
    profiles = relationship('Profile',back_populates="owner")

    def __repr__(self):
        return f"<User : {self.username}>"


class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(Integer(), primary_key=True)
    othername =Column(String(100))
    firstname = Column(String(100),nullable=False)
    lastname = Column(String(100),nullable=False)
    bio = Column(Text(),nullable=False)
    gender =Column(String(20),nullable=False)
    created_at = Column(DateTime(),default=datetime.utcnow)
    user_id = Column(Integer(), ForeignKey('users.id'))
    owner = relationship("User",back_populates="profiles")
    profileimages = relationship("ProfileImage",back_populates="profile") 
    
    def __repr__(self):
        return f"<Profile : {self.lastname} {self.firstname}>"

class ProfileImage(Base):
    __tablename__ = 'profileimages'
    id = Column(Integer(), primary_key=True)
    name = Column(String(200))
    img =Column(String(70))
    minetype = Column(String(100))
    profile_id = Column(Integer(), ForeignKey('profiles.id'))
    profile =relationship('Profile',back_populates="profileimages")

    def __repr__(self):
        return f"UserImage {self.name}"

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer(), primary_key=True) 
    size = Column(String(200),nullable=False)
    flavour = Column(Text(),nullable=False)
    order_status = Column(Enum(OrderStatus),default=OrderStatus.PENDING)
    quantity = Column(Integer())
    date_created =Column(DateTime(),default=datetime.utcnow)
    user_id = Column(Integer(), ForeignKey('users.id'))
    creator = relationship("User",back_populates="orders")

    def __repr__(self):
        return f"<Order : {self.id}>"


Base.metadata.create_all(bind=engine)




