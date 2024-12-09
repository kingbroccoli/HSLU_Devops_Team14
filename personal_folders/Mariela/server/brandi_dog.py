# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random


# -----------------------------------
# Base Card Class and Special Cards
# -----------------------------------

class Card:
    """
    Base class for all cards.
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def execute(self, marble, board, **kwargs):
        """
        Executes the action of the card.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")

class Ace(Card):
    """
    Special Card: Ace
    Rule 1: Marble can move distance 1
    Rule 2: Marble can move distance 11
    """
    def __init__(self):
        super().__init__("Ace", "Move a marble 1 or 11 spaces forward.")

    def execute(self, marble, board, distance):
        if distance not in (1, 11):
            raise ValueError("You can only choose distance 1 or 11.")
        marble.move_forward(board, distance)

class King(Card):
    """
    Special Card: King
    Rule 1: Bring a marble out
    Rule 2: Move 13 spaces forward
    """
    def __init__(self):
        super().__init__("King", "Bring a marble into play or move 13 spaces forward.")

    def execute(self, marble, board, move_out=False):
        if move_out:
            marble.enter_play(board)
        else:
            marble.move_forward(board, 13)

class Queen(Card):
    """
    Special Card: Queen
    Rule: Move a marble 10 spaces backward.
    """
    def __init__(self):
        super().__init__("Queen", "Move a marble 10 spaces backward.")

    def execute(self, marble, board):
        if not marble.is_in_play:
            raise ValueError("Marble is not in play.")
        marble.move_backward(board, 10)

class Seven(Card):
    """
    Special Card: Seven
    Rule: Divide the 7 points among different marbles.
    """
    def __init__(self):
        super().__init__("Seven", "Divide 7 points among different marbles.")

    def execute(self, marbles, board, moves):
        if sum(move[1] for move in moves) != 7:
            raise ValueError("The total movement must sum to 7.")
        for marble, distance in moves:
            marble.move_forward(board, distance)

class Joker(Card):
    """
    Special Card: Joker
    Rule: Acts as any card the player chooses.
    """
    def __init__(self):
        super().__init__("Joker", "Acts as any card the player chooses.")

    def execute(self, marble, board, substitute_card: Card, **kwargs):
        print(f"Joker played as {substitute_card.name}.")
        substitute_card.execute(marble, board, **kwargs)

# -----------------------------------
# Marble and Board Classes
# -----------------------------------

class Marble:
    """
    Represents a marble on the board.
    """
    def __init__(self, position=None, is_in_play=False):
        self.position = position
        self.is_in_play = is_in_play

    def move_forward(self, board, distance):
        if not self.is_in_play:
            raise ValueError("Marble is not in play.")
        self.position = board.calculate_new_position(self.position, distance)
        print(f"Marble moved to position {self.position}.")

    def move_backward(self, board, distance):
        if not self.is_in_play:
            raise ValueError("Marble is not in play.")
        self.position = board.calculate_new_position(self.position, -distance)
        print(f"Marble moved backward to position {self.position}.")

    def enter_play(self, board):
        if self.is_in_play:
            raise ValueError("Marble is already in play.")
        self.is_in_play = True
        self.position = board.get_starting_position()
        print(f"Marble entered play at position {self.position}.")

class Board:
    """
    Represents the game board.
    """
    def __init__(self, size):
        self.size = size

    def calculate_new_position(self, current_position, distance):
        return (current_position + distance) % self.size

    def get_starting_position(self):
        return 0  # Starting position for marbles entering play.

# -----------------------------------
# Player State Class
# -----------------------------------

class PlayerState(BaseModel):
    name: str                  # Player name
    list_card: List[Card]      # Player's hand of cards
    list_marble: List[Marble]  # Player's marbles

    def __init__(self, name: str, num_marbles: int = 4):
        super().__init__(
            name=name,
            list_card=[],
            list_marble=[Marble() for _ in range(num_marbles)]
        )

    def play_card(self, card: Card, marble_index: int, board, **kwargs):
        if marble_index < 0 or marble_index >= len(self.list_marble):
            print("Invalid marble index!")
            return
        marble = self.list_marble[marble_index]
        print(f"{self.name} plays {card.name}.")
        card.execute(marble, board, **kwargs)

# -----------------------------------
# Game State and Logic
# -----------------------------------

class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'

class GameState(BaseModel):
    cnt_player: int
    phase: GamePhase
    list_player: List[PlayerState]
    board: Board

    def __init__(self, cnt_player=4, board_size=40):
        board = Board(board_size)
        super().__init__(
            cnt_player=cnt_player,
            phase=GamePhase.SETUP,
            list_player=[PlayerState(name=f"Player {i+1}") for i in range(cnt_player)],
            board=board
        )

# -----------------------------------
# Example Game Setup
# -----------------------------------

if __name__ == "__main__":
    # Initialize the game
    game_state = GameState()

    # Get the first player
    player = game_state.list_player[0]

    # Set up cards for demonstration
    ace_card = Ace()
    king_card = King()
    queen_card = Queen()

    # Play cards
    player.play_card(king_card, 0, game_state.board, move_out=True)  # Bring a marble into play
    player.play_card(ace_card, 0, game_state.board, distance=11)    # Move marble forward by 11
    player.play_card(queen_card, 0, game_state.board)              # Move marble backward by 10
