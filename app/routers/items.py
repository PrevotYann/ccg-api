import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Item, User, UserItem
from app.schema import Item as ItemSchema, UserItem as UserItemSchema, UserItemInput


router = APIRouter(prefix="/items")


#################################
#################################
########### ENDPOINTS ###########
#################################
#################################
@router.post(
    "/{table_name}/{specific_id}",
    response_model=ItemSchema,
    tags=["items"]
)
def create_new_item(
    table_name: str,
    specific_id: int,
    db: Session = Depends(get_db)
):
    existing_item = get_item_from_source_table_and_id(
        origin_table_name=table_name,
        origin_id=specific_id,
        db=db
    )
    
    if existing_item is None:
        new_item = create_item(
            origin_table_name=table_name,
            origin_id=specific_id,
            db=db
        )
    
        db.commit()
        return new_item
    else:
        raise HTTPException(status_code=402, detail="Item already exists")


@router.get(
    "/{table_name}/{specific_id}",
    response_model=ItemSchema,
    tags=["items"]
)
def get_existing_item(
    table_name: str,
    specific_id: int,
    db: Session = Depends(get_db)
):
    existing_item = get_item_from_source_table_and_id(
        origin_table_name=table_name,
        origin_id=specific_id,
        db=db
    )
    
    if existing_item is not None:
        return existing_item
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.post(
    "/table/{table_name}/item/{specific_id}/user/{username}",
    tags=["items"]
)
def add_item_to_user_collection(
    table_name: str,
    specific_id: int,
    username: str,
    item_input: UserItemInput,
    db: Session = Depends(get_db)
):
    print(table_name)
    print(specific_id)
    print(username)
    print(item_input)
    existing_item = get_item_from_source_table_and_id(
        origin_table_name=table_name,
        origin_id=specific_id,
        db=db
    )
    
    if existing_item is not None:
        item_to_add = existing_item
    else:
        item_to_add = create_item(
            origin_table_name=table_name,
            origin_id=specific_id,
            db=db
        )
    
    link_item_to_user_collection(
        item_id = item_to_add.id,
        username = username,
        item_input = item_input,
        db = db
    )
    
    db.commit()
    

#################################
#################################
########### FUNCTIONS ###########
#################################
#################################
def create_item(
    origin_table_name: str,
    origin_id: int,
    db: Session = Depends(get_db)
) -> Item:
    new_item = Item(
        source_table = origin_table_name,
        specific_id = origin_id
    )
    db.add(new_item)
    db.flush()
    return new_item


def get_item_from_source_table_and_id(
    origin_table_name: str,
    origin_id: int,
    db: Session = Depends(get_db)
) -> Item:
    existing_item = (
        db.query(Item)
        .filter(
            Item.source_table == origin_table_name,
            Item.specific_id == origin_id
        )
        .one_or_none()
    )
    
    return existing_item


def link_item_to_user_collection(
    item_id: int,
    username: str,
    item_input: UserItemInput,
    db: Session = Depends(get_db)
) -> UserItemSchema:
    user = (
        db.query(User)
        .filter(User.username == username)
        .one_or_none()
    )
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    now = datetime.datetime.now()
    
    new_user_item = UserItem(
        user_id = user.id,
        item_id = item_id,
        quantity = item_input.quantity,
        added_date = now,
        condition = item_input.condition,
        extras = item_input.extras,
        is_first_edition = item_input.is_first_edition
    )
    db.add(new_user_item)
    db.flush()
    
    return new_user_item