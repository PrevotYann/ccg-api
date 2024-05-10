from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cardset, CardYuGiOh, CardPokemon


router = APIRouter(prefix="/cardsets")


@router.get("/", tags=["cardsets"])
def get_all_cardsets(db: Session = Depends(get_db)):
    return db.query(Cardset).all()


@router.get("/{cardset_id}", tags=["cardsets"])
def get_cardset_by_id(cardset_id: int, db: Session = Depends(get_db)):
    return db.query(Cardset).filter(Cardset.id == cardset_id).one_or_none()


@router.get("/pokemon", tags=["cardsets"])
def get_pokemon_cardsets(db: Session = Depends(get_db)):
    return db.query(Cardset).filter(Cardset.gameId == 2).all()


@router.get("/pokemon/{language}", tags=["cardsets"])
def get_pokemon_cardset_by_language(language: str, db: Session = Depends(get_db)):
    return (
        db.query(Cardset)
        .filter(Cardset.language == language, Cardset.gameId == 2)
        .all()
    )


@router.get("/yugioh", tags=["cardsets"])
def get_yugioh_cardsets(db: Session = Depends(get_db)):
    return db.query(Cardset).filter(Cardset.gameId == 1).all()


@router.get("/yugioh/{language}", tags=["cardsets"])
def get_yugioh_cardsets_by_language(language: str, db: Session = Depends(get_db)):
    return (
        db.query(Cardset)
        .filter(Cardset.language == language, Cardset.gameId == 1)
        .all()
    )


@router.get("/yugioh/{id}/cards", tags=["cardsets"])
def get_yugioh_cards_per_cardset_id(id: int, db: Session = Depends(get_db)):
    return db.query(CardYuGiOh).filter(CardYuGiOh.cardsetId == id).all()


@router.get("/pokemon/{id}/cards", tags=["cardsets"])
def get_pokemon_cards_per_cardset_id(id: int, db: Session = Depends(get_db)):
    return db.query(CardPokemon).filter(CardPokemon.cardset_id == id).all()
