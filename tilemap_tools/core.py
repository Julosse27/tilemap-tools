"""
Ce fichier gére toutes les implémentations de base du module `tilemap-tools`
"""
from os import remove, getcwd, listdir
from os.path import isfile, abspath, splitext, join, dirname
from typing import Literal
from .formateur import decode
from .commun import generate_temp, get_color, is_init, FICHIER_COLORS, add_color
from .tilemap_manager import map_create, map_view, map_modif
from .modele_manager import mdl_create, mdl_view, mdl_modif
from atexit import register
from tkinter import Tk, filedialog
from PIL import Image
import pyxel as px

@register
def __clean__():
    for file_name in listdir(join(dirname(__file__), "bin")):
        remove(join(dirname(__file__), "bin", file_name))

liste_tilemaps:list[Tilemap] = []

ancien_init = px.init

def new_init(width: int, height: int, *, title: str | None = None, fps: int | None = None, quit_key: int | None = None, display_scale: int | None = None, capture_scale: int | None = None, capture_sec: int | None = None):
    ancien_init(width, height, title= title, fps= fps, quit_key = quit_key, display_scale = display_scale, capture_scale = capture_scale, capture_sec = capture_sec)    
    if isfile(FICHIER_COLORS):
        px.load_pal(FICHIER_COLORS)

    global COULEUR_TRANSPARENTE
    COULEUR_TRANSPARENTE = add_color("000000")

    for tilemap in liste_tilemaps:
        tilemap.__load__()

    remove(FICHIER_COLORS)

px.init = new_init

class Tilemap:
    """
    Celle classe regroupe tout les différents fonctionnements que peut avoir un fichier tilemap.

    :arg chemin: Le chemin jusqu'au fichier de tilemap (en `.map`).
    :type chemin: str
    """
    def __init__(self, chemin: str) -> None:
        """Initialisation de l'objet `Tilemap`"""
        if splitext(chemin)[1] != ".map":
            raise ValueError("Le fichier n'est pas sous la bonne extension.")
        if not isfile(abspath(chemin)):
            raise ValueError("Le chemin jusqu'au fichier n'est pas valide.")
        
        elt_fichier = decode(chemin)
        
        chemin_img = generate_temp()
        self.chemin_img = chemin_img + ".png"
        elt_fichier.img_save(chemin_img)
        self.modifs = elt_fichier.get_raw_modifs()
        self.fichiers = elt_fichier.fichiers
        self.couleurs: dict[str, int] = {}
        
        for fichier in self.fichiers:
            fichier = decode(fichier)
            for couleur in fichier.couleurs:
                if couleur not in self.couleurs:
                    self.couleurs[couleur] = get_color(couleur)

        self.chemin_fichier = chemin

        if is_init():
            self.__load__()
        else:
            liste_tilemaps.append(self)

    @staticmethod
    def create(*fichiers_mdls:str | Modele):
        """
        Permet de créer un nouveau fichier `tilemap`.

        Parameter
        ---------
        fichiers_mdls: str | Modele
            Les noms des fichier modèles à utiliser pour construire ce fichier (`Nombre variable d'arguments`).
            Vous pouvez utiliser 1 à 3 fichiers.
            
        Return
        -------
        ~.Tilemap
            Retourne la classe construite avec ce nouveau fichier.  
        """
        if len(fichiers_mdls) < 1 or len(fichiers_mdls) > 3:
            raise ValueError("Vous ne pouvez utiliser que 1 à 3 fichier modèles.")
        
        fichiers = []
        for fichier in fichiers_mdls:
            if type(fichier) == str:
                if splitext(fichier)[1] != '.mdl':
                    raise ValueError("Un des chemin des fichier modèles est incorect.")
                if not isfile(abspath(fichier)):
                    raise ValueError("Un des chemin des fichier modèles est incorect.")
                fichiers.append(fichier)
            else:
                fichiers.append(fichier.chemin_fichier) # pyright: ignore[reportAttributeAccessIssue]

        root = Tk()
        root.withdraw()
        chemin = filedialog.asksaveasfilename(title="Créer sous le nom", defaultextension=".map", filetypes=[("Fichier tilemap", "*.map")])

        if chemin == "" or splitext(chemin)[1] != '.map':
            raise ValueError("Le chemin n'est pas valide.")
        
        map_create(fichiers, chemin, root)

        return Tilemap(chemin)

    def view(self):
        map_view(self.chemin_fichier)

    def modif(self):
        map_modif(self.chemin_fichier)
        
        elt_fichier = decode(self.chemin_fichier)

        chemin_img = generate_temp()
        self.chemin_img = chemin_img + ".png"
        elt_fichier.img_save(chemin_img)
        self.modifs = elt_fichier.get_raw_modifs()
        self.fichiers = elt_fichier.fichiers

        elt_fichier.close()

    def __load__(self):
        """
        Est éxécutée automatiquement lors de l'initialisation de pyxel ou lors de la création de cet objet,
        permet de mettre en place l'affichage de cette `tilemap`.
        """
        img_fichier = Image.open(self.chemin_img) # pyright: ignore[reportArgumentType]
        pixels = img_fichier.load()

        self.__image_px = px.Image(*img_fichier.size)

        for x in range(img_fichier.width):
            for y in range(img_fichier.height):
                rouge, vert, bleu, alpha = pixels[x, y]  # pyright: ignore[reportGeneralTypeIssues, reportOptionalSubscript]
                
                if alpha == 254: # pyright: ignore[reportIndexIssue]
                    self.__image_px.pset(x, y, COULEUR_TRANSPARENTE)
                else:
                    code_couleur = f"{hex(rouge)[2:]:02}{hex(vert)[2:]:02}{hex(bleu)[2:]:02}"

                    self.__image_px.pset(x, y, self.couleurs[code_couleur])

        remove(self.chemin_img) # pyright: ignore[reportArgumentType]
        self.chemin_img = None

    def draw(self, x:int, y:int, x_tile:int, y_tile:int, width:int, height:int, scale:float|None = None):
        """
        Permet de dessiner une partie de la tilemap aux coordonnées données (`x`, `y`).

        Si `pyxel` n'est pas initialisé cette fonction renverra une erreur

        Parameters
        -----------
        x: int
            La coordonnée `x` où doit être déssiné cette partie de la tilemap.
        y: int
            La coordonnée `y` où doit être déssiné cette partie de la tilemap.
        x_tile: int
            La coordonnée `x` sur la tilemap où doit commencer la partie de la tilemap.
        y_tile: int
            La coordonnée `y` sur la tilemap où doit commencer la partie de la tilemap.
        width: int
            La largeur que doit avoir le bout de tilemap que vous voulez dessiner.
        height: int
            La hauteur que doit avoir le bout de tilemap que vous voulez dessiner.
        scale: float
            (`Cet argument est optionel`) Permet de dessiner la tilemap sous une certaine taille.
        """
        if not is_init():
            raise SystemError("Pyxel n'est pas initialisé.")
        
        px.blt(x, y, self.__image_px, x_tile, y_tile, width, height, COULEUR_TRANSPARENTE, scale=scale)

class Modele:
    """
    Celle classe regroupe tout les différents fonctionnements que peut avoir un fichier modèle.

    :arg chemin: Le chemin jusqu'au fichier modèle (en `.mdl`).
    :type chemin: str
    """

    def __init__(self, chemin:str) -> None:
        """Initialisation de l'objet `Modele`"""
        if splitext(chemin)[1] != ".mdl":
            raise ValueError("Le fichier n'est pas sous la bonne extension.")
        if not isfile(abspath(chemin)):
            raise ValueError("Le chemin jusqu'au fichier n'est pas valide.")
        
        elt_fichier = decode(chemin)

        chemin_img = generate_temp()
        self.chemin_img = chemin_img + ".png"
        elt_fichier.img_save(chemin_img)
        self.taille = elt_fichier.taille
        self.nb_tiles = elt_fichier.nb_tiles
        self.couleurs = elt_fichier.couleurs
        self.chemin_fichier = chemin

        elt_fichier.close()

    @staticmethod
    def create(taille:int, nb_tiles: Literal[3, 4] = 3, couleurs:list[str] | None = None):
        """
        Permet de créer un nouveau fichier `modèle`.

        Parameters
        -----------
        chemin: str
            Le chemin jusqu'au fichier.
        taille: int
            La taille de chaque tuile de ce fichier (1 pixel au minimum et 32 au maximum).
        nb_tiles: Literal[`3`, `4`]
            Le nombre de tuiles de coté que doit contenir le fichier.
        couleurs: List[str] | None
            La liste des couleurs (code exadecimaux) vous devez indiquer entre 1 et 15 couleurs. 
            De base (ou quand la valeur est `None`) ce sont les couleurs de base de pyxel qui sont sélectionées.
        
        Return
        --------
        ~.Modele
            Retourne la classe construite avec ce nouveau fichier.
        """
        if taille < 1 or taille > 32:
            raise ValueError("La taille que vous avez indiqué n'est pas valide.")
        
        if nb_tiles not in (3, 4):
            raise ValueError("Le nombre de tuile n'est pas valide.")

        temp = Tk()
        temp.withdraw()
        chemin = filedialog.asksaveasfilename(title="Créer sous le nom", defaultextension=".mdl", filetypes=[("Fichier modèle", "*.mdl")], initialdir=getcwd())
        
        if chemin == "" or splitext(chemin)[1] != '.mdl':
            raise ValueError("Le chemin n'est pas valide.")
        
        mdl_create(taille, nb_tiles, chemin, couleurs, temp)

        return Modele(chemin)

    def view(self):
        mdl_view(self.chemin_fichier)

    def modif(self):
        mdl_modif(self.chemin_fichier)
        
        elt_fichier = decode(self.chemin_fichier)

        chemin_img = generate_temp()
        self.chemin_img = chemin_img + ".png"
        elt_fichier.img_save(chemin_img)
        self.taille = elt_fichier.taille
        self.nb_tiles = elt_fichier.nb_tiles
        self.couleurs = elt_fichier.couleurs

        elt_fichier.close()