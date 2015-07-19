from migrate.versioning import api
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO
#from models import Base as db
from app import db
import os.path

#engine = create_engine(SQLALCHEMY_DATABASE_URI)
#db.metadata.bind = engine

#db.metadata.drop_all(engine)
#db.metadata.create_all(engine)

db.create_all()

if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
  api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
  api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
  api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, \
      api.version(SQLALCHEMY_MIGRATE_REPO))



#DBSession = sessionmaker(bind = engine)
#session = DBSession()

