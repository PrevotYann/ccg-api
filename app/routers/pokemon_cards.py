from fastapi import APIRouter, Depends
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CardPokemon


router = APIRouter(prefix="/cards/pokemon")



@router.get("/search/{query:path}", tags=["cards"])
def get_pokemon_card_from_query(query: str, db: Session = Depends(get_db)):
    # Split the query using space to examine the potential parts
    parts = query.split()
    
    # Determine if the last part is a local_id by checking if it's numeric or has a numeric component followed by '/'
    if len(parts) > 1 and (parts[-1].isdigit() or (('/' in parts[-1]) and parts[-1].split('/')[0].isdigit())):
        name_query = " ".join(parts[:-1])  # All but the last part as name
        local_id_query = parts[-1].split('/')[0]  # Only take the numeric part before any '/'
    else:
        name_query = query
        local_id_query = None

    # Build the search query based on whether a local_id was detected
    if local_id_query:
        # More specific search when a local_id is present
        search_results = db.query(CardPokemon).filter(
            and_(
                CardPokemon.name.ilike(f"%{name_query}%"),
                CardPokemon.local_id.ilike(f"{local_id_query}%")
            )
        ).all()
    else:
        # Broader search when no local_id is found, treat the whole query as a potential name
        search_results = db.query(CardPokemon).filter(
            CardPokemon.name.ilike(f"%{name_query}%")
        ).all()

    return search_results


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

