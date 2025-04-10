# photon_game_gui_improved.py

import pygame
import random
import sys
import time
import math

pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚡ Photon → Electricity Simulation Game")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
DARK_GRAY = (30, 30, 30)
CYAN = (0, 255, 255)
GRAY = (80, 80, 80)
PURPLE = (200, 100, 255)

# Fonts
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 28, bold=True)
title_font = pygame.font.SysFont("georgia", 28, italic=True)

# Assets
bulb_off = pygame.transform.scale(pygame.image.load("bulb_off.png"), (80, 120))
bulb_on = pygame.transform.scale(pygame.image.load("bulb_on.png"), (80, 120))
zap_sound = pygame.mixer.Sound("zap.wav")

clock = pygame.time.Clock()

# Background stars
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.2, 1)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 2)

stars = [Star() for _ in range(120)]

# Photon class
class Photon:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 250)
        self.y = 0
        self.speed = random.randint(2, 4)
        self.color = BLUE

    def fall(self):
        self.y += self.speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 8)

# Spark class
class Spark:
    def __init__(self, x, y):
        self.particles = [(x, y, random.uniform(-2, 2), random.uniform(-2, 2), 10) for _ in range(10)]

    def update(self):
        for i, (x, y, dx, dy, life) in enumerate(self.particles):
            self.particles[i] = (x + dx, y + dy, dx, dy, life - 1)

    def draw(self):
        for x, y, _, _, life in self.particles:
            if life > 0:
                pygame.draw.circle(screen, CYAN, (int(x), int(y)), 2)

    def is_dead(self):
        return all(p[4] <= 0 for p in self.particles)

# Detector class
class Detector:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 30
        self.width = 100
        self.height = 15
        self.speed = 6

    def move(self, direction):
        if direction == "LEFT":
            self.x -= self.speed
        elif direction == "RIGHT":
            self.x += self.speed
        self.x = max(100, min(WIDTH - 250 - self.width, self.x))

    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height), border_radius=6)

    def detect(self, photon):
        return (self.x < photon.x < self.x + self.width and self.y < photon.y < self.y + self.height)

stored_electrons = []  # Global list to hold settled electrons
stored_holes = [] 
# Updated BandTransition class (fixed x-position with delay for stay effect and permanent placement)
class BandTransition:
    def __init__(self):
        self.electron_x = 50
        self.hole_y = 470     # Valence band Y
        self.electron_y = self.hole_y
        self.target_y = 220   # Conduction band Y
        self.active = True
        self.phase = "moving"
        self.timer = 60
        self.stay_duration = 30

        self.hole_pos = self.get_non_overlapping_hole_position()

    def get_non_overlapping_position(self):
        max_attempts = 50
        radius = 12
        for _ in range(max_attempts):
            new_x = random.randint(30 + radius, 80 - radius)
            new_y = random.randint(140 + radius, 250 - radius)
            overlap = False
            for ex, ey in stored_electrons:
                distance = math.hypot(new_x - ex, new_y - ey)
                if distance < radius:
                    overlap = True
                    break
            if not overlap:
                return (new_x, new_y)
        return (random.randint(30, 70), random.randint(150, 260))

    def get_non_overlapping_hole_position(self):
        max_attempts = 50
        radius = 10
        for _ in range(max_attempts):
            new_x = random.randint(30 + radius, 80 - radius)
            new_y = random.randint(440 + radius, 480 - radius)
            overlap = False
            for hx, hy in stored_holes:
                distance = math.hypot(new_x - hx, new_y - hy)
                if distance < radius:
                    overlap = True
                    break
            if not overlap:
                return (new_x, new_y)
        return (random.randint(30, 70), random.randint(450, 470))

    def update(self):
        if self.phase == "moving":
            if self.timer > 0:
                self.electron_y -= (self.hole_y - self.target_y) / 60
                self.timer -= 1
            else:
                self.phase = "staying"
                self.timer = self.stay_duration
        elif self.phase == "staying":
            self.timer -= 1
            if self.timer <= 0:
                ex, ey = self.get_non_overlapping_position()
                stored_electrons.append((ex, ey))       # Store electron
                stored_holes.append(self.hole_pos)      # Store non-overlapping hole
                self.active = False

    def draw(self):
        # Draw moving hole while active
        if self.active:
            pygame.draw.circle(screen, WHITE, (int(self.hole_pos[0]), int(self.hole_pos[1])), 5, 2)

        # Draw moving electron
        if self.active:
            pygame.draw.circle(screen, YELLOW, (int(self.hole_pos[0]), int(self.hole_pos[1])), 6)
            pygame.draw.circle(screen, ORANGE, (int(self.hole_pos[0]), int(self.electron_y)), 6)
            pygame.draw.line(screen, RED, (int(self.hole_pos[0]), int(self.hole_pos[1])),
                             (int(self.hole_pos[0]), int(self.electron_y)), 2)


def draw_stored_electrons():
    for (x, y) in stored_electrons:
        pygame.draw.circle(screen, ORANGE, (x, y), 6)
    for hx, hy in stored_holes:
        pygame.draw.circle(screen, WHITE, (hx, hy), 5, 2)
# Electron-Hole pair
class ElectronHolePair:
    def __init__(self, x, y):
        self.e_x = x
        self.h_x = x
        self.y = y
        self.timer = 80
        self.animate_current = True

    def update(self):
        self.e_x += 1.5
        self.h_x -= 1.5
        self.timer -= 1
        if self.timer <= 0:
            self.animate_current = False

    def draw(self):
        pygame.draw.circle(screen, ORANGE, (int(self.e_x), self.y), 6)
        pygame.draw.circle(screen, YELLOW, (int(self.h_x), self.y), 6)
        if self.animate_current:
            pygame.draw.line(screen, RED, (self.e_x, self.y), (WIDTH - 100, 120), 2)
            pygame.draw.line(screen, RED, (WIDTH - 100, 120), (WIDTH - 100, 240), 2)
# Quiz questions
quiz_questions = [
    ("What do photons generate in solar cells?", ["Current", "Heat", "Sound", "Radiation"], 0),
    ("Which particle is negatively charged?", ["Hole", "Electron", "Photon", "Proton"], 1),
    ("Photon energy is used in which medical tool?", ["Stethoscope", "PET Scan", "X-ray Film", "CT Machine"], 1),
    ("What color represents a hole in this game?", ["Orange", "Yellow", "Blue", "Green"], 1),
    ("Which of these travels at the speed of light?", ["Electron", "Hole", "Photon", "Current"], 2),
]

def run_quiz():
    current_q = 0
    score = 0
    while current_q < len(quiz_questions):
        screen.fill(DARK_GRAY)
        q, options, correct = quiz_questions[current_q]
        question_surf = big_font.render(f"Q{current_q+1}: {q}", True, WHITE)
        screen.blit(question_surf, (60, 100))
        for i, opt in enumerate(options):
            color = CYAN if i == correct else WHITE
            option_surf = font.render(f"{i+1}. {opt}", True, color)
            screen.blit(option_surf, (100, 160 + i * 40))
        pygame.display.flip()

        selected = -1
        while selected == -1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_4:
                        selected = event.key - pygame.K_1
            clock.tick(10)

        if selected == correct:
            score += 1
        current_q += 1

    screen.fill(BLACK)
    result = big_font.render(f"You scored {score}/5!", True, GREEN if score >= 3 else RED)
    screen.blit(result, (WIDTH // 2 - 120, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

def draw_energy_band():
    pygame.draw.rect(screen, GRAY, (20, 120, 60, 150))  # conduction band
    pygame.draw.rect(screen, GRAY, (20, 320, 60, 150))  # valence band
    vb_text = font.render("Conduction", True, WHITE)
    cb_text = font.render("Valance", True, WHITE)
    screen.blit(vb_text, (10, 90))
    screen.blit(cb_text, (5, 480))
    pygame.draw.line(screen, WHITE, (50, 270), (50, 320), 2)
    pygame.draw.polygon(screen, BLUE, [(45, 295), (55, 295), (50, 285)])

# Applications
application_texts = [
    ("1 Solar Cell", "Light to Current"),
    ("2 PET Scan", "Photon to Imaging"),
    ("3 Fiber Optic", "Photon to Signal"),
    ("4 Night Vision", "Photon to Vision"),
]

def main():
    photons, electron_holes, sparks = [], [], []
    detector = Detector()
    score = 0
    band_transitions = []
    valence_electrons = []
    use_case_index, use_case_timer, bulb_glow_timer = 0, 0, 0
    last_pair_time = 0
    quiz_shown = False

    screen.fill(BLACK)
    title_text = big_font.render("Photon → Power: A Game-Based Approach for Understanding Solar Panel Working", True, WHITE)
    subtitle_text = font.render("By Alankrit (21102064), Modit(21803019), Aviral(21803021) & Swastik(21803017) | Batch B12", True, CYAN)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()
    pygame.time.delay(2000)

    for i in range(3, 0, -1):
        screen.fill(BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 60))
        countdown_text = big_font.render(f"Starting in {i}...", True, YELLOW)
        screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2 + 70))
        pygame.display.flip()
        pygame.time.delay(1000)

    start_time = time.time()

    while True:
        screen.fill(BLACK)
        for star in stars:
            star.update()
            star.draw()

        draw_energy_band()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            detector.move("LEFT")
        if keys[pygame.K_RIGHT]:
            detector.move("RIGHT")

        if random.randint(1, 25) == 1:
            photons.append(Photon())

        for photon in photons[:]:
            photon.fall()
            photon.draw()
            if detector.detect(photon):
                photons.remove(photon)
                electron_holes.append(ElectronHolePair(photon.x, detector.y))
                sparks.append(Spark(photon.x, detector.y))
                band_transitions.append(BandTransition())
                score += 1
                zap_sound.play()
                bulb_glow_timer = 30
            elif photon.y > HEIGHT:
                photons.remove(photon)

        for pair in electron_holes[:]:
            pair.update()
            pair.draw()
            if pair.timer <= 0:
                electron_holes.remove(pair)

        for spark in sparks[:]:
            spark.update()
            spark.draw()
            if spark.is_dead():
                sparks.remove(spark)

        for bt in band_transitions[:]:
            bt.update()
            bt.draw()
            if not bt.active:
                band_transitions.remove(bt)

        detector.draw()
        draw_stored_electrons()
        score_txt = font.render(f"Photons Caught: {score}", True, WHITE)
        screen.blit(score_txt, (20, 20))

        pygame.draw.rect(screen, DARK_GRAY, (WIDTH - 200, 0, 200, HEIGHT))
        screen.blit(title_font.render("Applications", True, CYAN), (WIDTH - 180, 10))
        if use_case_timer <= 0:
            use_case_index = (use_case_index + 1) % len(application_texts)
            use_case_timer = 120
        title, desc = application_texts[use_case_index]
        screen.blit(font.render(title, True, GREEN), (WIDTH - 190, 60))
        screen.blit(font.render(desc, True, WHITE), (WIDTH - 190, 90))
        screen.blit(font.render("Photon → Blue", True, BLUE), (WIDTH - 190, 130))
        screen.blit(font.render("Electron → Orange", True, ORANGE), (WIDTH - 190, 160))
        screen.blit(font.render("Hole → Yellow", True, YELLOW), (WIDTH - 190, 190))
        use_case_timer -= 1

        if pygame.time.get_ticks() - last_pair_time < 2000:
            screen.blit(font.render("Electron → Orange", True, ORANGE), (WIDTH - 190, 160))
            screen.blit(font.render("Hole → Yellow", True, YELLOW), (WIDTH - 190, 190))

        if bulb_glow_timer > 0:
            screen.blit(bulb_on, (WIDTH - 130, 250))
            bulb_glow_timer -= 1
        else:
            screen.blit(bulb_off, (WIDTH - 130, 250))

        if not quiz_shown and time.time() - start_time >= 30:
            run_quiz()
            quiz_shown = True

        pygame.display.flip()
        clock.tick(60)

main()
