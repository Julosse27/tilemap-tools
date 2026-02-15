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
 - 👾 Création de tilemaps (à terminer) avec un systrème complet de création de platformes ou de modèles tierces
 - 👨‍💻 Utilisation facile dans un programme (a faire) utilisant le module pyxel (implémenté par ce module) 
 - 💻 Modification à tout moment

## Utilisation

### Créer un modèle
```bash
tilemap create modele 9 -c FF0000 00FF00 0000FF
tilemap create modele 12 mon_modèle_perso -n 4
```

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