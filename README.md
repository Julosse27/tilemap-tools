# Tilemap Tools



<font size=4> Outil python permettant de faciliter l'utilisation de modèles avec le module `pyxel`. 

[REDME in others languages](https://github.com/Julosse27/tilemap-tools/tree/main/Information)
</font>

---
## Installation
```bash
pip install tilemap-tools
```

----
## Fonctionnalités

<font size=3>

 - ✨ Créer des modèles de tilemaps interactifs en pixels art.
 - 🎨 Des palettes max de 32 couleurs pour un modèle.
 - 👁️ Visualisation et modification avec des grilles interactives.
 - 💻 Modification à tout moment
 - 👾 Création de tilemaps avec un systrème complet de création de platformes ou de modèles tierces.
 - 👨‍💻 Utilisation facile dans un programme utilisant le module pyxel ([documentation](https://kitao.github.io/pyxel/web/user-guide/))

 </font>

-------
## Utilisation

### **Créer un fichier**
La commande `tilemap create` permet de créer les fichier nécessaire à l'utilisation de ce module.

### Fichier modèle
Le fichier modèle (en .mdl) est créé avec la commande `tilemap create modele` il servira à créer un fichier tilemap (en .map).

Il contiendra un ensemble de tuiles constituées d'un maximum de 32 couleurs différentes.

Si aucune couleurs n'est données quelques couleurs de base seront à votre disposition.

#### Arguments
Cette commande demande 2 argument obligatoires:
- L'argument `taille`: nombre de pixels du coté de chaque tuile (le maximum est de 32 pixels).

- L'argument `output`: Le chemin où le fichier sera enregistré. Peut être absolu ou relatif.

Mais elle à aussi plusieurs arguments optionels:
- L'argument `--nb-tuiles` (ou `-n`): le nombre de tuiles que contiendra le fichier. Cela permettra d'avoir plus de choix lors de la création d'un fichier tilemap avec ce fichier.

- Et enfin, l'argument `--couleurs` (ou `-c`): Pour construire ce modèle vous pouvez utiliser n'importe quelle couleur, c'est dans ce paramètre que vous devrez spécifier lesquelles. Après avoir mentioné cet argument vous devez spécifier un ou plusieurs code exadécimaux correspondant aux couleurs que vous voulez utiliser. Vous pouvez utiliser de 1 à 32 couleurs différentes pour un seul modèle !!!

#### Exemples
```bash
tilemap create modele 9 mon_modèle.mdl -c FF0000 00FF00 0000FF

tilemap create modele 12 mon_modèle_perso.mdl -n 4
```

Pour plus d'aide:
```bash
tilemap create modele -h
```

### Fichier tilemap
Un fichier tilemap (`.map`) est le fichier qui vous permettra d'inclures vous créations dans votre programme. Ce fichier combinera les tuiles d'un ou plusieurs fichier modèle (`.mdl`) ayant pour seule limite un carré de 512 pixels de coté à remplir de vos créations.

#### Arguments
Cette commande à 2 argument obligatoires:
- L'argument `output`: le nom du fichier qui va être créé ( /!\ Ne pas oublier l'extension /!\ ). Vous pouvez indiquer ce chemin relatif ou absolu.

- L'argument `modeles`: il sagit du nom des fichier modèles (`.mdl`) que vous avez utilisé. Vous pouvez les indiquer sous un chemin relatif ou absolut.

#### Exemple

```bash
tilemap create map tilemap.map modèle1.mdl modèle2.mdl modèle3.mdl
```

Pour plus d'aide:
```bash
tilemap create map -h
```

### **Visualiser un modèle ou une tilemap**
Après avoir créé votre modèle pour votre futur jeu ou autre vous pourrez le visualiser avec cette simple commande.
```bash
tilemap view chemin_vers_la_tilemap.map
# ou
tilemap view chemin_vers_le_modèle.mdl
```

### **Vider les fichiers temporaires**
Ce module étant encore en développement, je laisse à disposition cette commande pour supprimer les fichiers temporaires qui ne seraient pas suprimés lors de potentielles erreurs ou interuptions du programme.
```bash
tilemap clear
```

## **Intégration dans un programme**

### **L'objet `~.Modele` et `~.Tilemap`**
Après avoir créé des fichier il faut pouvoir les modifiers. C'est à quoi servent ces 2 fichier qui vous permettent de faire un lien entre le fichier que vous venez de créer et votre programme.

Tant que vous connaissez le chemin jusqu'a votre fichier vous n'avez besoin que d'une ligne pour en créer un :
```python
from tilemap-tools import Modele, Tilemap

modele = Modele("C:\\chemin\\vers\\votre\\fichier.mdl")

tilemap = Tilemap("mon_fichier.map")
```

Vous pouvez directement créer un nouveau fichier avec `Modele.create` ou `Tilemap.create`.

```python
from tilemap-tools import Modele, Tilemap

# Pour créer un nouveau modèle
modele = Modele.create(taille=3, nb_tiles=3, couleurs=["ffffff", "f33aaa"])
# ou pour créer un nouveau fichier tilemap
tilemap = Tilemap.create("mon_fichier.mdl", modele)
```

Mais vous pouvez aussi les modifier ou les visualiser directement dans votre programme.
```python
from tilemap-tools import Modele

modele = Modele("mon_modele.mdl")

# Pour modifier ce fichier appeler:
modele.modif()
# ou pour voir son contenu:
modele.view()
# bien sur cela marche de la même façon pour l'objet tilemap
```

### **L'objet `~.Element`**
La première partie de l'intégration était concentré sur refaire ce que ce module faisait déjà dans un programme python.

Cette seconde partie met en place un système complet pour pouvoir afficher ce que vous venez de créer et l'animer dans un programme avec `pyxel`

Vous pouvez le créer de 2 façons:
```python
from tilemap_tools import Tilemap, Element

# Il faut d'abord dans tout les cas créer un lien
# avec un fichier tilemap (pour avoir le modèle)
tilemap = Tilemap("mon_fichier_tilemap.map")

# Ensuite soit vous utilisez la méthode Tilemap.create_element
element1 = tilemap.create_element(
    10, 10, # Les coordonnées x-y ou il doit être affiché.
    9, 12, # La taille (largeur puis heuteur) des modèles sur la tilemap.
    2 # Un multiplicateur qui permet d'agrandir la taille d'un modèle à l'affichage
    # Il faut faire attention avec ce dernier car il peut modifier le modèle
)
# Vous pouvez le créer aussi comme ça:
element2 = Element(
    10, 10,
    9, 12,
    2,
    tilemap # Pour fonctionner il à besoin de savoir d'où récupérer les modèles.
)
```

Après l'avoir créé vous pouvez l'animer avec sa méthode `Element.add_animation`
Vous pouvez en créer de plusieurs type et chacune d'entre elle à ses spécialitées :
* L'animation `idle` permet de créer un roulement de plusieurs modèles à un rythme précis en boucle. Pour chaque modèle que vous voudrez ajouter les cordonnées d'où vous voulez le récupérer (coordonnées x-y sur la tilemap) et le temps à attendre entre chaque stade de l'animation.
* Il viendra ensuite dans pas longtemps l'animation de type `action` qui comme son nom l'indique se déclenchera à l'apui d'une touche en particulier ou une action prédéfinie (comme l'éxécution d'un fonction). Ce type d'animation est encore en développement.
```python
from tilemap_tools import Tilemap

element = Tilemap("fichier.map").create_element(10, 10, 8, 6, 1)

animation_idle = element.add_animation(
    'idle', # Le permier argument est le type d'animation
    # Chaque type d'animation à ses propres paramètre et donc certains sont obligatoires
    images=[(3, 5), (9, 5)] # C'est une liste de tuple avec chaque coordonnées ou les modèles commencent
    # Dans cet exemple on à 2 images, une qui commence en x = 3 et y = 5 et une autre en x = 9 et y = 5
    temps_anim=500, # Comme celui-ci qui définit le temps à attendre entre chaque image en milisecondes.
    # PS: peut être aussi sous la forme d'une liste de temps pour chaque image
)
```
Un élément peut avoir plusieurs animation idle de stockées et peut les interchanger à tout moment avec sa méthode `Element.set_idle`. Pour cela soit vous connaisez l'indice de l'animation que vous voulez activer dans les animation `idle` soit vous avez sous la main sont objet.

```python
# Ce programme reprend la suite du dernier

# Creation d'une 2eme animation différente
animation_idle2 = element.add_animation(
    'idle',
    images = [(3, 15), (9, 15)]
    temps_anim = [300, 500] # L'animation restera 300 milisecondes avec la première image puis 500 avec la 2eme
)

# Vous pouvez activer cette nouvelle animation de 2 façons
element.set_idle(1) # Active la 2eme animation idle ajouté à l'élément
# ou
element.set_idle(animation_idle2)
```
Lorsque n'importe quelle animation est activée chaque image à sa propre hitbox, la méthode `element.position_in_hitbox` permet de vérifier si une position unique (comme celle de la souris par exemple) serait dans celle-ci et la méthode `element.compare_hitbox` permet de vérifier si 2 élément se touche.

### **Pour un petit plus**
Avec tout ces élément le créateur a développé plusieurs outils qu'il met à disposition comme un moyen de savoir si `pyxel` est initialisé avec la fonction `is_px_init`. Mais aussi un moyen de récupérer une couleur en particulier avec la fonction `get_color` ou plus interessant encore pour certain un moyen de savoir exactement depuis combien de temps le jeu est en train de tourner avec  la fonction `get_time`.

## License

MIT License - voir LICENSE pour plus de détails.

## Auteur

Julosse - julosse27110@gmail.com

## Remerciments
<font size=3>J'espère que ce simple module vous aidera dans la création de vos premiers jeux avec python.

Merci de m'avoir de votre attention et si ce module vous plait pensez à en faire parler autour de vous pour qu'il puisse aider encore d'autre personnes.</font>