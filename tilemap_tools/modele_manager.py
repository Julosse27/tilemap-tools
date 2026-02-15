"""Fichier qui gère toutes les commandes en rapport avec les modèles"""
from subprocess import run
from os.path import dirname, join, exists, abspath
from os import remove
from time import time, sleep
from pyxel import load, init, images, colors as col, Image, save, load_pal
from PIL import Image as Image_PIL, ImageTk, ImageDraw
import tkinter as tk

class TilemapViewer:
    def __init__(self, root: tk.Tk, image_path, nb_tiles, nom_fichier):
        self.nb_tiles = nb_tiles

        bg = "#6835c7"

        # Charger l'image
        self.original_image = Image_PIL.open(image_path)
        
        # Créer une copie pour dessiner la grille
        self.display_image = self.original_image.copy()
        self.display_image = self.display_image.resize((256, 256), Image_PIL.NEAREST) # pyright: ignore[reportAttributeAccessIssue]
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

def mdl_view(dossier:str, nom_fichier:str):
    fichier_temp = join(abspath(dirname(__file__)), "pyxres_bin", f"bin_{int(time() * 10)}")
    fichier = join(dossier, nom_fichier + ".mdl")
    
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

def mdl_create(taille:int, nb_tiles:int, file:str, colors: None | list[str], dossier:str): # pyright: ignore[reportRedeclaration]
    print()
    print("""Vous devez créer un modèle pour tilemap:
            - Vous devez créer un carré contenant les 4 coins, les 4 cotés et le milieu du modèle
            - Ce carré sera découpé en 9 (les 4 coins, les 4 cotés et le millieu) pour constituer
              la base pour une future tilemap.
            - Après avoir créé votre modèle complet pensez à l'enregistrer puis fermer la fenètre.
            - Le programme s'occupera de faire le reste pour vous et de l'enregistrer au nom que
              vous avez choisit.""")
    print()
    
    sleep(1)

    init(0, 0)

    nom_fichier_res = f'{join(dirname(__file__), "pyxres_bin", f"bin_{int(time() * 10)}")}'

    if colors is None:
        colors: list[str] = []
        for color in col.to_list():
            colors.append(hex(color)[2:])
    else:
        colors.insert(0, '000000')
        open(nom_fichier_res + ".pyxpal", "w").write("\n".join(map(str, colors)))

    tentative = 0
    ok = False
    while not ok:
        run(["pyxel", "edit", nom_fichier_res])

        try:
            load(f'{nom_fichier_res}.pyxres')
            img = images[0]
            tilemap: list[list[int]] = []
            nb_0 = 0
            for x in range(taille * nb_tiles):
                ligne:list[int] = []
                for y in range(taille * nb_tiles):
                    ligne.append(img.pget(x, y))
                    nb_0 += 1 if img.pget(x, y) == 0 else 0
                tilemap.append(ligne)
            if nb_0 != (taille * nb_tiles) ** 2:
                ok = True
            else:
                if tentative <= 10:
                    print("Je ne peut pas créer un fichier vide.")
                    print()
                    tentative += 1
                else:
                    if exists(nom_fichier_res + ".pyxres"):
                        remove(fr"{nom_fichier_res}.pyxres")
                    if exists(nom_fichier_res + ".pyxpal"):
                        remove(fr"{nom_fichier_res}.pyxpal")
                    return
                continue
            
        except Exception as e:
            ok = False
            print()
            print("Il y à eu un problème avec le fichier, pensez à l'enregistrer avant de le fermer.")
            print(f"Erreur : {e}")
            if tentative <= 10:
                print("Nouvelle tentative dans 1 seconde.")
                tentative += 1
                sleep(1)
            else:
                remove(fr"{nom_fichier_res}.pyxres")
                if exists(nom_fichier_res + ".pyxpal"):
                    remove(fr"{nom_fichier_res}.pyxpal")
                return
    test = Image(taille * nb_tiles, taille * nb_tiles)
    test.blt(0, 0, 0, 0, 0, taille * nb_tiles, taille * nb_tiles)
    test.save(nom_fichier_res + ".png", 1)
    with open(nom_fichier_res + ".png", "rb") as u:
        img_png = u.read()
    with open(join(dossier, file + ".mdl"), "wb") as f:
        f.write(img_png + f",{taille},{nb_tiles},{"\n".join(map(str, colors))}".encode())
            
    remove(fr"{nom_fichier_res}.pyxres")
    remove(fr"{nom_fichier_res}.png")
    if exists(nom_fichier_res + ".pyxpal"):
        remove(fr"{nom_fichier_res}.pyxpal")

    return

def mdl_modif(file:str, dossier:str):
    nom_fichier_temp = f'{join(dirname(__file__), "pyxres_bin", f"bin_{int(time() * 10)}")}'

    with open(join(dossier, file + ".mdl"), "rb") as f:
        liste = f.read().split(b",")
        img_bytes = liste[0]
        taille = int(liste[1])
        nb = int(liste[2])
        couleurs = liste[3].decode()

    print()
    print(f"""Ce fichier contient une tilemap:
          - de {nb}x{nb} tuiles;
          - de {taille} pixels de larges""")
    print()
    
    with open(nom_fichier_temp + ".png", "wb") as f:
        f.write(img_bytes)

    open(nom_fichier_temp + ".pyxpal", "w").write(couleurs)

    width, height = Image_PIL.open(nom_fichier_temp + ".png").size

    init(width, height, display_scale= 0)

    load_pal(nom_fichier_temp + ".pyxpal")

    images[0].load(0, 0, nom_fichier_temp + ".png")

    remove(nom_fichier_temp + ".png")

    save(nom_fichier_temp + ".pyxres")
    
    tentative = 1
    ok = False
    if not ok:
        run(["pyxel", "edit", nom_fichier_temp])

        try:
            load(nom_fichier_temp + ".pyxres")

            img = images[0]

            tilemap: list[list[int]] = []
            for x in range(width):
                ligne = []
                for y in range(height):
                    ligne.append(img.pget(x, y))
                tilemap.append(ligne)
            ok = True
        except Exception as e:
            ok = False
            print()
            print("Il y à eu un problème avec le fichier, pensez à l'enregistrer avant de le fermer.")
            print(f"Erreur : {e}")
            if tentative <= 11:
                print("Nouvelle tentative dans 1 seconde.")
                tentative += 1
                sleep(1)
            else:
                return
            
    test = Image(width, height)
    test.blt(0, 0, 0, 0, 0, width, height)
    test.save(nom_fichier_temp + ".png", 1)
    with open(nom_fichier_temp + ".png", "rb") as u:
        img_png = u.read()
    with open(join(dossier, file + ".mdl"), "wb") as f:
        f.write(img_png + f",{taille},{nb},{couleurs}".encode())
    remove(nom_fichier_temp + ".png")
    remove(nom_fichier_temp + ".pyxres")
    remove(nom_fichier_temp + ".pyxpal")