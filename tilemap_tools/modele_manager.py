"""Fichier qui gère toutes les commandes en rapport avec les modèles"""
from PIL import Image as Image_PIL, ImageTk, ImageDraw
import tkinter as tk
from .formateur import encode, decode, generate_temp
from .commun import Dessinateur, Selecteur, BASE_COLORS, get_name, image_vide

BG = "#6835c7"

class Modele_Viewer:
    def __init__(self, root: tk.Tk, image: Image_PIL.Image, nb_tiles, nom_fichier):
        self.nb_tiles = nb_tiles

        # Charger l'image
        self.original_image = image
        
        # Créer une copie pour dessiner la grille
        self.display_image = self.original_image.copy()
        self.display_image = self.display_image.resize((256, 256), Image_PIL.NEAREST) # pyright: ignore[reportAttributeAccessIssue]
        self.tile_size = 256 // nb_tiles
        self.draw_grid()
        
        # Convertir pour Tkinter
        self.photo = ImageTk.PhotoImage(self.display_image)

        frame = tk.Frame(root, bg=BG)
        frame.pack(fill=tk.BOTH, expand= True)

        tk.Label(frame, text= f"Voici le contenu du modèle\n{nom_fichier}", font=("Arial", 20, "bold"), bg=BG).pack()
        
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
        self.info_label = tk.Label(frame, text="Cliquez sur une tuile\n", font=("Arial", 19), pady= 30, bg=BG)
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

def mdl_view(chemin_fichier:str, root: tk.Tk | None=None):
    if root == None:
        root = tk.Tk() # Créer une fenètre avec tkinter
    else:
        root.deiconify()

    fichier = decode(chemin_fichier)
    
    root.title("Affichage de la tilemap.")
    root.grid_rowconfigure([0, 1], weight=1)
    root.geometry("500x500")

    Modele_Viewer(root, fichier.image, fichier.nb_tiles, chemin_fichier.split("/")[-1])
    
    fichier.close()

    root.mainloop()

def mdl_create(taille:int, nb_tiles:int, chemin_fichier:str, colors: None | list[str], root:tk.Tk | None = None): # pyright: ignore[reportRedeclaration]
    if colors == None:
        colors = BASE_COLORS
    else:
        if len(colors) > 32 or len(colors) == 0:
            raise ValueError("L'argument colors n'est pas valide.")
    if root == None:
        root = tk.Tk() # Créer une fenètre avec tkinter
    else:
        root.deiconify()

    root.title("Création de modele") # Définir le titre de la fenètre
    root.geometry("1000x650") # Définir la taille de la fenètre
    root.configure(bg= BG) # Mettre un background

    tk.Label(root, text=f"Créez votre fichier {get_name(chemin_fichier)} avec les éléments que vous avez demandé", font=('Arial', 15, 'bold'), bg=BG).pack()

    frame_principale = tk.Frame(root, width=1000, height=271, bg=BG)
    frame_principale.pack()

    tk.Label(frame_principale, text=f"Cette image sera ce que contiendra le fichier\n{get_name(chemin_fichier)} lors de son enregistrement.\nSélectionez des couleurs puis placez les sur cette fenètre\npour le construire.", font=('Arial', 15), bg=BG, justify=tk.CENTER).place(relx=0.7,rely=0.5, anchor=tk.CENTER)

    selector = Selecteur(root)

    ratio = 4
    if taille*nb_tiles*4 < 256:
        ratio = 256//(taille*nb_tiles)

    dessinateur = Dessinateur(frame_principale, selector, image_base= image_vide(taille * nb_tiles), ratio=ratio)
    dessinateur.toggle_sauvegarde(False)

    for x in range(taille*ratio, taille*nb_tiles*ratio, taille*ratio):
        dessinateur.canva.create_line(x, 0, x, taille*nb_tiles*ratio, fill="#000000")
        dessinateur.canva.create_line(0, x, taille*nb_tiles*ratio, x, fill="#000000")

    if len(colors) <= 16:
        liste_gr_colors = [colors]
    else:
        liste_gr_colors = [colors[:16], colors[16:]]

    for colors_gr in liste_gr_colors:
        canva = tk.Canvas(root, bg=BG, height= 90, width= 1000, highlightthickness=0, bd=0)

        decallage = 62
        longeur_ligne = 50 + decallage*(len(colors_gr) - 1)
        debut = 500 - (longeur_ligne // 2)

        canva.photos_list = getattr(canva, 'photos_list', []) # pyright: ignore[reportAttributeAccessIssue]
        canva.img_list = getattr(canva, 'img_list', []) # pyright: ignore[reportAttributeAccessIssue]
        for i, color in enumerate(colors_gr):
            img = Image_PIL.new("RGB", (1, 1),"#" + color)

            img_taille = img.resize((50, 50), Image_PIL.Resampling.NEAREST)
                        
            photo = ImageTk.PhotoImage(img_taille)

            canva.create_image(debut + i*decallage, 0, anchor=tk.NW, image= photo, tags=f"Couleur{i:02d}")

            canva.create_text(debut + i*decallage + 25, 58, anchor=tk.CENTER, text="#" + color.upper(), font=("Arial", 7), justify=tk.CENTER, tags="TEXT")

            canva.photos_list.append(photo) # pyright: ignore[reportAttributeAccessIssue]
            canva.img_list.append(img) # pyright: ignore[reportAttributeAccessIssue]
        
        canva.bind("<B1-Motion>", selector.hover)
        canva.bind("<Button-1>", selector.click)
        selector.canvas_list.append(canva)
        
        canva.pack()

    root.mainloop()
    nom_fichier_temp = generate_temp('png')
    dessinateur.stop_thread()
    dessinateur.source_img.save(nom_fichier_temp)
    encode(chemin_fichier, taille=taille, nb_tiles=nb_tiles, image=nom_fichier_temp, couleurs=colors)

def mdl_modif(chemin_fichier:str):
    root = tk.Tk()

    fichier = decode(chemin_fichier)

    taille = fichier.taille
    nb_tiles = fichier.nb_tiles
    colors = fichier.couleurs
    img = fichier.image

    root.title("Création de modele") # Définir le titre de la fenètre
    root.geometry("1000x650") # Définir la taille de la fenètre
    root.configure(bg= BG) # Mettre un background

    tk.Label(root, text=f"Créez votre fichier {get_name(chemin_fichier)} avec les couleurs que vous avez demandé", font=('Arial', 15, 'bold'), bg=BG).pack()

    frame_principale = tk.Frame(root, width=1000, height=271, bg=BG)
    frame_principale.pack()

    tk.Label(frame_principale, text=f"Cette image sera ce que contiendra le fichier\n{get_name(chemin_fichier)} lors de son enregistrement.\nSélectionez des couleurs puis placez les sur cette fenètre\npour le construire.", font=('Arial', 15), bg=BG, justify=tk.CENTER).place(relx=0.7,rely=0.5, anchor=tk.CENTER)

    selector = Selecteur(root)

    ratio = 4
    if taille*nb_tiles*4 < 256:
        ratio = 256//(taille*nb_tiles)

    dessinateur = Dessinateur(frame_principale, selector, image_base= img, ratio=ratio)
    dessinateur.toggle_sauvegarde(False)

    for x in range(taille*ratio, taille*nb_tiles*ratio, taille*ratio):
        dessinateur.canva.create_line(x, 0, x, taille*nb_tiles*ratio, fill="#ffffff")
        dessinateur.canva.create_line(0, x, taille*nb_tiles*ratio, x, fill="#ffffff")

    if len(colors) <= 16:
        liste_gr_colors = [colors]
    else:
        liste_gr_colors = [colors[:16], colors[16:]]

    for colors_gr in liste_gr_colors:
        canva = tk.Canvas(root, bg=BG, height= 90, width= 1000, highlightthickness=0, bd=0)

        decallage = 62
        longeur_ligne = 50 + decallage*(len(colors_gr) - 1)
        debut = 500 - (longeur_ligne // 2)

        canva.photos_list = getattr(canva, 'photos_list', []) # pyright: ignore[reportAttributeAccessIssue]
        canva.img_list = getattr(canva, 'img_list', []) # pyright: ignore[reportAttributeAccessIssue]
        for i, color in enumerate(colors_gr):
            img = Image_PIL.new("RGB", (1, 1),"#" + color)

            img_taille = img.resize((50, 50), Image_PIL.Resampling.NEAREST)
                        
            photo = ImageTk.PhotoImage(img_taille)

            canva.create_image(debut + i*decallage, 0, anchor=tk.NW, image= photo, tags=f"Couleur{i:02d}")

            canva.create_text(debut + i*decallage + 25, 58, anchor=tk.CENTER, text="#" + color.upper(), font=("Arial", 7), justify=tk.CENTER, tags="TEXT")

            canva.photos_list.append(photo) # pyright: ignore[reportAttributeAccessIssue]
            canva.img_list.append(img) # pyright: ignore[reportAttributeAccessIssue]
        
        canva.bind("<B1-Motion>", selector.hover)
        canva.bind("<Button-1>", selector.click)
        selector.canvas_list.append(canva)
        
        canva.pack(pady=10)

    root.mainloop()
    nom_fichier_temp = generate_temp('png')
    dessinateur.stop_thread()
    dessinateur.source_img.save(nom_fichier_temp)

    fichier.close()
    
    encode(chemin_fichier, taille=taille, nb_tiles=nb_tiles, image=nom_fichier_temp, couleurs=colors)