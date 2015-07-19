#from sqlalchemy import Column, ForeignKey, Integer, Text, String, Float
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import relationship
from app import db

#Base = declarative_base()

class Subscriber(db.Model):
  __tablename__ = 'subscriber'
  id = db.Column(db.Integer, primary_key = True)
  phone = db.Column(db.String(length = 10))
  # expects a 10-digit phone number in string text
  # require validation before creation of object
  time = db.Column(db.Integer)
  # expects a 4-digit phone number between 0000 and 2359
  # require validation before creation of object
  num_events = db.Column(db.Integer)
  neighborhood = db.Column(db.Integer, db.ForeignKey('neighborhood.id'))


class Neighborhood(db.Model):
  __tablename__ = 'neighborhood'
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String)
  latitude = db.Column(db.Float)
  longitude = db.Column(db.Float)
  zipcode = db.Column(db.Integer)
  


  
