#!/usr/bin/env python3
from sys import argv
from minigeo.stl import facettes_stl_binaire
from minigeo.affichable import affiche
from minigeo.utils import multiples_entre


# fct de tri rapide en (QuickSort in place) pour tris des segments selon leurs hauteurs

def partition(segments_h, inf, sup):
    pivot = segments_h[sup][1]
    i = inf - 1
    
    for j in range(inf, sup):
        if segments_h[j][1] <= pivot:
            i += 1
            segments_h[i], segments_h[j] = segments_h[j], segments_h[i]
    
    segments_h[i + 1], segments_h[sup] = segments_h[sup], segments_h[i + 1]
    return i + 1

def quicksort(segments_h, inf, sup):
    if inf < sup:
        pivot = partition(segments_h, inf, sup)
        quicksort(segments_h, inf, pivot - 1)
        quicksort(segments_h, pivot + 1, sup)



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
        hauteur = 0
        while hauteur < zmin :
            hauteur += epaisseur
        while hauteur <= zmax :
            segment = facette.intersection_plan_horizontal(hauteur)
            if segment != () :
                segments_h.append([segment, hauteur])
            hauteur += epaisseur

    if segments_h == [] :
        return []

    # Tris des segments selon leurs hauteurs ( O(nlog(n)) yy)
    # quicksort(segments_h, 0, len(segments_h) - 1)
    segments_h.sort(key=lambda x: x[1])

    # Ramassage des segments de meme hauteur
    tranches = [[segments_h[0][0]]]
    EPS = 1e-9
    for i in range(1, len(segments_h)) :
        # Pour éviter le problème de comparaison entre les floats
        # on compare avec une précision de 1e-9
        if abs(segments_h[i][1] - segments_h[i - 1][1]) < EPS:
            tranches[len(tranches) - 1].append(segments_h[i][0])
        else :
            tranches.append([segments_h[i][0]])

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
