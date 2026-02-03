import requests
from bs4 import BeautifulSoup
import csv
import os


def get_book_info(url):
    """Récupère les données d'UN livre"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    title = soup.find("h1").text
    upc = soup.find("th", string="UPC").find_next_sibling("td").text
    price_incl_tax = soup.find("th", string="Price (incl. tax)").find_next_sibling("td").text
    price_excl_tax = soup.find("th", string="Price (excl. tax)").find_next_sibling("td").text
    availability = soup.find("th", string="Availability").find_next_sibling("td").text
    
    description_div = soup.find("div", id="product_description")
    product_description = description_div.find_next_sibling("p").text if description_div else ""
    
    category = soup.find("ul", class_="breadcrumb").find_all("a")[2].text
    rating_tag = soup.find("p", class_="star-rating")
    review_rating = rating_tag["class"][1]
    
    image_tag = soup.find("div", class_="item active").find("img")
    image_url = "https://books.toscrape.com/" + image_tag["src"].replace("../../", "")
    
    return {
        "product_page_url": url,
        "universal_product_code": upc,
        "title": title,
        "price_including_tax": price_incl_tax,
        "price_excluding_tax": price_excl_tax,
        "number_available": availability,
        "product_description": product_description,
        "category": category,
        "review_rating": review_rating,
        "image_url": image_url
    }


def get_books_urls_category(category_url):
    """Récupère toutes les URLs des livres d'une catégorie"""
    book_urls = []
    current_url = category_url
    
    while current_url:
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        books = soup.find_all("h3")
        for book in books:
            link = book.find("a")["href"]
            full_url = "https://books.toscrape.com/catalogue/" + link.replace("../../../", "")
            book_urls.append(full_url)
        
        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_link = next_btn.find("a")["href"]
            base_url = current_url.rsplit("/", 1)[0]
            current_url = base_url + "/" + next_link
        else:
            current_url = None
    
    return book_urls


def get_all_categories():
    """Récupère toutes les catégories depuis la page d'accueil"""
    response = requests.get("https://books.toscrape.com/")
    soup = BeautifulSoup(response.content, "html.parser")
    
    categories = []
    nav = soup.find("ul", class_="nav-list").find("ul")
    for li in nav.find_all("li"):
        link = li.find("a")
        name = link.text.strip()
        url = "https://books.toscrape.com/" + link["href"]
        categories.append({"name": name, "url": url})
    
    return categories


# === PROGRAMME PRINCIPAL ===

# Créer un dossier pour les CSV
os.makedirs("data", exist_ok=True)

# Récupérer toutes les catégories
categories = get_all_categories()
print(f"Données en préparation")

# Pour chaque catégorie
for cat in categories:
    print(f"📚 {cat['name']}...")
    
    book_urls = get_books_urls_category(cat["url"])
    
    all_books = []
    for url in book_urls:
        book_info = get_book_info(url)
        all_books.append(book_info)
    
    # Créer le CSV
    csv_filename = f"data/{cat['name'].lower().replace(' ', '-')}.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_books[0].keys())
        writer.writeheader()
        writer.writerows(all_books)
    
    print(f"Création de → {csv_filename}")

print("\nVotre liste est prête!")