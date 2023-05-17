# ez-egy-projekt
Ez egy projekt

Megj: Valóban, ez egy projekt

Running the requires the following:
pyhton 3.8 or newer
java 17 or newer
py5 
For details about the setup, see http://py5coding.org/content/install.html

The checkers game consists of (and requires) the following files to run:
checkers.py
game_pvp.py
menu.py
player_movement.py
checkers_graphics.py

A game of checkers can be started by running the checkers.py file. A menu will show up, presenting the player with the following gamemodes:
- player vs. player
- player vs. bot
- bot    vs. bot

The bot's tactic is to count ahead three moves (for both players) and the choose the option that gives it the most points (it chooses at random in case of multiple best options). 
Points are assigned as:
+1 for taking a piece
+1 for crowning a piece
-1 for enemy taking a piece
-1 for enemy crowning a piece
+100 for winning the game
-100 for losing the game