from minigeo.polygone import Polygone
from minigeo.affichable import affiche
from graphviz import Source


class Noeud:
    def __init__(self, contenu):
        self.contenu = contenu
        self.enfants = []

    def affichage(self):
        """
        creation d'un fichier dot, conversion en png et affichage dans kitty
        """
        with open("./dot/arbre.dot", "w") as f:
            f.write("digraph g {\n")
            racines = self.enfants
            for racine in racines :
                f.write(f"nPLAN -> n{id(racine)};\n")
            pile = racines
            while pile :
                noeud = pile.pop()
                for newNoeud in noeud.enfants :
                    f.write(f"n{id(noeud)} -> n{id(newNoeud)};\n")
                    pile.append(newNoeud)
            f.write("}\n")

        with open("./dot/arbre.dot") as f:
            texte_dot = f.read()
        s = Source(texte_dot, format="png")
        s.render("./dot/arbre", cleanup=True)
        s = Source(texte_dot, format="svg")
        s.render("./dot/arbre", cleanup=True)

def arbre_inclusion(polygones):
    """
    prend un ensemble de polygones qui ne s'intersectent pas (hormis sur leur bord).
    renvoie un arbre (le noeud racine etant le plan) indiquant qui est inclu dans qui.
    pre-condition: pas de doublons, pas d'intersections hors bordures.
    """
    racines = [] # elements de type Noeud
    pile = polygones
    while pile :
        polygone = pile.pop()
        pere = None
        for racine in racines :
            if racine.contenu.contient(polygone) :
                pere = racine
                break # polygone ne peut avoir qu'un seul pere parmi les racines, grace a """pas d'intersections hors bordures"""
        if pere : # On determinera la place de polygone au sein des descendants de pere
            while pere.enfants :
                pere_est_changer = False
                for enfant in pere.enfants :
                    if enfant.contenu.contient(polygone) :
                        pere = enfant
                        pere_est_changer = True
                        break
                if not pere_est_changer :
                    break
            newNoeud = Noeud(polygone)
            newNoeud.enfants = []
            pere.enfants.append(newNoeud)
        else : # On rassemble les enfants de polygone et on ajoute ce dernier a racines
            newNoeud = Noeud(polygone)
            enfants = []
            for racine in racines[:]:
                if polygone.contient(racine.contenu):
                    racines.remove(racine)
                    enfants.append(racine)
            newNoeud.enfants = enfants
            racines.append(newNoeud)
    arbre = Noeud("PLAN")
    arbre.enfants = racines
    return arbre

def main():
    p1 = Polygone.carre((0, 0), 10)
    p2 = Polygone.carre((0, 0), 8)
    p3 = Polygone.carre((-2, -2), 2)
    p4 = Polygone.carre((2, 2), 1)
    p5 = Polygone.carre((15, 15), 5)
    polygones = [p1, p2, p3, p4, p5]
    affiche(*polygones)
    racine = arbre_inclusion(polygones)
    racine.affichage()


if __name__ == "__main__":
    # newNoeud1 = Noeud("PLAN")
    # newNoeud1.enfants = []
    # newNoeud2 = Noeud(Polygone.carre((0, 0), 10))
    # newNoeud2.enfants = []
    # newNoeud1.enfants.append(newNoeud2)
    # newNoeud2.enfants.append(Noeud(Polygone.carre((15, 15), 5)))
    # newNoeud1.affichage()
    main()
