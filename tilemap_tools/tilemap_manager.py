"""Fichier qui gère toutes les commandes en rapport avec les fichiers tilemaps"""
from subprocess import run
from typing import Any
from os import remove
from os.path import dirname, join, exists, abspath
from time import time, sleep
from pyxel import load, init, images, colors as col, Image, save, load_pal
from PIL import Image as Image_PIL, ImageTk
import tkinter as tk
from threading import Thread

# Stucture d'un fichier en .map
# Séparateurs possibles pour ne pas modifier l'image: ()&!,-
# sep général: &
# sep modèles: !
# sep intra-modèle: ,
# sep tilemap: !

def map_create(dossier:str, noms_fichiers_mdl:list[str], nom_fichier:str):
    
    nom_fichier_temp = f'{join(dirname(__file__), "pyxres_bin", f"bin_{int(time() * 10)}")}'

    bg = "#808254"

    liste_tiles: list[list[tuple[Image_PIL.Image, int, int, int]]] = []
    for fichier_mdl in noms_fichiers_mdl:
        with open(join(dossier, fichier_mdl + ".mdl"), "rb") as f:
            liste = f.read().split(b",,")
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
    root.geometry("1000x650") # Définir la taille de la fenètre
    root.configure(bg= bg) # Mettre un background
    # Permet d'équilibrer la fenètre pour ne pas avoir un élément qui prend plus de place qu'un autre.

    tk.Label(root, text=f"Créez vottre fichier {nom_fichier}.map avec les éléments que vous avez demandé", font=('Arial', 15, 'bold'), bg=bg).pack()

    frame_principale = tk.Frame(root, width=1000, height=271, bg=bg)
    frame_principale.pack()

    tk.Label(frame_principale, text=f"Cette image sera ce que contiendra le fichier\n{nom_fichier}.map lors de son enregistrement.\nSélectionez des tuiles puis placez les sur cette fenètre\npour le construire.", font=('Arial', 15), bg=bg, justify=tk.CENTER).place(relx=0.7,rely=0.5, anchor=tk.CENTER)

    selector = Tilemap_Selector(root)

    dessinateur = Tilemap_Dessinator(frame_principale, selector)

    for i, images in enumerate(liste_tiles):
        tk.Label(root, text=f"Voici le contenu du fichier {noms_fichiers_mdl[i]}", font=("Arial", 9, "bold"), bg=bg).pack()
        canva = tk.Canvas(root, bg=bg, height= 90, width= 1000, highlightthickness=0, bd=0)

        décallage = 62
        longeur_ligne = 50 + décallage*(len(images) - 1)
        debut = 500 - (longeur_ligne // 2)

        canva.photos_list = getattr(canva, 'photos_list', []) # pyright: ignore[reportAttributeAccessIssue]
        canva.img_list = getattr(canva, 'img_list', []) # pyright: ignore[reportAttributeAccessIssue]
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
                nom = f"coin en {y_position}\nà {x_position}"
            elif tile_x == 0 or tile_x == nb - 1 or tile_y == 0 or tile_y == nb - 1:
                if x_position:
                    nom = f"{x_position}"
                else:
                    nom = f"{y_position}"
            else:
                nom = "millieu"

            nom += f"\n({tile_x}, {tile_y})"

            nom = nom.capitalize()

            canva.create_text(debut + i*décallage + 25, 53 + 5*len(nom.splitlines()), anchor=tk.CENTER, text=nom, font=("Arial", 7), justify=tk.CENTER, tags="TEXT")

            canva.photos_list.append(photo) # pyright: ignore[reportAttributeAccessIssue]
            canva.img_list.append(img) # pyright: ignore[reportAttributeAccessIssue]

        canva.bind("<B1-Motion>", selector.hover)
        canva.bind("<Button-1>", selector.click)
        selector.canvas_list.append(canva)
        
        canva.pack()

    root.mainloop()
    dessinateur.stop_thread()

class Tilemap_Dessinator:
    def __init__(self, frame: tk.Frame, selector:Tilemap_Selector) -> None:
        self.source_img = Image_PIL.new('RGB', (512, 512))

        bg = frame.cget("bg")

        self.variations_toggle = True
        self._stop_thread = False

        frame_dessin = tk.Frame(frame, bg=bg)
        frame_dessin.place(relx=0.25, rely=0, anchor=tk.N)

        self.tile_img = None

        self.alpha = 132
        self._sens_alpha = -2
        self._limites = {"bas":100, "haut":164}

        photo = ImageTk.PhotoImage(self.get_display_img())

        self.canva = tk.Canvas(frame_dessin, width= 256, height=256, highlightthickness=0, bd=0)
        self.image_id = self.canva.create_image(0, 0, anchor = tk.NW, image=photo)
        self.canva.image = photo # pyright: ignore[reportAttributeAccessIssue]

        frame_h = tk.Frame(frame_dessin, width=256, height=15)
        frame_h.pack_propagate(False)
        h_scroll = tk.Scrollbar(frame_h, orient=tk.HORIZONTAL, command=self.canva.xview, bg=bg)
        frame_v = tk.Frame(frame_dessin, height=256, width=15)
        frame_v.pack_propagate(False)
        v_scroll = tk.Scrollbar(frame_v, orient=tk.VERTICAL, command=self.canva.yview, bg=bg)
        
        self.canva.configure(
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set,
            scrollregion=(0, 0, 2048, 2048)  # Taille réelle du canva
        )

        self.canva.bind("<Button-1>", self.click(selector))
        self.canva.bind("<Motion>", self.hover(selector))
        self.canva.bind("<Leave>", self.leave)

        h_scroll.pack(fill=tk.X, expand=True)
        v_scroll.pack(fill=tk.Y, expand=True)
        frame_h.pack(side=tk.BOTTOM, anchor=tk.SW)
        frame_v.pack(side=tk.RIGHT)
        self.canva.pack(side=tk.LEFT)
        self.variation_alpha()

    def get_display_img(self):
        return self.source_img.resize((2048, 2048), Image_PIL.Resampling.NEAREST)
    
    def set_new_img(self):
        image = self.get_display_img()
        photo = ImageTk.PhotoImage(image)

        self.canva.itemconfig(self.image_id, image=photo)
        self.canva.image = photo # pyright: ignore[reportAttributeAccessIssue]

    def variation_alpha(self):
        if self._stop_thread:
            return

        if self.variations_toggle:
            if self.alpha <= self._limites["bas"]:
                self._sens_alpha = 2
            elif self.alpha >= self._limites["haut"]:
                self._sens_alpha = -2
            
            self.alpha += self._sens_alpha

            if self.tile_img != None:
                self.tile_img.putalpha(self.alpha)

                photo = ImageTk.PhotoImage(self.tile_img)

                self.canva.itemconfig("fantome", image=photo)
                self.canva.image_apercu = photo # pyright: ignore[reportAttributeAccessIssue]
        else:
            self.alpha = 132
                
        self.canva.after(33, self.variation_alpha)

    def apercu(self, x:int, y:int, tile_img: Image_PIL.Image):
        self.canva.delete("fantome")
        width, height = tile_img.size
        self.tile_img = tile_img.convert('RGBA').resize((width * 4, height * 4), Image_PIL.Resampling.NEAREST)
        self.tile_img.putalpha(self.alpha)

        photo = ImageTk.PhotoImage(self.tile_img)
        
        reste_x = x % 4
        if reste_x < 2:
            pixel_x = x - reste_x
        else:
            pixel_x = x + 4 - reste_x
        
        reste_y = y % 4
        if reste_y < 2:
            pixel_y = y - reste_y
        else:
            pixel_y = y + 4 - reste_y

        self.canva.create_image(pixel_x, pixel_y, anchor = tk.CENTER, image=photo, tags="fantome")

        self.canva.image_apercu = photo # pyright: ignore[reportAttributeAccessIssue]

    def stop_thread(self):
        self._stop_thread = True

    def hover(self, selector:Tilemap_Selector):
        def callback(event:tk.Event):
            tuile = selector.get_tuile()
            if tuile != None:
                x = self.canva.canvasx(event.x)
                y = self.canva.canvasy(event.y)
                self.apercu(x, y, tuile)
        return callback
    
    def leave(self, event):
        self.canva.delete("fantome")
    
    def click(self, selector:Tilemap_Selector):
        def callback(event:tk.Event):
            pass
        return callback

class Tilemap_Selector:
    def __init__(self, root) -> None:
        self.B1 = False
        self.tuile = (None, None)
        self.canvas_list = []
        
        # Capturer le relâchement au niveau de la fenêtre
        root.bind("<ButtonRelease-1>", self.release)

    def get_tuile(self) -> Image_PIL.Image | None:
        """Renvoie la tuile qui à été sélectionnée"""
        if self.tuile[1] != None:
            canva, tag = self.tuile
            numero = int(tag[3:])
            return canva.img_list[numero]
            
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
                if self.tuile[0]:
                    self.tuile[0].delete("highlight")
                img_x, img_y = canvas.coords(tag)
                self.set_tuile(canvas, tag)
                
                canvas.create_rectangle(
                    img_x, img_y, img_x + 50, img_y + 50,
                    outline="yellow",
                    width=3,
                    tags="highlight"
                )
                break

    def hover(self, event: tk.Event):
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

    def release(self, event: tk.Event):
        """Traite le relachement du bouton B1 en indiquant au programme son état."""
        self.B1 = False

    def click(self, event: tk.Event):
        """Traite n'importe quel appui et indique que le bouton B1 est préssé."""
        self.B1 = True
        self._traiter_position(
            event.widget,
            event.widget.winfo_rootx() + event.x,
            event.widget.winfo_rooty() + event.y
        )