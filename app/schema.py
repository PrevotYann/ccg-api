from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel

from datetime import datetime


class Category(BaseModel):
    categoryId: Optional[str] = None
    categoryName: Optional[str] = None


class Image(BaseModel):
    imageUrl: Optional[str] = None


class Price(BaseModel):
    value: Optional[str] = None
    currency: Optional[str] = None


class Seller(BaseModel):
    username: Optional[str] = None
    feedbackPercentage: Optional[str] = None
    feedbackScore: Optional[int] = None


class OriginalPrice(BaseModel):
    value: Optional[str] = None
    currency: Optional[str] = None


class DiscountAmount(BaseModel):
    value: Optional[str] = None
    currency: Optional[str] = None


class MarketingPrice(BaseModel):
    originalPrice: Optional[OriginalPrice] = None
    discountPercentage: Optional[str] = None
    discountAmount: Optional[DiscountAmount] = None


class ThumbnailImage(BaseModel):
    imageUrl: Optional[str] = None


class ShippingCost(BaseModel):
    value: Optional[str] = None
    currency: Optional[str] = None


class ShippingOption(BaseModel):
    shippingCostType: Optional[str] = None
    shippingCost: Optional[ShippingCost] = None


class ItemLocation(BaseModel):
    postalCode: Optional[str] = None
    country: Optional[str] = None


class AdditionalImage(BaseModel):
    imageUrl: Optional[str] = None


class EbayItemSummary(BaseModel):
    itemId: Optional[str] = None
    title: Optional[str] = None
    leafCategoryIds: Optional[List[str]] = None
    categories: Optional[List[Category]] = None
    image: Optional[Image] = None
    price: Optional[Price] = None
    itemHref: Optional[str] = None
    seller: Optional[Seller] = None
    marketingPrice: Optional[MarketingPrice] = None
    condition: Optional[str] = None
    conditionId: Optional[str] = None
    thumbnailImages: Optional[List[ThumbnailImage]] = None
    shippingOptions: Optional[List[ShippingOption]] = None
    buyingOptions: Optional[List[str]] = None
    epid: Optional[str] = None
    itemWebUrl: Optional[str] = None
    itemLocation: Optional[ItemLocation] = None
    additionalImages: Optional[List[AdditionalImage]] = None
    adultOnly: Optional[bool] = None
    legacyItemId: Optional[str] = None
    availableCoupons: Optional[bool] = None
    itemCreationDate: Optional[str] = None
    topRatedBuyingExperience: Optional[bool] = None
    priorityListing: Optional[bool] = None
    listingMarketplaceId: Optional[str] = None


class UserBase(BaseModel):
    username: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class CardsetSchema(BaseModel):
    id: Optional[int]
    gameId: Optional[int]
    name: Optional[str]
    prefix: Optional[str]
    language: Optional[str]
    official_card_count_pokemon: Optional[int]
    total_card_count_pokemon: Optional[int]
    symbol_pokemon: Optional[str]
    logo_pokemon: Optional[str]


class PokemonCardSchema(BaseModel):
    id: Optional[str]
    name: Optional[str]
    illustrator: Optional[str]
    image: Optional[str]
    local_id: Optional[str]
    rarity: Optional[str]
    cardset_id: Optional[int]
    set_details: Optional[CardsetSchema]
    variant_normal: Optional[bool]
    variant_reverse: Optional[bool]
    variant_holo: Optional[bool]
    variant_firstEdition: Optional[bool]
    variant_wPromo: Optional[bool]
    hp: Optional[int]
    types: Optional[List[str]]
    evolve_from: Optional[str]
    description: Optional[str]
    stage: Optional[str]
    attacks: Optional[List[Dict[str, Optional[str]]]]
    weaknesses: Optional[List[Dict[str, str]]]
    retreat: Optional[int]
    regulation_mark: Optional[str]
    tcgdex_id: Optional[str]
    dexId: Optional[str]
    gameId: int
    language: str

    class Config:
        from_attributes = True


class YuGiOhCardSchema(BaseModel):
    id: Optional[int]
    cardsetId: int
    gameId: int
    language: Optional[str]
    konami_id: Optional[int]
    password: Optional[int]
    name: str
    text: Optional[str]
    images: Optional[str]
    rarity: Optional[str]
    card_type: Optional[str]
    monster_type_line: Optional[str]
    attribute: Optional[str]
    level: Optional[int]
    set_number: Optional[str]
    atk: Optional[str]
    def_: Optional[str]
    materials: Optional[str]
    series: Optional[str]
    limit_regulation_tcg: Optional[str]
    limit_regulation_ocg: Optional[str]
    pendulum_scale: Optional[int]
    pendulum_effect: Optional[str]
    link_arrows: Optional[str]
    property: Optional[str]

    class Config:
        from_attributes = True


class Item(BaseModel):
    id: Optional[int]
    source_table: str
    specific_id: int

    class Config:
        from_attributes = True


class UserItem(BaseModel):
    id: Optional[int] = None
    user_id: int
    item_id: int
    quantity: int
    added_date: datetime
    condition: Optional[str]
    extras: Optional[str]
    is_first_edition: Optional[bool]


class UserItemInput(BaseModel):
    quantity: int
    condition: Optional[str]
    extras: Optional[str] = None
    is_first_edition: Optional[bool] = None

class UserItemsInput(BaseModel):
    item_ids: List[int]
    quantity: int
    condition: Optional[str]
    extras: Optional[str] = None
    is_first_edition: Optional[bool] = None
