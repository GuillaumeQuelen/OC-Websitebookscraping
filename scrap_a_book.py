from bs4 import BeautifulSoup
import requests
import csv
import os

url = "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"

ddef book_data(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    data = {}

    # URL
    data["URL"] = url

    # UPC (Universal Product Code)
    upc_element = soup.find("td").text.strip()
    data["UPC"] = upc_element

    # Title
    data["Titre"] = soup.find("h1").text.strip()

    # Prices
    price_including_tax = soup.find("th", string= "Price (incl. tax)").find_next("td").text.strip()
    price_excluding_tax = soup.find("th", string= "Price (excl. tax)").find_next("td").text.strip()
    data["Prix TTC"] = price_including_tax
    data["Prix HT"] = price_excluding_tax

    # Availability
    number_available = soup.find("th", string="Availability").find_next("td").text.strip()
    data["Disponibilité"] = number_available.split("(")[0].strip()

    # Description
    desc_div = soup.find("div", id="Description")
    if desc_div:
        product_description = desc_div.find_next("p").text.strip()
    else:
        product_description = "Sans description"
    data["Description"] = product_description

    # Categories
    data["Catégorie"] = soup.find("ul", class_="breadcrumb").find_all("a")[2].text.strip()

    # Review (/ 5)
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    rating_tag = soup.find("p", class_="star-rating")
    data["Note des lecteurs"] = None
    if rating_tag:
        for cls in rating_tag.get("class", []):
            if cls in rating_map:
                data["review_rating"] = rating_map[cls]
                break

    # Image URL
    image_url = soup.find("div", class_="item active").find("img")["src"]
    data["image_url"] = URL_BASE + image_url.replace("../../", "")

    return data


# Appeler la fonction
resultat = bookdata(url)
print(resultat)