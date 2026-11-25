from fastapi import APIRouter,Depends,HTTPException,status
from app.core.dependencies import get_tag_service, get_card_service, get_list_service, get_board_service, get_current_user
from app.services.card_service import CardService
from app.services.list_service import ListService
from app.services.board_service import BoardService
from app.domain.schemas.tag import TagCreate,TagUpdate,TagReponse
from app.services.tag_service import TagService

# Cada etiqueta pertenece a un usuario (nombre único por usuario).
router = APIRouter(dependencies=[Depends(get_current_user)])

@router.get("/tags", response_model=list[TagReponse])
def get_tags(tag_service: TagService = Depends(get_tag_service), current_user=Depends(get_current_user)):
    return tag_service.get_tags(current_user.id)

@router.get("/tags/{tag_id}", response_model=TagReponse)
def get_tag(tag_id: int, tag_service: TagService = Depends(get_tag_service), current_user=Depends(get_current_user)):
    tag = tag_service.get_tag(tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag

@router.post("/tags", response_model=TagReponse)
def create_tag(tag_data: TagCreate, tag_service: TagService = Depends(get_tag_service), current_user=Depends(get_current_user)):
    if tag_service.tag_repo.get_by_name(tag_data.name, current_user.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists")
    return tag_service.create_tag(tag_data, current_user.id)

@router.put("/tags/{tag_id}", response_model=TagReponse)
def update_tag(tag_id: int, tag_data: TagUpdate, tag_service: TagService = Depends(get_tag_service), current_user=Depends(get_current_user)):
    tag = tag_service.get_tag(tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag_service.update_tag(tag_id, tag_data)

@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, tag_service: TagService = Depends(get_tag_service), current_user=Depends(get_current_user)):
    if not tag_service.get_tag(tag_id, current_user.id) or not tag_service.delete_tag(tag_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return

@router.post("/tags/{tag_id}/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_tag_to_card(
    tag_id: int,
    card_id: int,
    tag_service: TagService = Depends(get_tag_service),
    card_service: CardService = Depends(get_card_service),
    list_service: ListService = Depends(get_list_service),
    board_service: BoardService = Depends(get_board_service),
    current_user=Depends(get_current_user),
):
    if not tag_service.get_tag(tag_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    card = card_service.get_card(card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    card_list = list_service.get_list(card.list_id)
    if not card_list or not board_service.is_owner(card_list.board_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this card")
    if not tag_service.add_tag_to_card(tag_id, card_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return
    