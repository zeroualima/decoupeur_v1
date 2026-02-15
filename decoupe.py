#!/usr/bin/env python3
from sys import argv
from minigeo.stl import facettes_stl_binaire
from minigeo.affichable import affiche
from minigeo.utils import multiples_entre


def decoupe(facettes, epaisseur):
    """
    renvoie un vecteur de vecteurs de segments.
    chaque vecteur interne contient tous les segments 2d d'une seule tranche.
    le vecteur externe contient toutes les coupes de tranches de la plus basse (x minimal)
    a la plus haute (x maximal).
    """

    altitudes = [facette.zmin_et_zmax() for facette in facettes]
    zmin = min([altitude[0] for altitude in altitudes])
    zmax = max([altitude[1] for altitude in altitudes])

    hauteur = zmin
    # while hauteur < zmin :
    #     hauteur += epaisseur

    tranches = []
    while hauteur <= zmax :
        tranche = []
        for facette in facettes :
            segment = facette.intersection_plan_horizontal(hauteur)
            if segment != () :
                tranche.append(segment)
        tranches.append(tranche)
        hauteur += epaisseur

    return tranches


def main():
    if len(argv) != 3:
        print("donnez un nom de fichier stl, une epaisseur de tranches")
        exit()
    fichier_stl = argv[1]
    epaisseur = float(argv[2])

    facettes = list(
        f for f in facettes_stl_binaire(fichier_stl) if not f.est_horizontale()
    )
    print("on a charge", len(facettes), "facettes")

    tranches = decoupe(facettes, epaisseur)

    for tranche in tranches:
        affiche(tranche)


if __name__ == "__main__":
    main()
