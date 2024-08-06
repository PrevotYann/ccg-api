from fastapi import APIRouter, Depends, Query
from bs4 import BeautifulSoup
from selenium import webdriver
import time

router = APIRouter(prefix="/cardmarket")

def get_driver():
    driver = webdriver.Firefox()
    return driver

def get_search_term(search: str = Query(None, description="Search term")):
    return search

@router.get("/query/game/{game}/language/{language}/condition/{condition}/first/{first_edition}", tags=["cardmarket"])
def cardmarket_get_from_price(game: str, language: str, condition: str, first_edition: bool, search: str = Depends(get_search_term)):
    if language in ["ko", "ja"]:
        return # Not working for now on cardmarket

    driver = get_driver()
    driver.implicitly_wait(30)
    url_lang = "fr" if language == "fr" else "de" if language == "de" else "it" if language == "it" else "es" if language == "es" else "en"

    base_url = "https://www.cardmarket.com/{l}/{g}/Products/Search?searchString=".format(l=url_lang, g=game)
    
    formated_search = search.replace(" ", "+")

    url = f"{base_url}{formated_search}"

    languages = {
        "en": 1,
        "fr": 2,
        "de": 3,
        "es": 4,
        "it": 5,
        "pt": 6,
        "ja": 7,
        "ko": 10
    }

    conditions = {
        "mint": 1,
        "near_mint": 2,
        "excellent": 3,
        "good": 4,
        "light_played": 5,
        "played": 6,
        "poor": 7
    }
    
    try:
        driver.get(url)
        if not " challenges.cloudflare.com " in driver.page_source:
            new_url = driver.current_url + "?language={l}&minCondition={c}".format(l=languages[language],c=conditions[condition])
            if game == "YuGiOh":
                new_url = new_url + "&isFirstEd=" + ("Y" if first_edition else "N")
            driver.get(new_url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            price = soup.select_one("dl.labeled dd:nth-last-child(9)").text
        else:
            time.sleep(1)
            new_url = driver.current_url + "?language={l}&minCondition={c}".format(l=languages[language],c=conditions[condition])
            if game == "YuGiOh":
                new_url = new_url + "&isFirstEd=" + ("Y" if first_edition else "N")
            driver.get(new_url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            price = soup.select_one("dl.labeled dd:nth-last-child(9)").text
    except Exception as e:
        driver.get(url)
        # Find all elements with class "col" that contain a link
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        parent_divs = soup.find_all('div', class_='col')

        # Iterate over each parent div
        for parent_div in parent_divs:
            # Find the nested <a> tag within the parent div
            link = parent_div.find('a')
            # If a link is found, extract its href attribute
            if link:
                link_href = link.get('href')
                if link_href is not None and "Users" not in link_href:
                    break
        else:
            print("Link not found.")
        
        try:
            if not "Users/" in link_href:
                current_url = "/" + url_lang + "/" + link_href[4:]
                new_url = "https://www.cardmarket.com" + current_url + "?language={l}&minCondition={c}".format(l=languages[language],c=conditions[condition])
                if game == "YuGiOh":
                    new_url = new_url + "&isFirstEd=" + ("Y" if first_edition else "N")
                driver.get(new_url)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                price = soup.select_one("dl.labeled dd:nth-last-child(9)").text
            else:
                new_url = driver.current_url
                if "Single" in new_url:
                    if game == "YuGiOh":
                        new_url = new_url + "&isFirstEd=" + ("Y" if first_edition else "N")
                    driver.get(new_url)

                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    price = soup.select_one("dl.labeled dd:nth-last-child(9)").text
        except:
            return

    return price
