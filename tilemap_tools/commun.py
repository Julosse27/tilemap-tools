"""Stocke toutes les fonctions et les variables communes à tout les fichiers"""
import os
from os.path import join, dirname, splitext, isfile
from time import time
import pyxel as px
import tkinter as tk
from PIL import Image, ImageTk
from typing import Callable

def image_vide(taille:int = 512):
    img = Image.new('RGBA', (taille, taille))
    pixels = img.load()
    
    for y in range(taille):
        for x in range(taille):
            # Damier alterné
            if (x + y) % 2 == 0:
                pixels[x, y] = (192, 192, 192, 254) # pyright: ignore[reportOptionalSubscript]
            else:
                pixels[x, y] = (255, 255, 255, 254) # pyright: ignore[reportOptionalSubscript]

    return img

BASE_COLORS = ['000000', '2b335f', '7e2072', '19959c', '8b4852', '395c98', 'a9c1ff', 'eeeeee', 'd4186c', 'd38441', 'e9c35b', '70c6a9', '7696de', 'a3a3a3', 'ff9798', 'edc7b0']
FICHIER_COLORS = join(dirname(__file__), "bin", "liste_couleurs.pyxpal")

def generate_temp(extension:str|None = None):
    """
    Génère un chemin pour un fichier temporaire.

    Parameter
    ---------
    extension : `str`|`None`
        L'extension que doit obtenir le chemin du fichier qui va être retourné.

    Return
    ---------
    nom : `str`
        Le chemin généré avec une extension ou non.
    """
    nom = f'{join(dirname(__file__), "bin", f"bin_{int(time() * 1000)}")}'
    if extension != None:
        nom += "." + extension
    return nom

def is_init():
    """
    Permet de savoir si une fenètre `pyxel`est active.

    Return
    -----
    bool
        `True` si `pyxel` est initialisé sinon `False`
    """
    old_stdout_fd = os.dup(1)
    old_stderr_fd = os.dup(2)
    
    devnull = os.open(os.devnull, os.O_WRONLY)

    os.dup2(devnull, 1)
    os.dup2(devnull, 2)
    os.close(devnull)

    try:
        _ = px.width
        return True
    except:
        return False
    finally:
        os.dup2(old_stdout_fd, 1)
        os.dup2(old_stderr_fd, 2)
        os.close(old_stdout_fd)
        os.close(old_stderr_fd)

def get_name(path:str, extension:bool = True):
    """
    Permet de récupérer le nom du fichier à partir de son chemin.

    Attention si le chemin pointe vers un dossier la chaine de caractère renvoyée sera vide.

    Parameters
    ---------
    path : str
        Chemin qui contient le nom du fichier.
    extension : bool
        Définit si le chemin doit contenir l'extension du fichier ou non:
            - `True` si vous voulez la garder (par défault ce paramètre est à `True`)
            - `False` si vous voulez l'enlever

    Return
    --------
    str
        Le nom du fichier avec ou sans l'extension.
        Attention cette chaine de caractère peut être vide.

    Examples
    ---------
    >>> get_name("c:\\_chemin\\_absolu\\_vers\\_un\\_fichier.txt")
    '_fichier.txt'
    >>> get_name("chemin\\_relatif\\_vers\\_un\\_fichier.json", False)
    '_fichier'
    >>> get_name("C:\\_chemin\\_absolu\\_vers\\_un\\_dossier")
    ''
    """
    chemin, extension_name = splitext(path)

    if extension_name == "":
        return ""

    name = chemin.split("\\")[-1]

    if name == chemin:
        name = chemin.split("/")[-1]

    if extension:
        name += extension_name

    return name

def get_color(color_code:str):
    """
    Permet de récupérer l'index de la couleur `pyxel` mise en paramètre.

    Cette couleur est créé si elle n'existe pas encore.

    Parameter
    ----------
    color_code : str
        Un code `hexadécimal` de n'importe quelle couleur en `str` (par exemple: "FFFFFF" pour le blanc).

    Return
    ---------
    int
        L'index de cette couleur (présente avant l'exécution de ce programme ou non)
        dans le répertoire de pyxel.
    """
    if is_init():
        color = []
        for col in px.colors.to_list():
            color.append(hex(col)[2:])
    else:
        if not isfile(FICHIER_COLORS):
            with open(FICHIER_COLORS, "w") as f:
                f.write("\n".join(BASE_COLORS))
            color = BASE_COLORS
        else:
            with open(FICHIER_COLORS, "r") as f:
                color = f.read().splitlines()

    color_code = color_code.lower()

    if color_code not in color:
        index = add_color(color_code)
    else:
        index = color.index(color_code)

    return index

def add_color(color_code:str):
    """
    Rajoute une couleur à pyxel sans vérifier si elle existe déjà.
    """
    color_code = color_code.lower()
    if is_init():
        index = len(px.colors)
        px.colors.from_list(px.colors.to_list() + [int(color_code, 16)])
    else:
        with open(FICHIER_COLORS, "a+r") as f:
            index = len(f.read().splitlines())
            f.write("\n" + color_code)

    return index

class Dessinateur:
    def __init__(self, frame: tk.Frame, selector:Selecteur | None = None, *, image_base: Image.Image = image_vide(), modifs: list[tuple[bytes, str, int, int]] | None = None, rely:float = 0, relx:float = 0.25, ratio:int = 4) -> None:
        assert image_base.mode == "RGBA", "Le mode d'édition de cette image doit forcement être en RGB ou en RGBA"
        assert image_base.size[0] == image_base.size[1], "L'image doit être forcément un carré"

        self.source_img = image_base
        self.list_modifs: list[Image.Image] = [self.source_img.copy()]
        self.list_contruction: list[tuple[bytes, str, int, int]] = [] if modifs == None else modifs
        self.ratio = ratio
        self.size = self.source_img.size[0]
        self.__toggle_sauv = True

        self.selector = selector
        bg = frame.cget("bg")
        self.callback = None
        
        self._variations_toggle = False

        self.dernier_click = None

        frame_dessin = tk.Frame(frame, bg=bg)
        frame_dessin.place(relx=relx, rely=rely, anchor=tk.N)

        self.tile_img = None

        self.alpha = 132
        self._sens_alpha = -2
        self._limites = {"bas":100, "haut":164}

        photo = ImageTk.PhotoImage(self.get_display_img())

        self.canva = tk.Canvas(frame_dessin, width= 256, height=256, highlightthickness=0, bd=0, cursor="none")
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
            scrollregion=(0, 0, self.size * self.ratio, self.size * self.ratio)  # Taille réelle du canva
        )

        self.canva.bind("<Button-1>", self.click)
        self.canva.bind("<Motion>", self.hover)
        self.canva.bind("<Leave>", self.leave)
        self.canva.bind_all("<Control-z>", self.annuler)

        h_scroll.pack(fill=tk.X, expand=True)
        v_scroll.pack(fill=tk.Y, expand=True)
        frame_h.pack(side=tk.BOTTOM, anchor=tk.SW)
        frame_v.pack(side=tk.RIGHT)
        self.canva.pack(side=tk.LEFT)
        self.variation_alpha()       

    def toggle_sauvegarde(self, toggle:bool):
        """
        Toggle la sauvegarde des modifications.
        """
        self.__toggle_sauv = toggle

    def set_cursor(self, cursor:str):
        """
        Change le curseur quand la souris est sur l'image.
        """
        self.canva.config(cursor=cursor)

    def set_callback(self, callback: Callable):
        """
        Met en place une action à chaque click.
        """
        self.callback = callback

    def get_display_img(self):
        img = self.source_img.resize((self.size * self.ratio, self.size * self.ratio), Image.Resampling.NEAREST)

        return img
    
    def upd_img(self):
        """
        Met à jour l'image principale du fichier tilemap et sa représentation.
        """
        image = self.get_display_img()
        photo = ImageTk.PhotoImage(image)

        self.canva.itemconfig(self.image_id, image=photo)
        self.canva.image = photo # pyright: ignore[reportAttributeAccessIssue]

    def annuler(self, event: tk.Event):
        """
        Annule la dernière action que l'utilisateur à fait.
        """
        if len(self.list_modifs) != 1:
            old_img = self.list_modifs[-2]
            self.list_modifs.pop()
            if self.__toggle_sauv:
                self.list_contruction.pop()
            self.source_img = old_img.copy()
            self.upd_img()

    def add_new_img(self, x:int, y:int):
        """
        Ajoute la tuile sélectionnées au coordonnées données.
        
        :param x: L'ordonnée x du centre de l'image (taille réelle)
        :type x: int
        :param y: L'absice y du centre de l'image (taille réelle)
        :type y: int
        """
        if self.selector != None:
            tuile = self.selector.get_tuile()

            if tuile != None:
                x -= tuile.width // 2
                y -= tuile.height // 2
                
                if self.__toggle_sauv:    
                    nom_fichier_temp = generate_temp("png")

                    tuile.save(nom_fichier_temp)

                    with open(nom_fichier_temp, "rb") as f:
                        self.list_contruction.append((f.read(), tuile.nom_fichier, x, y)) # pyright: ignore[reportAttributeAccessIssue]

                    os.remove(nom_fichier_temp)
                
                self.source_img.paste(tuile, (x, y))
                
                self.list_modifs.append(self.source_img.copy())

                self.upd_img()

    def variation_alpha(self):
        if self._variations_toggle:
            return
        
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
                
        self.canva.after(33, self.variation_alpha)

    def apercu(self, x:int, y:int, tile_img: Image.Image):
        self.canva.delete("fantome")
        width, height = tile_img.size
        self.tile_img = tile_img.convert('RGBA').resize((width * self.ratio, height * self.ratio), Image.Resampling.NEAREST)
        self.tile_img.putalpha(self.alpha)

        photo = ImageTk.PhotoImage(self.tile_img)
        
        reste_x = x % self.ratio
        if reste_x < (self.ratio / 2):
            pixel_x = x - reste_x
        else:
            pixel_x = x + self.ratio - reste_x
        
        reste_y = y % self.ratio
        if reste_y < (self.ratio / 2):
            pixel_y = y - reste_y
        else:
            pixel_y = y + self.ratio - reste_y

        pixel_x -= width//2*self.ratio
        pixel_y -= height//2*self.ratio

        self.canva.create_image(pixel_x, pixel_y, anchor = tk.NW, image=photo, tags="fantome")

        self.canva.image_apercu = photo # pyright: ignore[reportAttributeAccessIssue]

    def stop_thread(self):
        self._variations_toggle = True

    def hover(self, event:tk.Event):
        if self.selector != None:
            tuile = self.selector.get_tuile()
            if tuile != None:
                x = self.canva.canvasx(event.x)
                y = self.canva.canvasy(event.y)
                self.apercu(x, y, tuile)
    
    def leave(self, event):
        self.canva.delete("fantome")
    
    def click(self, event:tk.Event):

        x_canva = int(self.canva.canvasx(event.x))
        y_canva = int(self.canva.canvasy(event.y))

        # Compression des coordonnées
        if x_canva % self.ratio < (self.ratio / 2):
            x = x_canva // self.ratio
        else:
            x = x_canva // self.ratio + 1
        if y_canva % self.ratio < (self.ratio / 2):
            y = y_canva // self.ratio
        else:
            y = y_canva // self.ratio + 1

        self.add_new_img(x, y) # Met à jour l'image principale au niveau du clic
        self.dernier_click = (x, y)
        if self.callback != None:
            self.callback()

class Selecteur:
    def __init__(self, root) -> None:
        self.B1 = False
        self.tuile = (None, None)
        self.canvas_list: list[tk.Canvas] = []
        
        # Capturer le relâchement au niveau de la fenêtre
        root.bind("<ButtonRelease-1>", self.release)

    def get_tuile(self) -> Image.Image | None:
        """Renvoie la tuile qui à été sélectionnée"""
        if self.tuile[1] != None:
            canva, tag = self.tuile
            numero = int(tag[-2:])
            img = canva.img_list[numero]
            img.nom_fichier = tag[:-2]
            return img
            
    def set_tuile(self, widget, tag):
        """Enregistre la tuile cliquée"""
        self.tuile = (widget, tag)

    def _traiter_position(self, canvas: tk.Canvas, x:int, y:int):
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
            canva_x = canvas.winfo_rootx()
            canva_y = canvas.winfo_rooty()
            canva_width = canvas.winfo_width()
            canva_height = canvas.winfo_height()
            
            # Vérifier si la souris est dans ce canvas
            if canva_x <= x <= canva_x + canva_width and canva_y <= y <= canva_y + canva_height:
                self._traiter_position(canvas, x, y)
                break

    def release(self, event: tk.Event):
        """Traite le relachement du bouton B1 en indiquant au programme son état."""
        self.B1 = False

    def click(self, event: tk.Event):
        """Traite n'importe quel appui et indique que le bouton B1 est préssé."""
        self.B1 = True
        self._traiter_position(
            event.widget, # pyright: ignore[reportArgumentType]
            event.widget.winfo_rootx() + event.x,
            event.widget.winfo_rooty() + event.y
        )