"""
Ce fichier gére toutes les implémentations de base du module `tilemap-tools`
"""
from os.path import isfile, abspath, splitext
from .formateur import decode, encode

def open(chemin: str):
    """
    Cette fonction ouvre un fichier et vous retourne son contenu.

    :param chemin: Le chemin jusqu'au fichier que vous voulez ouvrir.
    :type chemin: str

    :return: Contenu du fichier
    :rtype: `~.formateur.Fichier`
    """
    if isfile(abspath(chemin)):
        rep = decode(abspath(chemin))
    else:
        raise ValueError("Le chemin n'est pas valide.")

    return rep

class Tilemap:
    """
    Celle classe regroupe tout les différents fonctionnements que peut avoir un fichier tilemap.

    :arg chemin: Le chemin jusqu'au fichier de tilemap (en .map).
    :type chemin: str
    """
    def __init__(self, chemin: str) -> None:
        """Initialisation de l'objet `Tilemap`"""
        elt_fichier = decode(chemin)
        
