from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


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
