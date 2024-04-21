import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
WINDOW_SIZE = (1300, 900)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Hex Board Game")

# Load the background image
background_image = pygame.image.load("Hex-bord-leeg.png").convert()

# Define constants for clickable areas and colors
CLICKABLE_RADIUS = 34
BLUE = (0, 0, 255)
RED = (255, 0, 0)
SPACINGX = 70
SPACINGY = 61
SHIFT_AMOUNT = 35.2

# Declare the global variable for placed pieces
placed_pieces = []

# Disjoint set class for managing connections
class DisjointSet:
    def __init__(self, elems):
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
        self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return
        if self.size[root_x] < self.size[root_y]:
            self.parent[root_x] = root_y
            self.size[root_y] += self.size[root_x]
        else:
            self.parent[root_y] = root_x
            self.size[root_x] += self.size[root_y]

# Hex game class containing game logic and AI implementation
class HexGame:
    def __init__(self, n=11):
        self.n = n
        self.board = [[0 for _ in range(n)] for _ in range(n)]
        self.cells = [(i, j) for i in range(n) for j in range(n)]
        self.top_node = (-1, 0)
        self.bottom_node = (n, 0)
        self.left_node = (0, -1)
        self.right_node = (0, n)
        self.ds_red = DisjointSet(self.cells + [self.top_node, self.bottom_node])
        self.ds_blue = DisjointSet(self.cells + [self.left_node, self.right_node])

        # Union the nodes representing the edges
        for i in range(n):
            self.ds_red.union((0, i), self.top_node)
            self.ds_red.union((n - 1, i), self.bottom_node)
            self.ds_blue.union((i, 0), self.left_node)
            self.ds_blue.union((i, n - 1), self.right_node)

    # Place a stone and update the board and disjoint sets
    def play(self, i, j, player):
        if 0 <= i < self.n and 0 <= j < self.n and self.board[i][j] == 0:
            code = 1 if player == 'red' else 2
            self.board[i][j] = code  # Place the stone
            # Union adjacent cells of the same color
            for nei_i, nei_j in [
                (i + 1, j),
                (i + 1, j - 1),
                (i, j + 1),
                (i, j - 1),
                (i - 1, j),
                (i - 1, j + 1),
            ]:
                if 0 <= nei_i < self.n and 0 <= nei_j < self.n and code == self.board[nei_i][nei_j]:
                    if player == 'red':
                        self.ds_red.union((nei_i, nei_j), (i, j))
                    else:
                        self.ds_blue.union((nei_i, nei_j), (i, j))
            return True  # Successful placement
        return False  # Invalid placement

    # Get all available moves (empty cells)
    def get_available_moves(self):
        return [(i, j) for i in range(self.n) for j in range(self.n) if self.board[i][j] == 0]

    # Define a utility function to evaluate the board state
    def evaluate(self):
        if self.ds_red.find(self.top_node) == self.ds_red.find(self.bottom_node):
            return 1  # Red wins
        elif self.ds_blue.find(self.left_node) == self.ds_blue.find(self.right_node):
            return -1  # Blue wins
        return 0  # No winner yet

    # Define a simple heuristic for the minimax algorithm
    def heuristic(self):
        # Simple heuristic: count number of connected cells for each player
        red_count = 0
        blue_count = 0
        for row in self.board:
            for cell in row:
                if cell == 1:
                    red_count += 1
                elif cell == 2:
                    blue_count += 1
        return red_count - blue_count  # Difference in counts as a simple heuristic

    # Define the minimax algorithm with alpha-beta pruning
    def minimax(self, depth, is_maximizing, alpha=float("-inf"), beta=float("inf")):
        score = self.evaluate()  # Check if a player has won

        if score == 1:
            return score, None  # Red wins
        elif score == -1:
            return score, None  # Blue wins
        elif depth == 0 or len(self.get_available_moves()) == 0:
            return self.heuristic(), None  # Use heuristic for depth limit or draw

        if is_maximizing:
            best_score = float("-inf")
            best_move = None
            for move in self.get_available_moves():
                self.board[move[0]][move[1]] = 1  # Place red stone
                current_score, _ = self.minimax(depth - 1, False, alpha, beta)
                self.board[move[0]][move[1]] = 0  # Reset move
                if current_score > best_score:
                    best_score = current_score
                    best_move = move
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return best_score, best_move

        else:
            best_score = float("inf")
            best_move = None
            for move in self.get_available_moves():
                self.board[move[0]][move[1]] = 2  # Place blue stone
                current_score, _ = self.minimax(depth - 1, True, alpha, beta)
                self.board[move[0]][move[1]] = 0  # Reset move
                if current_score < best_score:
                    best_score = current_score
                    best_move = move
                beta = min(beta, best_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return best_score, best_move

# Function to draw placed pieces
def draw_pieces():
    for pos, color in placed_pieces:
        pygame.draw.circle(screen, color, pos, 20)

# Main game loop
def main():
    clickable_positions = []  # Store clickable areas
    global placed_pieces  # Reference the global variable
    game = HexGame(11)  # Initialize the Hex board game with an 11x11 board

    # Set the clickable positions for the game
    for row in range(11):
        clickable_positions.append([])
        for col in range(11):
            x = 103 + col * SPACINGX + row * SHIFT_AMOUNT
            y = 127 + row * SPACINGY
            clickable_positions[row].append((x, y))

    current_player = 0  # Start with red (human player)
    running = True  # Main game loop flag

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle human player's turn
            if current_player == 0 and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Determine which cell was clicked
                for row in range(len(clickable_positions)):
                    for col in range(len(clickable_positions[row])):
                        distance = pygame.math.Vector2(
                            mouse_pos[0] - clickable_positions[row][col][0],
                            mouse_pos[1] - clickable_positions[row][col][1]
                        ).length()
                        if distance <= CLICKABLE_RADIUS:
                            if all(pos != clickable_positions[row][col] for pos, _ in placed_pieces):
                                placed_pieces.append((clickable_positions[row][col], RED))  # Place red piece
                                if game.play(row, col, 'red'):  # Validate placement
                                    current_player = 1  # Switch to blue (AI)
                                    break

            # Handle AI's turn with minimax
            if current_player == 1:
                _, best_move = game.minimax(3, False)  # Use minimax to find the best move
                if best_move:
                    i, j = best_move
                    placed_pieces.append((clickable_positions[i][j], BLUE))  # Place blue piece
                    if game.play(i, j, 'blue'):  # Validate placement
                        current_player = 0  # Switch to red (human player)
                else:
                    running = False  # If no valid move, end the game

        # Draw the board and update the display
        screen.blit(background_image, (0, 0))
        draw_pieces()  # Draw all placed pieces
        pygame.display.flip()  # Refresh the display

    # Exit Pygame and clean up resources
    pygame.quit()
    sys.exit()

# Run the game loop if executed as the main script
if __name__ == "__main__":
    main()
