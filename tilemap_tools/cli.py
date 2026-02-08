"""Point d'entrée principal pour la CLI tilemap"""
import argparse
import sys
from .create_modele import main as create_mdl_main
from .view import main as view_main
from os import getcwd, listdir, remove, makedirs
from os.path import exists, join, dirname

dossier = join(dirname(__file__), "pyxres_bin")

# Créez le dossier s'il n'existe pas
if not exists(dossier):
    makedirs(dossier)

class Check_colors(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) < 2: # pyright: ignore[reportArgumentType]
            parser.error("Vous devez fournir au moins 2 couleurs différentes.")
        elif len(values) > 16: # pyright: ignore[reportArgumentType]
            parser.error("Vous ne pouvez pas dessiner un modèle avec plus de 16 couleurs.")
        else:
            tests = []
            for test in values: # pyright: ignore[reportOptionalIterable]
                if test not in tests:
                    tests.append(test)
                else:
                    parser.error("Les couleurs doivent êtres toutes différentes.")
        
        setattr(namespace, self.dest, values)

class Check_fichier(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: str, option_string: str | None = None) -> None:
        for name in [".mdl", ".map"]:
            if exists(join(getcwd(), values + name)):
                break
        else:
            parser.error("Vous devez proposer un fichier valide (soit .mdl, soit .map).")
        
        setattr(namespace, self.dest, values)

def main():
    dossier_commande = getcwd()
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
    create_mdl_parser.add_argument('taille', type=int, help="La taille d'un côté du modèle.")
    create_mdl_parser.add_argument('output', type=str, help='Fichier de sortie', default="mon_modèle")
    create_mdl_parser.add_argument('-n', '--nb-tuiles', type=int, help="Le nombre de tuiles sur le modèle(influe sur la génération de tilemap)", choices=[3, 4], default= 3)
    create_mdl_parser.add_argument('-c', "--couleurs", nargs="+", action=Check_colors, help="Les couleurs que tu voudrait utiliser (au moins 2 avec leurs codes hex: comme FFFFFF ou 06dd2e)", metavar="HEX", default=None)

    view_parser = subparsers.add_parser('view', help="Permet de consulter un fichier de modèle ou de tilemap.")
    view_parser.add_argument('fichier', type=str, action=Check_fichier, help="Le fichier que vous voulez consulter (.mdl ou .map)")

    subparsers.add_parser("clean", help="Permet de vider le fichier temporaire qui à peut être été rempli au cours d'erreurs.")
    
    # Parse les arguments
    args = parser.parse_args()
    
    # Exécuter la commande appropriée
    if args.command == 'create':
        if args.type == "modele":
            create_mdl_main(args.taille, args.nb_tuiles, args.output, args.couleurs, dossier_commande)
        else:
            create_parser.print_help()
    elif args.command == 'view':
        view_main(args.fichier, dossier_commande)
    elif args.command == 'clean':
        dossier = join(dirname(__file__), "pyxres_bin")
        for file_name in listdir(dossier):
            remove(join(dossier, file_name))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()