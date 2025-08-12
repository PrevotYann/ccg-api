from fastapi import APIRouter

from browseapi import BrowseAPI

import numpy as np
import requests
from bs4 import BeautifulSoup
import statistics

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


@router.post("/parse/sold", tags=["ebay"])
def ebay_sold_items(item: str):
    excluded_words = {
        "shop on ebay", "replica", "réplica", "fake", "vitrine", "présentation",
        "fan art", "metal card", "sleeve", "illustration holder", "artwork",
        "display case", "playmat", "plush"
    }
    url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={item}&LH_Sold=1'
    response = requests.get(url)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find_all('div', class_='s-item__info')

    valid_prices = []
    for i in items:
        title = i.find('div', class_='s-item__title')
        price = i.find('span', class_='s-item__price')

        if not title or not price:
            continue

        title_text = title.get_text().lower()
        price_text = price.get_text()

        # Skip invalid price formats
        if "to" in price_text or "à" in price_text:
            continue

        price_value = float(price_text.replace('$', '').replace(',', ''))
        price_unit = price_text[0]

        if not any(word in title_text for word in excluded_words):
            if item.replace('"', '').split(" ")[0].lower() in title_text:
                valid_prices.append(price_value)

    # Filter and calculate
    if len(valid_prices) > 10:
        threshold = statistics.quantiles(valid_prices, n=10)[0]
        valid_prices = [p for p in valid_prices if p >= threshold]

    if valid_prices:
        return {
            "mean_price": round(statistics.mean(valid_prices), 2),
            "median_price": round(statistics.median(valid_prices), 2),
            "lowest_price": min(valid_prices),
            "highest_price": max(valid_prices),
            "price_unit": "$",  # Update based on your scraping logic
            "prices": [f"${price:.2f}" for price in valid_prices],
        }
    return None


@router.post("/parse/selling", tags=["ebay"])
def ebay_selling_items(item: str):
    # List of excluded words (must be in lower case for case insensitive comparison)
    excluded_words = [
        "shop on ebay", "replica", "réplica", "fake", "vitrine", "présentation", 
        "fan art", "metal card", "sleeve", 
        "illustration holder", "artwork", "display case", "playmat", "plush"
    ]

    # URL of the eBay search page
    url = 'https://www.ebay.fr/sch/i.html?_from=R40&_nkw={}&_sacat=0'.format(item)

    # Send a request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all items
        items = soup.find_all('div', class_='s-item__info')

        # List to store prices of valid items
        valid_prices = []

        for i in items:
            title = i.find('div', class_='s-item__title')
            price = i.find('span', class_='s-item__price')

            if title and price:
                title_text = title.get_text().lower()  # Convert to lower case for case insensitive comparison
                price_text = price.get_text()

                if "to" in price_text or "à" in price_text:
                    continue

                # Extract price value and unit
                price_value = float(price_text.replace('$', '').replace(',', ''))
                price_unit = price_text[0]  # Assuming the unit is the first character
                # Check if any excluded word is in the title
                if all(w not in title_text for w in excluded_words):
                    if '' in item or "%22" in item:
                        if item.replace('"','').split(" ")[0].lower() in title_text or item.replace('%22','').split(" ")[0].lower() in title_text:
                            valid_prices.append(price_value)
                    else:
                        if item.split(" ")[0].lower() in title_text:
                            valid_prices.append(price_value)

        # Remove weirdly low amounts (e.g., below 25th percentile)
        if len(valid_prices) > 10:
            threshold = statistics.quantiles(valid_prices, n=10)[0]  # 25th percentile
            valid_prices = [price for price in valid_prices if price >= threshold]

        if len(valid_prices) > 0:
            # Calculate mean and median prices
            mean_price = statistics.mean(valid_prices) if valid_prices else 0
            median_price = statistics.median(valid_prices) if valid_prices else 0
            lowest_price = min([p for p in valid_prices])
            highest_price = max([p for p in valid_prices])

            return {
                "mean_price": round(mean_price,2),
                "median_price": round(median_price,2),
                "lowest_price": lowest_price,
                "highest_price": highest_price,
                "price_unit": price_unit,
                "prices": [f"{price_unit}{price:.2f}" for price in valid_prices]
            }
        else:
            return None
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None


@router.post("/parse/fr/sold", tags=["ebay"])
def ebay_sold_items_fr(item: str):
    # List of excluded words (must be in lower case for case insensitive comparison)
    excluded_words = [
        "shop on ebay", "replica", "réplica", "fake", "vitrine", "présentation", 
        "fan art", "metal card", "sleeve", 
        "illustration holder", "artwork", "display case", "playmat", "plush"
    ]

    # URL of the eBay search page
    url = 'https://www.ebay.fr/sch/i.html?_from=R40&_nkw={}&LH_Sold=1'.format(item)

    # Send a request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all items
        items = soup.find_all('div', class_='s-item__info')

        # List to store prices of valid items
        valid_prices = []

        for i in items:
            title = i.find('div', class_='s-item__title')
            price = i.find('span', class_='s-item__price')

            if title and price:
                title_text = title.get_text().lower()  # Convert to lower case for case insensitive comparison
                price_text = price.get_text()
            
                if "to" in price_text or "à" in price_text:
                    continue
            
                # Extract price value and unit
                price_value = float(price_text.replace('$', '').replace('EUR', '').replace(',', '.').replace('\xa0', '').replace(' ', ''))                
                price_unit = 'DOLLAR' if '$' in price_text else 'EURO' if 'EUR' in price_text else 'POUND' if '£' in price_text else None
                # Check if any excluded word is in the title
                if all(w not in title_text for w in excluded_words):
                    if '' in item or "%22" in item:
                        if item.replace('"','').split(" ")[0].lower() in title_text or item.replace('%22','').split(" ")[0].lower() in title_text:
                            valid_prices.append(price_value)
                    else:
                        if item.split(" ")[0].lower() in title_text:
                            valid_prices.append(price_value)

        # Remove weirdly low amounts (e.g., below 25th percentile)
        if len(valid_prices) > 10:
            threshold = statistics.quantiles(valid_prices, n=10)[0]  # 25th percentile
            valid_prices = [price for price in valid_prices if price >= threshold]

        if len(valid_prices) > 0:
            # Calculate mean and median prices
            mean_price = statistics.mean(valid_prices) if valid_prices else 0
            median_price = statistics.median(valid_prices) if valid_prices else 0
            lowest_price = min([p for p in valid_prices])
            highest_price = max([p for p in valid_prices])

            return {
                "mean_price": round(mean_price,2),
                "median_price": round(median_price,2),
                "lowest_price": lowest_price,
                "highest_price": highest_price,
                "price_unit": price_unit,
                "prices": [f"{price:.2f}" for price in valid_prices]
            }
        else:
            return None
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None


@router.post("/parse/fr/selling", tags=["ebay"])
def ebay_selling_items_fr(item: str):
    # List of excluded words (must be in lower case for case insensitive comparison)
    excluded_words = [
        "shop on ebay", "replica", "réplica", "fake", "vitrine", "présentation", 
        "fan art", "metal card", "sleeve", 
        "illustration holder", "artwork", "display case", "playmat", "plush"
    ]

    # URL of the eBay search page
    url = 'https://www.ebay.fr/sch/i.html?_from=R40&_nkw={}&_sacat=0'.format(item)

    # Send a request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all items
        items = soup.find_all('div', class_='s-item__info')

        # List to store prices of valid items
        valid_prices = []

        for i in items:
            title = i.find('div', class_='s-item__title')
            price = i.find('span', class_='s-item__price')

            if title and price:
                title_text = title.get_text().lower()  # Convert to lower case for case insensitive comparison
                price_text = price.get_text()
            
                if "to" in price_text or "à" in price_text:
                    continue
            
                # Extract price value and unit
                price_value = float(price_text.replace('$', '').replace('EUR', '').replace(',', '.').replace('\xa0', '').replace(' ', ''))                
                price_unit = 'DOLLAR' if '$' in price_text else 'EURO' if 'EUR' in price_text else 'POUND' if '£' in price_text else None
                # Check if any excluded word is in the title
                if all(w not in title_text for w in excluded_words):
                    if '' in item or "%22" in item:
                        if item.replace('"','').split(" ")[0].lower() in title_text or item.replace('%22','').split(" ")[0].lower() in title_text:
                            valid_prices.append(price_value)
                    else:
                        if item.split(" ")[0].lower() in title_text:
                            valid_prices.append(price_value)

        # Remove weirdly low amounts (e.g., below 25th percentile)
        if len(valid_prices) > 10:
            threshold = statistics.quantiles(valid_prices, n=10)[0]  # 25th percentile
            valid_prices = [price for price in valid_prices if price >= threshold]

        if len(valid_prices) > 0:
            # Calculate mean and median prices
            mean_price = statistics.mean(valid_prices) if valid_prices else 0
            median_price = statistics.median(valid_prices) if valid_prices else 0
            lowest_price = min([p for p in valid_prices])
            highest_price = max([p for p in valid_prices])

            return {
                "mean_price": round(mean_price,2),
                "median_price": round(median_price,2),
                "lowest_price": lowest_price,
                "highest_price": highest_price,
                "price_unit": price_unit,
                "prices": [f"{price:.2f}" for price in valid_prices]
            }
        else:
            return None
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None


@router.post("/unique-parse/sold", tags=["ebay"])
def ebay_sold_items_unique_string(query: str):
    # List of excluded words (must be in lower case for case insensitive comparison)
    excluded_words = [
        "shop on ebay", "replica", "réplica", "fake", "vitrine", "présentation", 
        "fan art", "metal card", "sleeve", "alt arts", "alt art", 
        "illustration holder", "artwork", "display case", "playmat", "plush"
    ]

    # URL of the eBay search page
    url = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={query}&_sacat=1&rt=nc&LH_Sold=1&LH_Complete=1"
    
    # Send a request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all items
        items = soup.find_all('div', class_='s-item__info')
        
        # List to store prices of valid items
        valid_prices = []
        price_unit = None

        for item in items:
            title = item.find('div', class_='s-item__title')
            price = item.find('span', class_='s-item__price')

            if title and price:
                title_text = title.get_text().lower()  # Convert to lower case for case insensitive comparison
                if "to" not in price.get_text() and "à" not in price.get_text():
                    price_text = price.get_text()
                    # Extract price value and unit
                    price_value = float(price_text.replace('$', '').replace(',', ''))
                    price_unit = price_text[0]  # Assuming the unit is the first character

                    # Check if any excluded word is in the title
                    if not any(word in title_text for word in excluded_words) and (query.split(" ")[0].lower() in title_text):
                        valid_prices.append(price_value)
                else:
                    continue

        # Remove weirdly low amounts (e.g., below 25th percentile)
        if len(valid_prices) > 10:
            threshold = statistics.quantiles(valid_prices, n=10)[0]  # 25th percentile
            valid_prices = [price for price in valid_prices if price >= threshold]
        if len(valid_prices) > 0:
            # Calculate mean and median prices
            mean_price = statistics.mean(valid_prices) if valid_prices else 0
            median_price = statistics.median(valid_prices) if valid_prices else 0
            lowest_price = min([p for p in valid_prices])
            highest_price = max([p for p in valid_prices])

            return {
                "mean_price": round(mean_price,2),
                "median_price": round(median_price,2),
                "lowest_price": lowest_price,
                "highest_price": highest_price,
                "price_unit": price_unit,
                "prices": [f"{price_unit}{price:.2f}" for price in valid_prices]
            }
        else:
            return None
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

