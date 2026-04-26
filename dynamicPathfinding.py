import pygame
import math
import heapq
import random
import time
import sys

pygame.init()
pygame.font.init()

WIDTH = 1100
HEIGHT = 800
GRID_WIDTH = 800
SIDEBAR_WIDTH = 300
ROWS = 20

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Dynamic Pathfinding Agent")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
DARK_GREY = (50, 50, 50)
RED = (255, 60, 60)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)
PURPLE = (155, 89, 182)
ORANGE = (230, 126, 34)
CYAN = (0, 255, 255)

try:
    FONT_TITLE = pygame.font.SysFont('arial', 24, bold=True)
    FONT_TEXT = pygame.font.SysFont('arial', 18)
    FONT_SMALL = pygame.font.SysFont('arial', 14)
except:
    FONT_TITLE = pygame.font.SysFont('comicsans', 24)
    FONT_TEXT = pygame.font.SysFont('comicsans', 18)
    FONT_SMALL = pygame.font.SysFont('comicsans', 14)

class Node:
    def __init__(self, row, col, size, total_rows):
        self.row = row
        self.col = col
        self.x = row * size
        self.y = col * size
        self.size = size
        self.color = WHITE
        self.neighbors = []
        self.total_rows = total_rows
        self.parent = None

    def get_pos(self):
        return self.row, self.col

    def is_barrier(self): return self.color == BLACK
    def is_start(self): return self.color == GREEN
    def is_end(self): return self.color == BLUE

    def reset(self): self.color = WHITE
    def make_start(self): self.color = GREEN
    def make_closed(self): self.color = RED
    def make_open(self): self.color = YELLOW
    def make_barrier(self): self.color = BLACK
    def make_end(self): self.color = BLUE
    def make_path(self): self.color = PURPLE
    def make_agent(self): self.color = CYAN

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

class Button:
    def __init__(self, x, y, w, h, text, action_code):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_code = action_code
        self.color = GREY
        self.hover_color = WHITE

    def draw(self, win):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(win, color, self.rect)
        pygame.draw.rect(win, BLACK, self.rect, 2)
        
        text_surf = FONT_TEXT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        win.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def h_manhattan(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def h_euclidean(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def algorithm(grid, start, end, heuristic, is_greedy, weight):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    came_from = {}
    
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())

    open_set_hash = {start}
    nodes_expanded = 0
    start_time = time.time()

    while not len(open_set) == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)

        if current == end:
            end_time = time.time()
            path = reconstruct_path(came_from, end)
            return path, nodes_expanded, (end_time - start_time) * 1000

        nodes_expanded += 1
        
        for neighbor in current.neighbors:
            temp_g = g_score[current] + 1

            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                h = heuristic(neighbor.get_pos(), end.get_pos())
                
                if is_greedy:
                    f_score[neighbor] = h * weight
                else:
                    f_score[neighbor] = temp_g + (h * weight)

                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end and neighbor != start:
                        neighbor.make_open()

        if current != start:
            current.make_closed()
            
    return None, nodes_expanded, 0

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid_lines(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def generate_maze(grid, rows):
    for row in grid:
        for node in row:
            if not node.is_start() and not node.is_end():
                if random.random() < 0.3:
                    node.make_barrier()

def draw_sidebar(win, buttons, metrics, settings):
    pygame.draw.rect(win, DARK_GREY, (GRID_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
    
    title = FONT_TITLE.render("Control Panel", True, WHITE)
    win.blit(title, (GRID_WIDTH + 70, 20))
    
    for btn in buttons:
        btn.draw(win)
        
    y_off = 450
    pygame.draw.line(win, WHITE, (GRID_WIDTH+20, y_off), (WIDTH-20, y_off), 2)
    
    headers = ["Nodes Visited:", "Path Cost:", "Time (ms):"]
    values = [str(metrics[0]), str(metrics[1]), f"{metrics[2]:.2f}"]
    
    for i, (h, v) in enumerate(zip(headers, values)):
        txt = FONT_TEXT.render(h, True, YELLOW)
        val = FONT_TEXT.render(v, True, WHITE)
        win.blit(txt, (GRID_WIDTH + 30, y_off + 20 + (i*60)))
        win.blit(val, (GRID_WIDTH + 30, y_off + 45 + (i*60)))

    s_y = 650
    pygame.draw.line(win, WHITE, (GRID_WIDTH+20, s_y), (WIDTH-20, s_y), 2)
    
    algo_txt = f"Algorithm: {'GBFS' if settings['greedy'] else 'A*'}"
    heur_txt = f"Heuristic: {'Euclidean' if settings['euclid'] else 'Manhattan'}"
    w_txt = f"Weight: {settings['weight']}x"
    d_txt = f"Dynamic Mode: {'ON' if settings['dynamic'] else 'OFF'}"
    
    win.blit(FONT_SMALL.render(algo_txt, True, WHITE), (GRID_WIDTH + 30, s_y + 20))
    win.blit(FONT_SMALL.render(heur_txt, True, WHITE), (GRID_WIDTH + 30, s_y + 45))
    win.blit(FONT_SMALL.render(w_txt, True, WHITE), (GRID_WIDTH + 30, s_y + 70))
    win.blit(FONT_SMALL.render(d_txt, True, ORANGE if settings['dynamic'] else GREY), (GRID_WIDTH + 30, s_y + 95))

def main():
    grid = make_grid(ROWS, GRID_WIDTH)
    
    start = None
    end = None
    
    bx = GRID_WIDTH + 50
    buttons = [
        Button(bx, 80, 200, 40, "Start Search", "START"),
        Button(bx, 130, 200, 40, "Reset Path", "RESET_PATH"),
        Button(bx, 180, 200, 40, "Clear Walls", "CLEAR"),
        Button(bx, 230, 200, 40, "Random Maze", "MAZE"),
        Button(bx, 290, 200, 30, "Toggle Algo", "TOGGLE_ALGO"),
        Button(bx, 330, 200, 30, "Toggle Heuristic", "TOGGLE_HEUR"),
        Button(bx, 370, 200, 30, "Toggle Weight", "TOGGLE_WEIGHT"),
        Button(bx, 410, 200, 30, "Dynamic Mode", "TOGGLE_DYN"),
    ]
    
    settings = {
        "greedy": False,
        "euclid": False,
        "weight": 1.0,
        "dynamic": False
    }
    metrics = (0, 0, 0)
    
    path = []
    agent_pos = None
    run = True
    
    while run:
        WIN.fill(WHITE)
        
        for row in grid:
            for node in row:
                node.draw(WIN)
        draw_grid_lines(WIN, ROWS, GRID_WIDTH)
        
        draw_sidebar(WIN, buttons, metrics, settings)
        
        if path:
            for node in path:
                if node != end and node != start and node != agent_pos:
                    node.make_path()
        
        pygame.display.update()
        
        if path and agent_pos:
            time.sleep(0.15)
            
            next_node = path.pop(0)
            
            if agent_pos != start:
                agent_pos.make_closed()
            
            agent_pos = next_node
            agent_pos.make_agent()
            
            if agent_pos == end:
                print("Goal Reached")
                path = []
                agent_pos = None
                continue

            if settings['dynamic']:
                if random.random() < 0.1: 
                    rx = random.randint(0, ROWS-1)
                    ry = random.randint(0, ROWS-1)
                    spot = grid[rx][ry]
                    if not spot.is_start() and not spot.is_end() and spot != agent_pos:
                        spot.make_barrier()
                        
                is_blocked = False
                for node in path:
                    if node.is_barrier():
                        is_blocked = True
                        break
                
                if is_blocked:
                    print("Path Blocked! Re-planning...")
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                            
                    h_func = h_euclidean if settings['euclid'] else h_manhattan
                    new_path, v, t = algorithm(grid, agent_pos, end, h_func, settings['greedy'], settings['weight'])
                    
                    if new_path:
                        path = new_path
                        metrics = (metrics[0] + v, len(path), metrics[2] + t)
                    else:
                        print("No Path Possible!")
                        path = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[0] < GRID_WIDTH:
                    row, col = pos[0] // (GRID_WIDTH // ROWS), pos[1] // (GRID_WIDTH // ROWS)
                    node = grid[row][col]
                    if not start and node != end:
                        start = node
                        start.make_start()
                    elif not end and node != start:
                        end = node
                        end.make_end()
                    elif node != end and node != start:
                        node.make_barrier()
                else:
                    for btn in buttons:
                        if btn.is_clicked(pos):
                            if btn.action_code == "START" and start and end:
                                for row in grid:
                                    for node in row:
                                        node.update_neighbors(grid)
                                h_func = h_euclidean if settings['euclid'] else h_manhattan
                                p, v, t = algorithm(grid, start, end, h_func, settings['greedy'], settings['weight'])
                                if p:
                                    path = p
                                    metrics = (v, len(p), t)
                                    agent_pos = start
                            
                            elif btn.action_code == "RESET_PATH":
                                path = []
                                agent_pos = None
                                metrics = (0,0,0)
                                for row in grid:
                                    for node in row:
                                        if node.color in [RED, YELLOW, PURPLE, CYAN]:
                                            node.reset()
                                        if node == start: node.make_start()
                                        if node == end: node.make_end()

                            elif btn.action_code == "CLEAR":
                                start = None
                                end = None
                                path = []
                                grid = make_grid(ROWS, GRID_WIDTH)
                                metrics = (0,0,0)

                            elif btn.action_code == "MAZE":
                                generate_maze(grid, ROWS)

                            elif btn.action_code == "TOGGLE_ALGO":
                                settings['greedy'] = not settings['greedy']

                            elif btn.action_code == "TOGGLE_HEUR":
                                settings['euclid'] = not settings['euclid']

                            elif btn.action_code == "TOGGLE_WEIGHT":
                                settings['weight'] = 2.5 if settings['weight'] == 1.0 else 1.0

                            elif btn.action_code == "TOGGLE_DYN":
                                settings['dynamic'] = not settings['dynamic']
                                
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[0] < GRID_WIDTH:
                    row, col = pos[0] // (GRID_WIDTH // ROWS), pos[1] // (GRID_WIDTH // ROWS)
                    node = grid[row][col]
                    node.reset()
                    if node == start: start = None
                    elif node == end: end = None

    pygame.quit()

if __name__ == "__main__":
    main()