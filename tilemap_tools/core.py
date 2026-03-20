"""
Ce fichier gére toutes les implémentations de base du module `tilemap-tools`
"""
from os import remove, getcwd, listdir
from os.path import isfile, abspath, splitext, join, dirname
from typing import Literal
from .formateur import decode
from .commun import generate_temp, get_color, is_init
from .tilemap_manager import map_create, map_view, map_modif
from .modele_manager import mdl_create, mdl_view, mdl_modif
from atexit import register
from tkinter import Tk, filedialog
import pyxel as px

def open(chemin: str):
    """
    Cette fonction ouvre un fichier `.map` ou `.mdl` et vous retourne la classe qui lui est associée.

    :arg chemin: Le chemin jusqu'au fichier que vous voulez ouvrir.
    :type chemin: str

    :return: Contenu du fichier
    :rtype: `~.Tilemap` | `~.Modele`
    """
    if isfile(abspath(chemin)):
        if splitext(chemin)[1] == ".mdl":
            rep = Modele(chemin)
        elif splitext(chemin)[1] == ".map":
            rep = Tilemap(chemin)
        else:
            raise ValueError("Le chemin n'est pas valide.")
    else:
        raise ValueError("Le chemin n'est pas valide.")

    return rep

@register
def __clean__():
    for file_name in listdir(join(dirname(__file__), "bin")):
        remove(join(dirname(__file__), "bin", file_name))

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

        self.couleurs = []
        for fichier in self.fichiers:
            fichier = decode(fichier)
            for couleur in fichier.couleurs:
                if couleur not in self.couleurs:
                    self.couleurs.append(get_color(couleur))

        self.chemin_fichier = chemin

        elt_fichier.close()

    @staticmethod
    def create(*fichiers_mdls:str | Modele):
        """
        Permet de créer un nouveau fichier `tilemap`.

        :param chemin: Le chemin pour le fichier que vous voulez créer.
        :type chemin: str
        :param noms_fichiers_mdls: Les noms des fichier modèles à utiliser pour construire ce fichier (`Nombre variable d'arguments`).
        Vous pouvez utiliser 1 à 3 fichiers.

        :return: Retourne la classe construite avec ce nouveau fichier.
        :rtype: ~.Tilemap    
        """
        root = Tk()
        root.withdraw()
        chemin = filedialog.asksaveasfilename(title="Créer sous le nom", defaultextension=".map", filetypes=[("Fichier tilemap", "*.map")])

        if chemin == "" or splitext(chemin)[1] != '.map':
            raise ValueError("Le chemin n'est pas valide.")
        
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

    def draw(self):
        pass

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

        :param chemin: Le chemin jusqu'au fichier.
        :type chemin: str
        :param taille: La taille de chaque tuile de ce fichier (1 pixel au minimum et 32 au maximum).
        :type taille: int
        :param nb_tiles: Le nombre de tuiles de coté que doit contenir le fichier.
        :type nb_tiles: Literal[`3`, `4`]
        :param couleurs: La liste des couleurs (code exadecimaux) vous devez indiquer entre 1 et 15 couleurs. 
        De base (ou quand la valeur est `None`) ce sont les couleurs de base de pyxel qui sont sélectionées.
        :type couleurs: List[str] | None
        
        :return: Retourne la classe construite avec ce nouveau fichier.
        :rtype: ~.Modele
        """
        temp = Tk()
        temp.withdraw()
        chemin = filedialog.asksaveasfilename(title="Créer sous le nom", defaultextension=".mdl", filetypes=[("Fichier modèle", "*.mdl")], initialdir=getcwd())

        temp.destroy()
        
        if chemin == "" or splitext(chemin)[1] != '.map':
            raise ValueError("Le chemin n'est pas valide.")

        if taille < 1 or taille > 32:
            raise ValueError("La taille que vous avez indiqué n'est pas valide.")
        
        mdl_create(taille, nb_tiles, chemin, couleurs)

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