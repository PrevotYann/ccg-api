from fastapi import APIRouter

from browseapi import BrowseAPI


router = APIRouter(prefix="/ebay")


app_id = "YannPrvo-CardsInB-PRD-172b2ae15-2d2a0806"
cert_id = "PRD-72b2ae153301-789a-4962-bc3c-a8e2"


@router.get("/search/us/", tags=["ebay"])
def ebay_search_query_us(query: str):
    api = BrowseAPI(app_id, cert_id, marketplace_id="EBAY_US")
    responses = api.execute("search", [{"q": query, "limit": 200}])
    if responses is not None:
        return responses[0].itemSummaries


@router.get("/search/fr/", tags=["ebay"])
def ebay_search_query_france(query: str):
    api = BrowseAPI(app_id, cert_id, marketplace_id="EBAY_FR")
    responses = api.execute("search", [{"q": query, "limit": 200}])
    if responses is not None:
        return responses[0].itemSummaries


@router.get("/search/fr/condition/{condition}", tags=["ebay"])
def ebay_search_query_france_with_condition(query: str, condition: str):
    api = BrowseAPI(app_id, cert_id, marketplace_id="EBAY_FR")
    responses = api.execute("search", [{"q": query + " " + condition, "limit": 200}])
    if responses is not None:
        return responses[0].itemSummaries


@router.get("/search/us/condition/{condition}", tags=["ebay"])
def ebay_search_query_USA_with_condition(query: str, condition: str):
    api = BrowseAPI(app_id, cert_id, marketplace_id="EBAY_US")
    responses = api.execute("search", [{"q": query + " " + condition, "limit": 200}])
    if responses is not None:
        return responses[0].itemSummaries
