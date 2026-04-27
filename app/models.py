from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Numeric, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    accounts = relationship('Account', back_populates='user')
    payments = relationship('Payment', back_populates='user')

class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    balance = Column(Numeric(precision=18, scale=2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='accounts')
    payments = relationship('Payment', back_populates='account')

    __table_args__ = (
        Index('idx_account_user_id', 'user_id'),
    )

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(255), unique=True, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship('Account', back_populates='payments')
    user = relationship('User', back_populates='payments')

    __table_args__ = (
        Index('idx_payment_account_id', 'account_id'),
        Index('idx_payment_user_id', 'user_id'),
    )