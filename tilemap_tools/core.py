"""
Ce fichier gére toutes les implémentations de base du module `tilemap-tools`
"""
from os.path import isfile, abspath
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