import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import cast, Integer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CardPokemon, CardYuGiOh, Item, ItemPrice, User, UserItem, get_class_by_tablename
from app.routers.ebay import ebay_search_query_france_prices, ebay_search_query_us_prices
from app.schema import Item as ItemSchema, UserItem as UserItemSchema, UserItemInput


router = APIRouter(prefix="/items")


conditions = {
    "poor": "PO",
    "played": "PL",
    "light_played": "LP",
    "good": "GD",
    "excellent": "EX",
    "near_mint": "NM",
    "mint": "MINT"
}


#################################
#################################
########### ENDPOINTS ###########
#################################
#################################
@router.post(
    "/table/{table_name}/item/{specific_id}", response_model=ItemSchema, tags=["items"]
)
def create_new_item(table_name: str, specific_id: int, db: Session = Depends(get_db)):
    existing_item = get_item_from_source_table_and_id(
        origin_table_name=table_name, origin_id=specific_id, db=db
    )

    if existing_item is None:
        new_item = create_item(
            origin_table_name=table_name, origin_id=specific_id, db=db
        )

        db.commit()
        return new_item
    else:
        raise HTTPException(status_code=402, detail="Item already exists")


@router.get(
    "/table/{table_name}/item/{specific_id}", response_model=ItemSchema, tags=["items"]
)
def get_existing_item(table_name: str, specific_id: int, db: Session = Depends(get_db)):
    existing_item = get_item_from_source_table_and_id(
        origin_table_name=table_name, origin_id=specific_id, db=db
    )

    if existing_item is not None:
        return existing_item
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.post("/table/{table_name}/item/{specific_id}/user/{username}", tags=["items"])
def add_item_to_user_collection(
    table_name: str,
    specific_id: int,
    username: str,
    item_input: UserItemInput,
    db: Session = Depends(get_db),
):
    existing_item = get_item_from_source_table_and_id(
        origin_table_name=table_name, origin_id=specific_id, db=db
    )

    if existing_item is not None:
        item_to_add = existing_item
    else:
        item_to_add = create_item(
            origin_table_name=table_name, origin_id=specific_id, db=db
        )

    # Check if item exist with this condition, and first edition check for the current item and user
    existing_user_item = existing_link_user_item_condition_edition(
        item_id=item_to_add.id,
        username=username,
        condition=item_input.condition,
        is_first_edition=item_input.is_first_edition,
        db=db,
    )

    if existing_user_item is None:
        link_item_to_user_collection(
            item_id=item_to_add.id, username=username, item_input=item_input, db=db
        )
    else:
        existing_user_item.quantity += item_input.quantity

    db.commit()


@router.post("/table/{table_name}/item/{specific_id}/condition/{condition}/first/{first_edition}/ebay/price", tags=["items"])
def ebay_price_for_item(
    table_name: str,
    specific_id: int,
    condition: str,
    first_edition: bool,
    db: Session = Depends(get_db),
):
    existing_item = get_item_from_source_table_and_id(
        origin_table_name=table_name, origin_id=specific_id, db=db
    )

    if existing_item is not None:
        item_to_look_for_price = existing_item
    else:
        item_to_look_for_price = create_item(
            origin_table_name=table_name, origin_id=specific_id, db=db
        )
    
    # defining prices
    if table_name == "cards_yugioh":
        card = db.query(CardYuGiOh).filter(CardYuGiOh.id == specific_id).one()

        set_number = card.set_number if card.set_number not in ["", None] else card.name if "<ruby>" not in card.name else None
        if set_number is None:
            return
        language = card.language
        if language == "fr":
            prices = ebay_search_query_france_prices(
                query=set_number + " " + conditions[condition] + (" 1st" if first_edition else "")
            )
            if prices is None:
                prices = ebay_search_query_france_prices(
                    query=set_number + " " + conditions[condition]
                )
                if prices is None:
                    prices = ebay_search_query_france_prices(
                    query=set_number + (" 1st" if first_edition else "")
                )
                    if prices is None:
                        prices = ebay_search_query_france_prices(
                            query=set_number
                        )
            currency = "EURO"
        else:
            prices = ebay_search_query_us_prices(
                query=set_number + " " + conditions[condition] + (" 1st" if first_edition else "")
            )
            if prices is None:
                prices = ebay_search_query_us_prices(
                    query=set_number + " " + conditions[condition]
                )
                if prices is None:
                    prices = ebay_search_query_us_prices(
                    query=set_number + (" 1st" if first_edition else "")
                )
                    if prices is None:
                        prices = ebay_search_query_us_prices(
                            query=set_number
                        )
            currency = "DOLLAR"
    
    elif table_name == "cards_pokemon":
        card = db.query(CardPokemon).filter(CardYuGiOh.id == specific_id).one()

        name = card.name
        card_number = card.local_id
        language = card.language

        if language == "fr":
            prices = ebay_search_query_france_prices(
                query=name + " " + card_number + " " + conditions[condition] + " 1st" if first_edition else ""
            )
            if prices is None:
                prices = ebay_search_query_france_prices(
                    query=name + " " + card_number + " " + conditions[condition]
                )
                if prices is None:
                    prices = ebay_search_query_france_prices(
                        query=name + " 1st" if first_edition else ""
                    )
                    if prices is None:
                        prices = ebay_search_query_france_prices(
                            query=name + " " + card_number
                        )
            currency = "EURO"
        else:
            prices = ebay_search_query_us_prices(
                query=name + " " + card_number + conditions[condition] + " 1st" if first_edition else ""
            )
            if prices is None:
                prices = ebay_search_query_us_prices(
                    query=name + " " + card_number + " " + conditions[condition]
                )
                if prices is None:
                    prices = ebay_search_query_us_prices(
                        query=name + " 1st" if first_edition else ""
                    )
                    if prices is None:
                        prices = ebay_search_query_us_prices(
                            query=name + " " + card_number
                        )
            currency = "DOLLAR"

    if prices is None:
        return None
    now = datetime.datetime.now()

    # Check if item exist with this condition, and first edition check for the current item and user
    item_price = (
        db.query(ItemPrice)
        .filter(
            ItemPrice.item_id == item_to_look_for_price.id,
            ItemPrice.condition == condition
        )
        .one_or_none()
    )
    
    if item_price is None:
        item_price = ItemPrice(
            item_id = item_to_look_for_price.id,
            condition = condition,
            ebay_currency = currency,
            ebay_last_update = now,
            ebay_highest = prices["high"],
            ebay_lowest = prices["low"],
            ebay_mean = prices["mean"],
            ebay_median = prices["median"],
        )
        db.add(item_price)
    else:
        item_price.ebay_last_update = now
        item_price.ebay_highest = prices["high"]
        item_price.ebay_lowest = prices["low"]
        item_price.ebay_mean = prices["mean"]
        item_price.ebay_median = prices["median"]
        db.flush()
    
    db.commit()

    return prices


@router.delete("/{user_item_id}/user/{username}/delete")
def delete_user_item_for_user_by_id(
    user_item_id: int, username: str, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_items = db.query(UserItem).filter(
        UserItem.id == user_item_id,
        UserItem.user_id == user.id
    ).all()

    for ui in user_items:
        db.delete(ui)
    db.commit()


@router.put("/{user_item_id}/user/{username}")
def edit_user_item_for_user_by_id(
    user_item_id: int,
    username: str,
    item_input: UserItemInput,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_item_to_edit = (
        db.query(UserItem)
        .filter(UserItem.id == user_item_id, UserItem.user_id == user.id)
        .one()
    )

    user_item_to_edit.quantity = item_input.quantity
    user_item_to_edit.condition = item_input.condition
    user_item_to_edit.extras = item_input.extras
    user_item_to_edit.is_first_edition = item_input.is_first_edition

    db.commit()


@router.get("/user/{username}", tags=["items"])
def query_items_with_dynamic_join(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Retrieve items and their corresponding user_items entries
    user_items = (
        db.query(Item, UserItem)
        .select_from(UserItem)
        .join(Item, Item.id == UserItem.item_id)
        .filter(UserItem.user_id == user.id)
        .all()
    )

    results = []

    for item, user_item in user_items:
        table_class = get_class_by_tablename(item.source_table)
        if table_class is not None:
            source_item = (
                db.query(table_class).filter(table_class.id == item.specific_id).first()
            )
            if source_item:
                # Create a dictionary that combines item, user_item, and source_item details
                item_details = {
                    "user_item_id": user_item.id,
                    "item_id": item.id,
                    "source_table": item.source_table,
                    "specific_id": item.specific_id,
                    "source_item_details": source_item,  # Assuming this is serializable; otherwise, customize serialization
                    "user_item_details": {
                        "quantity": user_item.quantity,
                        "condition": user_item.condition,
                        "added_date": user_item.added_date.isoformat(),
                        "extras": user_item.extras,
                        "is_first_edition": user_item.is_first_edition,
                    },
                }
                results.append(item_details)

    return results


#################################
#################################
########### FUNCTIONS ###########
#################################
#################################
def create_item(
    origin_table_name: str, origin_id: int, db: Session = Depends(get_db)
) -> Item:
    new_item = Item(source_table=origin_table_name, specific_id=origin_id)
    db.add(new_item)
    db.flush()
    return new_item


def get_item_from_source_table_and_id(
    origin_table_name: str, origin_id: int, db: Session = Depends(get_db)
) -> Item:
    existing_item = (
        db.query(Item)
        .filter(Item.source_table == origin_table_name, Item.specific_id == origin_id)
        .one_or_none()
    )

    return existing_item


def link_item_to_user_collection(
    item_id: int,
    username: str,
    item_input: UserItemInput,
    db: Session = Depends(get_db),
) -> UserItemSchema:
    user = db.query(User).filter(User.username == username).one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.datetime.now()

    new_user_item = UserItem(
        user_id=user.id,
        item_id=item_id,
        quantity=item_input.quantity,
        added_date=now,
        condition=item_input.condition,
        extras=item_input.extras,
        is_first_edition=item_input.is_first_edition,
    )
    db.add(new_user_item)
    db.flush()

    return new_user_item


def existing_link_user_item_condition_edition(
    item_id: int,
    username: str,
    condition: str,
    is_first_edition: bool,
    db: Session = Depends(get_db),
) -> UserItem:
    user = db.query(User).filter(User.username == username).one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    existing_user_item = (
        db.query(UserItem)
        .filter(
            UserItem.item_id == item_id,
            UserItem.user_id == user.id,
            UserItem.condition == condition,
            UserItem.is_first_edition == is_first_edition,
        )
        .one_or_none()
    )

    if existing_user_item is not None:
        return existing_user_item
