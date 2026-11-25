from typing import List as ListType, Optional
from app.domain.Interfaces.tag_repository import ITagRepository
from datetime import datetime
from sqlalchemy.orm import Session
from app.domain.entities.tag import Tag
from app.domain.schemas.tag import TagCreate , TagUpdate , TagReponse
from .base import BaseRepository

class TagRepository(BaseRepository[Tag], ITagRepository):
    def __init__(self, db: Session):
        super().__init__(db, Tag)

    def get_by_id(self,tag_id:int) -> Optional[Tag]:
        return self.db.query(Tag).filter(Tag.id == tag_id).first()
    
    def get_by_name(self, name: str, user_id: Optional[int] = None) -> Optional[Tag]:
        return self.db.query(Tag).filter(Tag.name == name, Tag.user_id == user_id).first()
    
    def get_all(self, user_id: Optional[int] = None) -> ListType[Tag]:
        query = self.db.query(Tag)
        if user_id is not None:
            query = query.filter(Tag.user_id == user_id)
        return query.all()
    
    def create_tag(self, tag_data: TagCreate, user_id: Optional[int] = None) -> Tag:
        tag = Tag(name=tag_data.name, color=tag_data.color, user_id=user_id)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag
    
    def update_tag(self, tag_id: int, tag_data: TagUpdate) -> Optional[Tag]:
        tag = self.get_by_id(tag_id)
        if tag:
            update_data = tag_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(tag, key, value)
            self.db.commit()
            self.db.refresh(tag)
        return tag
    
    def delete_tag(self, tag_id: int) -> bool:
        tag = self.get_by_id(tag_id)
        if tag:
            self.db.delete(tag)
            self.db.commit()
            return True
        return False
    
    def add_tag_to_card(self, tag_id: int, card_id: int) -> bool:
        from app.domain.entities.card import Card
        tag = self.get_by_id(tag_id)
        card = self.db.query(Card).filter(Card.id == card_id).first()
        if tag and card:
            if card not in tag.cards:
                tag.cards.append(card)
            self.db.commit()
            return True
        return False