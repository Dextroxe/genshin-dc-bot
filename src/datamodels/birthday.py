from sqlalchemy import BIGINT, Column, Text, DateTime

from datamodels import Base


class Birthday(Base):
    __tablename__ = "bday"

    discord_id = Column(BIGINT, primary_key=True)
    guild_id = Column(BIGINT, primary_key=True)
    month = Column(BIGINT, nullable=False)
    day = Column(BIGINT, nullable=False)
    timezone = Column(Text, nullable=False)
    reminded_at = Column(DateTime)  # UTC timezone
