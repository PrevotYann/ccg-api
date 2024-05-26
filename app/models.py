from sqlalchemy import create_engine, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    "mysql+pymysql://root:%40Danganronpa47@91.199.227.99:10965/ccgapi?charset=utf8"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(250), unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String(250))


class Cardset(Base):
    __tablename__ = "cardsets"

    id = Column(Integer, primary_key=True, index=True)
    gameId = Column(Integer)
    name = Column(String(250))
    prefix = Column(String(250), nullable=True)
    language = Column(String(250))
    official_card_count_pokemon = Column(Integer, nullable=True)
    total_card_count_pokemon = Column(Integer, nullable=True)
    symbol_pokemon = Column(String(250), nullable=True)
    logo_pokemon = Column(String(250), nullable=True)


class CardPokemon(Base):
    __tablename__ = "cards_pokemon"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    illustrator = Column(String, nullable=True)
    image = Column(String, nullable=True)
    local_id = Column(String, nullable=True)
    rarity = Column(String, nullable=True)
    cardset_id = Column(Integer, nullable=True)
    variant_normal = Column(Boolean, nullable=True)
    variant_reverse = Column(Boolean, nullable=True)
    variant_holo = Column(Boolean, nullable=True)
    variant_firstEdition = Column(Boolean, nullable=True)
    variant_wPromo = Column(Boolean, nullable=True)
    hp = Column(Integer, nullable=True)
    types = Column(Text, nullable=True)
    evolve_from = Column(String, nullable=True)
    description = Column(String, nullable=True)
    stage = Column(String, nullable=True)
    attacks = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    retreat = Column(Integer, nullable=True)
    regulation_mark = Column(String, nullable=True)
    legal = Column(Text, nullable=True)
    tcgdex_id = Column(String, nullable=True)
    dexId = Column(String, nullable=True)
    gameId = Column(Integer)
    language = Column(String)


class CardYuGiOh(Base):
    __tablename__ = "cards_yugioh"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cardsetId = Column(Integer, nullable=False)
    gameId = Column(Integer, nullable=False)
    language = Column(String(250), nullable=True)
    konami_id = Column(Integer, nullable=True)
    password = Column(Integer, nullable=True)
    name = Column(String(250), nullable=False)
    text = Column(Text, nullable=True)
    images = Column(Text, nullable=True, comment="LIST OF IMGs, even if one")
    rarity = Column(String(250), nullable=False)
    card_type = Column(String(250), nullable=False)
    monster_type_line = Column(String(250), nullable=True)
    attribute = Column(String(250), nullable=True)
    level = Column(Integer, nullable=True)
    set_number = Column(String(250), nullable=True)
    atk = Column(String(250), nullable=True)
    def_ = Column(String(250), nullable=True, name="def")
    materials = Column(Text, nullable=True)
    series = Column(Text, nullable=True, comment="liste")
    limit_regulation_tcg = Column(String(250), nullable=True)
    limit_regulation_ocg = Column(String(250), nullable=True)
    pendulum_scale = Column(Integer, nullable=True)
    pendulum_effect = Column(Text, nullable=True)
    link_arrows = Column(Text, nullable=True)
    property = Column(String(250), nullable=True)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_table = Column(String(255), nullable=False)  # tablename
    specific_id = Column(Integer, nullable=False)  # id of the tablename


class UserItem(Base):
    __tablename__ = "user_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    item_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    added_date = Column(DateTime, nullable=False)
    condition = Column(
        String(100), nullable=True
    )  # cards : POOR, LIGHT_PLAYED, GOOD, EXCELLENT, NEAR_MINT, MINT ; others :POOR, GOOD, EXCELLENT, SEALED
    extras = Column(Text, nullable=True)
    is_first_edition = Column(Boolean, nullable=True)


def get_class_by_tablename(tablename):
    """Return class reference mapped to table."""
    for c in Base.registry._class_registry.values():
        if hasattr(c, "__table__") and c.__table__.fullname == tablename:
            return c
    return None


class ItemPrice(Base):
    __tablename__ = "items_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, nullable=False)
    condition = Column(String(100), nullable=True)
    ebay_currency = Column(String(100), nullable=True)
    ebay_last_update = Column(String(100), nullable=True)
    ebay_lowest = Column(String(100), nullable=True)
    ebay_median = Column(String(100), nullable=True)
    ebay_mean = Column(String(100), nullable=True)
    ebay_highest = Column(String(100), nullable=True)
    is_first_edition = Column(Boolean, nullable=True)
    cardmarket_currency = Column(String(100), nullable=True)
    cardmarket_from_price = Column(String(100), nullable=True)
    cardmarket_last_update = Column(String(100), nullable=True)
