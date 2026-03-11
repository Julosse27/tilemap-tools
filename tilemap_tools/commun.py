"""Stocke toutes les fonctions et les variables communes à tout les fichiers"""
from os.path import join, dirname
from time import time


def generate_temp(extension:str|None = None):
    nom = f'{join(dirname(__file__), "bin", f"bin_{int(time() * 10)}")}'
    if extension != None:
        nom += "." + extension
    return nom