# from requests import session
from sqlalchemy import create_engine, false
from sqlalchemy.orm import sessionmaker, scoped_session, Session

# engine = create_engine("postgres://uopeepkchsqghl:9b5493488ea191ebdcdd3f513fdc3e8cb79c670ca8b8682ddb27b1815a3121ee@ec2-44-206-197-71.compute-1.amazonaws.com:5432/dev3aqeufilcc3", future=True)
engine = create_engine("postgresql+psycopg2://uopeepkchsqghl:9b5493488ea191ebdcdd3f513fdc3e8cb79c670ca8b8682ddb27b1815a3121ee@ec2-44-206-197-71.compute-1.amazonaws.com:5432/dev3aqeufilcc3", future=True)
session_factory = sessionmaker(bind=engine,autoflush=False)
session: Session = scoped_session(session_factory)()
# session_factory=session()
# conn=engine.connect()
# session_factory=session(bind=conn)