from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cardset, CardPokemon


router = APIRouter(prefix="/cards/pokemon")



@router.get("/id/{card_id}",
            tags=["cards"]
)
def get_yugioh_card_from_id(card_id: int, db: Session = Depends(get_db)):
    return (
        db.query(CardPokemon)
        .filter(CardPokemon.id == card_id)
        .all()
    )


@router.get("/set_prefix/{set_prefix}",
            tags=["cards"]
)
def get_pokemon_card_from_set_prefix(set_prefix: str, db: Session = Depends(get_db)):
    return (
        db.query(CardPokemon)
        .filter(CardPokemon.tcgdex_id.contains(set_prefix.split("-")[0]))
        .all()
    )


@router.get("/set_prefix/{set_prefix}/language/{language}",
            tags=["cards"]
)
def get_pokemon_card_from_set_prefix_and_language(set_prefix: str, language: str, db: Session = Depends(get_db)):
    return (
        db.query(CardPokemon)
        .filter(
            CardPokemon.tcgdex_id.contains(set_prefix.split("-")[0]),
            CardPokemon.language == language
        )
        .all()
    )


@router.get("/name/{name}/language/{language}",
            tags=["cards"]
)
def get_pokemon_card_from_set_number(name: str, language: str, db: Session = Depends(get_db)):
    return (
        db.query(CardPokemon)
        .filter(
            func.lower(CardPokemon.name).contains(func.lower(name)),
            CardPokemon.language == language
        )
        .all()
    )

