from fastapi import APIRouter

from browseapi import BrowseAPI

import numpy as np

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


@router.get("/search/fr/prices", tags=["ebay"])
def ebay_search_query_france_prices(query: str):
    query = query.replace("δ", "")
    api = BrowseAPI(app_id, cert_id, marketplace_id="EBAY_FR")
    responses = api.execute("search", [{"q": query, "limit": 200}])
    currency = "EURO"

    if responses[0] is not None:
        exclude_keywords = ["replica", "réplica", "fake", "vitrine", "présentation", "fan art", "metal card", "sleeve", "alt arts", "alt art", "illustration holder", "artwork", "display case", "playmat", " plush "]
        include_keywords = query.split(" ")

        try:
            prices = [
                i.price.value 
                for i in responses[0].itemSummaries 
                if not any(keyword in i.title.lower() for keyword in exclude_keywords)
                and any(include in i.title.lower() for include in include_keywords)
            ]
            if prices == []:
                prices = [
                    i.price.value 
                    for i in responses[0].itemSummaries 
                    if not any(keyword in i.title.lower() for keyword in exclude_keywords)
                ]
                if prices == []:
                    prices = [
                        i.price.value 
                        for i in responses[0].itemSummaries 
                    ]
        except:
            return None

        # Convert string values to floats
        float_prices = np.array(list(map(float, prices)))

        # Exception handling if not enough prices
        try:
            # Calculate Z1 and Z3
            Z1 = np.percentile(float_prices, 30)
            Z3 = np.percentile(float_prices, 70)
            IZR = Z3 - Z1

            # Define a factor for filtering out outliers, typically 1.5 or 2.0 times the IQR
            factor = 1.75

            # Filter outliers
            filtered_prices = [x for x in float_prices if Z1 - factor * IZR <= x <= Z3 + factor * IZR]
        except:
            filtered_prices = float_prices

        return {
            "low_not_filtered": np.min(float_prices),
            "low": np.min(filtered_prices),
            "high_not_filtered": np.max(float_prices),
            "high": np.max(filtered_prices),
            "mean": np.mean(filtered_prices),
            "median": np.median(filtered_prices),
            "currency": currency
        }
    else:
        return None


@router.get("/search/us/prices", tags=["ebay"])
def ebay_search_query_us_prices(query: str):
    query = query.replace("δ", "")
    api = BrowseAPI(app_id, cert_id, marketplace_id="EBAY_US")

    responses = api.execute("search", [{"q": query, "limit": 200}])
    currency = "DOLLAR"
    if responses is not None:
        exclude_keywords = ["replica", "réplica", "fake", "vitrine", "présentation", "fan art", "metal card", "sleeve", "alt arts", "alt art", "illustration holder", "artwork", "display case", "playmat", " plush "]
        include_keywords = query.split(" ")
        try:
            prices = [
                i.price.value 
                for i in responses[0].itemSummaries 
                if not any(keyword in i.title.lower() for keyword in exclude_keywords)
                and any(include in i.title.lower() for include in include_keywords)
            ]
            if prices == []:
                prices = [
                    i.price.value 
                    for i in responses[0].itemSummaries 
                    if not any(keyword in i.title.lower() for keyword in exclude_keywords)
                ]
                if prices == []:
                    prices = [
                        i.price.value 
                        for i in responses[0].itemSummaries 
                    ]
        except:
            return None
        # Convert string values to floats
        float_prices = np.array(list(map(float, prices)))

        # Exception handling if not enough prices
        try:
            # Calculate Z1 and Z3
            Z1 = np.percentile(float_prices, 30)
            Z3 = np.percentile(float_prices, 70)
            IZR = Z3 - Z1

            # Define a factor for filtering out outliers, typically 1.5 or 2.0 times the IQR
            factor = 1.75

            # Filter outliers
            filtered_prices = [x for x in float_prices if Z1 - factor * IZR <= x <= Z3 + factor * IZR]
        except:
            filtered_prices = float_prices
        return {
            "low_not_filtered": np.min(float_prices),
            "low": np.min(filtered_prices),
            "high_not_filtered": np.max(float_prices),
            "high": np.max(filtered_prices),
            "mean": np.mean(filtered_prices),
            "median": np.median(filtered_prices),
            "currency": currency
        }


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
