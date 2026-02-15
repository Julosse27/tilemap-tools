"""
Tilemap Tools - Outils pour créer et manipuler des tilemaps

Usage en CLI:
    tilemap create_model 9 mon_modele
    tilemap view mon_modele.mdl

Usage en module Python:
    (complètement à faire)
"""
__version__ = "0.1.5"

# Importation des fonctions est les méthodes utilisable en nomant le module dans un programme
from .core import (
    Tilemap,
    TilemapModel
)

__all__ = [
    'Tilemap',
    'TilemapModel',
]