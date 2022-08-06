# from requests import session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session


engine = create_engine("postgresql+psycopg2://mjhdlarrexrnfw:4bf4b97db8dc5d954e0ff32edd4266a9f9ab58fe16a334b404cc29a81d6a4889@ec2-3-223-242-224.compute-1.amazonaws.com:5432/dfg5ri88apl2s3", future=True)
session_factory = sessionmaker(bind=engine,autoflush=False)
session: Session = scoped_session(session_factory)()