from typing import List as ListType, Optional
from datetime import datetime
from app.infrastructure.repositories.card_repository import CardRepository
from app.domain.entities.card import Card
from app.domain.schemas.card import CardUpdate, CardCreate
from app.domain.Interfaces.tag_repository import ITagRepository

class CardService:
    def __init__(self,TagRepo:ITagRepository,cardRepo:CardRepository):
        self.tag_repo = TagRepo
        self.card_repo = cardRepo

    def get_cards_by_list(self, list_id: int) -> ListType[Card]:
        return self.card_repo.get_by_list(list_id)

    def get_card(self, card_id: int) -> Card | None:
        return self.card_repo.get_by_id(card_id)

    def create_card(self, title: str, list_id: int, description: str = None, tags: list[str] | None = None, user_id: int | None = None) -> Card:
        card_data = CardCreate(title=title, list_id=list_id, description=description, tags=tags or [])
        return self.card_repo.create_card(card_data, user_id)

    def update_card(self, card_id: int, card_data: CardUpdate) -> Card | None:
        return self.card_repo.update_card(card_id, card_data)

    def delete_card(self, card_id: int) -> bool:
        return self.card_repo.delete(card_id)

    def move_card(self, card_id: int, new_list_id: int, position: int | None = None) -> Card | None:
        return self.card_repo.move_card(card_id, new_list_id, position)

    def filter_by_tag(self, tag_name: str, user_id: Optional[int] = None) -> ListType[Card]:
        return self.card_repo.filter_by_tag(tag_name, user_id)

    def add_tag(self,card_id: int,tag_id:int)-> bool:
        card = self.get_by_id(card_id)

        if not card:
            return False
    def search_cards(self, q: Optional[str], tags_ids: list[int], due_before: Optional[datetime], due_after: Optional[datetime], user_id: Optional[int] = None) -> ListType[Card]:
        return self.card_repo.search_cards(q, tags_ids, due_before, due_after, user_id)