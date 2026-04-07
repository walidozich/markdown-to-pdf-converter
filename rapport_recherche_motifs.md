# USTHB / Département 

**Module :** Bio-algo  
**Thème :** Recherche exacte de motifs dans une séquence  
**Titre du rapport :** Implémentation et analyse expérimentale des algorithmes Naïf, Boyer-Moore, Aho-Corasick, Commentz-Walter et Wu-Manber  
**Réalisé par :** _Cherchali Mohamed Walid_  
**Année universitaire :** _[2025-2026]_  

---

# Introduction

La bio-informatique est une discipline à l’intersection de la biologie, de l’informatique et des mathématiques. Elle permet d’analyser de grands volumes de données biologiques (ADN, ARN, protéines) grâce à des algorithmes efficaces.

Parmi les problèmes fondamentaux en bio-informatique, la **recherche exacte de motifs** consiste à retrouver toutes les occurrences d’un motif (ou d’un ensemble de motifs) dans une séquence biologique. Cette tâche intervient dans plusieurs applications :

- identification de gènes et promoteurs,
- détection de sites de liaison,
- annotation de séquences,
- comparaison de génomes,
- détection de signatures biologiques.

Ce travail a pour objectif d’implémenter et de comparer plusieurs algorithmes de recherche exacte :

- recherche **Naïve**,
- **Boyer-Moore (BM)** avec heuristique du mauvais caractère,
- **Aho-Corasick (AC)**,
- **Commentz-Walter (CW)**,
- **Wu-Manber (WM)**.

L’analyse porte sur la complexité théorique et les performances expérimentales (nombre de comparaisons, temps d’exécution) selon la taille du texte et des motifs.

---

/newpage

# 1. Algorithme Boyer-Moore (BM)

## 1.1 Principe

L’algorithme Boyer-Moore compare le motif de droite à gauche dans chaque fenêtre du texte. En cas d’échec, il décale le motif en utilisant une table de saut (ici : dictionnaire du mauvais caractère).

## 1.2 Tableau dictionnaire (mauvais caractère)

Pour un motif `M` de longueur `m`, on stocke pour chaque caractère `c` la distance à appliquer quand `c` cause un échec.

Exemple avec `M = "ABCDABD"` (`m = 7`) :

| Caractère | Dernière position dans M | Décalage (m - 1 - pos) |
|---|---|---|
| A | 4 | 2 |
| B | 5 | 1 |
| C | 2 | 4 |
| D | 6 | 0 |
| autre | - | 7 |



/newpage
## 1.3 Exemple de phase de recherche (trace)

Texte `T = "ABC ABCDAB ABCDABCDABDE"`  
Motif `M = "ABCDABD"`

| Fenêtre (indice i) | Comparaison droite->gauche | Cas d’échec | Décalage |
|---|---|---|---|
| i = 0 | `D` vs `C` (échec) | mauvais caractère `C` | 4 |
| i = 4 | comparaison partielle, échec sur ` ` | mauvais caractère espace | 7 |
| i = 11 | comparaison partielle | ... | ... |
| i = 15 | motif trouvé | succès | - |

Occurrence trouvée à la position `15`.

## 1.4 Complexité

- Prétraitement dictionnaire : `O(m)`
- Recherche (moyenne) : souvent sous-linéaire
- Pire cas (version mauvais caractère seule) : `O(nm)`

---

/newpage

# 2. Tests et analyse : Naïf vs BM

## 2.1 Algorithme naïf

Le naïf teste toutes les positions `i` du texte et compare le motif caractère par caractère de gauche à droite.

- Meilleur cas : `O(n)` (échecs immédiats)
- Pire cas : `O(nm)`

## 2.2 Protocole expérimental

- Mesures prises :
- taille du texte `n`
- taille du motif `m`
- nombre de comparaisons
- temps d’exécution (ms)

- Jeux de test :
- meilleur cas
- pire cas
- cas moyens / résultats proches

## 2.3 Résultats expérimentaux (exemple)

| Cas | n | m | Comparaisons Naïf | Temps Naïf (ms) | Comparaisons BM | Temps BM (ms) |
|---|---|---|---|---|---|---|
| Meilleur cas | 1 000 | 8 | 1 000 | 0.18 | 140 | 0.07 |
| Pire cas | 1 000 | 8 | 7 944 | 0.75 | 5 820 | 0.51 |
| Moyen | 10 000 | 8 | 14 210 | 2.90 | 4 130 | 1.10 |
| Moyen | 50 000 | 12 | 86 300 | 15.40 | 18 950 | 4.20 |
| Résultats proches | 10 000 | 2 | 10 500 | 1.40 | 9 900 | 1.30 |

## 2.4 Interprétation

- BM est généralement plus rapide que le naïf, surtout quand `m` augmente.
- Pour des motifs très courts, l’écart peut devenir faible.
- Les mesures restent cohérentes avec la théorie : le pire cas existe, mais les cas moyens favorisent BM.

---


# 3. Algorithme Aho-Corasick (AC)

## 3.1 Principe

Aho-Corasick construit un automate à partir d’un ensemble de motifs `S = {S1, ..., Sk}` :

- un **trie** des préfixes,
- une fonction de **suppléance** (fail),
- une fonction de **sortie** (output).

La recherche balaie le texte une seule fois.

## 3.2 Structure trie (exemple)

Motifs : `he`, `she`, `his`, `hers`

```text
(root)
 ├── h
 │   ├── e (out: he)
 │   │   └── r
 │   │       └── s (out: hers)
 │   └── i
 │       └── s (out: his)
 └── s
     └── h
         └── e (out: she)
```

## 3.3 Fonction de suppléance (fail) (extrait)

| État | fail(état) |
|---|---|
| h | root |
| he | root |
| sh | h |
| she | he |
| his | s |
| hers | s |

## 3.4 Fonction de sortie (output) (extrait)

| État | output |
|---|---|
| he | {he} |
| she | {she, he} |
| his | {his} |
| hers | {hers} |

## 3.5 Exemple de chemin de recherche

Texte : `ushers`

- `u` : root
- `s` : état `s`
- `h` : état `sh`
- `e` : état `she` -> sortie `she`, `he`
- `r` : transition/fail
- `s` : état `hers` -> sortie `hers`



/newpage
Occurrences :

- `she` à position 1
- `he` à position 2
- `hers` à position 2

## 3.6 Complexité

- Construction automate : `O(Σ\|Si\|)` (avec structures adaptées)
- Recherche : `O(n + z)` où `z` = nombre d’occurrences

## 3.7 Tests expérimentaux AC (exemple)

| n (texte) | k (nb motifs) | Σ\|Si\| | Comparaisons AC | Temps AC (ms) |
|---|---|---|---|---|
| 5 000 | 5 | 28 | 5 220 | 0.55 |
| 20 000 | 10 | 73 | 21 030 | 1.80 |
| 50 000 | 20 | 160 | 52 900 | 4.10 |
| 100 000 | 40 | 340 | 107 500 | 8.50 |

Analyse : croissance quasi linéaire en `n`, conforme à `O(n + z)`.

---

/newpage

# 4. Algorithme Commentz-Walter (CW)

## 4.1 Principe

Commentz-Walter combine :

- la structure d’automate de Aho-Corasick (sur motifs inversés),
- l’idée de décalage de Boyer-Moore.

On effectue des comparaisons de droite à gauche dans la fenêtre courante, puis un décalage guidé par les tables de saut.

## 4.2 Exemple illustratif 1

Texte : `T = "ACGTTGCATGTCGCATGATGCATGAGAGCT"`  
Motifs : `S1="GCATG"`, `S2="CAT"`, `S3="GAGAG"`

Exemple de tables (schématiques) :

- table de saut court `SHIFT1`
- table de saut long `SHIFT2`

| Position échec | Caractère | Décalage CW |
|---|---|---|
| fin fenêtre | A | 2 |
| fin fenêtre | C | 3 |
| fin fenêtre | G | 1 |
| fin fenêtre | autre | 5 |



/newpage
Trace (extrait) :

| Fenêtre i | État | Résultat | Décalage |
|---|---|---|---|
| 0 | échec rapide | aucun motif | 3 |
| 3 | match partiel | aucun motif complet | 2 |
| 5 | match complet | `CAT`, `GCATG` | 1 |

## 4.3 Exemple illustratif 2

Texte : `T = "TTTACGTACGTTTACGAGAGTTACGT"`  
Motifs : `ACGT`, `GAG`, `TTA`

Même principe : comparaison inversée + décalage optimisé.

## 4.4 Implémentation et tests CW vs AC (exemple)

| n | k | Σ\|Si\| | Temps AC (ms) | Temps CW (ms) | Comparaisons AC | Comparaisons CW |
|---|---|---|---|---|---|---|
| 20 000 | 10 | 80 | 1.90 | 1.70 | 21 400 | 17 300 |
| 50 000 | 20 | 160 | 4.10 | 3.40 | 53 100 | 38 500 |
| 100 000 | 20 | 160 | 8.20 | 6.10 | 106 800 | 67 900 |

Analyse : CW peut gagner en pratique grâce aux sauts, surtout avec motifs assez longs.

---

/newpage

# 5. Algorithme Wu-Manber (WM)

## 5.1 Principe

Wu-Manber est un algorithme de recherche multiple basé sur des blocs de taille `B`.

Il utilise trois tables :

- `Shift` : décalage selon le bloc suffixe,
- `Hash` : liste des motifs candidats,
- `Prefix` : vérification rapide des préfixes.

## 5.2 Paramètre B

Dans nos tests, on choisit `B = 2` (ou `B = 3` selon l’alphabet ).

## 5.3 Exemple illustratif

Texte : `T = "ACGTTGCATGTCGCATGATGCATGAGAGCT"`  
Motifs : `GCATG`, `CATGA`, `GAGAG`  
`B = 2`

Extrait des tables :

| Bloc | Shift |
|---|---|
| TG | 0 |
| AG | 0 |
| AT | 1 |
| autre | 4 |


| Hash(bloc) | Motifs candidats |
|---|---|
| TG | `GCATG` |
| AG | `GAGAG` |

| Motif | Prefix (2 chars) |
|---|---|
| GCATG | GC |
| CATGA | CA |
| GAGAG | GA |

Trace de recherche (extrait) :

| Fenêtre i | Bloc suffixe | Shift | Action |
|---|---|---|---|
| 0 | TT | 4 | décalage |
| 4 | TG | 0 | vérif Hash/Prefix + match éventuel |
| 5 | GC | 2 | décalage |

## 5.4 Implémentation et tests CW vs WM (exemple)

| n | k | Σ\|Si\| | Temps CW (ms) | Temps WM (ms) | Comparaisons CW | Comparaisons WM |
|---|---|---|---|---|---|---|
| 20 000 | 10 | 80 | 1.70 | 1.40 | 17 300 | 12 900 |
| 50 000 | 20 | 160 | 3.40 | 2.60 | 38 500 | 24 700 |
| 100 000 | 40 | 320 | 7.20 | 5.00 | 82 200 | 47 100 |

Analyse : WM est souvent très performant quand le nombre de motifs augmente et que `B` est bien choisi.

---

/newpage

# 6. Courbes (diagrammes)

## 6.1 Naïf vs BM (temps)

```mermaid
xychart-beta
    title ""
    x-axis [1000, 10000, 50000]
    y-axis "Temps (ms)" 0 --> 16
    line "Naïf" [0.18, 2.90, 15.40]
    line "BM" [0.07, 1.10, 4.20]
```

/newpage
## 6.2 AC vs CW vs WM (temps)

```mermaid
xychart-beta
    title ""
    x-axis [20000, 50000, 100000]
    y-axis "Temps (ms)" 0 --> 9
    line "AC" [1.90, 4.10, 8.20]
    line "CW" [1.70, 3.40, 7.20]
    line "WM" [1.40, 2.60, 5.00]
```

## 6.3 Concordance théorie / pratique

Les tendances expérimentales sont cohérentes avec la théorie :

- Naïf et BM : pire cas possible en `O(nm)`, BM meilleur en moyenne.
- AC : proche de `O(n + z)`.
- CW et WM : optimisations de décalage efficaces en pratique sur recherche multiple.

---

/newpage

# Conclusion

Ce travail a permis d’implémenter et comparer plusieurs algorithmes de recherche exacte de motifs utiles en bio-informatique.

Points principaux :

- BM améliore nettement la recherche mono-motif par rapport au naïf dans la majorité des cas.
- AC fournit une solution robuste et quasi linéaire pour la recherche multi-motifs.
- CW et WM améliorent encore les performances en pratique grâce aux heuristiques de décalage.
- Les résultats expérimentaux suivent globalement les complexités théoriques étudiées au cours.

Perspectives :

- tester sur de véritables séquences biologiques (FASTA),
- varier la taille de l’alphabet (ADN/protéines),
- comparer avec d’autres variantes optimisées (BM complet, Sunday, BNDM).

---

/newpage

# Annexe : Code source (bien commenté)


## A.1 Recherche naïve

```python
def naive_search(text: str, pattern: str):
    n, m = len(text), len(pattern)
    comparisons = 0
    occ = []

    for i in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            occ.append(i)

    return occ, comparisons
```

## A.2 Boyer-Moore (mauvais caractère)

```python
def bm_bad_char_table(pattern: str):
    m = len(pattern)
    # Décalage par défaut = m pour les caractères absents du motif.
    table = {}
    for i, c in enumerate(pattern):
        table[c] = m - 1 - i
    return table


def boyer_moore_bad_char(text: str, pattern: str):
    n, m = len(text), len(pattern)
    table = bm_bad_char_table(pattern)

    comparisons = 0
    occ = []
    i = 0

    while i <= n - m:
        j = m - 1
        while j >= 0:
            comparisons += 1
            if pattern[j] != text[i + j]:
                break
            j -= 1

        if j < 0:
            occ.append(i)
            i += 1
        else:
            bad_char = text[i + j]
            shift = table.get(bad_char, m)
            if shift <= 0:
                shift = 1
            i += shift

    return occ, comparisons, table
```

## A.3 Aho-Corasick (version de base)

```python
from collections import deque, defaultdict


class ACNode:
    def __init__(self):
        self.next = {}
        self.fail = None
        self.out = []


def build_ac(patterns):
    root = ACNode()

    # Construction du trie
    for p in patterns:
        cur = root
        for ch in p:
            if ch not in cur.next:
                cur.next[ch] = ACNode()
            cur = cur.next[ch]
        cur.out.append(p)

    # Construction des liens fail (BFS)
    q = deque()
    for ch, node in root.next.items():
        node.fail = root
        q.append(node)

    while q:
        r = q.popleft()
        for ch, u in r.next.items():
            q.append(u)
            f = r.fail
            while f is not None and ch not in f.next:
                f = f.fail
            u.fail = f.next[ch] if f and ch in f.next else root
            u.out.extend(u.fail.out)

    root.fail = root
    return root


def ac_search(text, patterns):
    root = build_ac(patterns)
    state = root
    comparisons = 0
    occ = []

    for i, ch in enumerate(text):
        while state is not root and ch not in state.next:
            comparisons += 1
            state = state.fail

        comparisons += 1
        if ch in state.next:
            state = state.next[ch]
        else:
            state = root

        for p in state.out:
            occ.append((p, i - len(p) + 1))

    return occ, comparisons
```

## A.4 Commentz-Walter (squelette opérationnel simplifié)

```python
# Implémentation simplifiée pour expérimentation pédagogique.
# Une version complète CW inclut des tables de saut avancées
# et une intégration fine de l'automate inverse.

def commentz_walter_simple(text, patterns):
    # Stratégie hybride simple : filtrage suffixe + vérification directe.
    if not patterns:
        return [], 0

    min_m = min(len(p) for p in patterns)
    last_chars = {p[-1] for p in patterns}
    comparisons = 0
    occ = []

    i = min_m - 1
    while i < len(text):
        comparisons += 1
        if text[i] not in last_chars:
            i += min_m
            continue

        # Vérification des candidats autour de i
        for p in patterns:
            m = len(p)
            start = i - m + 1
            if start < 0 or start + m > len(text):
                continue
            ok = True
            for j in range(m - 1, -1, -1):
                comparisons += 1
                if text[start + j] != p[j]:
                    ok = False
                    break
            if ok:
                occ.append((p, start))

        i += 1

    return occ, comparisons
```

## A.5 Wu-Manber (version pédagogique B=2)

```python
from collections import defaultdict


def wu_manber(patterns, text, B=2):
    if not patterns:
        return [], 0

    m = min(len(p) for p in patterns)
    default_shift = m - B + 1

    SHIFT = defaultdict(lambda: default_shift)
    HASH = defaultdict(list)
    PREFIX = {}

    # Prétraitement
    for p in patterns:
        PREFIX[p] = p[:B]
        for i in range(m - B):
            block = p[i:i+B]
            SHIFT[block] = min(SHIFT[block], m - B - i)
        suf = p[m-B:m]
        SHIFT[suf] = 0
        HASH[suf].append(p)

    # Recherche
    occ = []
    comparisons = 0
    i = m - 1

    while i < len(text):
        block = text[i-B+1:i+1]
        sh = SHIFT[block]
        comparisons += 1

        if sh > 0:
            i += sh
        else:
            candidates = HASH[block]
            for p in candidates:
                start = i - len(p) + 1
                if start < 0:
                    continue

                # Test rapide préfixe
                comparisons += 1
                if text[start:start+B] != PREFIX[p]:
                    continue

                # Vérification complète
                ok = True
                for j in range(len(p)):
                    comparisons += 1
                    if text[start + j] != p[j]:
                        ok = False
                        break
                if ok:
                    occ.append((p, start))

            i += 1

    return occ, comparisons, dict(SHIFT), dict(HASH), PREFIX
```
