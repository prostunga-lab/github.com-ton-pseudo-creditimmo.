# CréditImmo – actualité immobilière belge

Contenu quotidien pour la chaîne YouTube [CréditImmo](https://www.youtube.com/@Cr%C3%A9ditImmo) et la page LinkedIn « Actualité Immo Belge ».

![Avatar CréditImmo](avatar-creditimmo.png)

## Contenu du dépôt

| Dossier | Rôle |
|---|---|
| `generateur/` | Générateur de Shorts verticaux (voix belge IA, sous-titres mot à mot, chiffres animés, avatar) |
| `generateur/img/` | Photos libres de droits (Wikimedia Commons) – citer les auteurs dans la description |
| `videos/AAAA-MM-JJ/` | Vidéos du jour + fiche de publication (titres, descriptions, sources, crédits) |
| `linkedin/` | Posts LinkedIn du jour |

## Générer une vidéo

Prérequis : `ffmpeg`, Node + Playwright (Chromium), Python 3 avec `pip install edge-tts`.

```bash
cd generateur
python3 make_short.py short1.json            # date du jour (Bruxelles)
python3 make_short.py short1.json 2026-10-29 # date imposée
```

Un fichier de scènes (`short1.json`) contient :
- `slug`, `voice` (**`fr-FR-VivienneMultilingualNeural`**, voix retenue), `rate` (débit, ex. `+3%`), `source` (affichée à l'écran), `credits` (photos) ;
- `format` : absent = Short vertical 1080×1920 ; `"long"` = vidéo YouTube 16:9 1920×1080 (`template_long.html`), avec scènes `chapter` + `title` (écran de chapitre) ;
- `scenes` : `text` (dit par la voix, nombres écrits en toutes lettres, « septante », « nonante »), `bg` (photo), puis
  `kicker` + `big` + `sub` (gros chiffre), **ou** `kicker` + `items` (barres : `label`, `value`, `pct`), **ou** `cta` (dernière scène).

La voix reçoit un traitement « studio » (EQ, compression, -14 LUFS) défini par `VOICE_FX` dans `make_short.py`.

Miniature (vidéos longues) :

```bash
node thumb.js img/bxl_grandplace.jpg "7 chiffres choc" "Immo belge&nbsp;: avant 2027" "+3.500 € ?" ../videos/<date>/<slug>-miniature.png
```

## Ingrédients viraux

- Accroche choc chiffrée dans les 5 premières secondes, puis promesse (« le n°1 va changer tes plans »).
- Structure en compte à rebours / chapitres : relance de l'attention toutes les 30-60 s.
- « Tu » direct, questions au spectateur, appel au commentaire au milieu et à la fin.
- Miniature : 3-4 mots énormes, un chiffre, l'avatar, contraste fort.

## Règles éditoriales

- Uniquement de l'actualité immobilière **belge** récente, chiffres **lus dans la source** et source citée.
- Pas de photos de presse (droits d'auteur) : photos libres (Wikimedia Commons, CC0/CC BY/CC BY-SA) avec crédit.
- Voix IA : déclarer « contenu modifié ou synthétique » sur YouTube.
- Information générale, jamais de conseil financier personnalisé ni de promesse de taux.
