from fastapi import APIRouter, Depends
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cardset, CardYuGiOh


router = APIRouter(prefix="/cards/yugioh")



@router.get("/search", tags=["cards"])
def get_yugioh_card_from_query(query: str, db: Session = Depends(get_db)):
    # Attempt to split the query into name and set_number parts
    parts = query.split()
    name_query = " ".join(parts[:-1])  # all but the last part as name
    set_number_query = parts[-1] if len(parts) > 1 else None  # last part as set_number

    # Filter query building based on the presence of name and set_number parts
    if set_number_query and name_query:
        search_results = db.query(CardYuGiOh).filter(
            or_(
                and_(CardYuGiOh.name.ilike(f"%{name_query}%"), CardYuGiOh.set_number.ilike(f"%{set_number_query}%")),
                CardYuGiOh.name.ilike(f"%{query}%"), 
                CardYuGiOh.set_number.ilike(f"%{query}%")
            )
        ).all()
    else:
        # This block executes if there is no clear distinction into name and set number
        search_results = db.query(CardYuGiOh).filter(
            or_(
                CardYuGiOh.name.ilike(f"%{query}%"), 
                CardYuGiOh.set_number.ilike(f"%{query}%")
            )
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
