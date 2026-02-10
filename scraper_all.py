cat > scraper_final.py << 'EOF'
import requests
from bs4 import BeautifulSoup
import csv
import os
import time

URL_BASE = "https://books.toscrape.com/"

def telecharger_image(image_url, dossier, nom_fichier):
    response = requests.get(image_url)
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, nom_fichier)
    with open(chemin, "wb") as f:
        f.write(response.content)

def extraire_infos_livre(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    titre = soup.find("h1").text
    upc = soup.find("th", string="UPC").find_next_sibling("td").text
    prix_ttc = soup.find("th", string="Price (incl. tax)").find_next_sibling("td").text
    prix_ht = soup.find("th", string="Price (excl. tax)").find_next_sibling("td").text
    dispo = soup.find("th", string="Availability").find_next_sibling("td").text
    
    div_desc = soup.find("div", id="product_description")
    description = div_desc.find_next_sibling("p").text if div_desc else ""
    
    categorie = soup.find("ul", class_="breadcrumb").find_all("a")[2].text
    
    balise_note = soup.find("p", class_="star-rating")
    note = balise_note["class"][1]
    
    balise_img = soup.find("div", class_="item active").find("img")
    url_image = URL_BASE + balise_img["src"].replace("../../", "")
    
    return {
        "product_page_url": url,
        "universal_product_code": upc,
        "title": titre,
        "price_including_tax": prix_ttc,
        "price_excluding_tax": prix_ht,
        "number_available": dispo,
        "product_description": description,
        "category": categorie,
        "review_rating": note,
        "image_url": url_image
    }

def recuperer_urls_livres(url_categorie):
    urls = []
    url_courante = url_categorie
    
    while url_courante:
        response = requests.get(url_courante)
        soup = BeautifulSoup(response.content, "html.parser")
        
        livres = soup.find_all("h3")
        for livre in livres:
            lien = livre.find("a")["href"]
            url_complete = URL_BASE + "catalogue/" + lien.replace("../../../", "")
            urls.append(url_complete)
        
        btn_suivant = soup.find("li", class_="next")
        if btn_suivant:
            lien_suivant = btn_suivant.find("a")["href"]
            base = url_courante.rsplit("/", 1)[0]
            url_courante = base + "/" + lien_suivant
        else:
            url_courante = None
    
    return urls

def recuperer_categories():
    response = requests.get(URL_BASE)
    soup = BeautifulSoup(response.content, "html.parser")
    
    liste_categories = []
    nav = soup.find("ul", class_="nav-list").find("ul")
    for li in nav.find_all("li"):
        lien = li.find("a")
        nom = lien.text.strip()
        url = URL_BASE + lien["href"]
        liste_categories.append({"nom": nom, "url": url})
    
    return liste_categories

# --- Programme principal ---

os.makedirs("data", exist_ok=True)

categories = recuperer_categories()

for cat in categories:
    urls_livres = recuperer_urls_livres(cat["url"])
    donnees_livres = []
    
    for url in urls_livres:
        try:
            infos = extraire_infos_livre(url)
            donnees_livres.append(infos)
            nom_image = infos["universal_product_code"] + ".jpg"
            telecharger_image(infos["image_url"], f"images/{cat['nom']}", nom_image)
            time.sleep(0.1)
        except:
            pass
    
    if donnees_livres:
        nom_csv = f"data/{cat['nom'].lower().replace(' ', '_')}.csv"
        with open(nom_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=donnees_livres[0].keys())
            writer.writeheader()
            writer.writerows(donnees_livres)

print("Termine")
EOF