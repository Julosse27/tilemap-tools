"""
Ce fichier gére toutes les implémentations de base du module `tilemap-tools`
"""


class Tilemap:
    """
    Tjr en construction
    """
    def __init__(self) -> None:
        pass

class TilemapModel:
    """
    Tjr en construction
    """
    def __init__(self) -> None:
        pass

    @classmethod
    def load(cls, fichier:str) -> TilemapModel:
        """
        Docstring for load
        
        :param fichier: Le nom du fichier (si l'extension n'est pas .mdl une erreur est renvoyé)
        :type fichier: str
        :return: L'objet avec le fichier chargé.
        :rtype: TilemapModel
        """

        return cls()

    @staticmethod
    def create(taille_tuile: int, nb_tuiles: int, *couleurs: str, nom_fichier: str = "modèle") -> TilemapModel:
        """
        Créer un fichier .mdl et retourne la classe qui à ouvert le fichier.
        
        :param taille_tuile: Description
        :type taille_tuile: int
        :param nb_tuiles: Le nombre de tuile de coté du fichier que tu veut créer (pour l'instant soit 3 soit 4)
        :type nb_tuiles: int
        :param nom_fichier: Le nom du fichier (seul les fichier .mdl seront acceptés)
        :type nom_fichier: str
        :param couleurs: `nb variable arguments` Les couleurs spéciales avec lesquelles tu veut dessiner ton modèle.
        :type couleurs: str
        :return: L'objet avec le fichier que tu vient de créer chargé.
        :rtype: TilemapModel
        """

        return TilemapModel.load(nom_fichier)