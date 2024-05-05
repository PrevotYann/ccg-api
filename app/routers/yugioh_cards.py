from fastapi import APIRouter, Depends
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cardset, CardYuGiOh

import re

router = APIRouter(prefix="/cards/yugioh")


def normalize_text(text):
    """Normalize text by removing punctuation and lowering the case."""
    text = re.sub(r'[^\w\s]', '', text) 
    return text.lower()



@router.get("/search", tags=["cards"])
def get_yugioh_card_from_query(query: str, db: Session = Depends(get_db)):
    # Normalize the query by removing special characters and lowering the case
    normalized_query = normalize_text(query)

    # Split the normalized query into parts to check for potential set numbers
    parts = normalized_query.split()
    name_query = " ".join(parts[:-1]) if len(parts) > 1 else normalized_query
    set_number_query = parts[-1] if len(parts) > 1 else None

    # Define a SQL expression for cleaning database fields
    clean_name = func.replace(func.replace(func.replace(CardYuGiOh.name, ',', ''), '.', ''), '-', '')
    clean_set_number = func.replace(func.replace(func.replace(CardYuGiOh.set_number, ',', ''), '.', ''), '-', '')

    # Build the query based on the presence of name and set number
    if set_number_query:
        search_results = db.query(CardYuGiOh).filter(
            or_(
                and_(
                    func.lower(clean_name).like(f"%{name_query}%"),
                    func.lower(clean_set_number).like(f"%{set_number_query}%")
                ),
                func.lower(clean_name).like(f"%{normalized_query}%")
            )
        ).all()
    else:
        search_results = db.query(CardYuGiOh).filter(
            func.lower(clean_name).like(f"%{normalized_query}%")
        ).all()

    return search_results


@router.get("/id/{card_id}",
            tags=["cards"]
)
def get_yugioh_card_from_id(card_id: int, db: Session = Depends(get_db)):
    return (
        db.query(CardYuGiOh)
        .filter(CardYuGiOh.id == card_id)
        .all()
    )


@router.get("/set_number/{set_number}",
            tags=["cards"]
)
def get_yugioh_card_from_set_number(set_number: str, db: Session = Depends(get_db)):
    return (
        db.query(CardYuGiOh)
        .filter(CardYuGiOh.set_number == set_number)
        .all()
    )


@router.get("/cardset/{cardset_id}",
            tags=["cards"]
)
def get_yugioh_cards_from_cardset_id(cardset_id: int, db: Session = Depends(get_db)):
    return (
        db.query(CardYuGiOh)
        .join(Cardset, CardYuGiOh.cardsetId == Cardset.id)
        .filter(Cardset.id == cardset_id)
        .all()
    )


@router.get("/cardset/prefix/{cardset_prefix}",
            tags=["cards"]
)
def get_yugioh_cards_from_cardset_prefix(cardset_prefix: str, db: Session = Depends(get_db)):
    return (
        db.query(CardYuGiOh)
        .join(Cardset, CardYuGiOh.cardsetId == Cardset.id)
        .filter(Cardset.prefix == cardset_prefix)
        .all()
    )


@router.get("/cardset/prefix/{cardset_prefix}/language/{language_code}",
            tags=["cards"]
)
def get_yugioh_cards_from_cardset_prefix_and_language(cardset_prefix: str, language_code: str, db: Session = Depends(get_db)):
    return (
        db.query(CardYuGiOh)
        .join(Cardset, CardYuGiOh.cardsetId == Cardset.id)
        .filter(
            Cardset.prefix == cardset_prefix,
            Cardset.language == language_code
        )
        .all()
    )
