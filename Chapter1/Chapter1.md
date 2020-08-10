# Chapter 1

## Looking One Step Ahead
I first started by programming my player to look at all possible moves. The player
will choose a random position to play out of all positions resulting in it winning.
If there are none, it will randomly choose a position that will result in the game not ending.
Finally, it will randomly choose a tile to play resulting in a loss or draw if no other move is possible.
This player won 81.2% of its games.

## Reinforcement Learning Without Exploration
The next iteration of my player used a value function that was updated as described on page 10 of the book.
However, none of the moves were exploration moves. This player won 81.3% of its games.

## Reinforcement Learning With Exploration
Finally, my player was implemented as described on page 10 with exploration moves. 
