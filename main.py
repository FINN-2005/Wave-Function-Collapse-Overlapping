from pygame_template import *

TOP, RIGHT, DOWN, LEFT = 0, 1, 2, 3
DIM, TILE_SIZE = 20, 3

def load_image(filename='City.png'):
    return pygame.image.load(filename)

def draw_image(screen, image, pos, size):
    size_x, size_y = image.get_size()
    for i in range(size_x):
        for j in range(size_y):
            col = image.get_at((i, j))
            pygame.draw.rect(screen, col, (pos[0] + i * size, pos[1] + j * size, size, size))

class Tile:
    def __init__(self, img, index):
        self.img = img
        self.tile_index = index
        self.adjacencies = [[] for _ in range(4)]
    
    def calculate_adjacencies(self, tiles):
        for i, other in enumerate(tiles):
            for direction in range(4):
                if self.overlapping(other, direction):
                    self.adjacencies[direction].append(i)
    
    def overlapping(self, other, direction):
        tile_x, tile_y = self.img.get_size()
        if direction == TOP:
            return all(self.img.get_at((x, 0)) == other.img.get_at((x, tile_y - 1)) for x in range(tile_x))
        if direction == RIGHT:
            return all(self.img.get_at((tile_x - 1, y)) == other.img.get_at((0, y)) for y in range(tile_y))
        if direction == DOWN:
            return all(self.img.get_at((x, tile_y - 1)) == other.img.get_at((x, 0)) for x in range(tile_x))
        if direction == LEFT:
            return all(self.img.get_at((0, y)) == other.img.get_at((tile_x - 1, y)) for y in range(tile_y))
        return False

class Cell:
    def __init__(self, tiles, x, y, w, index):
        self.x, self.y, self.w, self.index = x, y, w, index
        self.tiles = tiles
        self.options = list(range(len(tiles)))
        self.collapsed = False
    
    def draw(self, screen):
        if self.collapsed:
            img = self.tiles[self.options[0]].img
            draw_image(screen, img, (self.x, self.y), self.w / TILE_SIZE)
        else:
            pygame.draw.rect(screen, 'black', (self.x, self.y, self.w, self.w), 2)

def extract_tiles(image):
    img_width, img_height = image.get_size()
    new_tiles = []
    for y in range(0, img_height, TILE_SIZE):
        for x in range(0, img_width, TILE_SIZE):
            new_tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            new_tile.blit(image, (0, 0), pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            new_tiles.append(Tile(new_tile, len(new_tiles)))
    return new_tiles

def reduce_entropy(grid, cell):
    index = cell.index
    i, j = index % DIM, index // DIM
    neighbours = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    
    for direction, (di, dj) in enumerate(neighbours):
        ni, nj = i + di, j + dj
        if 0 <= ni < DIM and 0 <= nj < DIM:
            neighbour_cell = grid[ni + nj * DIM]
            if not neighbour_cell.collapsed:
                valid_options = set()
                for option in cell.options:
                    valid_options.update(cell.tiles[option].adjacencies[direction])
                neighbour_cell.options = list(set(neighbour_cell.options) & valid_options)
                if len(neighbour_cell.options) == 0:
                    return False
                if len(neighbour_cell.options) == 1:
                    neighbour_cell.collapsed = True
                    if not reduce_entropy(grid, neighbour_cell):
                        return False
    return True

class run(APP):
    def init(self):
        self.WIDTH, self.HEIGHT = 600, 600
        self.window_title = 'Wave Function Collapse'
        self.history = []
    
    def setup(self):
        self.image = load_image()
        self.tiles = extract_tiles(self.image)
        for tile in self.tiles:
            tile.calculate_adjacencies(self.tiles)
        w = self.WIDTH / DIM
        self.grid = [Cell(self.tiles, x * w, y * w, w, x + y * DIM) for y in range(DIM) for x in range(DIM)]
        self.history = []  # Clear history on reset
    
    def update(self):
        grid_copy = [cell for cell in self.grid if not cell.collapsed]
        if not grid_copy:
            return
        
        self.history.append([(cell.options[:], cell.collapsed) for cell in self.grid])
        min_entropy = min(len(cell.options) for cell in grid_copy)
        grid_copy = [cell for cell in grid_copy if len(cell.options) == min_entropy]
        
        chosen_cell = random.choice(grid_copy)
        chosen_cell.collapsed = True
        chosen_cell.options = [random.choice(chosen_cell.options)]
        
        if not reduce_entropy(self.grid, chosen_cell):
            while self.history:
                last_state = self.history.pop()
                for i, (options, collapsed) in enumerate(last_state):
                    self.grid[i].options = options
                    self.grid[i].collapsed = collapsed
                if any(len(cell.options) > 1 for cell in self.grid):
                    break
            else:
                self.setup()
    
    def draw(self):
        for cell in self.grid:
            cell.draw(self.screen)

run()
