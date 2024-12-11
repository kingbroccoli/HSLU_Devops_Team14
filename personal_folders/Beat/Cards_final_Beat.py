class Card:
    """
    Basic card class that all other cards inherit from.
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def execute(self, marble, board, *args, **kwargs):
        raise NotImplementedError("This method should be implemented in the child class.")

class Ace(Card):
    """
    Ace card: Move 1 or 11 spaces forward.
    """
    def __init__(self):
        super().__init__("Ace", "Start or move 1 or 11 spaces forward.")

    def execute(self, marble, board, distance):
        if distance not in (1, 11):
            print("You can only move 1 or 11 spaces with the Ace card!")
            return
        marble.move_forward(board, distance)

class King(Card):
    """
    King card: Bring a marble into play or move 13 spaces forward.
    """
    def __init__(self):
        super().__init__("King", "Start or move 13 spaces forward.")

    def execute(self, marble, board, move_out=False):
        if move_out:
            marble.enter_play(board)
        else:
            marble.move_forward(board, 13)

class Queen(Card):
    """
    Queen card: Move 12 spaces forward.
    """
    def __init__(self):
        super().__init__("Queen", "Move 12 spaces forward.")

    def execute(self, marble, board):
        marble.move_forward(board, 12)

class Two(Card):
    """
    Two card: Move 2 spaces forward.
    """
    def __init__(self):
        super().__init__("Two", "Move 2 spaces forward.")

    def execute(self, marble, board):
        marble.move_forward(board, 2)

class Three(Card):
    """
    Three card: Move 3 spaces forward.
    """
    def __init__(self):
        super().__init__("Three", "Move 3 spaces forward.")

    def execute(self, marble, board):
        marble.move_forward(board, 3)

class Four(Card):
    """
    Four card: Move 4 spaces forward or backward.
    """
    def __init__(self):
        super().__init__("Four", "Move 4 spaces forward or backward.")

    def execute(self, marble, board, forward=True):
        if forward:
            marble.move_forward(board, 4)
        else:
            marble.move_backward(board, 4)

class Five(Card):
    """
    Five card: Move 5 spaces forward.
    """
    def __init__(self):
        super().__init__("Five", "Move 5 spaces forward.")

    def execute(self, marble, board):
        marble.move_forward(board, 5)

class Six(Card):
    """
    Six card: Move 6 spaces forward.
    """
    def __init__(self):
        super().__init__("Six", "Move 6 spaces forward.")

    def execute(self, marble, board):
        marble.move_forward(board, 6)

class Seven(Card):
    """
    Seven card: Split 7 spaces between two marbles.
    """
    def __init__(self):
        super().__init__("Seven", "Split 7 spaces between two marbles.")

    def execute(self, marble1, marble2, board, split1, split2):
        if split1 + split2 != 7:
            print("The splits must add up to 7!")
            return
        marble1.move_forward(board, split1)
        marble2.move_forward(board, split2)

class Eight(Card):
    """
    Eight card: Move 8 spaces forward.
    """
    def __init__(self):
        super().__init__("Eight", "Move 8 spaces forward.")

    def execute(self, marble, board):
        marble.move_forward(board, 8)

class Nine(Card):
    """
    Nine card: Move 9 spaces forward.
    """
    def __init__(self):
        super().__init__("Nine", "Move 9 spaces forward.")

    def execute(self, marble, board):
        marble.move_forward(board, 9)

class Ten(Card):
    """
    Ten card: Move 10 spaces forward.
    """
    def __init__(self):
        super().__init__("Ten", "Move 10 spaces forward.")

    def execute(self, marble, board):
        marble.move_forward(board, 10)

class Swap(Card):
    """
    Swap card: Swap positions of two marbles.
    """
    def __init__(self):
        super().__init__("Swap", "Swap positions with another marble.")

    def execute(self, marble1, marble2):
        marble1.position, marble2.position = marble2.position, marble1.position
        print(f"Swapped positions: Marble1 is now at {marble1.position}, Marble2 is now at {marble2.position}.")

class Joker(Card):
    """
    Joker card: Mimic another card's functionality.
    """
    def __init__(self):
        super().__init__("Joker", "Use as any other card.")

    def execute(self, card, marble, board, *args, **kwargs):
        print(f"Using Joker as a {card.name} card.")
        card.execute(marble, board, *args, **kwargs)

class Marble:
    """
    A marble that moves around the board.
    """
    def __init__(self, position=None, is_in_play=False):
        self.position = position
        self.is_in_play = is_in_play

    def move_forward(self, board, distance):
        if not self.is_in_play:
            print("The marble is not in play!")
            return
        self.position = board.calculate_new_position(self.position, distance)
        print(f"Marble moved forward to position {self.position}.")

    def move_backward(self, board, distance):
        if not self.is_in_play:
            print("The marble is not in play!")
            return
        self.position = board.calculate_new_position(self.position, -distance)
        print(f"Marble moved backward to position {self.position}.")

    def enter_play(self, board):
        if self.is_in_play:
            print("The marble is already in play!")
            return
        self.is_in_play = True
        self.position = board.get_starting_position()
        print(f"Marble entered play at position {self.position}.")

class Board:
    """
    The board where the marbles move.
    """
    def __init__(self, size):
        self.size = size

    def calculate_new_position(self, current_position, distance):
        return (current_position + distance) % self.size

    def get_starting_position(self):
        return 0  # Starting position is 0

# Example Gameplay
board = Board(size=40)  # Create a board with 40 spaces
marble1 = Marble()  # Create the first marble
marble2 = Marble()  # Create a second marble

# Use King card to bring marble1 into play
king_card = King()
king_card.execute(marble1, board, move_out=True)

# Move marble1 forward 3 spaces with a Three card
three_card = Three()
three_card.execute(marble1, board)

# Move marble1 forward 5 spaces with a Five card
five_card = Five()
five_card.execute(marble1, board)

# Move marble1 forward 4 spaces with a Four card
four_card = Four()
four_card.execute(marble1, board, forward=True)

# Move marble1 backward 4 spaces with a Four card
four_card.execute(marble1, board, forward=False)

# Move marble1 forward 12 spaces with a Queen card
queen_card = Queen()
queen_card.execute(marble1, board)
