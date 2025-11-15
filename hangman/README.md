# Hangman Game AI Solutions

This directory contains two different approaches to solving the classic Hangman word-guessing game using AI techniques.

## stat_soln - Statistical Approach

The `stat_soln` directory implements a sophisticated rule-based statistical approach to playing Hangman, built through iterative refinement and empirical testing.

### Development Process

**Initial Strategy:**
The approach began with a naive frequency-based strategy that guessed letters in order of their global frequency across the training dictionary, achieving only ~15% success rate.

**Pruning Evolution:**
Early attempts at aggressive pruning (excluding words containing known incorrect letters) actually decreased performance. This revealed a key insight: while pruning helped with in-sample words, it often failed on out-of-sample words by eliminating plausible options too early.

**Ensemble Approach:**
The solution evolved into a hierarchical ensemble of strategies with decreasing strictness, where each layer activates when the previous one fails. This modular approach achieved ~35% success by balancing structural pattern matching with statistical frequency information.

### Key Components

**Prefix/Suffix Matching:**
The core innovation exploits the observation that test words, though unseen, often contain compound words or patterns from the training set. For each length k, matchers contain all prefixes/suffixes of size k from training words. Given a partially revealed word, matchers find matching patterns and suggest letters appearing in the largest number of matches.

**Dictionary Pruning System:**
- **LettersExistPruner**: Filters words that don't contain all revealed letters
- **ExactMatchPruner**: Matches words against the current pattern (e.g., "c.t" matches "cat")  
- **MissingLettersPruner**: Excludes words containing already-guessed incorrect letters
- **Hierarchical Guessers**: Fallback strategies with varying levels of pruning strictness

### Algorithm
1. Start with prefix/suffix matchers for the largest size where at least half the letters are known
2. If no valid candidates remain, proceed to smaller matchers
3. When matchers are exhausted, fall back to hierarchical guessers with decreasing pruning strictness
4. Final fallback uses global frequency statistics with no pruning
5. Select the most frequent unguessed letter from the chosen strategy

### Performance
- **Training set**: ~87% win rate (familiar words)
- **Validation set**: ~60% win rate (unseen words)
- Significantly outperforms naive frequency-based approaches through structural pattern matching

## transformer_soln - Deep Learning Approach

The `transformer_soln` directory implements a more principled transformer neural network to solve Hangman.

### Architecture

**Input Representation:**
- Character-level tokenization with special tokens (START, END, MISS, PAD)
- Current word pattern as sequence (e.g., "h*llo" for "hello")
- Guessed letters as binary vector

**Model Components:**
- **Character embeddings**: Learn representations for each character
- **Guess encoder**: 4-layer transformer to process guessed letters
- **Decoder**: 8-layer transformer with self-attention and cross-attention
- **Relative position bias**: Helps model understand positional relationships

### Training Process
1. **Data generation**: Randomly mask letters in training words to create game states
2. **Multi-round context**: Simulate multiple guessing rounds during training
3. **Loss function**: Binary cross-entropy to predict which letters are in the word
4. **Optimization**: AdamW optimizer with careful weight initialization

### Key Features
- **Cross-attention**: Allows decoder to focus on relevant parts of the guess encoding
- **Relative position embeddings**: Captures positional relationships in words
- **Context rounds**: Trains on sequences of guesses, not just single moves
- **Comprehensive logging**: Tracks activations and gradients for analysis

### Performance
- Achieves ~70% accuracy on validation set
- Significantly better than statistical approach on unseen words
- Demonstrates learning of complex letter patterns and word structures

## Comparison

| Approach | Win Rate (Train) | Win Rate (Val) | Strengths | Weaknesses |
|----------|------------------|----------------|-----------|------------|
| Statistical | 87% | 60% | Fast, interpretable, good on familiar words | Poor generalization to unseen words |
| Transformer | N/A | 70% | Learns complex patterns, better generalization | Requires training, less interpretable |
