# Books to Scrape - Extracteur de prix

Script Python pour extraire les donnees des livres du site Books to Scrape.

## Installation

1. Cloner le repo
2. Creer l'environnement virtuel :
```
python3 -m venv venv
source venv/bin/activate
```

3. Installer les dependances :
```
pip install -r requirements.txt
```

## Utilisation

Extraire un seul livre :
```
python3 scraper_livre.py
```

Extraire une categorie :
```
python3 scraper_categorie.py
```

Extraire tout le site (toutes categories + images) :
```
python3 scraper_all.py
```

## Donnees extraites

Pour chaque livre :
- URL de la page
- UPC
- Titre
- Prix TTC et HT
- Disponibilite
- Description
- Categorie
- Note
- URL de l'image

## Structure des fichiers

- `data/` : fichiers CSV par categorie
- `images/` : images des livres par categorie
