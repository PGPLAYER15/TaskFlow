from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_list_service, get_card_service, require_board_owner, require_list_in_board, get_board_service, get_current_user
from app.domain.schemas.list import ListCreate, ListResponse, ListUpdateCards
from app.services.list_service import ListService
from app.services.card_service import CardService
from app.services.board_service import BoardService

router = APIRouter(dependencies=[Depends(require_board_owner)])


@router.post("/", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
def create_list(
    board_id: int,
    list_data: ListCreate,
    list_service: ListService = Depends(get_list_service),
):
    if list_data.board_id != board_id:
        raise HTTPException(status_code=400, detail="board_id no coincide con la ruta")
    return list_service.create_list(list_data.title, list_data.board_id)


@router.get("/", response_model=list[ListResponse])
def get_lists_by_board(board_id: int, list_service: ListService = Depends(get_list_service)):
    return list_service.get_lists_by_board(board_id)


@router.get("/{list_id}", response_model=ListResponse, dependencies=[Depends(require_list_in_board)])
def get_list_by_id(list_id: int, list_service: ListService = Depends(get_list_service)):
    db_list = list_service.get_list(list_id)
    if not db_list:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    return db_list


@router.put("/{list_id}", response_model=ListResponse, dependencies=[Depends(require_list_in_board)])
def update_list(list_id: int, list_data: ListCreate, list_service: ListService = Depends(get_list_service)):
    db_list = list_service.update_list(list_id, list_data.title)
    if not db_list:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    return db_list


@router.put("/{list_id}/cards", response_model=ListResponse, dependencies=[Depends(require_list_in_board)])
def update_list_cards(list_id: int, cards_data: ListUpdateCards, list_service: ListService = Depends(get_list_service), card_service: CardService = Depends(get_card_service), board_service: BoardService = Depends(get_board_service), current_user=Depends(get_current_user)):
    db_list = list_service.get_list(list_id)
    if not db_list:
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    
    # Validar TODAS las tarjetas antes de mover ninguna
    for card_id in cards_data.cards:
        card = card_service.get_card(card_id)
        source = list_service.get_list(card.list_id) if card else None
        if not card or not source:
            raise HTTPException(status_code=404, detail=f"Tarjeta {card_id} no encontrada")
        if not board_service.is_owner(source.board_id, current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to move this card")

    for position, card_id in enumerate(cards_data.cards):
        card_service.move_card(card_id, list_id, position)
    
    return list_service.get_list(list_id)


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_list_in_board)])
def delete_list(list_id: int, list_service: ListService = Depends(get_list_service)):
    if not list_service.delete_list(list_id):
        raise HTTPException(status_code=404, detail="Lista no encontrada")
    return
