"""Texte écrit (sous-titres, avec chiffres et ponctuation) -> texte dit (voix), en français de Belgique.

Chaque mot écrit garde la trace de sa version prononcée, pour synchroniser les sous-titres sur la voix.
"""
import re

UNITES = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix",
          "onze", "douze", "treize", "quatorze", "quinze", "seize"]
DIZAINES = {2: "vingt", 3: "trente", 4: "quarante", 5: "cinquante", 6: "soixante",
            7: "septante", 8: "quatre-vingt", 9: "nonante"}

# Prononciations forcées : orthographe écrite -> ce que la voix doit dire
PRONONCIATION = {
    "Parles-en": "Parle zan", "parles-en": "parle zan",
    "Penses-y": "Pense zi", "penses-y": "pense zi",
    "Vas-y": "Va zi", "vas-y": "va zi",
    "BNB": "bé ène bé",
    "F": "èf", "D": "dé",
    "Be": "Bi", "Home": "Hôme",
    "Mijn": "Mèïne", "VerbouwPremie": "Ferbaou-prémie", "VerbouwLening": "Ferbaou-léning",
    "VerbouwLoket": "Ferbaou-loket", "PEB": "pé eu bé", "Rénopack": "Rénopak", "Rénopack,": "Rénopak,",
}


def _moins_de_cent(n):
    if n <= 16:
        return UNITES[n]
    if n < 20:
        return "dix-" + UNITES[n - 10]
    d, u = divmod(n, 10)
    if u == 0:
        return "quatre-vingts" if d == 8 else DIZAINES[d]
    if u == 1 and d != 8:
        return DIZAINES[d] + " et un"
    return DIZAINES[d] + "-" + UNITES[u]


def _moins_de_mille(n):
    c, r = divmod(n, 100)
    if c == 0:
        return _moins_de_cent(r)
    tete = "cent" if c == 1 else UNITES[c] + (" cents" if r == 0 else " cent")
    return tete if r == 0 else tete + " " + _moins_de_cent(r)


def nombre(n):
    """Entier -> lettres (jusqu'aux milliards)."""
    if n < 1000:
        return _moins_de_mille(n)
    parts = []
    for valeur, sing, plur in ((10**9, "un milliard", "milliards"), (10**6, "un million", "millions")):
        q, n = divmod(n, valeur)
        if q:
            parts.append(sing if q == 1 else _moins_de_mille(q) + " " + plur)
    q, n = divmod(n, 1000)
    if q:
        txt = _moins_de_mille(q).replace("cents", "cent").replace("vingts", "vingt")
        parts.append("mille" if q == 1 else txt + " mille")
    if n:
        parts.append(_moins_de_mille(n))
    return " ".join(parts)


def _decimal(entier, dec):
    s = nombre(int(entier.replace(".", "")))
    if dec is None:
        return s
    zeros = len(dec) - len(dec.lstrip("0"))
    reste = dec.lstrip("0")
    return s + " virgule " + " ".join(["zéro"] * zeros + ([nombre(int(reste))] if reste else []))


NUM = r"(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?"
REGLES = [
    (re.compile(r"^1er$"), lambda m: "premier"),
    (re.compile(r"^1re$"), lambda m: "première"),
    (re.compile(r"^n°(\d+)$"), lambda m: "numéro " + nombre(int(m[1]))),
    (re.compile(r"^T([1-4])$"), lambda m: ["", "premier", "deuxième", "troisième", "quatrième"][int(m[1])] + " trimestre"),
    (re.compile(r"^(\d+)[–-](\d+)$"), lambda m: nombre(int(m[1])) + " à " + nombre(int(m[2]))),
    (re.compile(r"^mi-(\d{4})$"), lambda m: "mi-" + nombre(int(m[1]))),
    (re.compile(r"^([+\-−]?)" + NUM + r"(%|€|€/mois)?$"),
     lambda m: ({"+": "plus ", "-": "moins ", "−": "moins "}.get(m[1], "")
                + _decimal(m[2], m[3])
                + {"%": " pour cent", "€": " euros", "€/mois": " euros par mois"}.get(m[4] or "", ""))),
    (re.compile(r"^%$"), lambda m: "pour cent"),
    (re.compile(r"^€$"), lambda m: "euros"),
    (re.compile(r"^€/mois$"), lambda m: "euros par mois"),
    (re.compile(r"^→$"), lambda m: "à"),
]
PONCT = ".,!?…:;»«\"()"


def prononcer(mot):
    """Un mot écrit -> sa prononciation (même mot si rien à convertir)."""
    debut = len(mot) - len(mot.lstrip(PONCT))
    fin = len(mot.rstrip(PONCT))
    if fin <= debut:  # ponctuation seule
        return mot
    coeur = mot[debut:fin]
    for regle, f in REGLES:
        m = regle.match(coeur)
        if m:
            coeur = f(m)
            break
    coeur = PRONONCIATION.get(coeur, coeur)
    return mot[:debut] + coeur + mot[fin:]


def decouper(texte):
    """-> liste de (mot_écrit, mot_dit). La ponctuation isolée (« : », « ? ») est collée au mot précédent."""
    mots = []
    for brut in texte.split():
        if mots and (all(c in PONCT + "—–" for c in brut) or brut.rstrip(PONCT) in ("%", "€", "€/mois")):
            ecrit, dit = mots[-1]
            mots[-1] = (ecrit + "\u00a0" + brut, dit + " " + prononcer(brut))
        else:
            mots.append((brut, prononcer(brut)))
    return mots


def aligner(mots, frontieres):
    """Associe à chaque mot écrit le temps (s, e) des mots prononcés par la voix.

    mots : sortie de decouper() ; frontieres : [{"w", "s", "e"}] renvoyés par la voix.
    """
    dit, spans, pos = "", [], 0
    for _, d in mots:
        if dit:
            dit += " "
        spans.append((len(dit), len(dit) + len(d)))
        dit += d
    curseur, places = 0, []
    for f in frontieres:
        i = dit.find(f["w"], curseur)
        if i < 0:
            continue
        places.append((i, i + len(f["w"]), f["s"], f["e"]))
        curseur = i + len(f["w"])
    sortie = []
    for (ecrit, _), (a, b) in zip(mots, spans):
        t = [(s, e) for (i, j, s, e) in places if i < b and j > a]
        sortie.append({"w": ecrit, "s": t[0][0] if t else None, "e": t[-1][1] if t else None})
    # mots sans horodatage (rare) : on les colle au mot voisin
    for k, w in enumerate(sortie):
        if w["s"] is None:
            avant = next((x for x in reversed(sortie[:k]) if x["e"] is not None), None)
            apres = next((x for x in sortie[k + 1:] if x["s"] is not None), None)
            w["s"] = avant["e"] if avant else (apres["s"] if apres else 0.0)
            w["e"] = apres["s"] if apres else w["s"] + 0.3
    return sortie


if __name__ == "__main__":
    for n in (1, 21, 71, 80, 81, 91, 99, 100, 200, 201, 1000, 2026, 80000, 200000, 270239, 398182, 1000000):
        print(n, nombre(n))
    for t in ["En 2026, une maison coûte 360.613 € (+3 %) : -2,2 % au T3.",
              "Le 1er janvier 2027 ; chiffre n°7 ; 31–35 ans ; 4,69 % ; mi-2025 ; 4.656 €/mois ; 2 % → 3 %. Parles-en !"]:
        print(" ".join(d for _, d in decouper(t)))
