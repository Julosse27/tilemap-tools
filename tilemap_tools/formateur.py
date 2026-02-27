"""
Encode et décode les fichier .mdl et .map
"""
from os import remove
from os.path import splitext
from PIL import Image
from time import time
from os.path import dirname, join

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
FICHIER_MDL = ["image", "taille", "nb_tiles", "couleurs"]
FICHIER_MAP = ["image", "fichiers", "modifs"]
VERIFICATION: dict[str, type|list[type]] = {"image": str, "taille": int, "nb_tiles": int, "couleurs": [list, str], "fichiers": [list, str], "modifs": [list, tuple, bytes, str, int, int]}

class Fichier:
    nb_tiles: int
    image: Image.Image
    couleurs: list[str]
    taille: int
    fichiers: list[str]
    modifs: list[tuple[str, str, int, int]]

    def __init__(self, type_fichier:str, elements:dict) -> None:
        _verification(type_fichier, elements, image=Image.Image, modifs=[list, tuple, Image.Image, str, int, int])
        self.TYPE_FICHIER = type_fichier

        for key, value in elements.items():
            setattr(self, key, value)

def _verification(type_fichier, elements, **exception:type | list[type]):
    if type_fichier == ".mdl":
        list_keys = FICHIER_MDL
    elif type_fichier == ".map":
        list_keys = FICHIER_MAP
    else:
        raise NameError(f"Le type{(" " + type_fichier) if type_fichier != None else ""} du fichier que vous voulez encoder n'est pas pris en charge", 
                        name=type_fichier if type_fichier != "" else None)
    
    if len(elements.keys()) != len(list_keys):
        raise ValueError("Il manque des arguments")
    
    for key in elements.keys():
        if key in list_keys:
            verification = VERIFICATION[key] if key not in exception.keys() else exception[key]
            if type(verification) != list:
                if type(elements[key]) != verification:
                    raise TypeError(f"Le type de l'arguments {key} n'est pas valide.")
            else:
                if verification[0] != type(elements[key]):
                    raise TypeError(f"Le type de l'arguments {key} n'est pas valide.")
                
                for element in elements[key]:
                    if type(element) != verification[1]:
                        raise TypeError(f"Le type de l'arguments {key} n'est pas valide.")
                    
                    if verification[1] == tuple:
                        if list(map(type, element)) != verification[2:]:
                            raise TypeError(f"Le type de l'arguments {key} n'est pas valide.")
        else:
            raise NameError("Ce nom ne fait pas partit des arguments demandés.", name=key)

def encode(chemin, **elements):
    if splitext(chemin)[1] == ".mdl":
        type_fichier = ".mdl"
    elif splitext(chemin)[1] == ".map":
        type_fichier = ".map"
    else:
        type_fichier = ""
    _verification(type_fichier, elements)
    
    if type_fichier == ".mdl":
        file = Image.open(elements["image"])
        image = file.copy()
        file.close()
        img_io = open(elements["image"], "rb")
        img_png = img_io.read()
        img_io.close()
        with open(chemin, "wb") as f:
            f.write(img_png + f",,{elements["taille"]},,{elements["nb_tiles"]},,{"\n".join(elements["couleurs"])}".encode())
        remove(elements["image"])
        elements["image"] = image
    elif type_fichier == ".map":
        file = Image.open(elements["image"])
        image = file.copy()
        file.close()
        img_io = open(elements["image"], "rb")
        img_png = img_io.read()
        img_io.close()
        modifs_list:list[bytes] = []
        for img, nom_fichier, x, y in elements["modifs"]:
            modifs_list.append(img + b",," + nom_fichier.encode() + b",," + f'{x}'.encode() + b',,' + f'{y}'.encode())
        modifs = b"!!".join(modifs_list)
        fichiers_mdl = "!!".join(elements["fichiers"]).encode()

        with open(chemin, "wb") as f:
            f.write(img_png + b"&&" + modifs + b'&&' + fichiers_mdl)
        remove(elements["image"])
        elements["image"] = image

def decode(chemin:str):
    if splitext(chemin)[1] == ".mdl":
        type_fichier = '.mdl'
    elif splitext(chemin)[1] == ".map":
        type_fichier = '.map'
    else:
        raise NameError(f"Le type{(" " + splitext(chemin)[1]) if splitext(chemin)[1] != None else ""} du fichier que vous voulez encoder n'est pas pris en charge", 
                        name=splitext(chemin)[1] if splitext(chemin)[1] != "" else None)
    
    elements = {}

    fichier_temp = f'{join(dirname(__file__), "pyxres_bin", f"bin_{int(time() * 10)}")}'

    if type_fichier == ".mdl":
        with open(chemin, "rb") as f:
            liste = f.read().split(b",,")
            elements["image"] = b",,".join(liste[:-3])
            elements["taille"] = int(liste[-3])
            elements["nb_tiles"] = int(liste[-2])
            elements["couleurs"] = liste[-1].decode()
    
        with open(fichier_temp + ".png", "wb") as d:
            d.write(elements["image"])

        file = Image.open(fichier_temp + ".png")
        elements["image"] = file.copy()
        file.close()
        remove(fichier_temp + ".png")
    elif type_fichier == ".map":
        with open(chemin, "rb") as f:
            liste = f.read().split(b"&&")
        print(len(liste))

        with open(fichier_temp + ".png", "wb") as d:
            d.write(liste[0])

        file = Image.open(fichier_temp + ".png")
        elements["image"] = file.copy()
        file.close()
        
        remove(fichier_temp + '.png')

        modifs = []
        for modif_raw in liste[1].split(b"!!"):
            list_raw = modif_raw.split(b',,')
            with open(fichier_temp + ".png", "wb") as f:
                f.write(list_raw[0])
            file = Image.open(fichier_temp + '.png')
            image = file.copy()
            file.close()

            remove(fichier_temp + '.png')

            modifs.append((image, list_raw[1].decode(), int(list_raw[2]), int(list_raw[3])))

        elements["modifs"] = modifs
        elements["fichiers"] = liste[2].decode().split('!!')

    return Fichier(type_fichier, elements)