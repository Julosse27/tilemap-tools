"""Commande pour créer des modèles de tilemaps"""
from subprocess import run
from os.path import dirname, join, exists
from os import remove
from time import time, sleep
from pyxel import load, init, images, colors as col, Image, save, load_pal
from PIL import Image as Image_PIL

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
    