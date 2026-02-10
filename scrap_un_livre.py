from bs4 import BeautifulSoup
import requests
import csv
import os

url = "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html"

def bookdata(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    data = {}
    
    # Infos principales
    data["Titre"] = soup.find("div", class_="item active").find("img")["alt"]
    urlimage = soup.find("div", class_="item active").find("img")["src"]
    data["Url Image"] = "https://books.toscrape.com/" + urlimage.replace("../../", "")
    data["Catégorie"] = soup.find("ul", class_="breadcrumb").find_all("a")[2].text
    
    # Informations du tableau
    lignes = soup.find("table", class_="table-striped").find_all("tr")
    for ligne in lignes:
        th = ligne.find("th")
        td = ligne.find("td")
        if th and td:
            data[th.text.strip()] = td.text.strip()
    
    return data

# Appeler la fonction
resultat = bookdata(url)
print(resultat)