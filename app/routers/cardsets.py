from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cardset

router = APIRouter(prefix="/cardset")

@router.get("/",
            tags=["cardsets"]
)
def get_cardsets_by_id(db: Session = Depends(get_db)):
    return db.query(Cardset).all()

@router.get("/{cardset_id}",
            tags=["cardsets"]
)
def get_cardset_by_id(cardset_id: int, db: Session = Depends(get_db)):
    return db.query(Cardset).filter(Cardset.id == cardset_id).one_or_none()
