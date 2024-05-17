import pygame
import random
import math

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

# Atom data list
ATOM_DATA = [
    {"symbol": "H", "name": "Väte", "electronegativity": 2.1, "valence": 1, "charge": "+", "color": BLUE, "radius": 35},
    {"symbol": "Na", "name": "Natrium", "electronegativity": 0.9, "valence": 1, "charge": "2+", "color": BLUE, "radius": 63},
    {"symbol": "C", "name": "Kol", "electronegativity": 2.5, "valence": 4, "charge": "", "color": RED, "radius": 25},
    {"symbol": "O", "name": "Syre", "electronegativity": 3.5, "valence": 2, "charge": "2-", "color": RED, "radius": 21},
    {"symbol": "Cl", "name": "Klor", "electronegativity": 3.0, "valence": 1, "charge": "2-", "color": RED, "radius": 35},
    {"symbol": "Ca", "name": "Kalcium", "electronegativity": 1.0, "valence": 2, "charge": "2-", "color": RED, "radius": 69},
]

# Known molecules map
MOLECULE_MAP = {
    "H2O": {"atoms": ["H", "H", "O"], "bonds": [(0, 2), (1, 2)]},
    "CH4": {"atoms": ["C", "H", "H", "H", "H"], "bonds": [(0, 1), (0, 2), (0, 3), (0, 4)]},
    "O2": {"atoms": ["O", "O"], "bonds": [(0, 1)]},
    "O3": {"atoms": ["O", "O", "O"], "bonds": [(0, 1), (1, 2)]},
    "NaCl": {"atoms": ["Na", "Cl"], "bonds": [(0, 1)]},
    "CO2": {"atoms": ["C", "O", "O"], "bonds": [(0, 1), (0, 2)]},
    "CaCl2": {"atoms": ["Ca", "Cl", "Cl"], "bonds": [(0, 1), (0, 2)]},
    "C2H4": {"atoms": ["C", "C", "H", "H", "H", "H"], "bonds": [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5)]},
    "HCl": {"atoms": ["H", "Cl"], "bonds": [(0, 1)]},
}

class Atom:
    def __init__(self, parent, x, y, symbol, name, electronegativity, valence, charge, color, radius):
        self.parent = parent
        self.x = x
        self.y = y
        self.symbol = symbol
        self.name = name
        self.electronegativity = electronegativity
        self.valence = valence
        self.charge = charge
        self.color = color
        self.radius = radius
        self.dragging = False
        self.bonds = []
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        symbol_text = self.font.render(self.symbol, True, WHITE)
        symbol_rect = symbol_text.get_rect(center=(self.x, self.y - 5))
        screen.blit(symbol_text, symbol_rect)
        if self.charge:
            charge_text = self.small_font.render(self.charge, True, WHITE)
            charge_rect = charge_text.get_rect(center=(self.x + 12, self.y - 15))
            screen.blit(charge_text, charge_rect)

    def check_collision(self, other):
        distance = math.hypot(other.x - self.x, other.y - self.y)
        if distance < self.radius + other.radius and other not in [bond[0] for bond in self.bonds]:
            self.form_bond(other)
            return True
        return False

    def form_bond(self, other):
        if self.can_bond() and other.can_bond():
            bond_type = get_bond_type(self, other)
            self.bonds.append((other, other.x - self.x, other.y - self.y))
            other.bonds.append((self, self.x - other.x, self.y - other.y))
            self.valence -= 1
            other.valence -= 1

            # Calculate the overlap distance
            min_radius = min(self.radius, other.radius)
            overlap_distance = min_radius / 2

            # Calculate the direction vector
            dx = other.x - self.x
            dy = other.y - self.y
            distance = math.hypot(dx, dy)
            direction_x = dx / distance
            direction_y = dy / distance

            # Adjust positions to overlap by half the radius of the smaller atom
            self.x += direction_x * overlap_distance
            self.y += direction_y * overlap_distance
            other.x -= direction_x * overlap_distance
            other.y -= direction_y * overlap_distance

            self.parent.check_molecule()

            return bond_type
        return None

    def can_bond(self):
        return self.valence > 0

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and self.contains_point(pos):
            if event.button == 1:
                self.dragging = True
                self.drag_offset_x = self.x - pos[0]
                self.drag_offset_y = self.y - pos[1]

            elif event.button == 3:
                self.delete()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_x = pos[0] + self.drag_offset_x
            new_y = pos[1] + self.drag_offset_y
            dx = new_x - self.x
            dy = new_y - self.y
            self.x = new_x
            self.y = new_y
            for bond in self.bonds:
                bonded_atom, _, _ = bond
                bonded_atom.update_position(self, dx, dy)

    def update_position(self, origin_atom, dx, dy):
        self.x += dx
        self.y += dy
        for bond in self.bonds:
            bonded_atom, _, _ = bond
            if bonded_atom != origin_atom:
                bonded_atom.update_position(self, dx, dy)

    def contains_point(self, pos):
        return math.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2) <= self.radius

    def delete(self):
        for bonded_atom, _, _ in self.bonds:
            bonded_atom.bonds = [bond for bond in bonded_atom.bonds if bond[0] != self]
            bonded_atom.valence += 1  # Increment valence electrons of bonded atoms
        self.parent.atoms.remove(self)
        self.parent.message = ""

    def __str__(self):
        return f"{self.symbol}: {self.name}"

def get_bond_type(atom1, atom2):
    delta_en = abs(atom1.electronegativity - atom2.electronegativity)
    if delta_en >= 1.8:
        return 'Jonbindning'
    elif 0.9 <= delta_en < 1.8:
        return 'Polär kovalent bindning'
    elif 0.4 <= delta_en < 0.9:
        return 'Svagt polär kovalent bindning'
    else:
        return 'Ren kovalent bindning'

class Button:
    def __init__(self, rect, label, color, action):
        self.rect = rect
        self.label = label
        self.color = color
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text = pygame.font.SysFont(None, 24).render(self.label, True, BLACK)
        screen.blit(text, text.get_rect(center=self.rect.center))

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pos):
            self.action()

class Game:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.atoms = []
        self.buttons = []
        self.running = True
        self.message = ""
        self.question = ""
        self.mode = "menu"

        self.create_buttons()

    def create_buttons(self):
        self.buttons.clear()
        x_offset = 10
        for atom in ATOM_DATA:
            button = Button(
                pygame.Rect(x_offset, 10, 50, 30),
                atom["symbol"],
                CYAN,
                lambda a=atom: self.add_atom(
                    400, 300, a["symbol"], a["name"], a["electronegativity"], a["valence"], a["charge"], a["color"], a["radius"]
                )
            )
            self.buttons.append(button)
            x_offset += 60

        clear_btn_pos = self.screen_width - 60
        clear_button = Button(pygame.Rect(clear_btn_pos, 10, 50, 30), "Rensa", WHITE, self.clear_atoms)
        self.buttons.append(clear_button)

        x_center = self.screen_width / 2
        y_center = self.screen_height / 2

        playground_button = Button(pygame.Rect(x_center, y_center + 50, 200, 50), "Playground", GREEN, self.start_playground)
        self.buttons.append(playground_button)

        quiz_button = Button(pygame.Rect(x_center, y_center - 50, 200, 50), "Quiz", GREEN, self.start_quiz)
        self.buttons.append(quiz_button)

    def start_playground(self):
        self.mode = "playground"
        self.create_buttons()

    def start_quiz(self):
        self.mode = "quiz"
        self.create_buttons()
        self.generate_quiz()

    def generate_quiz(self):
        self.target_molecule = random.choice(list(MOLECULE_MAP.keys()))
        self.target_atoms = MOLECULE_MAP[self.target_molecule]['atoms']
        self.target_bonds = MOLECULE_MAP[self.target_molecule]['bonds']
        self.question = f"Build the molecule: {self.target_molecule}"

    def add_atom(self, x, y, symbol, name, electronegativity, valence, charge, color, radius):
        self.atoms.append(Atom(self, x, y, symbol, name, electronegativity, valence, charge, color, radius))
        print(f"DEBUG: Added {symbol} at ({x}, {y})")

    def clear_atoms(self):
        self.atoms = []
        self.message = ""

    def check_molecule(self):
        if self.mode == "playground":
            for name, data in MOLECULE_MAP.items():
                if self.is_molecule_formed(data['atoms'], data['bonds']):
                    self.question = f"Formed {name} molecule!"
        elif self.mode == "quiz":
            if self.is_molecule_formed(self.target_atoms, self.target_bonds):
                self.question = f"Successfully built {self.target_molecule}!"

    def is_molecule_formed(self, atoms, bonds):
        if len(atoms) != len(self.atoms):
            return False

        # Create a dictionary to count the number of each atom
        atom_count = {atom: 0 for atom in atoms}
        
        for atom in self.atoms:
            if atom.symbol in atom_count:
                atom_count[atom.symbol] += 1
                # atom_instances[atom.symbol].append(atom)
        
        # Check if the counts match
        for atom in atoms:
            if atom_count[atom] != atoms.count(atom):
                return False

        for bond in bonds:
            atom1 = self.atoms[bond[0]]
            atom2 = self.atoms[bond[1]]
            res = [bonded_atom == atom2 for bonded_atom, _, _ in atom1.bonds]
            if any(res):
                break

        return True

    def run(self):
        clock = pygame.time.Clock()
        # self.mode = "quiz"
        while self.running:
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                for button in self.buttons:
                    button.handle_event(event, pos)
                for atom in self.atoms:
                    atom.handle_event(event, pos)

            self.screen.fill(BLACK)

            if self.mode == "menu":
                for button in self.buttons[-2:]:  
                    button.draw(self.screen)
            else:
                for button in self.buttons[:-2]:  
                    button.draw(self.screen)

                for i, atom in enumerate(self.atoms):
                    atom.draw(self.screen)
                    for other in self.atoms[i+1:]:
                        if atom.check_collision(other):
                            bond_type = get_bond_type(atom, other)
                            if bond_type:
                                self.message = f"{bond_type} mellan {atom.symbol} och {other.symbol}"
                                atom.color = RED
                                other.color = RED
                        else:
                            atom.color = BLUE
                            other.color = BLUE

            if self.message:
                message_text = self.font.render(self.message, True, WHITE)
                self.screen.blit(message_text, (10, self.screen_height - 50))

            if self.question and self.mode == "quiz":
                msg_txt = self.font.render(self.question, True, WHITE)
                self.screen.blit(msg_txt, (10, self.screen_height - 100))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

