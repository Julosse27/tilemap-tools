# Tilemap Tools

<font size=4> Outils python permettant de faciliter l'utilisation de modèles et de tilemap avec le module `pyxel`. </font>

---
## Installation
```bash
pip install tilemap-tools
```

----
## Fonctionnalités

<font size=3>

 - ✨ Créer des modèles de tilemaps interactifs.
 - 🎨 Des palettes max de 16 couleurs pour un modèle.
 - 👁️ Visualisation et modification avec des grilles interactives
 - 👾 Création de tilemaps avec un systrème complet de création de platformes ou de modèles tierces
 - 👨‍💻 Utilisation facile dans un programme utilisant le module pyxel (documentation en français: https://kitao.github.io/pyxel/web/user-guide/)
 - 💻 Modification à tout moment

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

- Et enfin, l'argument `--couleurs` (ou `-c`): toutes les couleurs qui seront utilisées pour créer ce modèle. Après avoir utilisé cet argument vous devez spécifier un ou plusieurs code exadécimaux correspondant aux couleurs que vous voulez utiliser. Vous pouvez utiliser au maximum 16 couleurs différentes (dont le noir imposé) et au minimum 1 couleur.

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

### **Intégration dans un programme**

#### **L'objet `~.Modele` et `~.Tilemap`**
Le gros point fort de ce module est encore de permettre de pouvoir afficher ce que vous venez de créer. Pour cela vous pouvez à tout moment importer `tilemap-tools`dans votre programme ce qui vous permetra d'accéder à 2 objets (`~.Modele` et `~.Tilemap`).

Ces objets représentent le lien entre le programme et le fichier vous pouvez en créer un très simplement:
```python
from tilemap-tools import Modele, Tilemap

modele = Modele("C:\\chemin\\vers\\votre\\fichier.mdl")

tilemap = Tilemap("mon_fichier.map")
```

Avec ces objets vous pouvez faire plusieur chose comme en créer un:

```python
from tilemap-tools import Modele, Tilemap

# Pour créer un nouveau modèle
modele = Modele.create(taille=3, nb_tiles=3, couleurs=["ffffff", "f33aaa"])
# ou pour créer un nouveau fichier tilemap
tilemap = Tilemap.create("mon_fichier.mdl", modele)
```
Vous pouvez remarquer que pour créer un fichier `tilemap` on peut utiliser soit un chemin jusqu'a un fichier (absolu ou relatif) ou un objet `~.Modele`.

Vous pouvez aussi avec ces objets les modifiers ou les visualiser à la manières des commandes:

```python
from tilemap-tools import Modele

modele = Modele("mon_modele.mdl")

# Pour modifier ce fichier appeler:
modele.modif()
# ou pour voir son contenu:
modele.view()
# bien sur cela marche de la même façon pour l'objet tilemap
```

De plus l'objet `~.Tilemap` présente un autre avantage, l'intégration dans un programme avec le module `pyxel` vous permet d'utiliser sa méthode `.draw()` qui vous permet d'afficher une partie de ce fichier sur votre fenètre de jeu.
```python
from tilemap_tools import Modele, Tilemap
import pyxel

tilemap = Tilemap("perso.map")

pyxel.init(100, 100)
def update():
    global x
    x = 10 if pyxel.frame_count % 10 <= 5 else 20

def draw():
    y = 0
    tilemap.draw(x, y, 0, 0, 10, 10)

pyxel.run(update, draw)
```

#### **Pour un petit plus**
En plus de ces objets ce module met à disposition une fonction qui permet de récupérer le numéro d'une couleur dans la palette `pyxel` et une autre permettant de savoir si pyxel est initialisé ou non.

## License

MIT License - voir LICENSE pour plus de détails.

## Auteur

Julosse - julosse27110@gmail.com