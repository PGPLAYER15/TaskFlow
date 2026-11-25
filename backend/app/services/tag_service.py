from typing import List as ListType, Optional   
from app.domain.Interfaces.tag_repository import ITagRepository
from app.domain.entities.tag import Tag
from app.domain.schemas.tag import TagCreate, TagUpdate

class TagService:
    def __init__(self,tag_repo:ITagRepository):
        self.tag_repo = tag_repo
    
    def get_tags(self, user_id: Optional[int] = None) -> ListType[Tag]:
        return self.tag_repo.get_all(user_id)
    
    def get_tag(self, tag_id: int, user_id: Optional[int] = None) -> Optional[Tag]:
        tag = self.tag_repo.get_by_id(tag_id)
        # Un tag ajeno se trata como inexistente (no revelamos que existe)
        if tag and user_id is not None and tag.user_id != user_id:
            return None
        return tag

    def create_tag(self, tag_data: TagCreate, user_id: Optional[int] = None) -> Tag:
        return self.tag_repo.create_tag(tag_data, user_id)
    
    def update_tag(self, tag_id: int, tag_data: TagUpdate) -> Optional[Tag]:
        return self.tag_repo.update_tag(tag_id, tag_data)
    
    def delete_tag(self, tag_id: int) -> bool:
        return self.tag_repo.delete_tag(tag_id)
    
    def add_tag_to_card(self, tag_id: int, card_id: int) -> bool:
        return self.tag_repo.add_tag_to_card(tag_id, card_id)