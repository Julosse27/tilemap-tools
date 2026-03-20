"""Fichier qui gère toutes les commandes en rapport avec les fichiers tilemaps"""
from PIL import Image as Image_PIL, ImageTk
import tkinter as tk
from .formateur import encode, decode
from .commun import get_name, generate_temp, Dessinateur, Selecteur

BG = "#774634"
COULEUR_ECRITURE = "#F4A460"

def map_view(nom_fichier:str, root: tk.Tk | None=None):
    if root == None:
        root = tk.Tk() # Créer une fenètre avec tkinter
    else:
        root.deiconify()

    fichier = decode(nom_fichier)
    root.title(f"Visualisation de la tilemap {get_name(nom_fichier)}")
    root.configure(bg=BG)
    root.geometry("1000x550")

    tk.Label(root, bg=BG, fg=COULEUR_ECRITURE, font=("Arial", 20, "bold"), text=f"Voici le contenu du fichier {get_name(nom_fichier)}").pack(pady=(5, 10))

    frame = tk.Frame(root, width=1000, height=300, bg=BG)
    frame.pack()

    dessinateur = Dessinateur(frame, image_base=fichier.image, cursor= "target")

    text = tk.StringVar(root, "Vous n'avez pas encore cliqué sur une tuile.")

    def change():
        if dessinateur.dernier_click != None:
            x_click, y_click = dessinateur.dernier_click
            for image, nom_fichier, x, y in fichier.modifs.__reversed__():
                if (x_click > x and x_click < x + image.width) and (y_click > y and y_click < y + image.height):
                    text.set(f"Vous avez cliqué sur la tuile aux coordonnées {x_click} {y_click}\nvenant du fichier {nom_fichier}")
                    img = ImageTk.PhotoImage(image.copy().resize([100, 100], resample=Image_PIL.Resampling.NEAREST))
                    
                    image_pres.config(image=img)
                    image_pres.img = img # pyright: ignore[reportAttributeAccessIssue]
                    break

    dessinateur.set_callback(change)

    tk.Label(root, bg=BG, fg=COULEUR_ECRITURE, font=("Arial", 15), textvariable=text, justify=tk.CENTER).pack(pady=(0, 15))

    tk.Label(frame, bg=BG, fg=COULEUR_ECRITURE, font=("Arial", 15), text="Cliquez sur une partie de l'image pour savoir\nd'où vient cette tuile.", justify=tk.CENTER).place(relx=0.75, rely=0.5, anchor=tk.CENTER)

    image_pres = tk.Label(root, bg=BG)
    image_pres.pack()

    root.mainloop()
    dessinateur.stop_thread()
    fichier.close()

def map_create(noms_fichiers_mdl:list[str], nom_fichier:str, root: tk.Tk | None=None):
    if root == None:
        root = tk.Tk() # Créer une fenètre avec tkinter
    else:
        root.deiconify()
    nom_fichier_temp = generate_temp("png")

    liste_tiles: list[list[tuple[Image_PIL.Image, int, int, int, str]]] = []
    for fichier_mdl in noms_fichiers_mdl:
        fichier = decode(fichier_mdl)
        image = fichier.image
        taille = fichier.taille
        nb = fichier.nb_tiles
        
        images_tiles: list[tuple[Image_PIL.Image, int, int, int, str]] = []
        tile_x = 0
        for x in range(0, image.width, taille):
            tile_y = 0
            for y in range(0, image.height, taille):
                partie_img = image.crop((x, y, x + taille, y + taille)) # Prend juste une tile de l'image du modèle
                images_tiles.append((partie_img, tile_x, tile_y, nb, get_name(fichier_mdl))) # L'ajoute à la liste
                tile_y += 1 # Met à jour les coordonnées de la tuile
            tile_x += 1
        liste_tiles.append(images_tiles)
        fichier.close()
    root.title("Création de tilemaps") # Définir le titre de la fenètre
    root.geometry("1000x650") # Définir la taille de la fenètre
    root.configure(bg= BG) # Mettre un background
    # Permet d'équilibrer la fenètre pour ne pas avoir un élément qui prend plus de place qu'un autre.

    tk.Label(root, text=f"Créez votre fichier {get_name(nom_fichier)} avec les éléments que vous avez demandé", font=('Arial', 15, 'bold'), bg=BG, fg=COULEUR_ECRITURE).pack()

    frame_principale = tk.Frame(root, width=1000, height=271, bg=BG)
    frame_principale.pack()

    tk.Label(frame_principale, text=f"Cette image sera ce que contiendra le fichier\n{get_name(nom_fichier)} lors de son enregistrement.\nSélectionez des tuiles puis placez les sur cette fenètre\npour le construire.", font=('Arial', 15), bg=BG, justify=tk.CENTER, fg=COULEUR_ECRITURE).place(relx=0.7,rely=0.5, anchor=tk.CENTER)

    selector = Selecteur(root)

    dessinateur = Dessinateur(frame_principale, selector)

    root.bind("<Control-z>", dessinateur.annuler)

    for i, images in enumerate(liste_tiles):
        tk.Label(root, text=f"Voici le contenu du fichier {get_name(noms_fichiers_mdl[i])}", font=("Arial", 9, "bold"), bg=BG, fg=COULEUR_ECRITURE).pack()
        canva = tk.Canvas(root, bg=BG, height= 90, width= 1000, highlightthickness=0, bd=0)

        decallage = 62
        longeur_ligne = 50 + decallage*(len(images) - 1)
        debut = 500 - (longeur_ligne // 2)

        canva.photos_list = getattr(canva, 'photos_list', []) # pyright: ignore[reportAttributeAccessIssue]
        canva.img_list = getattr(canva, 'img_list', []) # pyright: ignore[reportAttributeAccessIssue]
        for i, elements in enumerate(images):
            img, tile_x, tile_y, nb, nom = elements

            img_taille = img.resize((50, 50), Image_PIL.NEAREST) # pyright: ignore[reportAttributeAccessIssue]

            photo = ImageTk.PhotoImage(img_taille)

            canva.create_image(debut + i*decallage, 0, anchor=tk.NW, image= photo, tags=f"{nom}{i}")

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

            canva.create_text(debut + i*decallage + 25, 53 + 5*len(nom.splitlines()), anchor=tk.CENTER, text=nom, font=("Arial", 7), justify=tk.CENTER, tags="TEXT", fill=COULEUR_ECRITURE)

            canva.photos_list.append(photo) # pyright: ignore[reportAttributeAccessIssue]
            canva.img_list.append(img) # pyright: ignore[reportAttributeAccessIssue]

        canva.bind("<B1-Motion>", selector.hover)
        canva.bind("<Button-1>", selector.click)
        selector.canvas_list.append(canva)
        
        canva.pack()

    root.mainloop()
    dessinateur.stop_thread()
    dessinateur.source_img.save(nom_fichier_temp)
    encode(nom_fichier, image=nom_fichier_temp, fichiers=noms_fichiers_mdl, modifs=dessinateur.list_contruction)

def map_modif(nom_fichier:str, root: tk.Tk | None=None):
    if root == None:
        root = tk.Tk() # Créer une fenètre avec tkinter
    else:
        root.deiconify()
    fichier_origine = decode(nom_fichier)

    liste_tiles: list[list[tuple[Image_PIL.Image, int, int, int, str]]] = []
    for fichier_mdl in fichier_origine.fichiers:
        fichier = decode(fichier_mdl)
        image = fichier.image
        taille = fichier.taille
        nb = fichier.nb_tiles
        
        images_tiles: list[tuple[Image_PIL.Image, int, int, int, str]] = []
        tile_x = 0
        for x in range(0, image.width, taille):
            tile_y = 0
            for y in range(0, image.height, taille):
                partie_img = image.crop((x, y, x + taille, y + taille)) # Prend juste une tile de l'image du modèle
                images_tiles.append((partie_img, tile_x, tile_y, nb, fichier_mdl)) # L'ajoute à la liste
                tile_y += 1 # Met à jour les coordonnées de la tuile
            tile_x += 1
        liste_tiles.append(images_tiles)
        fichier.close()

    root.title("Modification de tilemaps") # Définir le titre de la fenètre
    root.geometry("1000x650") # Définir la taille de la fenètre
    root.configure(bg= BG) # Mettre un background
    # Permet d'équilibrer la fenètre pour ne pas avoir un élément qui prend plus de place qu'un autre.

    tk.Label(root, text=f"Créez votre fichier {get_name(nom_fichier)} avec les éléments que vous avez demandé", font=('Arial', 15, 'bold'), bg=BG, fg=COULEUR_ECRITURE).pack()

    frame_principale = tk.Frame(root, width=1000, height=271, bg=BG)
    frame_principale.pack()

    tk.Label(frame_principale, text=f"Cette image sera ce que contiendra le fichier\n{get_name(nom_fichier)} lors de son enregistrement.\nSélectionez des tuiles puis placez les sur cette fenètre\npour le construire.", font=('Arial', 15), bg=BG, justify=tk.CENTER, fg=COULEUR_ECRITURE).place(relx=0.7,rely=0.5, anchor=tk.CENTER)

    selector = Selecteur(root)

    dessinateur = Dessinateur(frame_principale, selector, image_base=fichier_origine.image, modifs=fichier_origine.get_raw_modifs())

    root.bind("<Control-z>", dessinateur.annuler)

    for i, images in enumerate(liste_tiles):
        tk.Label(root, text=f"Voici le contenu du fichier {get_name(fichier_origine.fichiers[i])}", font=("Arial", 9, "bold"), bg=BG, fg=COULEUR_ECRITURE).pack()
        canva = tk.Canvas(root, bg=BG, height= 90, width= 1000, highlightthickness=0, bd=0)

        decallage = 62
        longeur_ligne = 50 + decallage*(len(images) - 1)
        debut = 500 - (longeur_ligne // 2)

        canva.photos_list = getattr(canva, 'photos_list', []) # pyright: ignore[reportAttributeAccessIssue]
        canva.img_list = getattr(canva, 'img_list', []) # pyright: ignore[reportAttributeAccessIssue]
        for i, elements in enumerate(images):
            img, tile_x, tile_y, nb, nom = elements

            img_taille = img.resize((50, 50), Image_PIL.NEAREST) # pyright: ignore[reportAttributeAccessIssue]

            photo = ImageTk.PhotoImage(img_taille)

            canva.create_image(debut + i*decallage, 0, anchor=tk.NW, image= photo, tags=f"{nom}{i}")

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

            canva.create_text(debut + i*decallage + 25, 53 + 5*len(nom.splitlines()), anchor=tk.CENTER, text=nom, font=("Arial", 7), justify=tk.CENTER, tags="TEXT", fill=COULEUR_ECRITURE)

            canva.photos_list.append(photo) # pyright: ignore[reportAttributeAccessIssue]
            canva.img_list.append(img) # pyright: ignore[reportAttributeAccessIssue]

        canva.bind("<B1-Motion>", selector.hover)
        canva.bind("<Button-1>", selector.click)
        selector.canvas_list.append(canva)
        
        canva.pack()

    root.mainloop()
    dessinateur.stop_thread()
    fichier_temp = generate_temp("png")
    dessinateur.source_img.save(fichier_temp)
    encode(nom_fichier, image=fichier_temp, fichiers=fichier_origine.fichiers, modifs=dessinateur.list_contruction)
