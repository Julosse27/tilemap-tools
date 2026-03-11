# Tilemap Tools

Outils en ligne de commande pour créer et manipuler des tilemaps en pixel art.

## Installation
```bash
pip install tilemap-tools
```

## Fonctionnalités

 - ✨ Créer des modèles de tilemaps interactifs.
 - 🎨 Des palettes max de 16 couleurs pour un modèle.
 - 👁️ Visualisation et modification avec des grilles interactives
 - 👾 Création de tilemaps avec un systrème complet de création de platformes ou de modèles tierces
 - 👨‍💻 Utilisation facile dans un programme (a faire) utilisant le module pyxel (implémenté par ce module) 
 - 💻 Modification à tout moment

## Utilisation

### Créer un fichier
La commande `tilemap create` permet de créer les fichier nécessaire à l'utilisation de ce module.

### Fichier modèle
Le fichier modèle (en .mdl) est créé avec la commande `tilemap create modele` il servira à créer un fichier tilemap (en .map).

Il contiendra un ensemble de tuiles constituées d'un maximum de 16 couleurs différentes (dont le noir imposé).
```bash
tilemap create modele 9 -c FF0000 00FF00 0000FF

tilemap create modele 12 mon_modèle_perso -n 4
```

##### Arguments
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

#### Fichier tilemap
Un fichier tilemap (.map) est un fichier qui permettra d'avoir un modèle personnalisé dans un programme utilisant le module `pyxel`.

Il est créé grâce à 1 ou plusieurs fichier modèle (.mdl)

##### Arguments

### Visualiser un modèle ou une tilemap
```bash
tilemap view mon_modèle
```

### Vider les fichiers temporaires (peuvent s'accumuler au cours d'erreurs)
```bash
tilemap clear
```

## Examples
```bash
# Pour créer un modèle avec 3x3 tuiles de 9 pixels chacuns
tilemap create modele 9 niveau1

# Créer avec des couleurs personnalisées
tilemap create modele 9 niveau2 -c FF0000 00FF00 0000FF FFFF00

# Visualiser
tilemap view niveau1
```

## Dévellopement
```bash
git clone https://github.com/Julosse27/tilemap-tools.git

cd tilemap-tools

pip install -e .
```

## License

MIT License - voir LICENSE pour plus de détails.

## Auteur

Julosse - julosse27110@gmail.com