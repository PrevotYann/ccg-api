from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cardset, CardYuGiOh

router = APIRouter(prefix="/cards/yugioh")

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
def get_yugioh_card_from_id(set_number: str, db: Session = Depends(get_db)):
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
def get_yugioh_cards_from_cardset_id(cardset_id: int, db: Session = Depends(get_db)):
    return (
        db.query(CardYuGiOh)
        .join(Cardset, CardYuGiOh.cardsetId == Cardset.id)
        .filter(Cardset.id == cardset_id)
        .all()
    )


@router.get("/cardset/prefix/{cardset_prefix}/language/{language_code}",
            tags=["cards"]
)
def get_yugioh_cards_from_cardset_id(cardset_prefix: str, language_code: str, db: Session = Depends(get_db)):
    return (
        db.query(CardYuGiOh)
        .join(Cardset, CardYuGiOh.cardsetId == Cardset.id)
        .filter(
            Cardset.prefix == cardset_prefix,
            Cardset.language == language_code
        )
        .all()
    )
