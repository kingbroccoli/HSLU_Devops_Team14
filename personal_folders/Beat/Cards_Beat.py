class Card:
    """
    Base class for all cards.
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def execute(self, marble, board):
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
        """
       Execution of Rule 1 and 2
        """
        if distance not in (1, 11):
            raise ValueError("Based on the Rules, you can only choose distance 1 and 11.")
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
        """
        Execution of Rule 1 and 2
        """
        if move_out:
            marble.enter_play(board)
        else:
            marble.move_forward(board, 13)

class Queen(Card):
    """
    Special Card: Queen
    Rule: Move a marble 10 spaces backward
    """
    def __init__(self):
        super().__init__("Queen", "Move a marble 10 spaces backward.")

    def execute(self, marble, board):
        """
        Execution of the Queen card's rule: Move the marble 10 spaces backward.
        """
        if not marble.is_in_play:
            raise ValueError("Marble is not in play.")
        marble.position = board.calculate_new_position(marble.position, -10)
        print(f"Marble moved backward to position {marble.position}.")

class Marble:
    """
    Represents a marble on the board.
    """
    def __init__(self, position, is_in_play=False):
        self.position = position
        self.is_in_play = is_in_play

    def move_forward(self, board, distance):
        """
        Moves the marble forward by the given distance on the board.
        """
        if not self.is_in_play:
            raise ValueError("Marble is not in play.")
        self.position = board.calculate_new_position(self.position, distance)
        print(f"Marble moved to position {self.position}.")

    def enter_play(self, board):
        """
        Brings the marble into play.
        """
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
        """
        Calculates the new position of a marble based on the distance to move.
        """
        return (current_position + distance) % self.size

    def get_starting_position(self):
        """
        Returns the starting position for a marble entering play.
        """
        return 0  # position 0 is the starting position.


# Set up the board and marble
board = Board(size=40)  # The board has 40 spaces
marble = Marble(position=None, is_in_play=False)  # The marble starts off the board (not in play)

# Use the King card to bring the marble onto the board
king_card = King()
king_card.execute(marble, board, move_out=True)  # The marble is now in play at position 0

# Use the Ace card to move the marble forward by 1 space
ace_card = Ace()
ace_card.execute(marble, board, distance=1)  # Marble moves to position 1

# Use the Ace card again to move the marble forward by 11 spaces
ace_card.execute(marble, board, distance=11)  # Marble should move to position 12

# Use the King card to move the marble forward by 13 spaces
king_card.execute(marble, board, move_out=False)

# Use the Queen card to move the marble backward by 10 spaces
queen_card = Queen()
queen_card.execute(marble, board)  # Marble moves backward by 10 spaces
