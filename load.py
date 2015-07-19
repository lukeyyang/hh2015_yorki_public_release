from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URI
#from models import Base as db
from app import db, models
import os.path
import csv

#def loadSession():
#  engine = create_engine(SQLALCHEMY_DATABASE_URI)
#  DBSession = sessionmaker(bind = engine)
#  session = DBSession()
#  return session


if __name__ == "__main__":
#  session = loadSession() 

  datapath = os.path.join('app/static/data/', 'ManhattanNeighborhood.csv')
  with open(datapath, 'r') as neighborhoodfile:
    neighborhood_reader = csv.reader(neighborhoodfile)
    for row in neighborhood_reader:
      name = row[0]
      latitude = row[1]
      longitude = row[2]
      zipcode = row[3]
      db.session.add(models.Neighborhood(name = name, \
                                         latitude = latitude, \
                                         longitude = longitude, \
                                         zipcode = zipcode))


  db.session.commit()


