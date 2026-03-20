"""
Tilemap Tools - Outils pour créer et manipuler des tilemaps
"""
__version__ = "0.1.7"

# Importation des fonctions est les méthodes utilisable en nomant le module dans un programme
from .core import (
    Modele,
    Tilemap,
    is_init,
    get_color
)

__all__ = [
    "Modele",
    "Tilemap",
    "is_init",
    "get_color"
]