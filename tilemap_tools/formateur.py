"""
Encode et décode les fichier .mdl et .map
"""
from os import remove
from os.path import splitext
from PIL import Image
from .commun import generate_temp
from typing import Literal

# PNG_DEBUT = b'\x89PNG\r\n\x1a\n'
# PNG_FIN = b"IEND\xae\x42\x60\x82"
FICHIER_MDL = ["image", "taille", "nb_tiles", "couleurs"]
FICHIER_MAP = ["image", "fichiers", "modifs"]
VERIFICATION: dict[str, type|list[type]] = {"image": str, "taille": int, "nb_tiles": int, "couleurs": str, "fichiers": [list, tuple, str, str], "modifs": [list, tuple, bytes, str, int, int]}

class Fichier:
    _type_fichier: Literal['.mdl', ".map"]
    @property
    def type_fichier(self):
        """Le type du fichier"""
        return self._type_fichier
    
    @type_fichier.setter
    def type_fichier(self, type_f: Literal[".map", ".mdl"]):
        self._type_fichier = type_f

    _nb_tiles: int
    @property
    def nb_tiles(self):
        """Nombre de tuiles de chaque coté d'un fichier .mdl"""
        return self._nb_tiles

    @nb_tiles.setter
    def nb_tiles(self, nb:int):
        self._nb_tiles = nb

    _image: Image.Image
    @property
    def image(self):
        """L'image principale d'un fichier .mdl ou .map"""
        return self._image.copy()
    
    @image.setter
    def image(self, chemin:str):
        file = Image.open(chemin)
        self._image = file.copy()
        file.close()

        remove(chemin)

    _couleurs: list[str]
    @property
    def couleurs(self):
        """La liste des couleurs d'un fichier .mdl"""
        return self._couleurs
    
    @couleurs.setter
    def couleurs(self, couleurs:str):
        self._couleurs = couleurs.splitlines()
    
    _taille: int
    @property
    def taille(self):
        """La taille d'une tuile d'un fichier .mdl"""
        return self._taille
    
    @taille.setter
    def taille(self, nv_taille:int):
        self._taille = nv_taille
    
    _fichiers: list[tuple[str, str]]
    @property
    def fichiers(self):
        """La liste du nom des fichiers et de leurs couleurs d'un fichier .map"""
        return self._fichiers
    
    @fichiers.setter
    def fichiers(self, files: list[tuple[str, str]]):
        self._fichiers = files

    _modifs: list[tuple[Image.Image, str, int, int]]
    @property
    def modifs(self) -> list[tuple[Image.Image, str, int, int]]:
        """La liste de toutes les modification apportées à ce fichier .map"""
        res = []
        for image, nom, x, y in self._modifs:
            
            res.append((image.copy(), nom, x, y))
        
        return res
    
    @modifs.setter
    def modifs(self, file_modifs:list[tuple[bytes, str, int, int]]):
        nv_modifs: list[tuple[Image.Image, str, int, int]] = []
        for image, nom, x, y in file_modifs:
            fichier_temp = generate_temp('png')
            with open(fichier_temp, "wb") as f:
                f.write(image)
            
            file = Image.open(fichier_temp)
            nv_modifs.append((file.copy(), nom, x, y))
            file.close()
            remove(fichier_temp)
        
        self._modifs = nv_modifs

    def __init__(self, type_fichier:str, elements:dict) -> None:
        _verification(type_fichier, elements)
        self.type_fichier = type_fichier # pyright: ignore[reportAttributeAccessIssue]

        for key, value in elements.items():
            setattr(self, key, value)

    def close(self):
        self._image.close()

        if self.type_fichier == ".map":
            for modif in self._modifs:
                modif[0].close()

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
    type_fichier = splitext(chemin)[1]
    _verification(type_fichier, elements)
    
    if type_fichier == ".mdl":
        img_io = open(elements["image"], "rb")
        img_png = img_io.read()
        img_io.close()
        with open(chemin, "wb") as f:
            f.write(img_png + f",,{elements["taille"]},,{elements["nb_tiles"]},,{"\n".join(elements["couleurs"])}".encode())
        remove(elements["image"])
    elif type_fichier == ".map":
        img_io = open(elements["image"], "rb")
        img_png = img_io.read()
        img_io.close()
        modifs_list:list[bytes] = []
        for img, nom_fichier, x, y in elements["modifs"]:
            modifs_list.append(img + b",," + nom_fichier.encode() + b",," + f'{x}'.encode() + b',,' + f'{y}'.encode())
        modifs = b"!!".join(modifs_list)
        for i, fichier in enumerate(elements["fichiers"]):
            elements["fichiers"][i] = ",,".join(fichier)
        fichiers_mdl = "!!".join(elements["fichiers"]).encode()

        with open(chemin, "wb") as f:
            f.write(img_png + b"&&" + modifs + b'&&' + fichiers_mdl)
        remove(elements["image"])

def decode(chemin:str):
    if splitext(chemin)[1] == ".mdl":
        type_fichier = '.mdl'
    elif splitext(chemin)[1] == ".map":
        type_fichier = '.map'
    else:
        raise NameError(f"Le type{(" " + splitext(chemin)[1]) if splitext(chemin)[1] != None else ""} du fichier que vous voulez encoder n'est pas pris en charge", 
                        name=splitext(chemin)[1] if splitext(chemin)[1] != "" else None)
    
    elements = {}

    fichier_temp = generate_temp("png")

    if type_fichier == ".mdl":
        with open(chemin, "rb") as f:
            liste = f.read().split(b",,")
            elements["image"] = b",,".join(liste[:-3])
            elements["taille"] = int(liste[-3])
            elements["nb_tiles"] = int(liste[-2])
            elements["couleurs"] = liste[-1].decode()
    
        with open(fichier_temp, "wb") as d:
            d.write(elements["image"])
            
        elements["image"] = fichier_temp
    elif type_fichier == ".map":
        with open(chemin, "rb") as f:
            liste = f.read().split(b"&&")

        with open(fichier_temp, "wb") as d:
            d.write(liste[0])

        elements["image"] = fichier_temp

        modifs = []
        for modif_raw in liste[1].split(b"!!"):
            list_raw = modif_raw.split(b',,')

            modifs.append((list_raw[0], list_raw[1].decode(), int(list_raw[2]), int(list_raw[3])))

        elements["modifs"] = modifs
        fichiers = []
        for element in liste[2].decode().split('!!'):
            fichiers.append(tuple(element.split(",,")))
        elements["fichiers"] = fichiers

    return Fichier(type_fichier, elements)