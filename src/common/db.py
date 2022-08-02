# from requests import session
from sqlalchemy import create_engine, false
from sqlalchemy.orm import sessionmaker, scoped_session, Session

# engine = create_engine("postgres://xrpjbkhuzhrvgm:c799a517c97d0ecfc50d83d405072f5a2db99827c8af27b8dd10e44385b40ea5@ec2-34-193-44-192.compute-1.amazonaws.com:5432/dauoqi06pgtrpi", future=True)
engine = create_engine("postgresql+psycopg2://xrpjbkhuzhrvgm:c799a517c97d0ecfc50d83d405072f5a2db99827c8af27b8dd10e44385b40ea5@ec2-34-193-44-192.compute-1.amazonaws.com:5432/dauoqi06pgtrpi", future=True)
session_factory = sessionmaker(bind=engine,autoflush=False)
session: Session = scoped_session(session_factory)()
# session_factory=session()
# conn=engine.connect()
# session_factory=session(bind=conn)