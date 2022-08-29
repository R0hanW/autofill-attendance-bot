from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_login import UserMixin

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key = True)
    firstName = Column(String(250), nullable = False)
    lastName = Column(String(250), nullable = False)
    fullName = Column(String(250))
    email = Column(String(250), nullable = False, unique = True)
    password = Column(String(250), nullable = False)
    attendance = Column(Integer)
    historyPeriod = Column(String(250))
    historyAttendance = Column(Integer)
    englishPeriod = Column(String(250))
    englishAttendance = Column(Integer)
    physicsPeriod = Column(String(250))
    physicsAttendance = Column(Integer)
    TOKPeriod = Column(String(250))
    TOKAttendance = Column(Integer)

    @property
    def serialize(self):
        return{
            'id':self.id,
            'firstName':self.firstName,
            'lastName':self.lastName,
            'fullName':self.fullName,
            'email':self.email,
            'password':self.password,
            'historyPeriod':self.historyPeriod,
            'englishPeriod':self.englishPeriod,
            'TOKPeriod':self.TOKPeriod,
        }
engine = create_engine('sqlite:///autofill.db')
Base.metadata.create_all(engine)
