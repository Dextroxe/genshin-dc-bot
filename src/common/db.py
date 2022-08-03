# from requests import session
from sqlalchemy import create_engine, false
from sqlalchemy.orm import sessionmaker, scoped_session, Session

engine = create_engine("postgresql+psycopg2://rpthtjcezowuij:831fa4691b06b6787436122ec3ac33cf9d46d6b90af2abbc0dca990286e031e5@ec2-18-214-35-70.compute-1.amazonaws.com:5432/d2pr84p8u51i2g", future=True)
session_factory = sessionmaker(bind=engine,autoflush=False)
session: Session = scoped_session(session_factory)()
# session_factory=session()
# conn=engine.connect()
# session_factory=session(bind=conn)