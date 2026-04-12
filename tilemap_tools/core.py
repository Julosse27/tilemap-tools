"""
Ce fichier gére toutes les implémentations de base du module `tilemap-tools`
"""
from os import remove, getcwd, listdir
from os.path import isfile, abspath, splitext, join, dirname
from typing import Literal, Callable
from atexit import register
from tkinter import Tk, filedialog
from PIL import Image
import pyxel as px
from time import time_ns
from random import choice
from .formateur import decode
from .commun import generate_temp, get_color, is_px_init, FICHIER_COLORS, add_color
from .tilemap_manager import map_create, map_view, map_modif
from .modele_manager import mdl_create, mdl_view, mdl_modif

@register
def __clean__():
    for file_name in listdir(join(dirname(__file__), "bin")): # pyright: ignore[reportArgumentType]
        remove(join(dirname(__file__), "bin", file_name))

liste_anim:list[Animation] = []

ancien_init = px.init

get_color("000000")
COULEUR_TRANSPARENTE = add_color("000000")
TPS_DEBUT: int # Stocke le moment exact (à la nanoseconde près) le moment où le jeu démarre
__tps_frame: int = 0 # Stocke le temps qui s'est passé en nanosecondes depuis le lancement du jeu

def get_time():
    """
    Donne le temps qui s'est passé depuis le lancement du jeu (en milisecondes)
    """
    return __tps_frame / 1000000

def new_init(width: int, height: int, *, title: str | None = None, fps: int | None = None, quit_key: int | None = None, display_scale: int | None = None, capture_scale: int | None = None, capture_sec: int | None = None):
    ancien_init(width, height, title= title, fps= fps, quit_key = quit_key, display_scale = display_scale, capture_scale = capture_scale, capture_sec = capture_sec)    
    if isfile(FICHIER_COLORS):
        px.load_pal(FICHIER_COLORS)

    remove(FICHIER_COLORS)

px.init = new_init

ancien_run = px.run

def new_run(update: Callable[[], None], draw: Callable[[], None]):
    global TPS_DEBUT
    TPS_DEBUT = time_ns()
    def new_update():
        # faire les updates nécésaires
        global __tps_frame
        __tps_frame = time_ns() - TPS_DEBUT

        for anim in liste_anim:
            anim.update()
        update()

    def new_draw():
        # faire les potentiels dessins (peut être à supprimer)

        draw()

    ancien_run(new_update, new_draw)

px.run = new_run

class Texture:
    """
    La texture de n'importe lequel des élément que propose ce module.
    """
    master_elt: Element
    def __init__(self, x: int, y: int, image: px.Image, scale: float) -> None:
        self.__x__ = x
        self.__y__ = y
        self.x_draw = int(x + (scale - 1) / 2 * image.width)
        self.y_draw = int(y + (scale - 1) / 2 * image.height)
        
        width = int(image.width * scale) + (2 if image.width * scale % 2 > 1 else 0)
        height = int(image.height * scale) + (2 if image.height * scale % 2 > 1 else 0)

        self.image = image
        self.scale = scale

        self.hit_box: dict[int, dict[int, Literal[True]]] = {}

        hit_img = px.Image(width, height)
        hit_img.blt(0, 0, image, 0, 0, image.width, image.height, scale=scale)

        hit_limits = [-1, -1, -1, -1]
        
        for x_hit in range(hit_img.width):
            abs_x = x_hit + x
            self.hit_box[abs_x] = {}

            flag_y_min = True
            for y_hit in range(hit_img.height):
                if hit_img.pget(x_hit, y_hit) != COULEUR_TRANSPARENTE:
                    abs_y = y_hit + y
                    if flag_y_min:
                        if hit_limits[2] > abs_y:
                            hit_limits[2] = abs_y
                            flag_y_min = False
                    if hit_limits[3] < abs_y:
                        hit_limits[3] = abs_y
                    
                    self.hit_box[abs_x][abs_y] = True
            
            if len(self.hit_box[abs_x]) == 0:
                del self.hit_box[abs_x]
            else:
                if hit_limits[0] == -1:
                    hit_limits[0] = abs_x
                else:
                    hit_limits[1] = abs_x

        self.hit_limits: tuple[int, int, int, int] = tuple(hit_limits) # pyright: ignore[reportAttributeAccessIssue]

    def changer_placement(self, x: int, y: int):
        x_ch = x - self.__x__
        y_ch = y - self.__y__
        self.__x__ = x
        self.__y__ = y
        self.x_draw = int(x + (self.scale - 1) / 2 * self.image.width)
        self.y_draw = int(y + (self.scale - 1) / 2 * self.image.height)
        

        old_hitbox = self.hit_box
        self.hit_box: dict[int, dict[int, Literal[True]]] = {}

        for old_x, all_y in old_hitbox.items():
            abs_x = old_x + x_ch
            self.hit_box[abs_x] = {}
            for old_y in all_y.keys():
                self.hit_box[abs_x][old_y + y_ch] = True
        
        self.hit_limits = (self.hit_limits[0] + x_ch, self.hit_limits[1] + x_ch, self.hit_limits[2] + y_ch, self.hit_limits[3] + y_ch)        

    def copy(self):
        """
        Retourne une copie exacte de cette texture.
        """
        rep = self.__new__(type(self))

        rep.x_draw = self.x_draw
        rep.y_draw = self.y_draw

        rep.image = self.image
        rep.scale = self.scale

        rep.hit_box = self.hit_box

        return rep

    def draw(self):
        """
        Dessine cette texture aux coordonnées données.
        """
        
        px.blt(self.x_draw + self.master_elt.decallage_x, self.y_draw + self.master_elt.decallage_y, self.image, 0, 0, self.image.width, self.image.height, COULEUR_TRANSPARENTE, scale=self.scale)

class Animation:
    """
    La base de n'importe quelle animation.

    Args
    ------
    type_anim : Literal["idle"]
        Le type d'annimation que vous voulez définir. Chaque type d'animation a besoin de certains paramètres.
        Voici la liste des paramètres pour chaque type d'animation:
            - Pour une animation de type `idle` il ne faut remplir que le paramètre <param>`temps_anim`
            qui correspond au temps, en milisecondes, entre chaque stades de l'animation ou le temps après 
            chaque stade: le premier après la première image donnée etc... Vous pouvez aussi remplir le 
            paramètre <param>`images` qui correspond à l'indice des images que vous voulez utiliser pour
            cette animation.
            - Pour une animation de type `action` (encore en dévelloppement) il faut remplir le
            paramètre <param>`temps_anim`, le paramètre <param>`images` mais aussi le paramètre <param>`touche` 
            qui correspond à la touche avec laquelle cette action devrait se lancer. Vous pouvez y ajouter
            un <param>`callback` (optionel) qui est une fonction qui se déclanche en même temps que l'animation.
    """
    master_elt: Element
    """
    L'objet `parent` de cette animation.
    """
    master_anim_index: int
    """
    L'`index` de cette animation dans les animations de l'élément parent.
    """
    
    def __init__(self, type_anim:Literal["idle", 'action'], *, temps_anim:int | tuple[int, ...] | None = None, images:tuple[Texture, ...] | None = None, touche:int | None = None, callback:Callable[..., None] | None = None) -> None:
        self.type_anim = type_anim
        if type_anim == "idle":
            assert type(temps_anim) == int or type(temps_anim) == tuple, "Le paramètre temps_anim est obligatoire pour l'animation de type idle."
            assert type(images) == tuple, "Le paramètre images est obligatoire pour l'animation de type idle."
            if type(temps_anim) == tuple:
                assert len(temps_anim) == len(images), "La spécification du temps doit se faire entre chaque stades de l'animation."
                self.anim_time = [temps_anim[i] for i in range(len(temps_anim))]
            elif type(temps_anim) == int:
                self.anim_time = [temps_anim for _ in range(len(images))]
                print(self.anim_time)
            
            self.anim_imgs = list(images)
            
            self.dernier_ch = 0.0
            self.statut_anim = 0

            liste_anim.append(self)

    def update(self):
        if self.type_anim == "idle":
            if get_time() - self.dernier_ch > self.anim_time[self.statut_anim]:
                self.dernier_ch = get_time()
                self.statut_anim += 1
                if self.statut_anim == len(self.anim_imgs):
                    self.statut_anim = 0
    
    def anim_toggle(self, statut:bool = False):
        """
        Active ou désactive l'animation.

        Parameter
        ----------
        statut : bool
            Correspond à si cette animation doit être activé ou non.
        """
        if self.type_anim == "idle":
            if statut:
                if self not in liste_anim:
                    liste_anim.append(self)
            else:
                if self in liste_anim:
                    liste_anim.remove(self)

    def get_active_texture(self):
        """
        Donne la texture actuellement dessinée.

        Return
        -------
        ~.Texture
            L'objet qui assure l'affichage de ce modèle.
        """
        return self.anim_imgs[self.statut_anim]

    def draw(self):
        self.get_active_texture().draw()

class Element:
    """
    La base de n'importe quel élément que l'on peut créer.

    Args
    -------
    x : int
        L'ordonnée x de base ou se situera cet élément.
    y : int
        L'absice y de base ou se situera cet élément.
    width : int
        La largeur de chaque élément qui doit être pris sur le modèle.
    height : int
        La hauteur de chaque élément qui doit être pris sur le modèle.
    scale : float
        La taille générale de cette élément (sert à augmenter ou diminuer la taille d'un modèle).
    source : ~.Tilemap
        Le modèle à partir duquel vous pourrez constituer les différents modèles de cet élément.
    """
    @property
    def hit_box(self):
        """
        Donne toutes les position ou se situe cet élément (ne prend pas en compte le décallage)
        """
        if self.anim_active == -1:
            return None
        else:
            return self.anims[self.anim_active].get_active_texture().hit_box
        
    @property
    def hit_limits(self):
        """
        Donne les limites de la hitbox de cet élément
        """
        if self.anim_active == -1:
            return None
        else:
            limits = self.anims[self.anim_active].get_active_texture().hit_limits
            return (limits[0] + self.decallage_x, limits[1] + self.decallage_x, limits[2] + self.decallage_y, limits[3] + self.decallage_y)

    def __init__(self, x: int, y: int, width:int, height:int, scale: float, source: Tilemap) -> None:
        if scale < 1:
            raise ValueError("L'attribut scale ne peut pas être négatif ou nul.")
        self.x = x
        self.y = y
        self.decallage_x = 0
        self.decallage_y = 0
        self.taille = (width, height)
        self.scale = scale
        self.tilemap_source = source

        self.anims: list[Animation] = []
        self.anim_active: int = -1
        self.anim_types: dict[Literal["idle", "action"], list[int]] = {"idle": [], "action": []}
        self.idle_active:int = -1

    def add_animation(self, type_anim:Literal["idle", "action"], *, temps_anim:int | tuple[int, ...] | None = None, images:tuple[tuple[int, int], ...] | None = None, touche:int|None = None, callback: Callable[..., None] | None = None):
        """
        Cette méthode créé une animation qui fera s'afficher cet élément.

        Parameters
        ------------
        type_anim : Literal["idle", "action"]
            Le type d'annimation que vous voulez définir. Chaque type d'animation a besoin de certains paramètres.
            Voici la liste des paramètres pour chaque type d'animation:
                - Pour une animation de type `idle` il ne faut remplir que le paramètre <param>`temps_anim`
                qui correspond au temps, en milisecondes, entre chaque stades de l'animation ou le temps après 
                chaque stade: le premier après la première image donnée etc... Vous devez aussi remplir le 
                paramètre <param>`images` avec un ou plusieurs <class>`tuple` contenant, dans l'ordre, `x` et `y`
                qui représente le coin en haut à gauche de l'image que vous voulez utiliser. Pour définir leur
                `taille` c'est le paramètre du même nom qui définit, encore dans l'ordre, la longueur puis la largeur
                dans un tuple.
                \nLes animations de type `idle` peuvent être interchangées avec la méthode `~.Element.set_idle`
                - Pour une animation de type `action` (encore en dévelloppement) il faut remplir le
                paramètre <param>`temps_anim`, le paramètre <param>`images` ainsi que le paramètre <param>`taille`
                mais aussi le paramètre <param>`touche` qui correspond à la touche avec laquelle cette action devrait
                se lancer. Vous pouvez y ajouter un <param>`callback` (optionel) qui est une fonction qui se déclanche
                en même temps que l'animation.

        Return
        ----------
        ~.Animation
            Cette méthode retourne l'objet correspondant à l'animation que vous venez de créer.
        """
        assert type(temps_anim) in (int, tuple), "Le paramètre temps_anim n'est pas valide, il est nécessaire pour l'animation de type action ou idle."
        assert type(images) == tuple, "Le paramètre images n'est pas valide, il est nécessaire pour l'animation de type action ou idle."
        for x_y in images:
            assert type(x_y) == tuple and len(x_y) == 2, "Le paramètre images n'est pas valide, il est nécessaire pour l'animation de type action ou idle."
        if type_anim == "action":
            assert type(touche) == int, "Le paramètre touche n'est pas valide, il est nécessaire pour l'animation de type action."
        
        list_textures = []
        width, height = self.taille
        for coordonnees in images:
            x, y = coordonnees

            img_px = px.Image(width, height)
            img_px.blt(0, 0, self.tilemap_source.image_px, x, y, width, height, COULEUR_TRANSPARENTE)
            
            texture = Texture(self.x - self.decallage_x, self.y - self.decallage_y, img_px, self.scale)
            texture.master_elt = self

            list_textures.append(texture)
        list_textures = tuple(list_textures)

        animation = Animation(type_anim, temps_anim = temps_anim, images = list_textures, touche = touche, callback = callback)
        animation.master_elt = self

        numero = len(self.anims)
        self.anims.append(animation)
        animation.master_anim_index = numero
        
        self.anim_types[type_anim].append(numero)
        if self.idle_active == -1 and type_anim == "idle":
            self.idle_active = numero
            self.anim_active = numero

        return animation
    
    def set_idle(self, index:int | Animation):
        """
        Permet de changer l'animation de type `idle` active.

        Parameter
        ----------
        index : int | ~.Animation
            Le rang de l'animation parmis les aimations que vous avez atribué à cet élément, peut être aussi l'objet
            `~.Animation` en lui même. Dans ce dernier cas si l'objet ne fait pas partit des animations de cet élément
            alors une `ValueError` sera levé.
        """
        if type(index) == Animation:
            if self.anims.count(index) != 0 and self.anims.index(index) in self.anim_types["idle"]:
                self.idle_active = self.anims.index(index)
        else:
            self.idle_active = index # pyright: ignore[reportAttributeAccessIssue]

    def change_x(self, x: int):
        """
        Change le placement sur l'axe vertical de cet élément.

        Parameter
        ----------
        x : int
            La nouvelle valeur de x.
        """
        self.decallage_x += x - self.x

        self.x = x

    def change_y(self, y: int):
        """
        Change le placement sur l'axe horizontal de cet élément.

        Parameter
        ------------
        y : int
            La nouvelle valeur de y
        """
        self.decallage_y += y - self.y

        self.y = y

    def compare_hitbox(self, elt: Element):
        """
        Vérifie si la hitbox de cet élément et celle mise en paramètre s'entrecroisent.

        Parameter
        ----------
        elt : ~.core.Element
            L'autre élément avec lequel vous voulez comparer l'hitbox.

        Return
        -------
        bool
            `True` si c'est la cas `False` si ça ne l'est pas.
        """
        hitbox_elt: dict[int, dict[int, Literal[True]]] = elt.hit_box # pyright: ignore[reportAssignmentType]
        limits_elt = elt.hit_limits

        if type(limits_elt) == tuple and type(self.hit_limits) == tuple:
            min_x_hit, max_x_hit, min_y_hit, max_y_hit = limits_elt

            min_x_elt, max_x_elt, min_y_elt, max_y_elt = self.hit_limits

            if (min_x_hit <= max_x_elt and max_x_hit >= min_x_elt) and (min_y_hit <= max_y_elt and max_y_hit >= min_y_elt):
                for x, y_dict in self.hit_box.items(): # pyright: ignore[reportOptionalMemberAccess]

                    if x + self.decallage_x - elt.decallage_x in hitbox_elt.keys():
                        for y in y_dict.keys():

                            if y + self.decallage_y - elt.decallage_y in hitbox_elt[x].keys():
                                return True

        else:
            print("L'un de ces 2 élément à une hitbox non ou mal définie.")
        
        return False

    def pos_in_hitbox(self, x, y):
        """
        Vérifie si la position donné fait partie de l'hitbox de cet objet.

        Parameters
        -----------
        x : int
            L'ordonnée x de la position à vérifier.
        y : int
            L'absice y de la position à vérifier.

        Return
        -------
        bool
            `True` si c'est la cas `False` si ça ne l'est pas.
        """
        try:
            if type(self.hit_box) == dict:
                rep = self.hit_box[x][y]
            else:
                rep = False
        except:
            rep = False
        
        return rep

    def draw(self):
        """
        Cette méthode affiche cet élément.
        Attention pyxel doit être initialisé.
        """
        if not is_px_init():
            raise SystemError("Pyxel doit être initialisé.")
        
        self.anims[self.anim_active].draw()

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
        elt_fichier.img_save(chemin_img)
        chemin_img += ".png"
        self.modifs = elt_fichier.get_raw_modifs()
        self.fichiers = elt_fichier.fichiers
        self.couleurs: dict[str, int] = {}

        self.placements: list[tuple[int, int, int, int, int, int]] = []
        
        for fichier in self.fichiers:
            fichier = decode(fichier)
            for couleur in fichier.couleurs:
                if couleur not in self.couleurs:
                    self.couleurs[couleur] = get_color(couleur)
        
        img_fichier = Image.open(chemin_img) # pyright: ignore[reportArgumentType]
        pixels = img_fichier.load()

        self.image_px = px.Image(*img_fichier.size)

        for x in range(img_fichier.width):
            for y in range(img_fichier.height):
                rouge, vert, bleu, alpha = pixels[x, y]  # pyright: ignore[reportGeneralTypeIssues, reportOptionalSubscript]
                
                if alpha != 255: # pyright: ignore[reportIndexIssue]
                    self.image_px.pset(x, y, COULEUR_TRANSPARENTE)
                else:
                    code_couleur = f"{hex(rouge)[2:]:02}{hex(vert)[2:]:02}{hex(bleu)[2:]:02}"

                    self.image_px.pset(x, y, self.couleurs[code_couleur])
        
        remove(chemin_img)

        self.chemin_fichier = chemin

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
        
    def create_element(self, x: int, y: int, width: int, height: int, scale: float = 1):
        """
        Créé un élément basique (plusieurs autres viendront plus tard) qui vous servira pour afficher vos créations, les animer
        et pouvoir manipuler leur représentation à la source.

        Si vous voulez le faire s'afficher vous devrait créer la première animation idle.
        Pour plus d'information regardez la documentation de la méthode `~.Element.add_animation

        Parameters
        -----------
        x : int
            Correspond à où vous voulez afficher votre élément sur l'axe vertical (peut être modifié plus tard).
        y : int
            Correspond à où vous voulez afficher votre élément sur l'axe horizontal (peut être modifié plus tard).
        scale : float `optionel`
            L'agrandissement ou le rétrécissement de ce que vous voulez afficher.
        """

        return Element(x, y, width, height, scale, self)

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