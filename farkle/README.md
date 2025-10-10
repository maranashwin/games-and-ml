# Farkle Game Implementation

This notebook implements a complete Farkle dice game with AI strategies for optimal play.

## What is Farkle?

Farkle is a dice game where players roll 6 dice and score points based on specific combinations. Players can choose to keep rolling for more points or pass to bank their current round score. If a roll doesn't produce any scoring combinations, the player "busts" and loses all points from that round.

## Key Components

### Game Engine
- **Dice class**: Manages dice rolling and state
- **Rule class**: Defines scoring combinations (singles, three-of-a-kind, straights, etc.)
- **Move/Movelet classes**: Represent scoring actions and combinations
- **Farkle class**: Main game controller that manages rounds and gameplay

### Strategies

1. **SimpleStrategy**: A basic heuristic-based strategy that:
   - Rolls when you have 3+ dice and haven't reached victory points
   - Always takes the highest-scoring move available

2. **OptimalStrategy**: Uses dynamic programming to calculate the mathematically optimal play:
   - Pre-computes win probabilities for all game states
   - Makes decisions based on expected value calculations
   - Trains through iterative value updates until convergence

3. **HumanStrategy**: Interactive strategy for human players with command-line interface

### Features

- Complete rule set including singles (1s=100pts, 5s=50pts), three-of-a-kind, straights, and more
- Automated gameplay with detailed logging
- Batch simulation for strategy comparison
- Strategy serialization/deserialization for reuse

### Results

The optimal strategy significantly outperforms the simple strategy:
- Optimal vs Simple: ~68% win rate for player 1
- Optimal vs Optimal: ~58% win rate fir okayer 1

The notebook includes both interactive gameplay against AI opponents and statistical analysis of strategy performance.
