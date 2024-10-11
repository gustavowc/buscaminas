import pygame
import random
import time

# Configuración de la cuadrícula
GRID_SIZE = 10
CELL_SIZE = 50  # Tamaño de cada celda
NUM_MINES = 15

# Calcular el tamaño de la ventana
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + 100  # Espacio para los botones

# Colores
COLOR_BG = (255, 255, 255)
COLOR_CELL = (200, 200, 200)
COLOR_MINE = (255, 0, 0)
COLOR_FLAG = (0, 255, 0)
COLOR_TEXT = (0, 0, 0)
COLOR_BUTTON = (100, 100, 100)
COLOR_BUTTON_HOVER = (150, 150, 150)

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Buscaminas Mejorado")

# Fuente para los números
font = pygame.font.Font(None, 36)

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighboring_mines = 0

class Minesweeper:
    def __init__(self):
        self.grid = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.game_over = False
        self.flags_left = NUM_MINES
        self.place_mines()
        self.calculate_neighbors()
        self.solve_steps = []  # Para almacenar los pasos de solución

    def place_mines(self):
        mines_placed = 0
        while mines_placed < NUM_MINES:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            if not self.grid[x][y].is_mine:
                self.grid[x][y].is_mine = True
                mines_placed += 1

    def calculate_neighbors(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if self.grid[x][y].is_mine:
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and not self.grid[nx][ny].is_mine:
                                self.grid[nx][ny].neighboring_mines += 1

    def reveal_cell(self, x, y):
        if self.grid[x][y].is_flagged or self.grid[x][y].is_revealed:
            return

        self.grid[x][y].is_revealed = True

        if self.grid[x][y].is_mine:
            self.game_over = True
            return

        if self.grid[x][y].neighboring_mines == 0:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        self.reveal_cell(nx, ny)

    def flag_cell(self, x, y):
        if self.grid[x][y].is_revealed:
            return

        self.grid[x][y].is_flagged = not self.grid[x][y].is_flagged
        self.flags_left += -1 if self.grid[x][y].is_flagged else 1

    def draw(self, screen):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell = self.grid[x][y]
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                if cell.is_revealed:
                    if cell.is_mine:
                        pygame.draw.rect(screen, COLOR_MINE, rect)
                    else:
                        pygame.draw.rect(screen, COLOR_CELL, rect)
                        if cell.neighboring_mines > 0:
                            text = font.render(str(cell.neighboring_mines), True, COLOR_TEXT)
                            screen.blit(text, (x * CELL_SIZE + CELL_SIZE // 3, y * CELL_SIZE + CELL_SIZE // 6))
                else:
                    pygame.draw.rect(screen, COLOR_BG, rect)

                if cell.is_flagged:
                    pygame.draw.line(screen, COLOR_FLAG, (x * CELL_SIZE, y * CELL_SIZE), 
                                     (x * CELL_SIZE + CELL_SIZE, y * CELL_SIZE + CELL_SIZE), 5)
                    pygame.draw.line(screen, COLOR_FLAG, (x * CELL_SIZE + CELL_SIZE, y * CELL_SIZE), 
                                     (x * CELL_SIZE, y * CELL_SIZE + CELL_SIZE), 5)

                pygame.draw.rect(screen, COLOR_TEXT, rect, 1)

    def reset_game(self):
        self.grid = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.game_over = False
        self.flags_left = NUM_MINES
        self.solve_steps = []  # Resetear los pasos de solución
        self.place_mines()
        self.calculate_neighbors()

    def solve_game(self):
        self.solve_steps = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if not self.grid[x][y].is_mine:
                    self.solve_steps.append((x, y))

    def animate_solution(self, screen, clock):
        for x, y in self.solve_steps:
            if not self.grid[x][y].is_revealed:
                self.reveal_cell(x, y)
                self.draw(screen)
                pygame.display.flip()
                time.sleep(0.2)  # Esperar un poco entre revelaciones
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

def draw_button(screen, rect, text, hover=False):
    color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
    pygame.draw.rect(screen, color, rect)
    font_surface = font.render(text, True, COLOR_TEXT)
    text_rect = font_surface.get_rect(center=rect.center)
    screen.blit(font_surface, text_rect)

def main():
    game = Minesweeper()
    clock = pygame.time.Clock()
    button_start = pygame.Rect(WIDTH // 4, HEIGHT - 80, WIDTH // 2, 50)
    button_solve = pygame.Rect(WIDTH // 4, HEIGHT - 30, WIDTH // 2, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Verificar si se hace clic en el botón de inicio o de resolver
                if button_start.collidepoint(event.pos):
                    game.reset_game()  # Reinicia el juego
                elif button_solve.collidepoint(event.pos):
                    game.solve_game()  # Prepara la solución automática
                    game.animate_solution(screen, clock)  # Animar la solución

                # Solo procesar clics si el juego no ha terminado
                if not game.game_over:
                    grid_x = x // CELL_SIZE
                    grid_y = y // CELL_SIZE
                    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:  # Verificar límites
                        if event.button == 1:  # Botón izquierdo
                            game.reveal_cell(grid_x, grid_y)
                        elif event.button == 3:  # Botón derecho
                            game.flag_cell(grid_x, grid_y)

        screen.fill(COLOR_BG)
        game.draw(screen)

        # Dibujar botones
        draw_button(screen, button_start, "Iniciar Juego")
        draw_button(screen, button_solve, "Resolver con IA")

        if game.game_over:
            text = font.render("¡Juego Terminado!", True, COLOR_TEXT)
            screen.blit(text, (WIDTH // 4, HEIGHT // 2))
        
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
