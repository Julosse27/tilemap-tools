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
 - 👨‍💻 Utilisation facile dans un programme (a faire) utilisant le module pyxel (implémenté par ce module) 
 - 💻 Modification à tout moment

 </font>

-------
## Utilisation

### **Créer un fichier**
La commande `tilemap create` permet de créer les fichier nécessaire à l'utilisation de ce module.

### Fichier modèle
Le fichier modèle (en .mdl) est créé avec la commande `tilemap create modele` il servira à créer un fichier tilemap (en .map).

Il contiendra un ensemble de tuiles constituées d'un maximum de 16 couleurs différentes (dont le noir imposé).
```bash
tilemap create modele 9 -c FF0000 00FF00 0000FF

tilemap create modele 12 mon_modèle_perso -n 4
```

#### Arguments
Cette commande demande 2 argument obligatoires:
- L'argument `taille`: nombre de pixels du coté de chaque tuile (le maximum est de 32 pixels).

- L'argument `output`: le nom du fichier qui va être créé.

Mais elle à aussi plusieurs arguments optionels:
- L'argument `--nb-tuiles` (ou `-n`): le nombre de tuiles que contiendra le fichier. Cela permettra d'avoir plus de choix lors de la création d'un fichier tilemap avec ce fichier.

- Et enfin, l'argument `--couleurs` (ou `-c`): toutes les couleurs qui seront utilisées pour créer ce modèle. Après avoir utilisé cet argument vous devez spécifier un ou plusieurs code exadécimaux correspondant aux couleurs que vous voulez utiliser. Vous pouvez utiliser au maximum 16 couleurs différentes (dont le noir imposé) et au minimum 1 couleur.

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

```bash
# Exemple de création d'un fichier tilemap
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
Ce module étant encore en développement, je laisse à disposition cette commande pour supprimer les fichiers temporaires qui ne seraient pas suprimés lors de potentielles erreurs.
```bash
tilemap clear
```

## License

MIT License - voir LICENSE pour plus de détails.

## Auteur

Julosse - julosse27110@gmail.com