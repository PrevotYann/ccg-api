from fastapi import APIRouter
import requests

from app.routers.resources.enmus import QUALITIES
from app.routers.resources.strings import EBAY_OAUTH_TOKEN
from app.schema import EbayItemSummary

router = APIRouter(prefix="/ebay")

headers_FR = {
    "Authorization": "Bearer %s" % EBAY_OAUTH_TOKEN,
    "X-EBAY-C-MARKETPLACE-ID": "EBAY_FR",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

headers_US = {
    "Authorization": "Bearer %s" % EBAY_OAUTH_TOKEN,
    "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


@router.get(
    "/search/us/",
    tags=["ebay"],
)
def ebay_search_query_usa(query: str) -> list[EbayItemSummary] | None:
    response = requests.get(
        url="https://api.ebay.com/buy/browse/v1/item_summary/search?q=%s&limit=200"
        % query,
        headers=headers_US,
    )

    if response.status_code == 200:
        return (
            response.json()["itemSummaries"]
            if response.json().get("itemSummaries")
            else None
        )
    else:
        return "Error: %s" % response.status_code


@router.get(
    "/search/fr/",
    tags=["ebay"],
)
def ebay_search_query_france(query: str) -> list[EbayItemSummary] | None:
    response = requests.get(
        url="https://api.ebay.com/buy/browse/v1/item_summary/search?q=%s&limit=200"
        % query,
        headers=headers_FR,
    )

    if response.status_code == 200:
        return (
            response.json()["itemSummaries"]
            if response.json().get("itemSummaries")
            else None
        )
    else:
        return "Error: %s" % response.status_code


@router.get(
    "/search/france/quality/{quality}",
    tags=["ebay"],
)
def ebay_search_query_with_card_quality_france(
    query: str, quality: int
) -> list[EbayItemSummary] | None:
    response = requests.get(
        url="https://api.ebay.com/buy/browse/v1/item_summary/search?q=%s&limit=200"
        % (query + " " + QUALITIES[quality]),
        headers=headers_FR,
    )

    if response.status_code == 200:
        return (
            response.json()["itemSummaries"]
            if response.json().get("itemSummaries")
            else None
        )
    else:
        return "Error: %s" % response.status_code


@router.get(
    "/search/us/quality/{quality}",
    tags=["ebay"],
)
def ebay_search_query_with_card_quality_usa(
    query: str, quality: int
) -> list[EbayItemSummary] | None:
    response = requests.get(
        url="https://api.ebay.com/buy/browse/v1/item_summary/search?q=%s&limit=200"
        % (query + " " + QUALITIES[quality]),
        headers=headers_US,
    )

    if response.status_code == 200:
        return (
            response.json()["itemSummaries"]
            if response.json().get("itemSummaries")
            else None
        )
    else:
        return "Error: %s" % response.status_code
