import html
from random import randint
from fastapi import APIRouter, Depends
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CardFFTCG

import re

router = APIRouter(prefix="/cards/fftcg")


def normalize_text(text: str):
    """Remove punctuation and other special characters, replace them with nothing, and decode HTML entities."""
    # Decode HTML entities (e.g., &middot; becomes ·)
    text = html.unescape(text)
    
    # Remove any invisible characters (e.g., zero-width spaces, etc.)
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)  # Removes zero-width space and similar
    
    # Remove punctuation and special characters, replace with nothing, and convert to lower case
    text = re.sub(r'[^\w\s]', '', text).lower()
    
    return text.strip()  # Also strip any surrounding whitespace


@router.get("/search", tags=["cards"])
def get_fftcg_card_from_query(query: str, db: Session = Depends(get_db)):
    # Normalize the input query by removing special characters
    normalized_query = normalize_text(query)

    # Broader search when no local_id is found, treat the whole query as a potential name
    search_results = db.query(CardFFTCG).filter(
        CardFFTCG.name.ilike(f"%{normalized_query}%")
    ).all()

    return search_results


@router.get("/id/{card_id}",
            tags=["cards"]
)
def get_yugioh_card_from_id(card_id: int, db: Session = Depends(get_db)):
    return (
        db.query(CardFFTCG)
        .filter(CardFFTCG.id == card_id)
        .all()
    )


@router.get("/set_prefix/{set_prefix}",
            tags=["cards"]
)
def get_fftcg_card_from_code(set_prefix: str, db: Session = Depends(get_db)):
    return (
        db.query(CardFFTCG)
        .filter(CardFFTCG.code.contains(set_prefix.split("-")[0]))
        .all()
    )


@router.get("/set_prefix/{set_prefix}/language/{language}",
            tags=["cards"]
)
def get_fftcg_card_from_set_prefix_and_language(set_prefix: str, language: str, db: Session = Depends(get_db)):
    return (
        db.query(CardFFTCG)
        .filter(
            CardFFTCG.code.contains(set_prefix.split("-")[0]),
            CardFFTCG.lang == language
        )
        .all()
    )


@router.get("/name/{name}/language/{language}",
            tags=["cards"]
)
def get_fftcg_card_from_set_number(name: str, language: str, db: Session = Depends(get_db)):
    return (
        db.query(CardFFTCG)
        .filter(
            func.lower(CardFFTCG.name).contains(func.lower(name)),
            CardFFTCG.lang == language
        )
        .all()
    )


@router.get("/random/{limit}", tags=["cards"])
def get_random_fftcg_cards(limit: int, db: Session = Depends(get_db)):
    # Get the maximum ID in the table
    max_id = db.query(func.max(CardFFTCG.id)).scalar()

    # Generate random IDs within the range
    random_ids = [randint(1, max_id) for _ in range(limit)]

    # Fetch cards with these random IDs
    random_cards = db.query(CardFFTCG).filter(CardFFTCG.id.in_(random_ids)).all()

    return random_cards


@router.get("/latest/{limit}", tags=["cards"])
def get_latest_fftcg_cards(limit: int, db: Session = Depends(get_db)):
    return (
        db.query(CardFFTCG)
        .order_by(desc(CardFFTCG.id))
        .limit(limit)
        .all()
    )
