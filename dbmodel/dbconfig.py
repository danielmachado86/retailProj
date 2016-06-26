from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

engine = create_engine('postgresql+psycopg2://danielmc86:Freqm0d+@localhost:5432/retailProj')
# engine = create_engine('sqlite:////home/danielmc86/Dropbox/Programacion/Python/retailProj/dbmodel.test.db')
Base.metadata.bind = engine
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))
s = session()
Base.query = session.query_property()

