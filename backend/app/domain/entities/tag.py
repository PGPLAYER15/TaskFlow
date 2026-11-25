from app.infrastructure.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, String, ForeignKey, UniqueConstraint


card_tag = Table(
    "card_tag",
    Base.metadata,
    Column("card_id", Integer, ForeignKey("cards.id") , primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id") , primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_tag_user_name"),)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    cards = relationship("Card", secondary=card_tag, back_populates="tags")

    