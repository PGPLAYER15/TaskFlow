from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.domain.schemas.card import CardCreate, CardResponse, CardUpdate, CardMove
from app.services.card_service import CardService
from app.core.dependencies import get_card_service, get_list_service, get_board_service, get_current_user, require_list_in_board
from app.services.list_service import ListService
from app.services.board_service import BoardService
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError
from datetime import datetime
from typing import Optional

def _ensure_card_in_list(card_service, card_id, list_id):
    card = card_service.get_card(card_id)
    if not card or card.list_id != list_id:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    return card


router = APIRouter(dependencies=[Depends(require_list_in_board)])


@router.post("/create", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(list_id: int, card_data: CardCreate, card_service: CardService = Depends(get_card_service), current_user=Depends(get_current_user)):
    if card_data.list_id != list_id:
        raise HTTPException(status_code=400, detail="list_id no coincide con la ruta")
    try:
        return card_service.create_card(
            title=card_data.title,
            list_id=card_data.list_id,
            description=card_data.description,
            tags=card_data.tags,
            user_id=current_user.id,
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear la tarjeta: {str(e)}"
        )


@router.get("/", response_model=list[CardResponse])
def get_cards_by_list(list_id: int, card_service: CardService = Depends(get_card_service)):
    try:
        return card_service.get_cards_by_list(list_id)
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener las tarjetas: {str(e)}"
        )


@router.get("/filter_by_tag", response_model=list[CardResponse])
def filter_by_tag(tag_name: str, card_service: CardService = Depends(get_card_service), current_user=Depends(get_current_user)):
    try:
        if not tag_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de la etiqueta no puede estar vacío"
            )
        return card_service.filter_by_tag(tag_name, current_user.id)
    except HTTPException:
        raise
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al filtrar tarjetas: {str(e)}"
        )


@router.get("/search", response_model=list[CardResponse])
def search_cards(
    q: Optional[str] = Query(None, description="Buscar tarjeta por nombre"),
    tag_id: Optional[list[int]] = Query(None, description="IDs de etiquetas"),
    due_before: Optional[datetime] = Query(None, description="Vencimiento antes de"),
    due_after: Optional[datetime] = Query(None, description="Vencimiento después de"),
    card_service: CardService = Depends(get_card_service),
    current_user=Depends(get_current_user),
):
    try:
        # Validar que due_before sea posterior a due_after
        if due_before and due_after and due_before < due_after:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha 'due_before' debe ser posterior a 'due_after'"
            )
        return card_service.search_cards(q=q, tags_ids=tag_id, due_before=due_before, due_after=due_after, user_id=current_user.id)
    except HTTPException:
        raise
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al buscar tarjetas: {str(e)}"
        )


@router.get("/{card_id}", response_model=CardResponse)
def get_card_by_id(list_id: int, card_id: int, card_service: CardService = Depends(get_card_service)):
    try:
        card = _ensure_card_in_list(card_service, card_id, list_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarjeta no encontrada"
            )
        return card
    except HTTPException:
        raise
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener la tarjeta: {str(e)}"
        )


@router.put("/{card_id}", response_model=CardResponse)
def update_card(list_id: int, card_id: int, card_data: CardUpdate, card_service: CardService = Depends(get_card_service)):
    try:
        _ensure_card_in_list(card_service, card_id, list_id)
        card = card_service.update_card(
            card_id=card_id,
            card_data=card_data
        )
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarjeta no encontrada"
            )
        return card
    except HTTPException:
        raise
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar la tarjeta: {str(e)}"
        )


@router.put("/{card_id}/move", response_model=CardResponse)
def move_card(
    list_id: int,
    card_id: int,
    move_data: CardMove,
    card_service: CardService = Depends(get_card_service),
    list_service: ListService = Depends(get_list_service),
    board_service: BoardService = Depends(get_board_service),
    current_user=Depends(get_current_user),
):
    card = _ensure_card_in_list(card_service, card_id, list_id)
    source_list = list_service.get_list(card.list_id)
    target_list = list_service.get_list(move_data.list_id)
    if not target_list:
        raise HTTPException(status_code=404, detail="Lista destino no encontrada")
    if not board_service.is_owner(source_list.board_id, current_user.id) or \
            not board_service.is_owner(target_list.board_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to move this card")
    return card_service.move_card(card_id, move_data.list_id, move_data.position)


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(list_id: int, card_id: int, card_service: CardService = Depends(get_card_service)):
    try:
        _ensure_card_in_list(card_service, card_id, list_id)
        if not card_service.delete_card(card_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarjeta no encontrada"
            )
        return
    except HTTPException:
        raise
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar la tarjeta: {str(e)}"
        )

