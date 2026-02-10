from bs4 import BeautifulSoup
import requests
import csv
import os

url = "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"

def book_data(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    data = {}

    # URL de la page du produit
    data["product_page_url"] = url

    # UPC (Universal Product Code)
    upc_element = soup.find("td").text.strip()
    data["universal_product_code"] = upc_element

    # Titre
    data["title"] = soup.find("h1").text.strip()

    # Prix incluant et excluant les taxes
    price_including_tax = soup.find("td", text="Price (incl. tax)").find_next("td").text.strip()
    price_excluding_tax = soup.find("td", text="Price (excl. tax)").find_next("td").text.strip()
    data["price_including_tax"] = price_including_tax
    data["price_excluding_tax"] = price_excluding_tax

    # Nombre disponible
    number_available = soup.find("td", text="Availability").find_next("td").text.strip()
    data["number_available"] = number_available.split("(")[0].strip()

    # Description du produit
    product_description = soup.find("p", attrs={False: True}).text.strip() if soup.find("article", class_="product_page") else "No description"
    data["product_description"] = product_description

    # Catégorie
    data["category"] = soup.find("ul", class_="breadcrumb").find_all("a")[2].text.strip()

    # Note de review (sur 5)
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    rating_tag = soup.find("p", class_="star-rating")
    data["review_rating"] = None
    if rating_tag:
        for cls in rating_tag.get("class", []):
            if cls in rating_map:
                data["review_rating"] = rating_map[cls]
                break

    # URL de l'image
    image_url = soup.find("div", class_="item active").find("img")["src"]
    data["image_url"] = URL_BASE + image_url.replace("../../", "")

    return data


# Appeler la fonction
resultat = bookdata(url)
print(resultat)