# "Hex" Board Game
## Table of Contents
- Usage
- API Reference
- Compile
- Contributors

## Usage
Hex Board game, also called Nash, is a two player strategy game where players attempt to connect two different sides of a hexagonal board. This board is 11x11 and it allows each player to place one piece at a time. In this version the user will play against an AI that calculates movements using "minimax algorithm". The first player who connects the two sides of the board wins the game. 

## API Reference
- ### Disjoint Set Class
All functions related to disjoint set that is used to check if any player won the game.
- ### HexGame Class
All functions related to the initial set of the game including the ones with the heuristic logic.
- ### minimax
Function that implement minimax algorithm to figure out the best AI move.
- ### play
Function that allows the player to make a move in the board that will be added to de disjoint sets.
- ### draw_pieces
Function to draw all the pieces in the UI board
- ### main()
Function where game is executed
  
## Compile
In order to use our implementation, please follow the instructions provided below:
1. Download Python in terminal: https://www.python.org/downloads/
2. Install library pygame: [https://pypi.org/project/networkx/](https://www.pygame.org/news)

   ![Screenshot 2024-04-20 at 10 03 14 PM](https://github.com/chayex18/Hex/assets/133992144/5de8e564-4d21-4694-8810-85fbb845a3b5)
4. Download zip file from main repository
5. After installing python and the mentioned library, open the folder where hex_game.py is located by using Terminal.
6. Run the program by typing the following line in terminal:
![Screenshot 2024-04-20 at 10 05 18 PM](https://github.com/chayex18/Hex/assets/133992144/3db579ba-6a56-4c46-866e-907b5a3d7523)
7. Enjoy the game. 
## Contributors
- Yeixon Chacon - U24830068
- Elias Hurtado - U00042456
  
