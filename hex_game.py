import pygame
import sys
import math
from collections import deque
import random
# Initialize Pygame
pygame.init()

# Set the dimensions of the window
WINDOW_SIZE = (1300, 900)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Hex Board Game")

# Load the background image
background_image = pygame.image.load("Hex-bord-leeg.png").convert()

CLICKABLE_CENTER = (103,127)
CLICKABLE_RADIUS = 34
BLUE = (0, 0, 255)
RED = (255, 0 , 0)
SPACINGX = 70
SPACINGY = 61
SHIFT_AMOUNT = 35.2

HEX_SIZE = 30
HEX_GAP = 3

updated_cells = []
clickable_positions = []
placed_pieces = []
def draw_pieces():
    for pos, color in placed_pieces:
        pygame.draw.circle(screen, color, pos, 20)

class DisjointSet:
    def __init__(self, elems):
        self.elems = elems
        self.parent = {}
        self.size = {}
        for elem in elems:
            self.make_set(elem)

    def make_set(self, x):
        self.parent[x] = x
        self.size[x] = 1

    def find(self, x):
        if self.parent[x] == x:
            return x
        else:
            self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
    def undo_union(self, parent, size, x, y):
        root_x = self.find(parent)
        root_y = self.find(parent)
        if root_x != root_y:
            if size[root_x] < size[root_y]:
                parent[root_x] = root_x
                size[root_y] -= size[root_x]
            else:
                parent[root_y] = root_y
                size[root_x] -= size[root_y]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return
        elif self.size[root_x] < self.size[root_y]:
            self.parent[root_x] = root_y
            self.size[root_y] += self.size[root_x]
        else:
            self.parent[root_y] = root_x
            self.size[root_x] += self.size[root_y]

class HexGame:
    def __init__(self, n=11):
        self.n = n
        self.board = [[0]*n for _ in range(n)]
        self.cells = [(i, j) for i in range(n) for j in range(n)]
        self.top_node = (-1, 0)
        self.bottom_node = (n, 0)
        self.left_node = (0, -1)
        self.right_node = (0, n)
        self.ds_red = DisjointSet(self.cells + [self.top_node, self.bottom_node])
        self.ds_blue = DisjointSet(self.cells + [self.left_node, self.right_node])
        for i in range(n):
            self.ds_red.union((0, i), self.top_node)
            self.ds_red.union((n-1, i), self.bottom_node)
            self.ds_blue.union((i, 0), self.left_node)
            self.ds_blue.union((i, n-1), self.right_node)
    
    def play(self, i, j, player, mainCalled):
        # print("Player:")
        # print(player)
        # print(i)
        # print("===========")
        # print(j)
        # print("-----------------")
        assert 0 <= i < self.n and 0 <= i < self.n and self.board[i][j] == 0
        code = 1 if player == 'red' else 2
        self.board[i][j] = code
        for nei_i, nei_j in [(i+1, j), (i+1, j-1), (i, j+1), (i, j-1), (i-1, j), (i-1, j+1)]:
            if 0 <= nei_i < self.n and 0 <= nei_j < self.n and code == self.board[nei_i][nei_j]:
                if player == 'red':
                    self.ds_red.union((nei_i, nei_j), (i, j))
                    # updated_cells.append((nei_i, nei_j))
                else:
                    self.ds_blue.union((nei_i, nei_j), (i, j))
                    # updated_cells.append((nei_i, nei_j))
        if ((self.ds_red.find(self.top_node) == self.ds_red.find(self.bottom_node)) and (mainCalled == 1)):
            print('red won')
            draw_pieces()
            pygame.display.flip()
            
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

        elif (self.ds_blue.find(self.left_node) == self.ds_blue.find(self.right_node) and (mainCalled == 1)):
            print('blue won')
            draw_pieces()
            pygame.display.flip()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

    # def undo_play(self, i, j, player, updated_cells):
    #         print("Played Undoned")
    #         self.board[i][j] = 0
    #         for cell in updated_cells:
    #             self.board[cell[0]][cell[1]] = 0  # Reset the neighboring cells to empty

    #         if player == 'red':
    #             for cell in updated_cells:
    #                 self.ds_red.undo_union(cell, len(cell), i, j)  # Undo changes in disjoint set for red player
    #         else:
    #             for cell in updated_cells:
    #                 self.ds_blue.undo_union(cell, len(cell), i, j)  # Undo changes in disjoint set for blue player

    # def is_piece_placed(self, row, col):
    #     for piece in placed_pieces:
    #         if piece[0] == clickable_positions[row][col]:
    #             return True
    #     return False  
    
    # def evaluate_game_state(self):
    #     if self.ds_red.find(self.top_node) == self.ds_red.find(self.bottom_node):
    #         return 1
    #     elif self.ds_blue.find(self.left_node) == self.ds_blue.find(self.right_node):
    #         return -1
    #     else:
    #         return 0
        
    # def minimax(self, depth, maximizing_player):
    #     if (depth == 3) or (self.ds_red.find(self.top_node) == self.ds_red.find(self.bottom_node)) or (self.ds_blue.find(self.left_node) == self.ds_blue.find(self.right_node)):
    #         return self.evaluate_game_state(), None, None
        
    #     if maximizing_player:
    #         best_value = -100000
    #         best_col = None
    #         best_row = None
    #         for row in range(0, 11):
    #             for col in range(0, 11):
    #                 if not self.is_piece_placed(row, col):
    #                     self.play(row, col, 'blue', 0)
    #                     placed_pieces.append((clickable_positions[row][col], BLUE))
    #                     value, _, _ = self.minimax(depth + 1, False)
    #                     self.undo_play(row, col, 'blue', updated_cells)
    #                     placed_pieces.pop()
    #                     if value > best_value:
    #                         best_value = value
    #                         best_col = col
    #                         best_row = row
    #         return best_value, best_col, best_row
    #     else:
    #         best_value = 100000
    #         best_col = None
    #         best_row = None
    #         for row in range(0, 11):
    #             for col in range(0, 11):
    #                 if not self.is_piece_placed(row, col):
    #                     self.play(row, col, 'red', 0)
    #                     placed_pieces.append((clickable_positions[row][col], RED, 0))
    #                     value, _, _ = self.minimax(depth + 1, True)
    #                     self.undo_play(row, col, 'red', updated_cells)
    #                     placed_pieces.pop()
    #                     if value > best_value:
    #                         best_value = value
    #                         best_col = col
    #                         best_row = row
    #         return best_value, best_col, best_row


# def evaluate_game_state(graph): # Evaluating the game state 
#     if isTriangle(graph, 1):  # If player 1 forms a triangle, return a winning score
#         return 1
#     elif isTriangle(graph, 0):  # If player 2 (AI) forms a triangle, return a loosing score
#         return -1
#     else:
#         return 0  # Game is ongoing 

# def minimax(graph, depth, is_maximizing_player): # Function with minimax algorithm
#     if depth == 3 or isTriangle(graph, 0) or isTriangle(graph, 1):  # If Depth limit reached or a triangle is found evaluate the game state
#         return evaluate_game_state(graph), None, None   # Return the game state - The other nones represent edges that are not used here.
    
#     if is_maximizing_player:    # If looking for mac
#         best_value = -100000 #float('-inf') # Set to a large value (represents negative infinity)
#         best_edge1 = None
#         best_edge2 = None
#         for edge1 in range(1, 7):   # Look for all possible combinations
#             for edge2 in range(edge1 + 1, 7):
#                 if isCondition2(edge1, edge2):  # If conditions are met
#                     graph.add_edge(edge1, edge2, weight = 0 )   # Add values to edge
#                     value, _, _ = minimax(graph, depth + 1, False)  # Call minimax to return value of nodes
#                     if value > best_value:  # If value is greater than best value (for first iteration negative infinite)
#                         best_value = value  # Best value equals value
#                         best_edge1 = edge1  # Best_edge1 equals edge1
#                         best_edge2 = edge2  # Best_edge2 equals edge2
#                     graph.remove_edge(edge1, edge2) # Remove the edge from graph                    
#         return best_value, best_edge1, best_edge2   # Return values
#     else:   # Else looking for min
#         best_value = 100000 #float('inf') # Set to a large value (represents infinity)
#         best_edge1 = None
#         best_edge2 = None
#         for edge1 in range(1, 7):   # Look for all possible combinations
#             for edge2 in range(edge1 + 1, 7):
#                 if isCondition2(edge1, edge2):  # If conditions are met
#                     graph.add_edge(edge1, edge2, weight = 0)    # Add the edge 
#                     value, _, _ = minimax(graph, depth + 1, True) # Call minimax to return value of nodes
#                     if value < best_value:  # If value is smeller than best value (for first iteration positive infinite)
#                         best_value = value  # Best value equals value
#                         best_edge1 = edge1  # Best_edge1 equals edge1
#                         best_edge2 = edge2  # Best_edge2 equals edge2
#                     graph.remove_edge(edge1, edge2) # Remove the edge from graph  
#         return best_value, best_edge1, best_edge2   # Return values






def main():
    waiting_for_click = False
    game = HexGame(11)

    # 2D Array to store the positions of clickable areas
    for row in range(11):
        clickable_positions.append([])
        for col in range(11):
            x = 103 + col * SPACINGX + row * SHIFT_AMOUNT
            y = 127 + row * SPACINGY
            clickable_positions[row].append((x, y))
        
    current_player = 0
    # Main game loop
    running = True
    while running:
        # if (current_player == 0) or (current_player == 1):
        #     # current_player = 0
        #     print("Player is Red")
        # elif (current_player == 2):
        #     # current_player = 'blue'
        #     print("Player is Blue")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #if (current_player == 1) or (current_player == 0):
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Get the mouse position
                mouse_pos = pygame.mouse.get_pos()
                for row in range(len(clickable_positions)):
                    for col in range(len(clickable_positions)):
                        distance = pygame.math.Vector2(mouse_pos[0] - clickable_positions[row][col][0],
                                                    mouse_pos[1] - clickable_positions[row][col][1]).length()
                # Check if the distance is within the clickable radius
                        if distance <= CLICKABLE_RADIUS:
                            if all(pos != clickable_positions[row][col] for pos, _ in placed_pieces):
                                i, j = row, col
                                if current_player == 0:
                                    placed_pieces.append((clickable_positions[row][col], RED))
                                    game.play(i, j, 'red', 1)
                                    current_player = 1
                                else:
                                    placed_pieces.append((clickable_positions[row][col], BLUE))
                                    game.play(i , j, 'blue', 1)
                                    current_player = 0
                            # if not waiting_for_click:  # Check if waiting for mouse click
                            #     if event.type == pygame.MOUSEBUTTONDOWN:
                            #         waiting_for_click = True  # Set to True to wait for click
                            #         current_player = 2

            # elif current_player == 2:
            #     _,y, x = game.minimax(0, True)
            #     print("succesfully Returned")
            #     placed_pieces.append((clickable_positions[x][y], BLUE))
            #     game.play(x, y, 'blue', 1)
            #     print("Play made")
            #     current_player = 0
            #     waiting_for_click = False
                # current_player = (current_player + 1) % 2                

        # Draw the background image
        screen.blit(background_image, (0, 0))

        # for row in range(len(clickable_positions)):
        #     for col in range(len(clickable_positions[row])):
                #pygame.draw.circle(screen, GREEN, clickable_positions[row][col], CLICKABLE_RADIUS, 3)  # Draw the circle outline

        draw_pieces()
        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()

main()
