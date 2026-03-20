"""Point d'entrée principal pour la CLI tilemap"""
import argparse
import sys
from .modele_manager import mdl_create, mdl_modif, mdl_view
from .tilemap_manager import map_create, map_view, map_modif
from os import getcwd, listdir, remove, makedirs
from os.path import exists, join, dirname, splitext, isdir, isfile, isabs

DOSSIER = join(dirname(__file__), "bin")

# Créez le dossier s'il n'existe pas
if not exists(DOSSIER):
    makedirs(DOSSIER)

class Check_colors(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) > 15: # pyright: ignore[reportArgumentType]
            parser.error("Vous ne pouvez pas dessiner un modèle avec plus de 16 couleurs.")

        if len(set(values)) != len(values): # pyright: ignore[reportArgumentType]
            parser.error("Les couleurs doivent êtres toutes différentes.")
        
        setattr(namespace, self.dest, values)

class Check_modeles(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values, option_string: str | None = None) -> None:
        if len(values) > 3 or len(values) < 1: # pyright: ignore[reportArgumentType]
            parser.error("Vous ne pouvez prendre que 1 à 3 modèles.")

        liste_chemins = []

        for i in range(len(values)): # pyright: ignore[reportArgumentType]
            name = values[i] # pyright: ignore[reportOptionalSubscript]
            if isabs(name):
                if isfile(name) and splitext(name)[1] == ".mdl":
                    liste_chemins.append(name)
                else:
                    if splitext(name) == ".mdl":
                        parser.error("Vous devez proposer des fichier modèles modèles réels.")
                    else:
                        parser.error("Vous devez proposer des fichier modèles valides (en .mdl).")
            else:
                if isfile(join(DOSSIER_COMMANDE, name)) and splitext(name)[1] == ".mdl":
                    liste_chemins.append(join(DOSSIER_COMMANDE, name))
                else:
                    if splitext(name) == ".mdl":
                        parser.error("Vous devez proposer des fichier modèles modèles réels.")
                    else:
                        parser.error("Vous devez proposer des fichier modèles valide (en .mdl).")
        
        setattr(namespace, self.dest, values)

class Check_taille(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values, option_string: str | None = None) -> None:
        if int(values) < 0 or int(values) > 32: # pyright: ignore[reportArgumentType]
            parser.error("Les tuiles de votre modèle doivent faire au moins 1 de coté.")

        setattr(namespace, self.dest, values)

class Check_creation(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values, option_string: str | None = None) -> None:
        if splitext(values)[1] not in (".mdl", ".map"): # pyright: ignore[reportArgumentType, reportCallIssue]
            parser.error("Vous devez proposer un fichier valide (soit .mdl, soit .map).")

        if isabs(values): # pyright: ignore[reportArgumentType, reportCallIssue]
            if isdir(dirname(values)): # pyright: ignore[reportArgumentType, reportCallIssue]
                setattr(namespace, self.dest, values)
            else:
                parser.error("Vous devez proposer un chemin valide.")
        else:
            if isdir(dirname(join(DOSSIER_COMMANDE, values))): # pyright: ignore[reportArgumentType, reportCallIssue]
                setattr(namespace, self.dest, join(DOSSIER_COMMANDE, values)) # pyright: ignore[reportArgumentType, reportCallIssue]
            else:
                parser.error("Vous devez proposer un chemin valide.")

class Check_existance(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values, option_string: str | None = None) -> None:
        if splitext(values)[1] not in (".mdl", ".map"): # pyright: ignore[reportArgumentType, reportCallIssue]
            parser.error("Vous devez proposer un fichier valide (soit .mdl, soit .map).")

        if exists(values): # pyright: ignore[reportCallIssue, reportArgumentType]
            setattr(namespace, self.dest, values)
        else:
            if exists(join(DOSSIER_COMMANDE, values)): # pyright: ignore[reportArgumentType, reportCallIssue]
                setattr(namespace, self.dest, join(DOSSIER_COMMANDE, values)) # pyright: ignore[reportArgumentType, reportCallIssue]
            else:
                parser.error("Vous devez proposer un fichier valide (soit .mdl, soit .map).")
        
        setattr(namespace, "type_fichier", splitext(values)[1]) # pyright: ignore[reportCallIssue, reportArgumentType]
        

def main():
    global DOSSIER_COMMANDE
    DOSSIER_COMMANDE = getcwd()
    parser = argparse.ArgumentParser(
        description='Outils pour créer et manipuler des tilemaps (avec pyxel)',
        usage='tilemap <command> [options]'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande create
    create_parser = subparsers.add_parser('create', help='Créer une nouvelle tilemap ou un nouveau modèle de tilemap.')
    create_subparser = create_parser.add_subparsers(dest='type', help="Le type de fichier que tu veut créer.")

    # Créer un modèle
    create_mdl_parser = create_subparser.add_parser("modele", help='Pour créer un modèle.')
    create_mdl_parser.add_argument('taille', type=int, action=Check_taille, help="La taille d'un côté du modèle.")
    create_mdl_parser.add_argument('output', type=str, action=Check_creation, help='Nom du fichier créé.')
    create_mdl_parser.add_argument('-n', '--nb-tuiles', type=int, help="Le nombre de tuiles sur le modèle(influe sur la génération de tilemap)", choices=[3, 4], default= 3)
    create_mdl_parser.add_argument('-c', "--couleurs", nargs="+", action=Check_colors, help="Les couleurs que tu voudrait utiliser (au moins 2 avec leurs codes hex: comme FFFFFF ou 06dd2e)", metavar="HEX", default=None)

    # Créer un fichier de tilemap
    create_map_parser = create_subparser.add_parser("map", help="Pour créer un fichier de tilemap.")
    create_map_parser.add_argument('output', type=str, action=Check_creation, help="Le nom du fichier qui sera créé.")
    create_map_parser.add_argument('modeles', nargs='+', action=Check_modeles, help="Les fichiers que tu veut utiliser pour construire ta tilemap.")

    # Visualiser un fichier
    view_parser = subparsers.add_parser('view', help="Permet de consulter un fichier de modèle ou de tilemap.")
    view_parser.add_argument('fichier', type=str, action=Check_existance, help="Le fichier que vous voulez consulter (.mdl ou .map)")

    # Modifier un fichier
    modif_parser = subparsers.add_parser('modif', help="Permet de modifier un fichier .map ou .mdl.")
    modif_parser.add_argument('fichier', type=str, action=Check_existance, help="Le fichier que vous voulez modifier.", metavar="*.mdl, *.map")

    subparsers.add_parser("clean", help="Permet de vider le fichier temporaire qui à peut être été rempli au cours d'erreurs.")
    
    # Parse les arguments
    args = parser.parse_args()
    
    # Exécuter la commande appropriée
    if args.command == 'create':
        if args.type == "modele":
            mdl_create(args.taille, args.nb_tuiles, args.output, args.couleurs)
        elif args.type == "map":
            map_create(args.modeles, args.output)
    elif args.command == 'view':
        if args.type_fichier == ".mdl":
            mdl_view(args.fichier)
        else:
            map_view(args.fichier)
    elif args.command == 'clean':
        for file_name in listdir(DOSSIER):
            remove(join(DOSSIER, file_name))
        print()
        print("Fichiers temporaires suprimés.")
        print()
    elif args.command == 'modif':
        if args.type_fichier == ".mdl":
            mdl_modif(args.fichier)
        else:
            map_modif(args.fichier)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()