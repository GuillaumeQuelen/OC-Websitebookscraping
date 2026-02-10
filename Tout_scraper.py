import requests
from bs4 import BeautifulSoup
import csv
import os
import time

URL_BASE = "https://books.toscrape.com/"


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

    return liste_categories


def urls_livres_categorie(url_categorie):
    urls = []
    url_courante = url_categorie

    while url_courante:
        try:
            response = requests.get(url_courante, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Erreur pagination {url_courante} : {e}")
            break

        soup = BeautifulSoup(response.content, "html.parser")

        livres = soup.find_all("h3")
        for livre in livres:
            lien = livre.find("a")["href"]
            url_complete = URL_BASE + "catalogue/" + lien.replace("../../../", "")
            urls.append(url_complete)

        suite = soup.find("li", class_="next")
        if suite:
            lien_suite = suite.find("a")["href"]
            url_courante = url_courante.rsplit("/", 1)[0] + "/" + lien_suite
        else:
            url_courante = None

    return urls



def telecharger_image(url_image, dossier):
    os.makedirs(dossier, exist_ok=True)
    nom_fichier = os.path.basename(url_image)
    chemin = os.path.join(dossier, nom_fichier)

    response = requests.get(url_image, timeout=10)
    with open(chemin, "wb") as f:
        f.write(response.content)


# ==================== PROGRAMME PRINCIPAL ====================

os.makedirs("data", exist_ok=True)
liste_categories = get_categories()

for cat in liste_categories:
    nom_cat = cat["nom"]
    print(f"{nom_cat}...")

    urls = urls_livres_categorie(cat["url"])
    dossier_images = f"images/{nom_cat}"
    donnees_categorie = []

    for i, url in enumerate(urls, start=1):
        try:
            print(f"{nom_cat} - livre {i}/{len(urls)}")
            data = book_data(url)
            donnees_categorie.append(data)
            telecharger_image(data["Url Image"], dossier_images)
            time.sleep(0.1)
        except Exception as e:
            print(f"Erreur sur {url} : {e}")

    if donnees_categorie:
        nom_csv = f"data/{nom_cat.lower().replace(' ', '_')}.csv"
        with open(nom_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=donnees_categorie[0].keys())
            writer.writeheader()
            writer.writerows(donnees_categorie)

print("Terminé ")
