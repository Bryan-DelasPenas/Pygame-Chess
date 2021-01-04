# Pygame-Chess
A self created library that creates and handles a chess game
This program is a self created library, that handles a game of chess.  
This version of only allows for one person to move both white and black pieces. 
<br> 

## Features
It has valid moves, meaning that only proper chess moves are allowed, <br> 
ie) pawns can only move foward, bishops moves diagonally.<br>

Includes checks and pins, and check mates. <br>
Includes a pawn promotion only makes a pawn into a queen <br>
Includes castling 
<br>

## Installation
### Virtual Enviroment 
By using anaconda, these are the following steps to create a virtual enviroment <br> 
```
conda -V 
```
This checks if conda is installed and in your PATH <br>

```
conda update conda 
```
Updates any packages if neccessary 

```
conda create -n yourenvname python=x.x anaconda 
```
Where yourenvname is the name of your enviroment, and x.x is the version of python <br>

```
source activate yourenvname 
source deactivate 
```
Activates your virtual enviroment and deactivates it <br>

### Modules
```
conda install numpy 
conda install pygame 
```
These are the only two libraries being used for this program <br>
Also download the images directory for the images of each chess piece
