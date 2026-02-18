"""
Tilemap Tools - Outils pour créer et manipuler des tilemaps

Usage en commandes
----------------
    Commandes:
        tilemap create modele 9 mon_modele
        tilemap modif mon_fichier
        tilemap view mon_fichier
        
Usage en module Python
------------------------
    pas encore fait
"""
__version__ = "0.1.6"

# Importation des fonctions est les méthodes utilisable en nomant le module dans un programme
from .core import (
    Tilemap,
    TilemapModel
)

__all__ = [
    'Tilemap',
    'TilemapModel',
]