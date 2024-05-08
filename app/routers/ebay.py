from fastapi import APIRouter
import requests
from requests.auth import HTTPBasicAuth

from app.routers.resources.enmus import QUALITIES
from app.routers.resources.strings import EBAY_TOKEN
from app.schema import EbayItemSummary

router = APIRouter(prefix="/ebay")


headers_US = {
    "Authorization": "Bearer %s" % EBAY_TOKEN,
    "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


@router.get(
    "/search/us/",
    tags=["ebay"],
)
def ebay_search_query_usa(query: str):  # -> list[EbayItemSummary]:
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
def ebay_search_query_france(query: str):  # list[EbayItemSummary]:
    # Set the endpoint URL
    url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"

    # Client credentials
    client_id = "YannPrvo-CardsInB-SBX-0727b8eb0-552146d4"
    client_secret = "SBX-727b8eb0cc0d-9b6f-41a9-8072-eada"

    # Define the headers
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Define the payload
    data = {
        "grant_type": "client_credentials",
        "scope": " ".join(
            [
                "https://api.ebay.com/oauth/api_scope",
                "https://api.ebay.com/oauth/api_scope/buy.guest.order",
                "https://api.ebay.com/oauth/api_scope/buy.item.feed",
                "https://api.ebay.com/oauth/api_scope/buy.marketing",
                "https://api.ebay.com/oauth/api_scope/buy.product.feed",
                "https://api.ebay.com/oauth/api_scope/buy.marketplace.insights",
                "https://api.ebay.com/oauth/api_scope/buy.proxy.guest.order",
                "https://api.ebay.com/oauth/api_scope/buy.item.bulk",
                "https://api.ebay.com/oauth/api_scope/buy.deal",
            ]
        ),
    }

    # Send the POST request
    response = requests.post(
        url, headers=headers, data=data, auth=HTTPBasicAuth(client_id, client_secret)
    )

    # Check the response
    if response.status_code == 200:
        EBAY_TOKEN = response.json()["access_token"]
        headers_FR = {
            "Authorization": "Bearer %s" % EBAY_TOKEN,
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_FR",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    else:
        return response.text

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
) -> list[EbayItemSummary]:
    # Set the endpoint URL
    url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"

    # Client credentials
    client_id = "YannPrvo-CardsInB-SBX-0727b8eb0-552146d4"
    client_secret = "SBX-727b8eb0cc0d-9b6f-41a9-8072-eada"

    # Define the headers
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Define the payload
    data = {
        "grant_type": "client_credentials",
        "scope": " ".join(
            [
                "https://api.ebay.com/oauth/api_scope",
                "https://api.ebay.com/oauth/api_scope/buy.guest.order",
                "https://api.ebay.com/oauth/api_scope/buy.item.feed",
                "https://api.ebay.com/oauth/api_scope/buy.marketing",
                "https://api.ebay.com/oauth/api_scope/buy.product.feed",
                "https://api.ebay.com/oauth/api_scope/buy.marketplace.insights",
                "https://api.ebay.com/oauth/api_scope/buy.proxy.guest.order",
                "https://api.ebay.com/oauth/api_scope/buy.item.bulk",
                "https://api.ebay.com/oauth/api_scope/buy.deal",
            ]
        ),
    }

    # Send the POST request
    response = requests.post(
        url, headers=headers, data=data, auth=HTTPBasicAuth(client_id, client_secret)
    )

    # Check the response
    if response.status_code == 200:
        EBAY_TOKEN = response.json()["access_token"]
        headers_FR = {
            "Authorization": "Bearer %s" % EBAY_TOKEN,
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_FR",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    else:
        return response.text

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
) -> list[EbayItemSummary]:
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
