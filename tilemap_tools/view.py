"""
Commande pour voir le contenu du fichier de modèle ou du fichier de tilemap.
"""
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from os.path import join, exists, dirname, abspath
from os import remove
from time import time

class TilemapViewer:
    def __init__(self, root: tk.Tk, image_path, nb_tiles, nom_fichier):
        self.nb_tiles = nb_tiles

        bg = "#6835c7"

        # Charger l'image
        self.original_image = Image.open(image_path)
        
        # Créer une copie pour dessiner la grille
        self.display_image = self.original_image.copy()
        self.display_image = self.display_image.resize((256, 256), Image.NEAREST) # pyright: ignore[reportAttributeAccessIssue]
        self.tile_size = 256 // nb_tiles
        self.draw_grid()
        
        # Convertir pour Tkinter
        self.photo = ImageTk.PhotoImage(self.display_image)

        frame = tk.Frame(root, bg=bg)
        frame.pack(fill=tk.BOTH, expand= True)

        tk.Label(frame, text= f"Voici le contenu du modèle\n{nom_fichier}.mdl", font=("Arial", 20, "bold"), bg=bg).pack()
        
        # Canvas
        self.canvas = tk.Canvas(
            frame,
            width=self.display_image.width,
            height=self.display_image.height,
            bg='lightgray'
        )
        self.canvas.pack(expand= True)
        
        # Afficher l'image
        self.canvas.create_image(128, 128, anchor=tk.CENTER, image=self.photo)
        
        # Info label
        self.info_label = tk.Label(frame, text="Cliquez sur une tuile\n", font=("Arial", 19), pady= 30, bg=bg)
        self.info_label.pack()
        
        # Événement de clic
        self.canvas.bind("<Button-1>", self.on_tile_click)
        self.canvas.bind("<B1-Motion>", self.on_tile_click)
    
    def draw_grid(self):
        """Dessine la grille sur l'image"""
        draw = ImageDraw.Draw(self.display_image)
        
        # Lignes verticales
        for x in range(0, self.display_image.width, self.tile_size):
            draw.line(
                [(x, 0), (x, self.display_image.height)],
                fill=(255, 0, 0, 128),
                width=1
            )
        
        # Lignes horizontales
        for y in range(0, self.display_image.height, self.tile_size):
            draw.line(
                [(0, y), (self.display_image.width, y)],
                fill=(255, 0, 0, 128),
                width=1
            )
    
    def on_tile_click(self, event):
        """Gérer le clic sur une tuile"""
        if event.x >= self.display_image.width or event.x <= 0 or event.y <= 0 or event.y >= self.display_image.height:
            self.canvas.delete("highlight")
            self.info_label.config(text="Cliquez sur une tuile\n")
            return
        tile_x = event.x // self.tile_size
        tile_y = event.y // self.tile_size

        if tile_x == 0:
            x_position = "gauche"
        elif tile_x == self.nb_tiles - 1:
            x_position = "droite"
        else:
            x_position = None

        if tile_y == 0:
            y_position = "haut"
        elif tile_y == self.nb_tiles - 1:
            y_position = "bas"
        else:
            y_position = None

        if (tile_x == 0 or tile_x == self.nb_tiles - 1) and (tile_y == 0 or tile_y == self.nb_tiles - 1):
            nom = f"coin en {y_position} à {x_position}"
        elif tile_x == 0 or tile_x == self.nb_tiles - 1 or tile_y == 0 or tile_y == self.nb_tiles - 1:
            if x_position:
                nom = f"coté {x_position if x_position == "gauche" else "droit"}"
            else:
                nom = f"{y_position}"
        else:
            nom = "millieu"

        nom += f"\n({tile_x}, {tile_y})"
        
        # Mettre à jour l'info
        self.info_label.config(
            text=f"Tuile sélectionnée : {nom}"
        )
        
        # Surligner la tuile
        self.highlight_tile(tile_x, tile_y)
    
    def highlight_tile(self, tile_x, tile_y):
        """Surligner une tuile"""
        # Effacer les anciens rectangles
        self.canvas.delete("highlight")
        
        # Dessiner un nouveau rectangle
        x1 = tile_x * self.tile_size
        y1 = tile_y * self.tile_size
        x2 = x1 + self.tile_size
        y2 = y1 + self.tile_size
        
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="yellow",
            width=3,
            tags="highlight"
        )

def main(nom_fichier:str, dossier:str):
    fichier_temp = join(abspath(dirname(__file__)), "pyxres_bin", f"bin_{int(time() * 10)}")

    for name in [".mdl", ".map"]:
        if exists(join(dossier, nom_fichier + name)):
            fichier = join(dossier, nom_fichier + name)
            extension = name
            break

    if extension == ".mdl":
        with open(fichier, "rb") as f:
            liste = f.read().split(b",")
            img = liste[0]
            nb_tuiles = int(liste[2].decode())
        with open(fichier_temp + ".png", "wb") as f:
            f.write(img)
        root = tk.Tk()
        root.title("Affichage de la tilemap.")
        root.grid_rowconfigure([0, 1], weight=1)
        root.geometry("500x500")

        TilemapViewer(root, fichier_temp + ".png", nb_tuiles, nom_fichier)
        
        root.mainloop()

        remove(fichier_temp + ".png")