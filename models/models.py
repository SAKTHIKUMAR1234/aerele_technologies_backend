from models.basemodel import Base
from sqlalchemy import Column,String,Integer,DateTime,Text,func,ForeignKey,Double,Boolean
from sqlalchemy.orm import relationship
from factory import bcrypt
from enum import Enum as pyenum

class RoleEnum(pyenum):
  user = 1
  admin = 2


class User(Base):
    
    __tablename__ = 'user_table'
    
    name = Column(String(50),nullable=False)
    email = Column(String(60),nullable=False,unique=True)
    password = Column(Text,nullable=False)
    role_id = Column(Integer,default=RoleEnum.user.value,nullable=False)
    
    activities = relationship('Activity',uselist=True, back_populates='user')
    
    def __init__(self,name,email,password) -> None:
        self.name = name
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email

class Activity(Base):
    
    __tablename__ = 'user_activity_table'
    
    user_id = Column(Integer,ForeignKey('user_table.id'),nullable=False)
    login_at = Column(DateTime(timezone=True),default=func.now())
    logout_at = Column(DateTime(timezone=True))
    session_id = Column(String(50),nullable=False)
    
    def __init__(self,user):
        self.user = user
    
    user = relationship('User', back_populates='activities')
    
class Product(Base):
  
  __tablename__ = 'product_table'
  
  product_name = Column(String(100),nullable=False)
  price = Column(Double,nullable=False)
  quantity = Column(Integer,default=1)
  location_id = Column(Integer,ForeignKey('location_table.id'),nullable=False)
  is_deleted = Column(Boolean,default=False)
  
  location = relationship('Location',uselist=False,back_populates='products')
  movement = relationship('ProductMovement',uselist=False,back_populates='product')


class Location(Base):
  
  __tablename__ = 'location_table'
  
  location_name = Column(String(100),nullable=False,unique=True)
  
  products = relationship('Product',uselist=True,back_populates='location')
  
  
  
class ProductMovement(Base):
  
  __tablename__ = 'product_movement_table'
  
  product_id = Column(Integer,ForeignKey('product_table.id'),nullable=False)
  from_id = Column(Integer,ForeignKey('location_table.id'),nullable=True,default=None)
  to_id = Column(Integer,ForeignKey('location_table.id'),nullable=True,default=None)
  
  product = relationship("Product", back_populates='movement')
  from_location = relationship("Location", foreign_keys=[from_id])
  to_location = relationship("Location", foreign_keys=[to_id])
  
  