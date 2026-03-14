"""Stocke toutes les fonctions et les variables communes à tout les fichiers"""
from os.path import join, dirname, splitext, splitroot
from time import time


def generate_temp(extension:str|None = None):
    """
    Génère un chemin pour un fichier temporaire.

    Parameter
    ---------
    extension : `str`|`None`
        L'extension que doit obtenir le chemin du fichier qui va être retourné.

    Return
    ---------
    nom : `str`
        Le chemin généré avec une extension ou non.
    """
    nom = f'{join(dirname(__file__), "bin", f"bin_{int(time() * 10)}")}'
    if extension != None:
        nom += "." + extension
    return nom

def get_name(path:str, extension:bool = True):
    """
    Permet de récupérer le nom du fichier à partir de son chemin.

    Attention si le chemin pointe vers un dossier la chaine de caractère renvoyée sera vide.

    Parameters
    ---------
    path : `str`
        Chemin qui contient le nom du fichier.
    extension : `bool`
        Définit si le chemin doit contenir l'extension du fichier ou non:
            - `True` si vous voulez la garder (par défault ce paramètre est à `True`)
            - `False` si vous voulez l'enlever

    Return
    --------
    name : `str`
        Le nom du fichier avec ou sans l'extension.
        Attention cette chaine de caractère peut être vide.

    Examples
    ---------
    >>> get_name("c:\\_chemin\\_absolu\\_vers\\_un\\_fichier.txt")
    '_fichier.txt'
    >>> get_name("chemin\\_relatif\\_vers\\_un\\_fichier.json", False)
    '_fichier'
    >>> get_name("C:\\_chemin\\_absolu\\_vers\\_un\\_dossier")
    ''
    """
    chemin, extension_name = splitext(path)

    if extension_name == "":
        return ""

    name = chemin.split("\\")[-1]

    if extension:
        name += extension_name

    return name