"""
Tilemap Tools - Outils pour créer et manipuler des tilemaps
"""
__version__ = "1.5.0"

# Importation des fonctions est les méthodes utilisable en nomant le module dans un programme
from .core import (
    Modele,
    Tilemap,
    is_px_init,
    get_color,
    get_time,
    Element,
    Texture,
    Animation
)

__all__ = [
    "Modele",
    "Tilemap",
    "is_px_init",
    "get_color",
    "get_time",
    "Element",
    "Texture",
    "Animation"
]