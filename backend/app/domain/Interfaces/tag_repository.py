from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.tag import Tag
from app.domain.schemas.tag import TagCreate, TagUpdate

class ITagRepository(ABC):
    @abstractmethod
    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        pass

    @abstractmethod
    def get_by_name(self, name: str, user_id: Optional[int] = None) -> Optional[Tag]:
        pass

    @abstractmethod
    def get_all(self, user_id: Optional[int] = None) -> List[Tag]:
        pass

    @abstractmethod
    def create_tag(self, tag_data: TagCreate, user_id: Optional[int] = None) -> Tag:
        pass
        
    @abstractmethod
    def update_tag(self, tag_id: int, tag_data: TagUpdate) -> Optional[Tag]:
        pass

    @abstractmethod
    def delete_tag(self, tag_id: int) -> bool:
        pass
    
    @abstractmethod
    def add_tag_to_card(self, tag_id: int, card_id: int) -> bool:
        pass
        