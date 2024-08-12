from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CardPokemon, CardYuGiOh, Cardset, Item, ItemPrice, User, UserItem, get_class_by_tablename
from app.routers.cardmarket import cardmarket_get_from_price
from app.routers.ebay import ebay_search_query_france_prices, ebay_search_query_us_prices, ebay_selling_items, ebay_selling_items_fr, ebay_sold_items, ebay_sold_items_fr
from app.schema import Item as ItemSchema, UserItem as UserItemSchema, UserItemInput, UserItemsInput


router = APIRouter(prefix="/items")


conditions = {
    "poor": "POOR",
    "played": "PLAYED",
    "light_played": "LP",
    "good": "GOOD CONDITION",
    "excellent": "EXCELLENT",
    "near_mint": "NM",
    "mint": "MINT"
}

DOLLAR_TO_EURO = 0.92

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

    extras = item_input.extras if item_input.extras not in ["", "null"] else None

    # Check if item exist with this condition, and first edition check for the current item and user
    existing_user_item = existing_link_user_item_condition_edition(
        item_id=item_to_add.id,
        username=username,
        condition=item_input.condition,
        is_first_edition=item_input.is_first_edition,
        extras=extras,
        db=db,
    )

    if existing_user_item is None:
        link_item_to_user_collection(
            item_id=item_to_add.id, username=username, item_input=item_input, db=db
        )
    else:
        existing_user_item.quantity += item_input.quantity

    db.commit()

@router.post("/table/{table_name}/items/user/{username}", tags=["items"])
def add_multiple_items_to_user_collection(
    table_name: str,
    username: str,
    items_input: UserItemsInput,
    db: Session = Depends(get_db),
):
    for specific_id in items_input.item_ids:
        existing_item = get_item_from_source_table_and_id(
            origin_table_name=table_name, origin_id=specific_id, db=db
        )

        if existing_item is not None:
            item_to_add = existing_item
        else:
            item_to_add = create_item(
                origin_table_name=table_name, origin_id=specific_id, db=db
            )

        extras = items_input.extras if items_input.extras not in ["", "null"] else None

        existing_user_item = existing_link_user_item_condition_edition(
            item_id=item_to_add.id,
            username=username,
            condition=items_input.condition,
            is_first_edition=items_input.is_first_edition,
            extras=extras,
            db=db,
        )

        if existing_user_item is None:
            link_item_to_user_collection(
                item_id=item_to_add.id, username=username, item_input=items_input, db=db
            )
        else:
            existing_user_item.quantity += items_input.quantity

    db.commit()
    return {"message": "Items added successfully"}

@router.post("/table/{table_name}/item/{specific_id}/condition/{condition}/first/{first_edition}/extras/{extras}/ebay/price", tags=["items"])
def ebay_price_for_item(
    table_name: str,
    specific_id: int,
    condition: str,
    extras: str,
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
        rarity = card.rarity
        set_number = card.set_number if card.set_number not in ["", None] else card.name if "<ruby>" not in card.name else None
        if set_number is None:
            return
        language = card.language
        if language == "fr":
            prices = ebay_search_query_france_prices(
                query=set_number + " " + conditions[condition] + (" 1st" if first_edition else "") + (" " + rarity if any(keyword in rarity.lower() for keyword in ["collector", "ghost", "ultimate"]) else "")
            )
            if prices is None:
                prices = ebay_search_query_france_prices(
                    query=set_number #+ " " + conditions[condition] + (" 1st" if first_edition else "")
                )
                # if prices is None:
                #     prices = ebay_search_query_france_prices(
                #         query=set_number + " " + rarity
                #     )
            currency = "EURO"
        else:
            prices = ebay_search_query_us_prices(
                query=set_number + " " + conditions[condition] + (" 1st" if first_edition else "") + (" " + rarity if any(keyword in rarity.lower() for keyword in ["collector", "ghost", "ultimate"]) else "")
            )
            if prices is None:
                prices = ebay_search_query_us_prices(
                    query=set_number
                )
                # if prices is None:
                #     prices = ebay_search_query_us_prices(
                #     query=set_number + " " + rarity
                # )
            currency = "DOLLAR"
    
    elif table_name == "cards_pokemon":
        card = db.query(CardPokemon).filter(CardPokemon.id == specific_id).one()

        name = card.name
        #rarity = card.rarity
        card_number = str(card.local_id)
        language = card.language
        extra_in_query = (" " + extras if extras not in [None, "null"] else "")
        if language == "fr":
            prices = ebay_search_query_france_prices(
                query=name + " " + card_number + " " + conditions[condition] + extra_in_query + (" 1st" if first_edition else "") #+ " " + rarity 
            )
            if prices is None:
                prices = ebay_search_query_france_prices(
                    query=name + " " + card_number + extra_in_query + (" 1st" if first_edition else "") #+ rarity 
                )
                # if prices is None:
                #     prices = ebay_search_query_france_prices(
                #         query=name + " " + card_number
                #     )
            currency = "EURO"
        else:
            prices = ebay_search_query_us_prices(
                query=name + " " + card_number + " " + conditions[condition] + extra_in_query + (" 1st" if first_edition else "") #+ " " + rarity + (" 1st" if first_edition else "")
            )
            if prices is None:
                prices = ebay_search_query_us_prices(
                    query=name + " " + card_number + extra_in_query + (" 1st" if first_edition else "")#+ " " + rarity 
                )
                # if prices is None:
                #     prices = ebay_search_query_us_prices(
                #         query=name + " " + card_number
                #     )
            currency = "DOLLAR"

    if prices is None:
        return None
    now = datetime.now()

    # Check if item exist with this condition, and first edition check for the current item and user
    item_price = (
        db.query(ItemPrice)
        .filter(
            ItemPrice.item_id == item_to_look_for_price.id,
            ItemPrice.condition == condition,
            ItemPrice.is_first_edition == first_edition
        )
        .one_or_none()
    )
    
    if item_price is None:
        item_price = ItemPrice(
            item_id = item_to_look_for_price.id,
            condition = condition,
            ebay_currency = currency,
            ebay_last_update = now,
            ebay_highest = "%.2f" % prices["high"],
            ebay_lowest = "%.2f" % prices["low"],
            ebay_mean = "%.2f" % prices["mean"],
            ebay_median = "%.2f" % prices["median"],
            is_first_edition = first_edition
        )
        db.add(item_price)
    else:
        item_price.ebay_last_update = now
        item_price.ebay_highest = "%.2f" % prices["high"]
        item_price.ebay_lowest = "%.2f" % prices["low"]
        item_price.ebay_mean = "%.2f" % prices["mean"]
        item_price.ebay_median = "%.2f" % prices["median"]
        item_price.is_first_edition = first_edition
        db.flush()
    
    db.commit()

    return prices


@router.post("/table/{table_name}/item/{specific_id}/condition/{condition}/first/{first_edition}/extras/{extras}/ebay/sold_prices", tags=["items"])
def ebay_price_for_item(
    table_name: str,
    specific_id: int,
    condition: str,
    extras: str,
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
        rarity = card.rarity
        language = card.language
        set_number = card.set_number if card.set_number not in ["", None] else card.name if "<ruby>" not in card.name else None

        if language == "fr":
            if set_number is None:
                return
            formatted_query = '"' + set_number + '" ' + condition + " " + rarity + (" 1ere" if first_edition else "")
            prices = ebay_sold_items_fr(formatted_query)
            if prices is None:
                prices = ebay_sold_items_fr('"' + set_number + '" ' + condition + (" 1ere" if first_edition else ""))
                if prices is None:
                    prices = ebay_sold_items_fr('"' + set_number + '" ' + condition)
                    if prices is None:
                        prices = ebay_sold_items_fr('"' + set_number + '"')
                        if prices is None:
                            prices = ebay_sold_items_fr(set_number)
                            if prices is None:
                                prices = ebay_selling_items_fr('"' + set_number + '"')
        else:
            if set_number is None:
                return
            formatted_query = '"' + set_number + '" ' + condition + " " + rarity + (" 1st" if first_edition else "")
            prices = ebay_sold_items(formatted_query)
            if prices is None:
                prices = ebay_sold_items('"' + set_number + '" ' + condition + (" 1st" if first_edition else ""))
                if prices is None:
                    prices = ebay_sold_items('"' + set_number + '" ' + condition)
                    if prices is None:
                        prices = ebay_sold_items('"' + set_number + '"')
                        if prices is None:
                            prices = ebay_sold_items(set_number)
                            if prices is None:
                                prices = ebay_selling_items('"' + set_number + '"')
    
    elif table_name == "cards_pokemon":
        card = db.query(CardPokemon).filter(CardPokemon.id == specific_id).one()
        cardset_count = db.query(Cardset).filter(Cardset.id == card.cardset_id).one().official_card_count_pokemon
        name = card.name
        language = card.language
        #rarity = card.rarity
        card_number = str(card.local_id)
        extra_in_query = (" " + extras if extras not in [None, "null"] else "")
        formatted_query = name + ' "' + card_number + "/" + str(cardset_count) + '" ' + condition + " " + extra_in_query

        if language == "fr":
            prices = ebay_sold_items_fr(formatted_query.replace("'",'"'))
            if prices is None:
                prices = ebay_sold_items_fr(name + ' "' + card_number + "/" + str(cardset_count) + '" ' + condition)
                if prices is None:
                    prices = ebay_sold_items_fr(name + ' "' + card_number + "/" + str(cardset_count) + '" ')
                    if prices is None:
                        ebay_selling_items_fr(name + ' "' + card_number + "/" + str(cardset_count) + '" ')
        else:
            prices = ebay_sold_items(formatted_query.replace("'",'"'))
            if prices is None:
                prices = ebay_sold_items(name + ' "' + card_number + "/" + str(cardset_count) + '" ' + condition)
                if prices is None:
                    prices = ebay_sold_items(name + ' "' + card_number + "/" + str(cardset_count) + '" ')
                    if prices is None:
                        prices = ebay_selling_items(name + ' "' + card_number + "/" + str(cardset_count) + '" ')

    if prices is None:
        return None
    now = datetime.now()

    # Check if item exist with this condition, and first edition check for the current item and user
    item_price = (
        db.query(ItemPrice)
        .filter(
            ItemPrice.item_id == item_to_look_for_price.id,
            ItemPrice.condition == condition,
            ItemPrice.is_first_edition == first_edition
        )
        .one_or_none()
    )

    if item_price is None:
        item_price = ItemPrice(
            item_id = item_to_look_for_price.id,
            condition = condition,
            ebay_currency = prices["price_unit"],
            ebay_last_update = now,
            ebay_highest = "%.2f" % prices["highest_price"],
            ebay_lowest = "%.2f" % prices["lowest_price"],
            ebay_mean = "%.2f" % prices["mean_price"],
            ebay_median = "%.2f" % prices["median_price"],
            is_first_edition = first_edition
        )
        db.add(item_price)
    else:
        item_price.ebay_last_update = now
        item_price.ebay_currency = prices["price_unit"]
        item_price.ebay_highest = "%.2f" % prices["highest_price"]
        item_price.ebay_lowest = "%.2f" % prices["lowest_price"]
        item_price.ebay_mean = "%.2f" % prices["mean_price"]
        item_price.ebay_median = "%.2f" % prices["median_price"]
        item_price.is_first_edition = first_edition
        db.flush()
    
    db.commit()

    return prices


@router.get("/table/{table_name}/item/{specific_id}/ebay/prices/all", tags=["items"])
def get_ebay_item_all_prices(
    table_name: str,
    specific_id: int,
    db: Session = Depends(get_db)
):
    existing_item = get_item_from_source_table_and_id(
        origin_table_name=table_name, origin_id=specific_id, db=db
    )

    if existing_item is not None:
        return (
            db.query(ItemPrice)
            .filter(ItemPrice.item_id == existing_item.id)
            .all()
        )
    else:
        return None


@router.delete("/{user_item_id}/user/{username}/delete", tags=["items"])
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


@router.put("/{user_item_id}/user/{username}", tags=["items"])
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
        db.query(Item, UserItem, ItemPrice)
        .select_from(UserItem)
        .join(Item, Item.id == UserItem.item_id)
        .outerjoin(ItemPrice, UserItem.item_id == ItemPrice.item_id)
        .filter(
            UserItem.user_id == user.id,
            or_(
                ItemPrice.id == None,
                and_(
                    UserItem.condition == ItemPrice.condition,
                    UserItem.is_first_edition == ItemPrice.is_first_edition
                )
            )
        )
        .all()
    )

    results = []

    for item, user_item, item_price in user_items:
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
                    "prices":
                        {
                            "low": item_price.ebay_lowest,
                            "high": item_price.ebay_highest,
                            "mean": item_price.ebay_mean,
                            "median": item_price.ebay_median,
                            "currency": item_price.ebay_currency
                        } if item_price is not None else {
                            "low": None,
                            "high": None,
                            "mean": None,
                            "median": None,
                            "currency": None
                        }
                }
                results.append(item_details)

    return results


@router.get("/user/v2/{username}", tags=["items"])
def query_items_with_dynamic_join(
    username: str,
    page: int,
    size: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Calculate offset for pagination
    offset = (page - 1) * size

    # Retrieve items and their corresponding user_items entries with pagination
    user_items_query = (
        db.query(Item, UserItem, ItemPrice)
        .select_from(UserItem)
        .join(Item, Item.id == UserItem.item_id)
        .outerjoin(ItemPrice, UserItem.item_id == ItemPrice.item_id)
        .filter(
            UserItem.user_id == user.id,
            or_(
                ItemPrice.id == None,
                and_(
                    UserItem.condition == ItemPrice.condition,
                    UserItem.is_first_edition == ItemPrice.is_first_edition
                )
            )
        )
        .offset(offset)
        .limit(size)
    )

    user_items = user_items_query.all()

    results = []

    for item, user_item, item_price in user_items:
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
                    "prices":
                        {
                            "low": item_price.ebay_lowest,
                            "high": item_price.ebay_highest,
                            "mean": item_price.ebay_mean,
                            "median": item_price.ebay_median,
                            "currency": item_price.ebay_currency
                        } if item_price is not None else {
                            "low": None,
                            "high": None,
                            "mean": None,
                            "median": None,
                            "currency": None
                        }
                }
                results.append(item_details)

    # Get the total number of items for the user to calculate total pages
    total_items = db.query(UserItem).filter(UserItem.user_id == user.id).count()
    total_pages = (total_items + size - 1) // size  # Calculate total pages

    return {
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "total_items": total_items,
        "items": results
    }


@router.get("/user/{username}/collection/prices", tags=["items"])
def get_user_collection_prices(
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_items_prices = (
        db.query(ItemPrice)
        .select_from(UserItem)
        .join(Item, Item.id == UserItem.item_id)
        .outerjoin(ItemPrice, UserItem.item_id == ItemPrice.item_id)
        .filter(
            UserItem.user_id == user.id,
            or_(
                ItemPrice.id == None,
                and_(
                    UserItem.condition == ItemPrice.condition,
                    UserItem.is_first_edition == ItemPrice.is_first_edition
                )
            )
        )
    ).all()

    low = sum([float(i.ebay_lowest) if i.ebay_currency == "DOLLAR" else float(i.ebay_lowest) / DOLLAR_TO_EURO for i in user_items_prices if i is not None])
    high = sum([float(i.ebay_highest) if i.ebay_currency == "DOLLAR" else float(i.ebay_lowest) / DOLLAR_TO_EURO for i in user_items_prices if i is not None])
    mean = sum([float(i.ebay_mean) if i.ebay_currency == "DOLLAR" else float(i.ebay_lowest) / DOLLAR_TO_EURO for i in user_items_prices if i is not None])
    median = sum([float(i.ebay_median) if i.ebay_currency == "DOLLAR" else float(i.ebay_lowest) / DOLLAR_TO_EURO for i in user_items_prices if i is not None])

    return {
        "low": round(low, 2),
        "high": round(high, 2),
        "mean": round(mean, 2),
        "median": round(median, 2),
        "currency": "DOLLAR"
    }


@router.post("/user/{username}/prices/ebay/update", tags=["items"])
def update_all_user_item_ebay_prices(
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    data = (
        db.query(UserItem, Item)
        .select_from(Item)
        .join(UserItem, Item.id == UserItem.item_id)
        .outerjoin(ItemPrice, and_(
                Item.id == ItemPrice.item_id,
                UserItem.condition == ItemPrice.condition,
                ItemPrice.is_first_edition == UserItem.is_first_edition,
            )
        )
        .filter(
            UserItem.user_id == user.id,
            or_(
                ItemPrice.ebay_last_update < twenty_four_hours_ago,
                ItemPrice.item_id == None
            )
        )
        .all()
    )

    for row in data:
        ebay_price_for_item(
            table_name = row.Item.source_table,
            specific_id = row.Item.specific_id,
            condition = row.UserItem.condition,
            first_edition = row.UserItem.is_first_edition,
            extras = row.UserItem.extras,
            db= db
        )

    return {"message": "{0} Items prices updated".format(len(data))}


@router.post("/user/{username}/prices/cardmarket/update", tags=["items"])
def update_all_user_item_cardmarket_prices(
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    data = (
        db.query(UserItem, Item)
        .select_from(Item)
        .join(UserItem, Item.id == UserItem.item_id)
        .outerjoin(ItemPrice, and_(
                Item.id == ItemPrice.item_id,
                UserItem.condition == ItemPrice.condition,
                ItemPrice.is_first_edition == UserItem.is_first_edition,
            )
        )
        .filter(
            UserItem.user_id == user.id,
            or_(
                ItemPrice.ebay_last_update < twenty_four_hours_ago,
                ItemPrice.item_id == None
            )
        )
        .all()
    )

    for row in data:
        cardmarket_price_for_item(
            table_name = row.Item.source_table,
            specific_id = row.Item.specific_id,
            condition = row.UserItem.condition,
            first_edition = row.UserItem.is_first_edition,
            extras = row.UserItem.extras,
            db= db
        )

    return {"message": "{0} Items prices updated".format(len(data))}


@router.post("/table/{table_name}/item/{specific_id}/condition/{condition}/first/{first_edition}/extras/{extras}/cardmarket/price", tags=["items"])
def cardmarket_price_for_item(
    table_name: str,
    specific_id: int,
    condition: str,
    extras: str,
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
    
        # Check if item exist with this condition, and first edition check for the current item and user
    item_price = (
        db.query(ItemPrice)
        .filter(
            ItemPrice.item_id == item_to_look_for_price.id,
            ItemPrice.condition == condition,
            ItemPrice.is_first_edition == first_edition
        )
        .one_or_none()
    )

    if item_price.cardmarket_last_update is not None:
        db_datetime = datetime.strptime(item_price.cardmarket_last_update, "%Y-%m-%d %H:%M:%S.%f")
        current_datetime = datetime.now()
        
        time_difference = current_datetime - db_datetime
        
        # Check if the time difference is greater than 24 hours
        if time_difference < timedelta(hours=24):
            return item_price.cardmarket_from_price
    
    # defining prices
    if table_name == "cards_yugioh":
        
        card = db.query(CardYuGiOh).filter(CardYuGiOh.id == specific_id).one()
        set_number = card.set_number if card.set_number not in ["", None] else card.name if "<ruby>" not in card.name else None
        if set_number is None:
            return
        language = card.language

        price = cardmarket_get_from_price(
            game = "YuGiOh",
            language = language,
            condition = condition,
            search = set_number,
            first_edition = first_edition
        )
    
    elif table_name == "cards_pokemon":
        card = db.query(CardPokemon).filter(CardPokemon.id == specific_id).one()

        name = card.name
        card_number = str(card.local_id)
        language = card.language
        #extra_in_query = (" " + extras if extras not in [None, "null"] else "")

        price = cardmarket_get_from_price(
            game = "Pokemon",
            language = language,
            condition = condition,
            search = name + " " + card_number,
            first_edition = first_edition
        )

    if price is None:
        return None
    now = datetime.now()
    
    if item_price is None:
        item_price = ItemPrice(
            item_id = item_to_look_for_price.id,
            condition = condition,
            cardmarket_currency = "EURO" if "€" in price else "POUND" if "£" in price else "DOLLAR",
            cardmarket_from_price = price,
            is_first_edition = first_edition,
            cardmarket_last_update = now
        )
        db.add(item_price)
    else:
        item_price.cardmarket_last_update = now
        item_price.cardmarket_currency = "EURO" if "€" in price else "POUND" if "£" in price else "DOLLAR",
        item_price.cardmarket_from_price = price,
        item_price.is_first_edition = first_edition
        db.flush()
    
    db.commit()

    return price


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

    now = datetime.now()

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
    extras: str,
    db: Session = Depends(get_db),
) -> UserItem:
    user = db.query(User).filter(User.username == username).one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    formated_extras = extras if extras not in ["", "null", None] else None

    existing_user_item = (
        db.query(UserItem)
        .filter(
            UserItem.item_id == item_id,
            UserItem.user_id == user.id,
            UserItem.condition == condition,
            UserItem.is_first_edition == is_first_edition,
            UserItem.extras == formated_extras
        )
        .one_or_none()
    )

    if existing_user_item is not None:
        return existing_user_item
