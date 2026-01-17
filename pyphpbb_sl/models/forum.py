from dataclasses import dataclass


@dataclass(slots=True)
class SubForum:
    name: str
    url: str


# Pourquoi slots=True ?
# - tu l’utilises déjà ailleurs
# - ça réduit l’empreinte mémoire
# - ça rend les instances plus rapides
# - ça évite les attributs dynamiques accidentels
# C’est exactement ce qu’il faut pour des objets simples et nombreux.
