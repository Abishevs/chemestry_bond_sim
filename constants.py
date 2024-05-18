from dataclasses import dataclass

@dataclass
class Color:
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    PINK = (255, 192, 203)
    BROWN = (165, 42, 42)
    LIME = (0, 255, 0)
    BLACK = (0, 0, 0)

ATOM_MAP = {
    "H": [2.1, 1],
    "Na": [0.9, 1],
    "C": [2.5, 4],
    "O": [3.5, 2],
    "Cl": [3.0, 1],
    "Ca": [1.0, 2],
}

ATOM_DATA = [
        {"symbol": "H",
         "name": "Väte",
         "electronegativity": 2.1,
         "valence": 1,
         "charge": "+",
         "color": Color.BLUE,
         "radius": 30},

        {"symbol": "Na",
         "name": "Natrium",
         "electronegativity": 0.9,
         "valence": 1,
         "charge": "2+",
         "color": Color.BROWN,
         "radius": 80},

        {"symbol": "C",
         "name": "Kol",
         "electronegativity": 2.5,
         "valence": 4,
         "charge": "",
         "color": Color.MAGENTA,
         "radius": 35},

        {"symbol": "O",
         "name": "Syre",
         "electronegativity": 3.5,
         "valence": 2,
         "charge": "2-",
         "color": Color.RED,
         "radius": 40},

        {"symbol": "Cl",
         "name": "Klor",
         "electronegativity": 3.0,
         "valence": 1,
         "charge": "-",
         "color": Color.ORANGE,
         "radius": 45},

        {"symbol": "Ca",
         "name": "Kalcium",
         "electronegativity": 1.0,
         "valence": 2,
         "charge": "2+",
         "color": Color.PINK,
         "radius": 90},

        ]

MOLECULE_NAME_MAP = {
        "H2O": "Vatten",
        "O2": "Syrgas",
        "O3": "Ozon",
        "NaCl": "Natriumklorid",
        "CO2": "Koldioxid",
        "CaCl2": "Kalciumklorid",
        "CH4": "Mettan",
        "C2H6": "Etan",
        "HCl": "Saltsyra",
        }

MOLECULE_MAP = {
        "H2O": {"atoms": ["H", "H", "O"], "bonds": [(0, 2), (1, 2)]},
        "CH4": {"atoms": ["C", "H", "H", "H", "H"], "bonds": [(0, 1), (0, 2), (0, 3), (0, 4)]},
        "O2": {"atoms": ["O", "O"], "bonds": [(0, 1)]},
        "O3": {"atoms": ["O", "O", "O"], "bonds": [(0, 1), (1, 2)]},
        "NaCl": {"atoms": ["Na", "Cl"], "bonds": [(0, 1)]},
        "CO2": {"atoms": ["C", "O", "O"], "bonds": [(0, 1), (0, 2)]},
        "CaCl2": {"atoms": ["Ca", "Cl", "Cl"], "bonds": [(0, 1), (0, 2)]},
        "C2H6": {"atoms": ["C", "C", "H", "H", "H", "H", "H", "H"], "bonds": [(0, 1), (0, 2), (0, 3), (0, 4), (1, 5), (1, 6), (1, 7)]},
        "HCl": {"atoms": ["H", "Cl"], "bonds": [(0, 1)]},
        "H2O2": {"atoms": ["H", "H", "O", "O"], "bonds": [(0, 2), (1, 3), (2, 3)]},
        }
