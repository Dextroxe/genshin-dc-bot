from sqlalchemy import BIGINT, Column, Boolean, ForeignKey
from datamodels.genshin_user import GenshinUser

from datamodels import Base


class UidMapping(Base):
    __tablename__ = "uidmapping"

    uid = Column(BIGINT, primary_key=True)
    mihoyo_id = Column(
        BIGINT, ForeignKey(GenshinUser.mihoyo_id, ondelete="CASCADE"), nullable=False
    )
    main = Column(Boolean, nullable=False, default=False)
