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


def get_categories():
    response = requests.get(URL_BASE, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    category_list = []
    nav = soup.find("ul", class_="nav-list").find("ul")

    for li in nav.find_all("li"):
        link = li.find("a")
        name = link.text.strip()
        url_cat = URL_BASE + link["href"]
        category_list.append({"name": name, "url": url_cat})

    return category_list


def urls_books_category(url_category):
    urls = []
    current_url = url_category

    while current_url:
        try:
            response = requests.get(current_url, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Erreur pagination {current_url} : {e}")
            break

        soup = BeautifulSoup(response.content, "html.parser")

        books = soup.find_all("h3")
        for book in books:
            link = book.find("a")["href"]
            full_url = URL_BASE + "catalogue/" + link.replace("../../../", "")
            urls.append(full_url)

        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_link = next_btn.find("a")["href"]
            current_url = current_url.rsplit("/", 1)[0] + "/" + next_link
        else:
            current_url = None

    return urls


def download_image(image_url, folder):
    os.makedirs(folder, exist_ok=True)
    file_name = os.path.basename(image_url)
    file_path = os.path.join(folder, file_name)

    response = requests.get(image_url, timeout=10)
    with open(file_path, "wb") as f:
        f.write(response.content)


# ==================== Orchestrator program ====================

os.makedirs("data", exist_ok=True)
category_list = get_categories()

for cat in category_list:
    cat_name = cat["name"]
    print(f"{cat_name}...")

    urls = urls_books_category(cat["url"])
    image_folder = f"images/{cat_name}"
    category_data = []

    for i, url in enumerate(urls, start=1):
        try:
            print(f"{cat_name} - livre {i}/{len(urls)}")
            data = book_data(url)
            category_data.append(data)
            download_image(data["image_url"], image_folder)
            time.sleep(0.1)
        except Exception as e:
            print(f"Erreur sur {url} : {e}")

    if category_data:
        csv_name = f"data/{cat_name.lower().replace(' ', '_')}.csv"
        with open(csv_name, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=category_data[0].keys())
            writer.writeheader()
            writer.writerows(category_data)

print("Terminé !")