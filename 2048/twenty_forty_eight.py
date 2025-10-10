import random
import pygame
import os
import copy
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass


class GameState(Enum):
    """Represents the current state of the game."""
    START_SCREEN = "start_screen"
    PLAYING = "playing"
    GAME_OVER = "game_over"




@dataclass
class GameConfig:
    """Configuration constants for the game."""
    # Display settings
    FPS: int = 60
    DISPLAY_WIDTH: int = 600
    DISPLAY_HEIGHT: int = 720
    GAME_BOX_SIZE: int = 540
    MARGIN: int = 12
    TILE_SIZE: int = 120
    
    # Game settings
    BOARD_SIZE: int = 4
    MAX_HISTORY: int = 5
    AI_LOOKUP_DISTANCE: int = 5
    AI_LOOKUP_LIMIT: int = 200
    
    # File paths
    BEST_SCORE_FILE: str = 'best_score.txt'
    ICON_FILE: str = 'icon.PNG'
    FONT_FILE: str = 'ClearSans-Medium.ttf'


@dataclass
class Colors:
    """Color definitions for the game."""
    BACKGROUND: Tuple[int, int, int] = (183, 176, 157)
    WHITE: Tuple[int, int, int] = (251, 249, 240)
    SCORE_BG: Tuple[int, int, int] = (187, 174, 158)
    TITLE: Tuple[int, int, int] = (125, 115, 103)
    BUTTON: Tuple[int, int, int] = (255, 120, 13)
    
    # Tile colors for different values
    TILE_COLORS: Dict[int, Tuple[int, int, int]] = None
    
    # Text colors for different values
    TEXT_COLORS: Dict[int, Tuple[int, int, int]] = None
    
    def __post_init__(self):
        if self.TILE_COLORS is None:
            self.TILE_COLORS = {
                0: (204, 193, 181), 2: (238, 229, 219), 4: (237, 225, 202),
                8: (240, 178, 127), 16: (247, 151, 91), 32: (248, 124, 98),
                64: (246, 94, 57), 128: (237, 206, 115), 256: (237, 202, 100),
                512: (237, 198, 81), 1024: (238, 199, 68), 2048: (236, 194, 48),
                4096: (254, 61, 62), 8192: (255, 32, 33), 16384: (255, 32, 33),
                32768: (255, 32, 33), 65536: (255, 32, 33)
            }
        
        if self.TEXT_COLORS is None:
            self.TEXT_COLORS = {
                0: (0, 0, 0), 2: (119, 110, 102), 4: (119, 110, 102),
                8: (255, 255, 255), 16: (255, 255, 255), 32: (255, 255, 255),
                64: (255, 255, 255), 128: (255, 255, 255), 256: (255, 255, 255),
                512: (255, 255, 255), 1024: (255, 255, 255), 2048: (255, 255, 255),
                4096: (255, 255, 255), 8192: (255, 32, 33), 16384: (255, 255, 255),
                32768: (255, 255, 255), 65536: (255, 255, 255)
            }


class GameBoard:
    """Handles the game board logic and operations."""
    
    def __init__(self, size: int = 4):
        self.size = size
        self.total_cells = size * size
        self.board = [0] * self.total_cells
        self._initialize_board()
    
    def _initialize_board(self) -> None:
        """Initialize the board with two random tiles."""
        self.board = [0] * self.total_cells
        self._add_random_tile()
        self._add_random_tile()
    
    def _add_random_tile(self) -> bool:
        """Add a random tile (2 or 4) to an empty cell."""
        empty_cells = [i for i in range(self.total_cells) if self.board[i] == 0]
        if not empty_cells:
            return False
        
        position = random.choice(empty_cells)
        # 90% chance for 2, 10% chance for 4
        self.board[position] = 2 if random.random() < 0.9 else 4
        return True
    
    def is_game_over(self) -> bool:
        """Check if the game is over (no moves possible)."""
        # Check for empty cells
        if 0 in self.board:
            return False
        
        # Check for possible merges
        for i in range(self.total_cells):
            value = self.board[i]
            # Check right neighbor
            if i % self.size < self.size - 1 and self.board[i + 1] == value:
                return False
            # Check bottom neighbor
            if i // self.size < self.size - 1 and self.board[i + self.size] == value:
                return False
        
        return True
    
    def get_max_value(self) -> int:
        """Get the maximum value on the board."""
        return max(self.board) if self.board else 0
    
    def get_empty_cell_count(self) -> int:
        """Get the number of empty cells."""
        return self.board.count(0)
    
    def copy(self) -> 'GameBoard':
        """Create a deep copy of the board."""
        new_board = GameBoard(self.size)
        new_board.board = self.board.copy()
        return new_board


class MoveDirection:
    """Handles movement directions using the original indexing system."""
    
    def __init__(self, size: int = 4):
        self.size = size
        self.total_cells = size * size
        self._initialize_directions()
    
    def _initialize_directions(self) -> None:
        """Initialize direction mappings exactly like the original."""
        # Up: process columns from top to bottom
        self.up = list(range(self.total_cells))
        
        # Down: process columns from bottom to top
        self.down = list(range(self.total_cells - 1, -1, -1))
        
        # Left: process rows from left to right
        self.left = []
        for i in range(self.size):
            self.left.extend(range(i, self.total_cells, self.size))
        
        # Right: process rows from right to left
        self.right = []
        for i in range(self.size - 1, -1, -1):
            self.right.extend(range(i, self.total_cells, self.size))
        
        self.directions = {
            'w': self.up, 'a': self.left,
            's': self.down, 'd': self.right
        }
    
    def get_direction_indices(self, direction: str) -> List[int]:
        """Get the indices for processing a specific direction."""
        return self.directions.get(direction, [])


class GameLogic:
    """Handles the core game logic and move processing using original algorithm."""
    
    def __init__(self, board: GameBoard, move_direction: MoveDirection):
        self.board = board
        self.move_direction = move_direction
    
    def make_move(self, direction: str) -> Tuple[int, bool]:
        """
        Make a move in the specified direction using the original algorithm.
        Returns (score_gained, move_made).
        """
        if direction not in self.move_direction.directions:
            return 0, False
        
        # Create a copy to test the move
        original_board = self.board.board.copy()
        score = self._process_move(direction)
        
        # Check if the move actually changed anything
        move_made = self.board.board != original_board
        
        # Add new tile if move was made
        if move_made:
            self.board._add_random_tile()
        
        return score, move_made
    
    def _process_move(self, direction: str) -> int:
        """Process the actual move using the original algorithm."""
        move_indices = self.move_direction.get_direction_indices(direction)
        score = 0
        add_point = False
        
        # Process each position in the move order
        for i in range(self.board.total_cells):
            pos = move_indices[i]
            if self.board.board[pos] == 0:
                continue
            
            # Look backward in the processing order
            next_i = i - self.board.size
            while next_i >= 0:
                next_pos = move_indices[next_i]
                if self.board.board[next_pos] == 0:
                    # Move tile to empty position
                    self.board.board[next_pos] = self.board.board[pos]
                    self.board.board[pos] = 0
                    pos = next_pos
                    next_i -= self.board.size
                    add_point = True
                elif self.board.board[pos] == self.board.board[next_pos]:
                    # Merge tiles
                    self.board.board[next_pos] = 2 * self.board.board[next_pos]
                    self.board.board[pos] = 0
                    add_point = True
                    score += self.board.board[next_pos]
                    break
                else:
                    break
        
        return score


class Player:
    """Base class for all players."""
    
    def __init__(self, name: str):
        self.name = name
    
    def get_move(self, board: GameBoard, score: int) -> str:
        """
        Get the next move for the player.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_move method")
    
    def __str__(self) -> str:
        return self.name


class HumanPlayer(Player):
    """Human player controlled by keyboard input."""
    
    def __init__(self):
        super().__init__("Human")
        self.pending_move: Optional[str] = None
    
    def get_move(self, board: GameBoard, score: int) -> str:
        """Get the next move from keyboard input."""
        if self.pending_move:
            move = self.pending_move
            self.pending_move = None
            return move
        return 'w'  # Default move if no input
    
    def set_move(self, direction: str) -> None:
        """Set the move to be returned on next get_move call."""
        self.pending_move = direction


class AIPlayer(Player):
    """AI player that uses heuristic evaluation and lookahead."""
    
    def __init__(self, game_logic: GameLogic):
        super().__init__("AI")
        self.game_logic = game_logic
        self.config = GameConfig()
        self.stuck_counter = 0
    
    def get_move(self, board: GameBoard, score: int) -> str:
        """Get the best move using minimax with heuristics."""
        # If stuck too long, make random moves
        if self.stuck_counter > 15:
            return random.choice(['w', 'a', 's', 'd'])
        elif self.stuck_counter > 5:
            return random.choice(['a', 's', 'd'])  # Avoid 'w' which might be causing the issue
        
        try:
            best_move, _ = self._get_best_move(board, score)
            return best_move
        except Exception:
            return random.choice(['w', 'a', 's', 'd'])
    
    def _get_best_move(self, board: GameBoard, score: int) -> Tuple[str, int]:
        """Get the best move using minimax with heuristics."""
        best_score = float('-inf')
        best_move = 'w'
        
        for direction in ['w', 'a', 's', 'd']:
            # Create a copy for evaluation
            test_board = board.copy()
            test_logic = GameLogic(test_board, self.game_logic.move_direction)
            
            # Make the move
            move_score, move_made = test_logic.make_move(direction)
            
            if not move_made:
                continue  # Skip invalid moves
            
            # Evaluate this position
            total_score = score + move_score
            heuristic_value = self._evaluate_position(test_board, total_score)
            
            if heuristic_value > best_score:
                best_score = heuristic_value
                best_move = direction
        
        return best_move, best_score
    
    def _evaluate_position(self, board: GameBoard, score: int) -> float:
        """Evaluate a board position using heuristics."""
        if board.is_game_over():
            return -1 * (score ** 4)  # Heavily penalize game over
        
        # Calculate various heuristics
        empty_cells = board.get_empty_cell_count()
        max_value = board.get_max_value()
        bottom_right_bias = self._calculate_bottom_right_bias(board)
        variety_score = self._calculate_variety_score(board, max_value)
        
        # Weighted combination of heuristics (based on original)
        evaluation = (
            empty_cells * empty_cells * max_value * 1024 +  # Empty cells bonus
            bottom_right_bias * 4 +                         # Bottom-right bias
            max_value * score +                             # Score bonus
            variety_score                                   # Variety bonus
        )
        
        return evaluation
    
    def _calculate_bottom_right_bias(self, board: GameBoard) -> float:
        """Calculate bottom-right bias (prefer higher values in bottom-right)."""
        total = 0
        for i in range(board.total_cells):
            # Weight by position (bottom-right gets higher weights)
            weight = (i % board.size + i // board.size) ** 3
            total += weight * board.board[i]
        return total
    
    def _calculate_variety_score(self, board: GameBoard, max_value: int) -> float:
        """Calculate variety score (prefer diverse tile values)."""
        variety = {}
        for value in board.board:
            variety[value] = variety.get(value, 0) + 1
        
        variety_score = 0
        for value, count in variety.items():
            if value != 0:
                variety_score += (max_value // value) * count
        
        return variety_score


class GameHistory:
    """Manages game history for undo functionality."""
    
    def __init__(self, max_history: int = 5):
        self.max_history = max_history
        self.board_history: List[List[int]] = []
        self.score_history: List[int] = []
    
    def add_state(self, board: List[int], score: int) -> None:
        """Add a game state to history."""
        # Only add if different from last state
        if not self.board_history or self.board_history[-1] != board:
            self.board_history.append(board.copy())
            self.score_history.append(score)
            
            # Limit history size
            if len(self.board_history) > self.max_history + 1:
                self.board_history.pop(0)
                self.score_history.pop(0)
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.board_history) > 1
    
    def undo(self) -> Tuple[List[int], int]:
        """Undo the last move."""
        if not self.can_undo():
            raise ValueError("Cannot undo: insufficient history")
        
        self.board_history.pop(-1)
        self.score_history.pop(-1)
        
        return self.board_history.pop(-1), self.score_history.pop(-1)


class Game2048:
    """Main game class that coordinates all components."""
    
    def __init__(self, config: GameConfig = None):
        self.config = config or GameConfig()
        self.colors = Colors()
        
        # Initialize game components
        self.board = GameBoard(self.config.BOARD_SIZE)
        self.move_direction = MoveDirection(self.config.BOARD_SIZE)
        self.game_logic = GameLogic(self.board, self.move_direction)
        self.history = GameHistory(self.config.MAX_HISTORY)
        
        # Initialize players
        self.human_player = HumanPlayer()
        self.ai_player = AIPlayer(self.game_logic)
        
        # Game state
        self.state = GameState.START_SCREEN
        self.current_player: Optional[Player] = None
        self.score = 0
        self.best_score = self._load_best_score()
        
        # Initialize pygame
        self._initialize_pygame()
    
    def _initialize_pygame(self) -> None:
        """Initialize pygame components."""
        pygame.init()
        pygame.font.init()
        
        self.screen = pygame.display.set_mode((self.config.DISPLAY_WIDTH, self.config.DISPLAY_HEIGHT))
        pygame.display.set_caption("2048")
        
        # Load icon if available
        if os.path.exists(self.config.ICON_FILE):
            icon = pygame.image.load(self.config.ICON_FILE)
            pygame.display.set_icon(icon)
        
        # Initialize fonts
        self._initialize_fonts()
    
    def _initialize_fonts(self) -> None:
        """Initialize pygame fonts."""
        font_path = self.config.FONT_FILE if os.path.exists(self.config.FONT_FILE) else None
        
        self.fonts = {
            'title': pygame.font.Font(font_path, 60),
            'tile': pygame.font.Font(font_path, 48),
            'button': pygame.font.Font(font_path, 20),
            'score_label': pygame.font.Font(font_path, 16),
            'score_value': pygame.font.Font(font_path, 20),
            'final_score': pygame.font.Font(font_path, 30)
        }
    
    def _load_best_score(self) -> int:
        """Load the best score from file."""
        if os.path.exists(self.config.BEST_SCORE_FILE):
            try:
                with open(self.config.BEST_SCORE_FILE, 'r') as f:
                    return int(f.read().strip())
            except (ValueError, IOError):
                pass
        return 0
    
    def _save_best_score(self) -> None:
        """Save the best score to file."""
        try:
            with open(self.config.BEST_SCORE_FILE, 'w') as f:
                f.write(str(self.best_score))
        except IOError:
            pass
    
    def start_game(self, is_human: bool) -> None:
        """Start a new game with the specified player type."""
        self.current_player = self.human_player if is_human else self.ai_player
        self.state = GameState.PLAYING
        self.score = 0
        self.board._initialize_board()
        self.history = GameHistory(self.config.MAX_HISTORY)
        self.history.add_state(self.board.board, self.score)
        
        # Reset AI stuck counter
        if isinstance(self.current_player, AIPlayer):
            self.current_player.stuck_counter = 0
    
    def make_move(self, direction: str) -> bool:
        """Make a move and return True if successful."""
        if self.state != GameState.PLAYING:
            return False
        
        # Add current state to history before making move
        self.history.add_state(self.board.board, self.score)
        
        # Make the move
        score_gained, move_made = self.game_logic.make_move(direction)
        
        if move_made:
            self.score += score_gained
            
            # Update AI stuck counter
            if isinstance(self.current_player, AIPlayer):
                self.current_player.stuck_counter = 0
            
            # Update best score
            if self.score > self.best_score:
                self.best_score = self.score
                self._save_best_score()
            
            # Check for game over
            if self.board.is_game_over():
                self.state = GameState.GAME_OVER
        else:
            # Update AI stuck counter
            if isinstance(self.current_player, AIPlayer):
                self.current_player.stuck_counter += 1
        
        return move_made
    
    def undo_move(self) -> bool:
        """Undo the last move."""
        if not self.history.can_undo() or self.state != GameState.PLAYING:
            return False
        
        try:
            self.board.board, self.score = self.history.undo()
            return True
        except ValueError:
            return False
    
    def reset_game(self) -> None:
        """Reset the current game."""
        is_human = isinstance(self.current_player, HumanPlayer)
        self.start_game(is_human)
    
    def clear_best_score(self) -> None:
        """Clear the best score."""
        self.best_score = 0
        self._save_best_score()
    
    def get_ai_move(self) -> str:
        """Get the next move from the AI."""
        if self.player_type != PlayerType.COMPUTER or self.state != GameState.PLAYING:
            return 'w'
        
        # If stuck too long, make random moves
        if self.stuck_counter > 15:
            return random.choice(['w', 'a', 's', 'd'])
        elif self.stuck_counter > 5:
            return random.choice(['a', 's', 'd'])  # Avoid 'w' which might be causing the issue
        
        try:
            best_move, _ = self.ai.get_best_move(self.board, self.score)
            return best_move
        except Exception:
            return random.choice(['w', 'a', 's', 'd'])
    
    def run(self) -> None:
        """Main game loop."""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            clock.tick(self.config.FPS)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYUP:
                    self._handle_key_event(event)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_event(event)
            
            # AI moves
            if isinstance(self.current_player, AIPlayer) and self.state == GameState.PLAYING:
                ai_move = self.current_player.get_move(self.board, self.score)
                self.make_move(ai_move)
            
            # Render
            self._render()
            pygame.display.update()
        
        pygame.quit()
    
    def _handle_key_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard events."""
        if self.state != GameState.PLAYING or not isinstance(self.current_player, HumanPlayer):
            return
        
        direction_map = {
            pygame.K_UP: 'w',
            pygame.K_DOWN: 's',
            pygame.K_LEFT: 'a',
            pygame.K_RIGHT: 'd'
        }
        
        direction = direction_map.get(event.key)
        if direction:
            self.make_move(direction)
    
    def _handle_mouse_event(self, event: pygame.event.Event) -> None:
        """Handle mouse events."""
        mouse_pos = event.pos
        
        if self.state == GameState.START_SCREEN:
            self._handle_start_screen_click(mouse_pos)
        elif self.state == GameState.PLAYING and isinstance(self.current_player, HumanPlayer):
            self._handle_game_click(mouse_pos)
        elif self.state == GameState.GAME_OVER:
            self._handle_game_over_click(mouse_pos)
    
    def _handle_start_screen_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle clicks on the start screen."""
        # Player buttons (approximate positions from original code)
        player_rect = pygame.Rect(80, 327, 155, 66)
        computer_rect = pygame.Rect(302, 327, 218, 66)
        
        if player_rect.collidepoint(mouse_pos):
            self.start_game(True)  # Human player
        elif computer_rect.collidepoint(mouse_pos):
            self.start_game(False)  # AI player
    
    def _handle_game_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle clicks during gameplay."""
        # Button rectangles (approximate positions)
        reset_rect = pygame.Rect(30, 115, 60, 30)
        undo_rect = pygame.Rect(510, 115, 60, 30)
        clear_rect = pygame.Rect(530, 40, 15, 12)
        
        if reset_rect.collidepoint(mouse_pos):
            self.reset_game()
        elif undo_rect.collidepoint(mouse_pos):
            self.undo_move()
        elif clear_rect.collidepoint(mouse_pos):
            self.clear_best_score()
    
    def _handle_game_over_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Handle clicks on the game over screen."""
        # Play again button (approximate position)
        play_again_rect = pygame.Rect(170, 420, 265, 66)
        
        if play_again_rect.collidepoint(mouse_pos):
            self.state = GameState.START_SCREEN
            self.current_player = None
    
    def _render(self) -> None:
        """Render the current game state."""
        self.screen.fill(self.colors.WHITE)
        
        if self.state == GameState.START_SCREEN:
            self._render_start_screen()
        elif self.state == GameState.PLAYING:
            self._render_game()
        elif self.state == GameState.GAME_OVER:
            self._render_game_over()
    
    def _render_start_screen(self) -> None:
        """Render the start screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.config.DISPLAY_WIDTH, self.config.DISPLAY_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(self.colors.WHITE)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = self.fonts['title'].render("2048", True, self.colors.TITLE)
        title_rect = title_text.get_rect(center=(self.config.DISPLAY_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Choose player text
        choose_text = self.fonts['tile'].render("CHOOSE PLAYER", True, (0, 0, 0))
        choose_rect = choose_text.get_rect(center=(self.config.DISPLAY_WIDTH // 2, 200))
        self.screen.blit(choose_text, choose_rect)
        
        # Player buttons
        self._render_button("Human", 80, 327, 155, 66)
        self._render_button("Computer", 302, 327, 218, 66)
    
    def _render_game(self) -> None:
        """Render the main game screen."""
        # Title
        title_text = self.fonts['title'].render("2048", True, self.colors.TITLE)
        self.screen.blit(title_text, (30, 15))
        
        # Score boxes
        self._render_score_box("SCORE", str(self.score), 320, 30)
        self._render_score_box("BEST", str(self.best_score), 450, 30)
        
        # Buttons
        self._render_button("RESET", 30, 115, 60, 30)
        self._render_button("UNDO", 510, 115, 60, 30)
        
        # Clear button (small square)
        clear_rect = pygame.Rect(530, 40, 15, 12)
        pygame.draw.rect(self.screen, self.colors.SCORE_BG, clear_rect)
        
        # Game board
        self._render_board()
    
    def _render_game_over(self) -> None:
        """Render the game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.config.DISPLAY_WIDTH, self.config.DISPLAY_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(self.colors.WHITE)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.fonts['tile'].render("Game Over!", True, (0, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.config.DISPLAY_WIDTH // 2, 300))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.fonts['final_score'].render(f"Score: {self.score}", True, (0, 0, 0))
        score_rect = score_text.get_rect(center=(self.config.DISPLAY_WIDTH // 2, 350))
        self.screen.blit(score_text, score_rect)
        
        # Play again button
        self._render_button("PLAY AGAIN", 170, 420, 265, 66)
    
    def _render_board(self) -> None:
        """Render the game board."""
        board_surface = pygame.Surface((self.config.GAME_BOX_SIZE, self.config.GAME_BOX_SIZE))
        board_surface.fill(self.colors.WHITE)
        
        # Draw background
        pygame.draw.rect(board_surface, self.colors.BACKGROUND, 
                        (0, 0, self.config.GAME_BOX_SIZE, self.config.GAME_BOX_SIZE), 
                        border_radius=5)
        
        # Draw tiles
        for i in range(self.config.BOARD_SIZE):
            for j in range(self.config.BOARD_SIZE):
                index = i * self.config.BOARD_SIZE + j
                value = self.board.board[index]
                
                # Calculate position
                x = self.config.MARGIN + (self.config.MARGIN + self.config.TILE_SIZE) * j
                y = self.config.MARGIN + (self.config.MARGIN + self.config.TILE_SIZE) * i
                
                # Draw tile background
                color = self.colors.TILE_COLORS.get(value, self.colors.TILE_COLORS[0])
                pygame.draw.rect(board_surface, color, 
                               (x, y, self.config.TILE_SIZE, self.config.TILE_SIZE), 
                               border_radius=10)
                
                # Draw tile text
                if value > 0:
                    text_color = self.colors.TEXT_COLORS.get(value, self.colors.TEXT_COLORS[0])
                    text = self.fonts['tile'].render(str(value), True, text_color)
                    text_rect = text.get_rect(center=(x + self.config.TILE_SIZE // 2, 
                                                    y + self.config.TILE_SIZE // 2))
                    board_surface.blit(text, text_rect)
        
        # Position board on screen
        board_x = (self.config.DISPLAY_WIDTH - self.config.GAME_BOX_SIZE) // 2
        board_y = self.config.DISPLAY_HEIGHT - self.config.GAME_BOX_SIZE - 30
        self.screen.blit(board_surface, (board_x, board_y))
    
    def _render_score_box(self, label: str, value: str, x: int, y: int) -> None:
        """Render a score box."""
        box_width, box_height = 120, 60
        box_surface = pygame.Surface((box_width, box_height))
        box_surface.fill(self.colors.WHITE)
        
        # Draw background
        pygame.draw.rect(box_surface, self.colors.SCORE_BG, 
                        (0, 0, box_width, box_height), border_radius=5)
        
        # Draw label
        label_text = self.fonts['score_label'].render(label, True, self.colors.SCORE_BG)
        label_rect = label_text.get_rect(center=(box_width // 2, box_height // 2 - 10))
        box_surface.blit(label_text, label_rect)
        
        # Draw value
        value_text = self.fonts['score_value'].render(value, True, self.colors.WHITE)
        value_rect = value_text.get_rect(center=(box_width // 2, box_height // 2 + 10))
        box_surface.blit(value_text, value_rect)
        
        self.screen.blit(box_surface, (x, y))
    
    def _render_button(self, text: str, x: int, y: int, width: int, height: int) -> None:
        """Render a button."""
        button_surface = pygame.Surface((width, height))
        button_surface.fill(self.colors.WHITE)
        
        # Draw button text
        text_surface = self.fonts['button'].render(text, True, self.colors.BUTTON)
        text_rect = text_surface.get_rect(center=(width // 2, height // 2))
        button_surface.blit(text_surface, text_rect)
        
        self.screen.blit(button_surface, (x, y))


def main():
    """Main entry point for the game."""
    config = GameConfig()
    game = Game2048(config)
    game.run()


if __name__ == "__main__":
    main()
