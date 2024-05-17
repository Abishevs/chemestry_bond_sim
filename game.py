import random
import time
import math

import pygame

from constants import ATOM_DATA, MOLECULE_NAME_MAP, Color, MOLECULE_MAP
from utils import get_bond_type
        

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
        symbol_text = self.font.render(self.symbol, True, Color.WHITE)
        symbol_rect = symbol_text.get_rect(center=(self.x, self.y - 5))
        screen.blit(symbol_text, symbol_rect)
        if self.charge:
            charge_text = self.small_font.render(self.charge, True, Color.WHITE)
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


class Button:
    def __init__(self, rect, label, color, action, text_color = Color.BLACK):
        self.rect = rect
        self.label = label
        self.color = color
        self.action = action
        self.text_color = text_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text = pygame.font.SysFont(None, 24).render(self.label, True, self.text_color)
        screen.blit(text, text.get_rect(center=self.rect.center))

    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pos):
            self.action()
class Menu:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        x_center = self.game.screen_width // 2 - 100
        y_center = self.game.screen_height // 2 - 25
        playground_button = Button(pygame.Rect(x_center, y_center + 50, 200, 50), "Playground", Color.GREEN, self.game.start_playground)
        self.buttons.append(playground_button)
        quiz_button = Button(pygame.Rect(x_center, y_center - 50, 200, 50),
                             "Quiz", Color.GREEN, self.game.start_quiz)
        self.buttons.append(quiz_button)

        quit_button = Button(pygame.Rect(x_center, y_center + 150, 200, 50),
                             "Stäng", Color.RED, self.game.quit_game,
                             text_color=Color.WHITE)
        self.buttons.append(quit_button)

    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.handle_event(event, pos)

    def draw(self):
        self.game.screen.fill(Color.BLACK)
        for button in self.buttons:
            button.draw(self.game.screen)

class Playground:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        x_offset = 10
        for atom in ATOM_DATA:
            button = Button(
                pygame.Rect(x_offset, 10, 50, 30),
                atom["symbol"],
                Color.BROWN,
                lambda a=atom: self.game.add_atom(
                    *self.get_random_position(), a["symbol"], a["name"], a["electronegativity"], a["valence"], a["charge"], a["color"], a["radius"]
                ),
                text_color=Color.WHITE

            )
            self.buttons.append(button)
            x_offset += 60

        clear_btn_pos = self.game.screen_width - 130
        clear_button = Button(pygame.Rect(clear_btn_pos, 10, 60, 30), "Rensa",
                              Color.RED, self.game.clear_atoms, text_color=Color.WHITE)
        self.buttons.append(clear_button)

        menu_btn_pos = self.game.screen_width - 60
        menu_button = Button(pygame.Rect(menu_btn_pos, 10, 50, 30), "Meny", Color.WHITE, self.game.open_menu)
        self.buttons.append(menu_button)

    def get_random_position(self):
        min_distance = 100  
        max_attempts = 100
        offset_range = 10  # Small offset range to avoid perfect overlap

        for _ in range(max_attempts):
            x = random.randint(50, self.game.screen_width - 50)
            y = random.randint(50, self.game.screen_height - 50)
            if all(math.hypot(x - atom.x, y - atom.y) > min_distance for atom in self.game.atoms):
                x += random.randint(-offset_range, offset_range)
                y += random.randint(-offset_range, offset_range)
                return x, y

        # If a suitable position is not found, still return a random position with an offset
        return (self.game.screen_width // 2 + random.randint(-offset_range, offset_range), 
                self.game.screen_height // 2 + random.randint(-offset_range, offset_range))

    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.handle_event(event, pos)

        for atom in self.game.atoms:
            atom.handle_event(event, pos)

    def update(self):
        for i, atom in enumerate(self.game.atoms):
            for other in self.game.atoms[i + 1:]:
                if atom.check_collision(other):
                    bond_type = get_bond_type(atom, other)
                    if bond_type:
                        self.game.message = f"{bond_type} mellan {atom} och {other}"

    def draw(self):
        self.game.screen.fill(Color.BLACK)
        for button in self.buttons:
            button.draw(self.game.screen)
        for atom in self.game.atoms:
            atom.draw(self.game.screen)
        if self.game.message:
            message_text = self.game.font.render(self.game.message, True, Color.WHITE)
            self.game.screen.blit(message_text, (10, self.game.screen_height - 50))


class Quiz(Playground):
    def __init__(self, game):
        super().__init__(game)
        self.target_molecule = ""
        self.target_atoms = []
        self.target_bonds = []
        self.success_timestamp = None
        self.generate_quiz()

    def generate_quiz(self):
        self.target_molecule = random.choice(list(MOLECULE_MAP.keys()))
        self.target_atoms = MOLECULE_MAP[self.target_molecule]['atoms']
        self.target_bonds = MOLECULE_MAP[self.target_molecule]['bonds']
        molecule_name = MOLECULE_NAME_MAP[self.target_molecule]
        self.game.question = f"Bygg: {molecule_name} ({self.target_molecule})"
        self.game.clear_atoms()

    def draw(self):
        super().draw()
        if self.game.question:
            question_text = self.game.font.render(self.game.question, True, Color.WHITE)
            question_rect = question_text.get_rect()
            question_x = (self.game.screen_width - question_rect.width) // 2
            question_y = 50 + 40  # 50 for the button height and 40 for the padding
            self.game.screen.blit(question_text, (question_x, question_y))

    def update(self):
        if self.success_timestamp and (time.time() - self.success_timestamp) > 5:  # 2 seconds display time
            self.generate_quiz()  # Generate a new quiz
            self.success_timestamp = None


class Game:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.atoms = []
        self.running = True
        self.message = ""
        self.question = ""
        self.mode = "menu"
        self.menu = Menu(self)
        self.playground = Playground(self)
        self.quiz = Quiz(self)

    def reset(self):
        self.message = ""
        self.question = ""

    def start_playground(self):
        self.mode = "playground"

    def start_quiz(self):
        self.mode = "quiz"

    def open_menu(self):
        self.mode = "menu"

    def quit_game(self):
        self.running = False

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
                    self.question = f"Byggd {MOLECULE_NAME_MAP[name]} ({name})!"
        elif self.mode == "quiz":
            if self.is_molecule_formed(self.quiz.target_atoms, self.quiz.target_bonds):
                molecule = self.quiz.target_molecule
                molecule_name = MOLECULE_NAME_MAP[molecule]
                self.question = f"Korrekt byggd: {molecule_name} ({molecule})!"
                self.quiz.success_timestamp = time.time()

    def is_molecule_formed(self, atoms, bonds):
        if len(atoms) != len(self.atoms):
            return False

        # Create a dictionary to count the number of each atom
        atom_count = {atom: 0 for atom in atoms}
        
        for atom in self.atoms:
            if atom.symbol in atom_count:
                atom_count[atom.symbol] += 1
        
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
    
    def event_handler(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        if self.mode == "menu":
            self.menu.handle_event(event)
        elif self.mode == "playground":
            self.playground.handle_event(event)
        elif self.mode == "quiz":
            self.quiz.handle_event(event)

    def screen_handler(self):
        if self.mode == "menu":
            self.menu.draw()
        elif self.mode == "playground":
            self.playground.update()
            self.playground.draw()
        elif self.mode == "quiz":
            self.playground.update()
            self.quiz.update()
            self.quiz.draw()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                self.event_handler(event)
            self.screen_handler()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()           
