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

    # Collection de tous les segments, chacun avec sa heuteur
    segments_h = []
    for facette in facettes :
        zmin, zmax = facette.zmin_et_zmax()
        hauteur = zmin // epaisseur + 1
        while hauteur <= zmax :
            segments_h.append([facette.intersection_plan_horizontal(hauteur), hauteur])
            hauteur += epaisseur

    if segments_h == [] :
        return []

    # Tris des segments selon leurs hauteurs
    for i in range(len(segments_h) - 1) :
        idx = i
        for j in range(i + 1, len(segments_h)) :
            if segments_h[j][1] < segments_h[idx][1] :
                idx = j
        if idx != i :
            segments_h[i], segments_h[idx] = segments_h[idx], segments_h[i]
    
    # Ramassage des segments de meme hauteur
    tranches = [[segments_h[0][0]]]
    for i in range(1, len(segments_h)) :
        if segments_h[i][0] != () :
            if segments_h[i][1] == segments_h[i - 1][1] :
                tranches[len(tranches) - 1].append(segments_h[i][0])
            else :
                tranches.append([segments_h[i][0]])
            
    if segments_h[0][0] == () : 
        tranches[0].pop(0)

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
