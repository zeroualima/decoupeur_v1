#!/usr/bin/env python3
from sys import argv
from minigeo.stl import facettes_stl_binaire
from minigeo.affichable import affiche
from minigeo.utils import multiples_entre
from minigeo.doublons import suppression_doublons
from minigeo.polygone import construction_polygones
from minigeo.classification import arbre_inclusion


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

    hauteurs = multiples_entre(zmin, zmax, epaisseur)

    tranches = []
    for hauteur in hauteurs:
        segments_tranche = []
        for facette in facettes:
            zmin, zmax = facette.zmin_et_zmax()
            if zmin <= hauteur <= zmax:
                segments = facette.intersection_plan_horizontal(hauteur)
                segments_tranche.extend(segments)
        tranches.append(segments_tranche)

    return tranches


def traitement_tranche(segments):
    segments_dedoublonnes = suppression_doublons(segments)
    affiche(segments_dedoublonnes)
    polygones = construction_polygones(segments_dedoublonnes)
    print(f"on a {len(polygones)} polygones")
    # affiche(polygones)
    hierarchie = arbre_inclusion(polygones)
    hierarchie.affichage()


def main():
    if len(argv) != 4:
        print(
            "donnez un nom de fichier stl, une epaisseur de tranches, un numero de tranche a traiter"
        )
        exit()
    fichier_stl = argv[1]
    epaisseur = float(argv[2])
    tranche_cible = int(argv[3])

    facettes = list(
        f for f in facettes_stl_binaire(fichier_stl) if not f.est_horizontale()
    )
    print("on a charge", len(facettes), "facettes")

    tranches = decoupe(facettes, epaisseur)

    # for tranche in tranches:
    #     affiche(tranche)

    traitement_tranche(tranches[tranche_cible])



if __name__ == "__main__":
    main()
