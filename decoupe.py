#!/usr/bin/env python3
from sys import argv
from minigeo.stl import facettes_stl_binaire
from minigeo.affichable import affiche
from minigeo.utils import multiples_entre
from minigeo.doublons import suppression_doublons
from minigeo.polygone import construction_polygones
from minigeo.classification import arbre_inclusion
from minigeo.polygone_a_trous import construction_polygones_a_trous


from minigeo.segment import Segment
from minigeo.point import distance
import math



class KDNoeud :
    """
    un arbre KD (a 2 dimensions) partitionnant le plan de travail
    """

    def __init__(self, point, axe, bbox, gauche, droite) :
        self.point = point
        self.axe = axe # 0 si coupure selon x, 1 si selon y
        self.bbox = bbox # (x_min, x_max, y_min, y_max) de tout le sous-arbre
        self.droite = droite # fils droit ou None/[] (fils haut si verticalemet)
        self.gauche = gauche # fils gauche ou None/[] (fils bas si verticalement)


# un algo un peu lent pour la decoupe
def decoupe(facettes, epaisseur):
    zmin = min(z for f in facettes for _, _, z in f.points)
    zmax = max(z for f in facettes for _, _, z in f.points)
    tranches = []
    for hauteur in multiples_entre(zmin, zmax, epaisseur):
        facettes_tranche = []
        for facette in facettes:
            facettes_tranche.extend(facette.intersection_plan_horizontal(hauteur))
        tranches.append(facettes_tranche)
    return tranches


def distance_rectangle(point, bbox) :
    x, y = point
    xmin, xmax, ymin, ymax = bbox
    if xmin <= x <= xmax :
        if ymin <= y <= ymax :
            return 0
        else : 
            return min(abs(ymax - y), abs(ymin - y))
    else :
        if ymin <= y <= ymax :
            return min(abs(xmax - x), abs(xmin - x))
        elif y < ymin :
            if x < xmin :
                return distance((x, y), (xmin, ymin))
            else :
                return distance((x, y), (xmax, ymin))
        else :
            if x < xmin :
                return distance((x, y), (xmin, ymax))
            else :
                return distance((x, y), (xmax, ymax))
            

def quicksort_points(points, direction):
    if len(points) <= 1:
        return points

    pivot = points[len(points) // 2]

    left   = [p for p in points if p[direction] <  pivot[direction]]
    middle = [p for p in points if p[direction] == pivot[direction]]
    right  = [p for p in points if p[direction] >  pivot[direction]]

    return quicksort_points(left, direction) + middle + quicksort_points(right, direction)
            
def arbre_kd(x_sorted_points, y_sorted_points, axe) :
    if len(x_sorted_points) == 0 :
        return None
    if len(x_sorted_points) == 1 :
        point = x_sorted_points[0]
        return KDNoeud(point, (axe + 1) % 2, (point[0], point[0], point[1], point[1]), None, None)
    bbox = (x_sorted_points[0][0], x_sorted_points[-1][0], y_sorted_points[0][1], y_sorted_points[-1][1])
    if axe == 0 : # ie axe = 0 pour la direction x
        idx = len(x_sorted_points)//2
        point = x_sorted_points[idx]
        new_x_sorted_gauche = x_sorted_points[:idx]
        new_x_sorted_droite = x_sorted_points[idx + 1:]
        new_y_sorted_gauche = [p for p in y_sorted_points if p in set(new_x_sorted_gauche)]
        new_y_sorted_droite = [p for p in y_sorted_points if p in set(new_x_sorted_droite)]
        return KDNoeud(point, axe, bbox, arbre_kd(new_x_sorted_gauche, new_y_sorted_gauche, 1), arbre_kd(new_x_sorted_droite, new_y_sorted_droite, 1))
    else :
        idx = len(y_sorted_points)//2
        point = y_sorted_points[idx]
        new_y_sorted_bas = y_sorted_points[:idx]
        new_y_sorted_haut = y_sorted_points[idx + 1:]
        new_x_sorted_bas = [p for p in x_sorted_points if p in set(new_y_sorted_bas)]
        new_x_sorted_haut = [p for p in x_sorted_points if p in set(new_y_sorted_haut)]
        return KDNoeud(point, axe, bbox, arbre_kd(new_x_sorted_bas, new_y_sorted_bas, 0), arbre_kd(new_x_sorted_haut, new_y_sorted_haut, 0))
    
def plus_proche_segment(point, noeud, segments_visites, r_best=math.inf):
    """
    Retourne (point_le_plus_proche, distance) parmi les endpoints
    de segments non visités.
    """
    if noeud is None:
        return (None, r_best)

    meilleur = None

    if noeud.point not in segments_visites:
        d = distance(point, noeud.point)
        if d < r_best:
            r_best = d
            meilleur = noeud.point

    if noeud.axe == 0:
        premier = noeud.droite if point[0] >= noeud.point[0] else noeud.gauche
        second  = noeud.gauche if point[0] >= noeud.point[0] else noeud.droite
    else:
        premier = noeud.droite if point[1] >= noeud.point[1] else noeud.gauche
        second  = noeud.gauche if point[1] >= noeud.point[1] else noeud.droite

    candidat, r_best = plus_proche_segment(point, premier, segments_visites, r_best)
    if candidat is not None:
        meilleur = candidat

    if second is not None and distance_rectangle(point, second.bbox) < r_best:
        candidat2, r_best = plus_proche_segment(point, second, segments_visites, r_best)
        if candidat2 is not None:
            meilleur = candidat2

    return (meilleur, r_best)
    
def extract_rectangles(racine_kd) :
    if racine_kd == None :
        return []
    bbox = racine_kd.bbox
    p1 = (bbox[0], bbox[2])
    p2 = (bbox[0], bbox[3])
    p3 = (bbox[1], bbox[2])
    p4 = (bbox[1], bbox[3])
    return [Segment(p1, p2), Segment(p1, p3), Segment(p2, p4), Segment(p3, p4)] + extract_rectangles(racine_kd.gauche) + extract_rectangles(racine_kd.droite)
 

def traitement_tranche(segments, buse):
    segments_dedoublonnes = suppression_doublons(segments)
    #affiche(segments_dedoublonnes)
    polygones = construction_polygones(segments_dedoublonnes)
    print(f"on a {len(polygones)} polygones")
    #affiche(polygones)
    polygones_a_trous = construction_polygones_a_trous(polygones)
    #affiche(polygones_a_trous)
    segments = []
    for poly in polygones_a_trous:
        segments.extend(poly.decoupe(buse))
        # NOTE: on pourrait ajouter egalement les segments des polygones

    x_sorted_points = quicksort_points([p for segment in segments for p in (segment.debut, segment.fin)], 0)
    y_sorted_points = quicksort_points([p for segment in segments for p in (segment.debut, segment.fin)], 1)
    racine_kd = arbre_kd(x_sorted_points, y_sorted_points, 0)
    
    # segments.extend(extract_rectangles(racine_kd))
    affiche(segments)

    # Construction d'un index point → segment pour retrouver l'autre bout
    endpoint_to_segment = {}
    for seg in segments:
        endpoint_to_segment[seg.debut] = seg
        endpoint_to_segment[seg.fin]   = seg

    points_visites = set()   # endpoints déjà consommés
    tableau = []             # trajectoire finale (impressions + transitions)

    courant = segments[0].debut
    points_visites.add(segments[0].debut)
    points_visites.add(segments[0].fin)
    tableau.append(segments[0])         # on imprime le premier segment
    courant = segments[0].fin           # on est maintenant à son autre bout

    while len(points_visites) < 2 * len(segments):
        # Chercher l'endpoint non visité le plus proche
        proche, _ = plus_proche_segment(courant, racine_kd, points_visites)
        if proche is None:
            break

        # Transition sans impression
        tableau.append(Segment(courant, proche))
        affiche(tableau)

        # Retrouver le segment auquel appartient cet endpoint
        seg = endpoint_to_segment[proche]

        # Déterminer l'autre bout du segment pour savoir où on finit
        autre_bout = seg.fin if proche == seg.debut else seg.debut

        # Imprimer le segment
        tableau.append(Segment(proche, autre_bout))
        affiche(tableau)

        # Marquer les deux bouts comme visités
        points_visites.add(proche)
        points_visites.add(autre_bout)

        courant = autre_bout
    


def main():
    if len(argv) != 5:
        print(
            "donnez un nom de fichier stl, une epaisseur de tranches, un diametre de buse, un numero de tranche a traiter"
        )
        exit()
    fichier_stl = argv[1]
    epaisseur = float(argv[2])
    buse = float(argv[3])
    tranche_cible = int(argv[4])

    facettes = list(
        f for f in facettes_stl_binaire(fichier_stl) if not f.est_horizontale()
    )
    print("on a charge", len(facettes), "facettes")

    tranches = decoupe(facettes, epaisseur)

    # for tranche in tranches:
    #     affiche(tranche)

    traitement_tranche(tranches[tranche_cible], buse)


if __name__ == "__main__":
    main()
