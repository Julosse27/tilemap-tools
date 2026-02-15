"""Fichier qui gère toutes les commandes en rapport avec les fichiers tilemaps"""
from subprocess import run
from os import remove
from os.path import dirname, join, exists, abspath
from time import time, sleep
from pyxel import load, init, images, colors as col, Image, save, load_pal
from PIL import Image as Image_PIL, ImageTk, ImageDraw
import tkinter as tk

# Stucture d'un fichier en .map
# Séparateurs possibles pour ne pas modifier l'image: ()&!,-
# sep général: &
# sep modèles: !
# sep intra-modèle: ,
# sep tilemap: !

def map_create(dossier:str, noms_fichiers_mdl:list[str]):
    
    nom_fichier_temp = f'{join(dirname(__file__), "pyxres_bin", f"bin_{int(time() * 10)}")}'

    bg = "#808254"

    liste_tiles = []
    for fichier_mdl in noms_fichiers_mdl:
        with open(join(dossier, fichier_mdl + ".mdl"), "rb") as f:
            liste = f.read().split(b",")
            img = liste[0]
            taille = int(liste[1])
        with open(nom_fichier_temp + ".png", "wb") as f:
            f.write(img)
        image = Image_PIL.open(nom_fichier_temp + ".png")
        
        images_tiles = []
        for x in range(0, image.width, taille):
            for y in range(0, image.height, taille):
                images_tiles.append(image.crop((x, y, x + taille, y + taille)))
        liste_tiles.append(images_tiles)
        image.close()
        remove(nom_fichier_temp + ".png")

    root = tk.Tk()
    root.title("Création de tilemaps")
    root.geometry("500x500")
    root.configure(bg= bg)
    root.rowconfigure([i for i in range(len(liste_tiles) + 2)])

    for images in liste_tiles:
        canva = tk.Canvas(root, bg=bg, height= 50, width= 500)

        for img in images:
            
            canva.create_image()

    root.mainloop()