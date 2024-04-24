import pygame
import sys

# Initialize Pygame
pygame.init()
placed_pieces = []

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
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def traverse_matrixforRed(matrix):
    global flagRedTop
    global flagRedBottom
    flagRedTop = 0
    flagRedBottom = 0
    def explore_path(start_i, start_j, copy_matrix, multiple_ones, f):
        global flagRedTop
        global flagRedBottom
        if (flagRedTop == 1 and flagRedBottom == 1):
            return True, copy_matrix

        if copy_matrix[start_i - 1][start_j] == 3:
            flagRedTop = 1
            if flagRedBottom == 1:
                return True, copy_matrix
        
        if copy_matrix[start_i + 1][start_j] == 4:
            flagRedBottom = 1
            if flagRedTop == 1:
                return True, copy_matrix

        copy_matrix[start_i][start_j] = 0
        for di, dj in [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]:
            next_i, next_j = start_i + di, start_j + dj
            if copy_matrix[next_i][next_j] == 1:
                f = f + 1
                if f == 0:
                    return False, list(map(list, matrix))
                multiple_ones[0] = True
                result, copy_matrix = explore_path(next_i, next_j, copy_matrix, multiple_ones, f)
                if result:
                    return True, copy_matrix

        return False, copy_matrix

    # Traverse through each column in the current row
    for j in range(len(matrix[0])):
        if matrix[1][j] == 1:
            f = 0
            copy_matrix = [row[:] for row in matrix]
            result, new_matrix = explore_path(1, j, copy_matrix, [False], f)
            if result:
                return True, new_matrix

    return False, matrix

def traverse_matrixforBlue(matrix):
    global flagBlueLeft
    global flagBlueRight
    flagBlueLeft = 0
    flagBlueRight = 0
    def explore_path(start_i, start_j, copy_matrix, multiple_ones, f):
        global flagBlueLeft
        global flagBlueRight
        if (flagBlueLeft == 1 and flagBlueRight == 1):
            return True, copy_matrix

        if copy_matrix[start_i][start_j - 1] == 5:
            flagBlueLeft = 1
            if flagBlueRight == 1:
                    return True, copy_matrix

        if copy_matrix[start_i][start_j + 1] == 6:
            flagBlueRight = 1
            if flagBlueLeft == 1:
                    return True, copy_matrix

        copy_matrix[start_i][start_j] = 0
        for di, dj in [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]:
            next_i, next_j = start_i + di, start_j + dj

            if copy_matrix[next_i][next_j] == 2:
                f = f + 1
                if f == 0:
                    return False, list(map(list, matrix))
                multiple_ones[0] = True
                found_path, copy_matrix = explore_path(next_i, next_j, copy_matrix, multiple_ones, f)
                if found_path:
                    return True, copy_matrix

        return False, copy_matrix
    
    for i in range(len(matrix)):
        if matrix[i][1] == 2:
            f = 0
            copy_matrix = [row[:] for row in matrix]
            result, new_matrix = explore_path(i, 1, copy_matrix, [False], f)
            if result:
                return True, new_matrix

    return False, matrix

def heuristics(boardtest, player):
    # Define the weights for different features
    weights = {
        'blocks': 100,  # Blocking opponent's paths
        'clusters': 50,  # Encouraging building clusters of pieces
        'right_to_left': 60,  # Encouraging connections from right to left
        'distance': 40,  # Encouraging pieces to move towards the center
        'win': 10000  # Winning the game
    }

    # Initialize the evaluation score
    score = 0

    resultBlue, _ = traverse_matrixforBlue(boardtest)
    # Check for winning condition
    if resultBlue:
        return weights['win']

    # Check for opponent's winning condition
    resultRed, _ = traverse_matrixforRed(boardtest)
    if resultRed:
        return -weights['win']

    center_column = len(boardtest[0]) // 2
    rightmost_column = len(boardtest[0]) - 1

    for row in range(len(boardtest)):
        for col in range(len(boardtest[row])):
            if boardtest[row][col] == player:
                # Check neighboring cells
                for dr, dc in [(0, 1), (1, 0), (-1, 1), (-1, 0), (0, -1), (1, -1)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < len(boardtest) and 0 <= c < len(boardtest[r]):
                        if boardtest[r][c] == 1:  # Encourage blocking opponent's paths
                            score += weights['blocks']

                # Calculate distance from the rightmost column
                distance_to_right = rightmost_column - col
                score += weights['right_to_left'] * (distance_to_right / rightmost_column)  # Penalize distance

                # Calculate distance from the center column
                distance_to_center = abs(col - center_column)
                score += weights['distance'] * (1 - distance_to_center / center_column)

    # Encourage building clusters of pieces
    cluster_count = count_clusters(boardtest, player)
    score += weights['clusters'] * cluster_count

    return score

def count_clusters(board, player):
    visited = set()
    cluster_count = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == player and (row, col) not in visited:
                cluster_count += 1
                dfs(board, player, row, col, visited)
    return cluster_count

def dfs(board, player, row, col, visited):
    if (row, col) in visited or board[row][col] != player:
        return
    visited.add((row, col))
    directions = [(0, 1), (1, 0), (-1, 1), (-1, 0), (0, -1), (1, -1)]
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < len(board) and 0 <= c < len(board[0]):
            dfs(board, player, r, c, visited)

flagRedTop = 0
flagBlueLeft = 0
flagBlueRight = 0
flagRedBottom = 0

def minimax(boardtest, depth, alpha, beta, ismaximizing):
    # print("Minimax")
    if depth >= 2:
        # print(heuristics(board))
        return heuristics(boardtest, 2), None, None
    else: 
        if ismaximizing:
            # print("It is maximizing")
            best_value = -1000000
            best_move_i = None
            best_move_j = None
            for i in range(0, 11):
                for j in range(0, 11):
                    if boardtest[i+1][j+1] == 0:
                        boardtest[i+1][j+1] = 2
                        value,_,_ = minimax(boardtest, depth + 1, alpha, beta, False)
                        boardtest[i+1][j+1] = 0
                        if value > best_value:
                            best_value = value
                            best_move_i = i
                            best_move_j = j
                        alpha = max(alpha, best_value) 
                        if beta <= alpha:
                            break
            return best_value, best_move_i, best_move_j
        else:
            best_value = 1000000
            best_move_i = None
            best_move_j = None
            for i in range(0, 11):
                for j in range(0, 11):
                    if boardtest[i+1][j+1] == 0:
                        boardtest[i+1][j+1] = 1
                        value,_,_ = minimax(boardtest, depth + 1, alpha, beta, True)
                        boardtest[i+1][j+1] = 0
                        if value < best_value:
                            best_value = value
                            best_move_i = i
                            best_move_j = j
                        beta = min(beta, best_value)
                        if beta <= alpha:
                            break
            return best_value, best_move_i, best_move_j

def draw_pieces():
    for pos, color in placed_pieces:
        pygame.draw.circle(screen, color, pos, 20)
    return None

def show_popup(message):
    font = pygame.font.Font(None, 36)
    popup_width, popup_height = 400, 100
    popup_surface = pygame.Surface((popup_width, popup_height))
    popup_surface.fill(WHITE)

    text_surface = font.render(message, True, BLACK)
    text_rect = text_surface.get_rect(center=(popup_width // 2, popup_height // 2))

    popup_surface.blit(text_surface, text_rect)

    screen_width, screen_height = WINDOW_SIZE
    popup_rect = popup_surface.get_rect(center=(screen_width // 2, screen_height // 2))

    screen.blit(popup_surface, popup_rect)
    pygame.display.flip()  # Update the display to show the pop-up

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        pygame.time.delay(100)

def play_game():
    clickable_positions = []  # Store clickable areas
    global placed_pieces  # Reference the global variable

    for row in range(11):
        clickable_positions.append([])
        for col in range(11):
            x = 103 + col * SPACINGX + row * SHIFT_AMOUNT
            y = 127 + row * SPACINGY
            clickable_positions[row].append((x, y))

    board = [
        [7, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 7],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
        [7, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 7],
    ]
    current_player = 1  # 1 starts
    running = True
    winnerBlue = 0
    boardCheck = [row[:] for row in board]
    while running:
        if current_player == 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
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
                                            placed_pieces.append((clickable_positions[row][col], RED)) 
                                            winnerBlue, _ = traverse_matrixforBlue(boardCheck)
                                            if winnerBlue:
                                                show_popup("Blue Player Won!!!")
                                                print("Blue Won")
                                            board[row+1][col+1] = 1
                                            boardCheck = [row[:] for row in board]
                                            current_player = 2

        elif current_player == 2:
            winnerRed, _ = traverse_matrixforRed(boardCheck)
            if winnerRed:
                print("Red Won")
                show_popup("Red Player Won!!!")
            boardTest = [row[:] for row in board]
            boardCheck = [row[:] for row in board]
            _,i,j = minimax(boardTest, 0, -float('inf'), float('inf'), True)
            placed_pieces.append((clickable_positions[i][j], BLUE)) 
            board[i + 1][j + 1] = 2
            current_player = 1   

        # Draw the board and update the display
        screen.blit(background_image, (0, 0))
        draw_pieces()  # Draw all placed pieces
        pygame.display.flip()  # Refresh the display

    # Exit Pygame and clean up resources
    pygame.quit()
    sys.exit()
    
play_game()
    
