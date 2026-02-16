import requests
from bs4 import BeautifulSoup
import time
import os

URL_BASE = "https://books.toscrape.com/"

def get_categories():
    response = requests.get(URL_BASE, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    liste_categories = []
    nav = soup.find("ul", class_="nav-list").find("ul")

    for li in nav.find_all("li"):
        lien = li.find("a")
        nom = lien.text.strip()
        url_cat = URL_BASE + lien["href"]
        liste_categories.append({"nom": nom, "url": url_cat})

    print(f"  → Total : {len(liste_categories)} catégories")
    
    return liste_categories

# Test
if __name__ == "__main__":
    categories = get_categories()
