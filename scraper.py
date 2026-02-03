import requests
from bs4 import BeautifulSoup
import csv


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


category_url = "https://books.toscrape.com/catalogue/category/books/food-and-drink_33/index.html"
category_name = "food-and-drink"

print(f"Récupération de la librairie{category_name}...")

book_urls = get_books_urls_category(category_url)

all_books = []
for i, url in enumerate(book_urls):
    book_info = get_book_info(url)
    all_books.append(book_info)

csv_filename = f"{category_name}.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=all_books[0].keys())
    writer.writeheader()
    writer.writerows(all_books)

print(f"\nFichier {csv_filename} créé avec {len(all_books)} livres !")