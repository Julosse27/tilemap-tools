"""Fichier qui gère toutes les commandes en rapport avec les fichiers tilemaps"""
from subprocess import run
from typing import Any
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

def map_create(dossier:str, noms_fichiers_mdl:list[str], nom_fichier:str):
    
    nom_fichier_temp = f'{join(dirname(__file__), "pyxres_bin", f"bin_{int(time() * 10)}")}'

    bg = "#808254"

    liste_tiles: list[list[tuple[Any, int, int, int]]] = []
    for fichier_mdl in noms_fichiers_mdl:
        with open(join(dossier, fichier_mdl + ".mdl"), "rb") as f:
            liste = f.read().split(b",")
            img = liste[0]
            taille = int(liste[1])
            nb = int(liste[2])
        with open(nom_fichier_temp + ".png", "wb") as f:
            f.write(img)
        image = Image_PIL.open(nom_fichier_temp + ".png")
        
        images_tiles = []
        tile_x = 0
        for x in range(0, image.width, taille):
            tile_y = 0
            for y in range(0, image.height, taille):
                partie_img = image.crop((x, y, x + taille, y + taille)) # Prend juste une tile de l'image du modèle
                images_tiles.append((partie_img, tile_x, tile_y, nb)) # L'ajoute à la liste
                tile_y += 1 # Met à jour les coordonnées de la tuile
            tile_x += 1
        liste_tiles.append(images_tiles)
        image.close()
        remove(nom_fichier_temp + ".png")

    root = tk.Tk() # Créer une fenètre avec tkinter
    root.title("Création de tilemaps") # Définir le titre de la fenètre
    root.geometry("1000x900") # Définir la taille de la fenètre
    root.configure(bg= bg) # Mettre un background
    # Permet d'équilibrer la fenètre pour ne pas avoir un élément qui prend plus de place qu'un autre.

    tk.Label(root, text=f"Créez vottre fichier {nom_fichier}\navec les éléments que vous avez demandé", font=('Arial', 15, 'bold'), bg=bg).pack()

    frame = tk.Frame(root, width=1000, height=256, bg=bg)
    frame.pack()

    canva_principal = tk.Canvas(frame, width= 256, height=256, highlightthickness=0, bd=0)

    canva_principal.place(relx=0.3, rely=0, anchor=tk.N)

    tk.Label(frame, text=f"Cette image sera ce que contiendra le fichier\n{nom_fichier} lors de son enregistrement.\nSélectionez des tuiles puis placez les sur cette fenètre\npour le construire.", font=('Arial', 15), bg=bg, justify=tk.CENTER).place(relx=0.7,rely=0.5, anchor=tk.CENTER)

    selector = TilemapSelector(root)
    for i, images in enumerate(liste_tiles):
        tk.Label(root, text=f"Voici le contenu du fichier {noms_fichiers_mdl[i]}", font=("Arial", 9, "bold"), bg=bg).pack()
        canva = tk.Canvas(root, bg=bg, height= 90, width= 1000, highlightthickness=0, bd=0)

        décallage = 62
        longeur_ligne = 50 + décallage*(len(images) - 1)
        debut = 500 - (longeur_ligne // 2)

        canva.photos_list = getattr(canva, 'photos_list', []) # pyright: ignore[reportAttributeAccessIssue]
        for i, elements in enumerate(images):
            img, tile_x, tile_y, nb = elements

            img_taille = img.resize((50, 50), Image_PIL.NEAREST) # pyright: ignore[reportAttributeAccessIssue]

            photo = ImageTk.PhotoImage(img_taille)

            canva.create_image(debut + i*décallage, 0, anchor=tk.NW, image= photo, tags=f"img{i}")

            if tile_x == 0:
                x_position = "gauche"
            elif tile_x == nb - 1:
                x_position = "droite"
            else:
                x_position = None

            if tile_y == 0:
                y_position = "haut"
            elif tile_y == nb - 1:
                y_position = "bas"
            else:
                y_position = None

            if (tile_x == 0 or tile_x == nb - 1) and (tile_y == 0 or tile_y == nb - 1):
                nom = f"coin {y_position}\n - {x_position}"
            elif tile_x == 0 or tile_x == nb - 1 or tile_y == 0 or tile_y == nb - 1:
                if x_position:
                    nom = f"{x_position}"
                else:
                    nom = f"{y_position}"
            else:
                nom = "millieu"

            nom += f"\n({tile_x}, {tile_y})"

            nom = nom.capitalize()

            canva.create_text(debut + i*décallage, 53, anchor=tk.NW, text=nom, font=("Arial", 7), justify=tk.CENTER, tags="TEXT")
            
            canva.photos_list.append(photo) # pyright: ignore[reportAttributeAccessIssue]

        canva.bind("<B1-Motion>", selector.hover)
        canva.bind("<Button-1>", selector.click)
        selector.canvas_list.append(canva)
        
        canva.pack()

    root.mainloop()

class TilemapSelector:
    def __init__(self, root) -> None:
        self.B1 = False
        self.old_canva = None
        self.tuile = (None, None)
        self.canvas_list = []
        
        # Capturer le relâchement au niveau de la fenêtre
        root.bind("<ButtonRelease-1>", self.release)

    def get_tuile(self):
        """Renvoie la tuile qui à été sélectionnée"""
        return self.tuile
    
    def set_tuile(self, widget, tag):
        """Enregistre la tuile cliquée"""
        self.tuile = (widget, tag)

    def _traiter_position(self, canvas, x, y):
        """Logique commune à hover et click"""
        # Convertir les coordonnées relatives au canvas
        canvas_x = canvas.winfo_rootx()
        canvas_y = canvas.winfo_rooty()
        local_x = x - canvas_x
        local_y = y - canvas_y
        
        for id in canvas.find_closest(local_x, local_y):
            tag = canvas.gettags(id)[0]
            if tag != "TEXT" and tag != "highlight":
                if self.old_canva:
                    self.old_canva.delete("highlight")
                img_x, img_y = canvas.coords(tag)
                self.old_canva = canvas
                self.set_tuile(canvas, tag)
                
                canvas.create_rectangle(
                    img_x, img_y, img_x + 50, img_y + 50,
                    outline="yellow",
                    width=3,
                    tags="highlight"
                )
                break

    def hover(self, event):
        """Vérifie à chaque moment si qd tu passe sur une tuile il faut la sélectioner."""
        if not self.B1:
            return
        
        # Trouver quel canvas est sous la souris
        x, y = event.widget.winfo_pointerx(), event.widget.winfo_pointery()
        
        for canvas in self.canvas_list:
            cx = canvas.winfo_rootx()
            cy = canvas.winfo_rooty()
            cw = canvas.winfo_width()
            ch = canvas.winfo_height()
            
            # Vérifier si la souris est dans ce canvas
            if cx <= x <= cx + cw and cy <= y <= cy + ch:
                self._traiter_position(canvas, x, y)
                break

    def release(self, event):
        """Traite le relachement du bouton B1 en indiquant au programme son état."""
        self.B1 = False

    def click(self, event):
        """Traite n'importe quel appui et indique que le bouton B1 est préssé."""
        self.B1 = True
        self._traiter_position(
            event.widget,
            event.widget.winfo_rootx() + event.x,
            event.widget.winfo_rooty() + event.y
        )