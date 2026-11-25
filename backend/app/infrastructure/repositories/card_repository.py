from typing import List as ListType, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.domain.schemas.card import CardCreate, CardUpdate
from app.domain.entities.card import Card
from app.domain.entities.tag import Tag
from app.domain.entities.list import List
from app.domain.entities.board import Board
from app.core.exceptions import DatabaseError
from .base import BaseRepository


class CardRepository(BaseRepository[Card]):
    def __init__(self, db: Session):
        super().__init__(db, Card)

    def get_by_list(self, list_id: int) -> ListType[Card]:
        try:
            return self.db.query(Card).filter(Card.list_id == list_id).all()
        except SQLAlchemyError as e:
            raise DatabaseError("Error al obtener tarjetas de la lista", e)

    def create_card(self, card_data: CardCreate, user_id: Optional[int] = None) -> Card:
        try:
            card = Card(
                title=card_data.title, 
                list_id=card_data.list_id, 
                description=card_data.description, 
                due_date=card_data.due_date,
                position=self.db.query(Card).filter(Card.list_id == card_data.list_id).count()
            ) 

            existing_tags = self.db.query(Tag).filter(Tag.name.in_(card_data.tags or []), Tag.user_id == user_id).all()
            
            existing_tag_names = {tag.name for tag in existing_tags}
            new_tags = [
                Tag(name=name, color="#808080", user_id=user_id)
                for name in (card_data.tags or [])
                if name not in existing_tag_names
            ]

            card.tags.extend(existing_tags + new_tags)
            
            self.db.add(card)
            self.db.commit()
            self.db.refresh(card)
            return card
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError("Error al crear la tarjeta", e)

    def update_card(self, card_id: int, card_data: CardUpdate) -> Optional[Card]:
        try:
            card = self.get_by_id(card_id)
            if card:
                update_data = card_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(card, key, value)
                self.db.commit()
                self.db.refresh(card)
            return card
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError("Error al actualizar la tarjeta", e)

    def move_card(self, card_id: int, new_list_id: int, position: Optional[int] = None) -> Optional[Card]:
        try:
            card = self.get_by_id(card_id)
            if card:
                if position is None:
                    position = self.db.query(Card).filter(Card.list_id == new_list_id).count()
                card.list_id = new_list_id
                card.position = position
                self.db.commit()
                self.db.refresh(card)
            return card
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError("Error al mover la tarjeta", e)

    def _owned_by(self, query, user_id: Optional[int]):
        if user_id is None:
            return query
        return query.join(List, Card.list_id == List.id).join(Board, List.board_id == Board.id).filter(Board.user_id == user_id)

    def filter_by_tag(self, tag_name: str, user_id: Optional[int] = None) -> ListType[Card]:
        try:
            query = self._owned_by(self.db.query(Card), user_id)
            return query.filter(Card.tags.any(Tag.name.ilike(tag_name))).all()
        except SQLAlchemyError as e:
            raise DatabaseError("Error al filtrar tarjetas por etiqueta", e)

    def search_cards(self, q: Optional[str], tags_ids: list[int], due_before: Optional[datetime], due_after: Optional[datetime], user_id: Optional[int] = None) -> ListType[Card]:
        try:
            query = self._owned_by(self.db.query(Card), user_id)
            if q:
                query = query.filter(Card.title.ilike(f'%{q}%'))
            if tags_ids:
                query = query.filter(Card.tags.any(Tag.id.in_(tags_ids)))
            if due_before:
                query = query.filter(Card.due_date <= due_before)
            if due_after:
                query = query.filter(Card.due_date >= due_after)
            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError("Error al buscar tarjetas", e)
