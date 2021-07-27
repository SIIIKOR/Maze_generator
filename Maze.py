from abc import ABC, abstractmethod
import numpy as np
from random import choice
import pygame
from PIL import Image


class Visualisation_maze_solver:
    def __init__(self, maze, gap_size):
        self.maze_matrix = maze.maze
        self.gap_size = gap_size
        self.row_amount = len(self.maze_matrix)
        self.row_len = len(self.maze_matrix[0])
        self.height = self.get_height()
        self.width = self.get_width()
        self.screen = pygame.display.set_mode((self.width, self.height))

    def get_width(self):
        """ Calculates height of the window """
        output = 0
        for obj in self.maze_matrix[0]:
            if isinstance(obj, Cell):
                output += self.gap_size
            elif isinstance(obj, Wall):
                output += 1
        return output

    def get_height(self):
        """ Calculates width of the window """
        output = 0
        for row in self.maze_matrix:
            for index, obj in enumerate(row):
                if index == 0:
                    if isinstance(obj, Cell):
                        output += self.gap_size
                    else:
                        output += 1
        return output

    def render(self, obj):
        """ Draws single General_cell onto screen """
        ind = Indicator(obj.get_draw_cords(self.gap_size))
        ind.draw(self.screen, self.gap_size)

        obj.draw(self.screen, self.gap_size)
        pygame.display.update()
        # pygame.time.wait(10)
        ind.un_draw(self.screen, self.gap_size)

    def draw_everything(self):
        """ Draws every object contained in the maze_matrix """
        for row in self.maze_matrix:
            for obj in row:
                obj.draw(self.screen, self.gap_size)

    def draw_not_cells(self):
        """ Draws every object except cells contained in the maze_matrix """
        for row in self.maze_matrix:
            for obj in row:
                if not isinstance(obj, Cell):
                    obj.draw(self.screen, self.gap_size)

    @staticmethod
    def start():
        """ Displays screen till closed """
        while True:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


class Indicator:
    def __init__(self, cords):
        self.cords = cords

    def draw(self, screen, gap_size):
        return pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(self.cords[0], self.cords[1], gap_size, gap_size))

    def un_draw(self, screen, gap_size):
        return pygame.draw.rect(screen, (25, 25, 0), pygame.Rect(self.cords[0], self.cords[1], gap_size, gap_size))


class General_cell(ABC):
    """ Abstract cell """
    def __init__(self, cords):
        """ Knows it's coordinates """
        self.cords = cords

    def neighbours(self):
        """ Can calculate it's neighbouring cells, only used in cell object """
        xs = [(self.cords[0] + i, self.cords[1]) for i in range(-2, 3, 4)]
        ys = [(self.cords[0], self.cords[1] + i) for i in range(-2, 3, 4)]
        return xs + ys

    @abstractmethod
    def name(self):
        pass

    def __str__(self):
        return f"I'am {self.name()} y: {self.cords[1]} x: {self.cords[0]}"

    def get_draw_cords(self, gap_size):
        """ Calculates coordinates used to draw on screen from matrix coordinates and variable - gap_size """
        x, y = 0, 0
        for i in range(self.cords[0]):
            if i % 2 == 0:
                x += gap_size
            else:
                x += 1

        for i in range(self.cords[1]):
            if i % 2 == 0:
                y += gap_size
            else:
                y += 1
        return x, y

    def draw(self, screen, gap_size):
        """ Method to draw every single type of object """
        x, y = self.get_draw_cords(gap_size)
        if isinstance(self, Cell):
            color = (25, 25, 0)
            shape = pygame.Rect(x, y, gap_size, gap_size)
        elif isinstance(self, Wall):
            if self.is_wall:
                color = (200, 0, 0)
            else:
                color = (0, 0, 0)
            if self.cords[1] % 2 == 0:
                shape = pygame.Rect(x, y, 1, gap_size)
            else:
                shape = pygame.Rect(x, y, gap_size, 1)
        else:
            color = (0, 0, 200)
            shape = pygame.Rect(x, y, 1, 1)
        return pygame.draw.rect(screen, color, shape)


class Cell(General_cell):
    """ Cell knows whether it was visited or not """
    def __init__(self, cords):
        super().__init__(cords)
        self.visited = False

    def make_visited(self):
        self.visited = True

    def name(self):
        return "Cell"


class Wall(General_cell):
    """ Wall knows whether it is still a wall or not """
    def __init__(self, cords):
        super().__init__(cords)
        self.is_wall = True

    def un_wall(self):
        self.is_wall = False

    def name(self):
        return "Wall"


class Point(General_cell):
    """ Just a point to fill a gap in the matrix """
    def __init__(self, cords):
        super().__init__(cords)

    def name(self):
        return "Point"


def get_middle_cords(start, end):
    """ Calculates coordinates between two parallel points with maximal distance of one """
    start_x, start_y = start.cords
    end_x, end_y = end.cords
    if start_x == end_x:
        if start_y > end_y:
            smaller = end_y
        else:
            smaller = start_y
        return start_x, smaller + 1
    elif start_y == end_y:
        if start_x > end_x:
            smaller = end_x
        else:
            smaller = start_x
        return smaller + 1, start_y


class Maze:
    """ Maze - matrix filled with abstract cell objects """
    def __init__(self, height, width, gap_size):
        self.height = height
        self.width = width
        self.gap_size = gap_size
        self.maze = self.fill_maze()

    def fill_maze(self):
        """ Method to fill matrix with abstract cell objects """
        output = np.empty((self.height, self.width), dtype=object)
        for y in range(self.height):
            for x in range(self.width):
                if x % 2 == 1 and y % 2 == 0:
                    output[y][x] = Wall((x, y))
                elif x % 2 == 0 and y % 2 == 1:
                    output[y][x] = Wall((x, y))
                elif y % 2 == 1 and x % 2 == 1:
                    output[y][x] = Point((x, y))
                else:
                    output[y][x] = Cell((x, y))
        return output

    def get_neighbours(self, cell):
        """ Return existing cell neighbours of a given cell """
        output = []
        potential_neighbours = cell.neighbours()
        for cords in potential_neighbours:
            x, y = cords
            if 0 <= x < self.width and 0 <= y < self.height and (x, y) != cell.cords:
                output.append(self.maze[y][x])
        return output

    def access_cell(self, cords):
        return self.maze[cords[1]][cords[0]]

    @staticmethod
    def remove_wall(cell):
        cell.un_wall()

    def get_unvisited_neighbours(self, cell):
        """ Return neighbouring cells that were not visited yet """
        output = []
        neighbours = self.get_neighbours(cell)
        for neighbour in neighbours:
            if not neighbour.visited:
                output.append(neighbour)
        return output

    def gen(self, cords):
        """ Iterative dfs maze generation algorithm with visualisation """
        start_cell = self.maze[cords[1]][cords[0]]
        start_cell.make_visited()
        stack = [start_cell]

        vis = Visualisation_maze_solver(self, self.gap_size)
        vis.draw_not_cells()

        while stack:
            curr_cell = stack.pop()

            vis.render(curr_cell)
            if len(self.get_unvisited_neighbours(curr_cell)) != 0:
                stack.append(curr_cell)
                neighbour = choice(self.get_unvisited_neighbours(curr_cell))
                wall = self.access_cell(get_middle_cords(curr_cell, neighbour))
                self.remove_wall(wall)
                vis.render(wall)
                neighbour.make_visited()
                stack.append(neighbour)
        self.save_to_jpg()
        vis.start()

    def save_to_jpg(self):
        new_array = np.zeros(self.maze.shape)
        for r_index, row in enumerate(self.maze):
            for o_index, obj in enumerate(row):
                if isinstance(obj, Cell):
                    new_array[r_index][o_index] = 1
                elif isinstance(obj, Wall) and not obj.is_wall:
                    new_array[r_index][o_index] = 1
        im = Image.fromarray(new_array*255)
        im.show()

    def __str__(self):
        """ Command line matrix visualisation """
        output = ""
        for r_index, row in enumerate(self.maze):
            var = ""
            for c_index, cell in enumerate(row):
                if c_index != len(row)-1:
                    if isinstance(cell, Cell):
                        var += " c "
                    elif isinstance(cell, Wall):
                        if cell.is_wall:
                            var += " w "
                        else:
                            var += " n "
                    else:
                        var += " . "
                else:
                    if isinstance(cell, Cell):
                        var += " c \n"
                    else:
                        if cell.is_wall:
                            var += " w \n"
                        else:
                            var += " n \n"
            output += var
        return output
