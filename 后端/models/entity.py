from sqlalchemy import Column, Integer, String, Text
from db.DB import Base


class Paients(Base):
    __tablename__ = 'paients'

    name = Column(String(20))
    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String(5))
    age = Column(Integer)
    time = Column(String(50))
    reportId = Column(String(50))
    leftPhoto = Column(Text)
    rightPhoto = Column(Text)
    outCome = Column(String(50))


class User(Base):
    __tablename__ = 'users'

    name = Column(String(20))
    accountId = Column(Integer, primary_key=True, index=True)
    gender = Column(String(5))
    age = Column(Integer)
    department = Column(String(50))
    email = Column(String(50))
    phone = Column(String(50))
    password = Column(String(50))
    photo = Column(Text)


class Test(Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    age = Column(Integer)
