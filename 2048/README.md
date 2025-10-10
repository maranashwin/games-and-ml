# 2048 Game Implementation

An old implementation of the classic 2048 puzzle game with both human and AI players.

## Overview

This is an updated version of an old implementation of the 2048 game built with Python and Pygame, that I made years ago to practice my coding.

## Features

### Game Features
- **Classic 2048 Gameplay**: Slide numbered tiles to combine them and reach 2048
- **Human Player**: Control with arrow keys (↑↓←→)
- **AI Player**: Intelligent computer opponent using heuristic evaluation
- **Undo Functionality**: Step back up to 5 moves
- **Score Tracking**: Current score and best score persistence
- **Game History**: Track and replay moves

### Technical Features
- **Object-Oriented Design**: Clean separation of game logic, AI, and UI
- **Polymorphic Player System**: Human and AI players implement the same interface
- **Configurable**: Easy to modify game parameters, colors, and behavior
- **Type Hints**: Full type annotations for better code maintainability
- **Error Handling**: Robust error handling for file operations and edge cases

## Architecture

### Core Components

**GameBoard**: Manages the 4x4 game grid and tile operations
**GameLogic**: Handles move processing using the original 2048 algorithm
**MoveDirection**: Manages directional transformations for sliding tiles
**GameHistory**: Tracks move history for undo functionality

### Player System

**Player** (Base Class): Defines the interface for all players
- `get_move(board, score)`: Returns the next move to make

**HumanPlayer**: Handles keyboard input from human players
- Queues moves from arrow key presses
- Provides default moves when no input available

**AIPlayer**: Intelligent computer player using heuristics
- Evaluates board positions using multiple criteria
- Implements stuck detection and recovery
- Uses minimax-like approach with heuristic evaluation

### AI Strategy

The AI uses several heuristics to evaluate board positions:
- **Empty Cells Bonus**: Prefers positions with more empty spaces
- **Bottom-Right Bias**: Encourages high-value tiles in bottom-right corner
- **Score Integration**: Considers current score in evaluation
- **Variety Score**: Prefers diverse tile values for flexibility
- **Stuck Detection**: Makes random moves when stuck in local minima

## Controls

- **Arrow Keys**: Move tiles (↑=up, ↓=down, ←=left, →=right)
- **Mouse**: Click buttons for Reset, Undo, Clear Best Score
- **Start Screen**: Choose between Human or Computer player


## Running the Game

```bash
python twenty_forty_eight.py
```

The game will start with a player selection screen. Choose "Human" for manual play or "Computer" to watch the AI play.

## Game Rules

1. Use arrow keys to slide all tiles in one direction
2. Tiles with the same number merge when they collide
3. Each move adds a new tile (2 or 4) to an empty space
4. Goal: Create a tile with the number 2048
5. Game ends when the board is full and no moves are possible

The implementation preserves the exact movement logic and scoring system of the original 2048 game while providing a clean, extensible codebase for further development.
