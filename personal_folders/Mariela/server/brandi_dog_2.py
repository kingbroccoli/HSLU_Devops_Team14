# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
# python /Users/elals/Documents/GitHub/HSLU_Devops_Team14/personal_folders/devops_project/benchmark/benchmark_dog.py python brandi_dog_update.Dog
from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import random



class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank

    def __repr__(self):
        return f"Card(suit={self.suit}, rank={self.rank})"

    def __str__(self):
        """
        String representation of the card.

        Returns:
            str: Formatted string of suit and rank.
        """
        if self.rank == "JKR":
            return "JOKER"
        return f"{self.rank}{self.suit}"

    def __eq__(self, other: object) -> bool:
        """
        Compare two cards for equality.

        Args:
            other (object): Another card.

        Returns:
            bool: True if cards are equal, False otherwise.
        """
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self):
        """
        Hash method to allow Card to be used in sets or dictionaries.

        Returns:
            int: Hash value of the card.
        """
        return hash((self.suit, self.rank))

    def is_start_card(self) -> bool:
        """
        Check if the card is a "start card" (Ace, King, or Joker).

        Returns:
            bool: True if the card can start a marble from the kennel, False otherwise.
        """
        return self.rank in ["A", "K", "JKR"]

    def get_movement_value(self) -> Optional[int]:
        """
        Get the movement value associated with the card.

        Returns:
            Optional[int]: The movement value of the card, or None for non-movement cards.
        """
        if self.rank == "A":
            return 1
        if self.rank == "K":
            return 13
        if self.rank == "Q":
            return 12
        if self.rank in ["2", "3", "5", "6", "8", "9", "10"]:
            return int(self.rank)
        if self.rank == "4":
            return -4
        if self.rank == "7":
            return 7
        return None  # JOKER and J have no fixed movement value

    def is_divisible_move(self) -> bool:
        """
        Check if the card allows divisible movement (e.g., SEVEN).

        Returns:
            bool: True if the card allows divisible movement, False otherwise.
        """
        return self.rank == "7"

    def is_swap_card(self) -> bool:
        """
        Check if the card allows swapping positions (e.g., JACK).

        Returns:
            bool: True if the card allows swapping, False otherwise.
        """
        return self.rank == "J"

    def can_move_backward(self) -> bool:
        """
        Check if the card allows backward movement.

        Returns:
            bool: True if the card allows backward movement, False otherwise.
        """
        return self.rank == "4"

    def can_be_any_card(self) -> bool:
        """
        Check if the card can act as any other card (JOKER functionality).

        Returns:
            bool: True if the card can act as any card, False otherwise.
        """
        return self.rank == "JKR"

class Marble(BaseModel):
    player_id: int
    pos: Optional[int] = None
    is_safe: bool = False
    finished: bool = False
    completed_cycle: bool = False

    def to_dict(self):
        return {
                "player_id": self.player_id,
                "pos": self.pos,
                "is_safe": self.is_safe,
                "finished": self.finished,
                "completed_cycle": self.completed_cycle,
        }

    def is_in_kennel(self) -> bool:
        return self.pos is None

    def can_use_card(self, card_rank: str) -> bool:
        """
        Check if the marble can perform the action associated with the given card.

        Args:
            card_rank (str): The rank of the card being played.

        Returns:
            bool: True if the card's effect can be applied to this marble, False otherwise.
        """
        if card_rank in ["A", "K"] and self.is_in_kennel():
            return True  # ACE or KING to leave kennel
        if card_rank in ["2", "3", "5", "6", "8", "9", "10", "Q"] and not self.is_in_kennel():
            return True  # Forward-moving cards
        if card_rank == "4" and not self.is_in_kennel():
            return True  # Move backward
        if card_rank == "7" and not self.is_in_kennel():
            return True  # Divide movement
        if card_rank == "J" and not self.is_in_kennel():
            return True  # Swap
        if card_rank == "JKR":
            return True  # Joker acts as any card
        return False

    def leave_kennel(self, start_pos: int, card_rank: str) -> bool:
        if self.is_in_kennel() and card_rank in ["A", "K", "JKR"]:
            print(f"Marble {self} leaving kennel to position {start_pos} using card {card_rank}")
            self.pos = start_pos
            self.is_safe = True
            return True
        print(f"Marble {self} cannot leave kennel with card {card_rank}")
        return False

    def move(self, steps: int, board_size: int, overtaken_marbles: Optional[List["Marble"]] = None) -> None:
        if self.is_in_kennel():
            raise ValueError("Cannot move a marble still in the kennel.")
        previous_pos = self.pos
        self.pos = (self.pos + steps) % board_size
        print(f"Marble {self} moved from {previous_pos} to {self.pos} (steps: {steps})")

        # Handle safety and collisions
        if overtaken_marbles:
            for marble in overtaken_marbles:
                if marble.pos == self.pos and marble.player_id != self.player_id:
                    marble.send_to_kennel()

        # Reset is_safe after first move
        if self.is_safe and self.pos != previous_pos:
            self.is_safe = False

    def move_to_finish(self, steps: int, finish_positions: List[int]) -> bool:
        """
        Move the marble within the finish zone.

        Args:
            steps (int): Number of steps to move.
            finish_positions (List[int]): The list of valid finish positions.

        Returns:
            bool: True if the move was successful, False otherwise.
        """
        if self.pos not in finish_positions:
            raise ValueError("Marble is not in the finish zone.")

        current_index = finish_positions.index(self.pos)
        new_index = current_index + steps

        if new_index == len(finish_positions) - 1:
            self.finished = True
            self.pos = finish_positions[new_index]
            return True
        elif new_index < len(finish_positions):
            self.pos = finish_positions[new_index]
            return True
        return False

    def divide_move(self, steps: List[int], board_size: int, overtaken_marbles: List["Marble"]) -> None:
        """
        Divide the movement for a SEVEN card.

        Args:
            steps (List[int]): List of movements to make.
            board_size (int): Total size of the board.
            overtaken_marbles (List[Marble]): List of marbles to check for collisions.
        """
        if sum(steps) != 7:
            raise ValueError("The total movement must equal 7 for a SEVEN card.")
        for step in steps:
            self.move(step, board_size, overtaken_marbles)

    def check_cycle(self, start_pos: int) -> None:
        """
        Check if the marble has completed a second loop past its starting position.

        Args:
            start_pos (int): The starting position of the marble.
        """
        if self.pos == start_pos:
            self.completed_cycle = True

    def send_to_kennel(self) -> None:
        """
        Send the marble back to the kennel.
        """
        self.pos = None
        self.is_safe = False
        self.completed_cycle = False
        self.finished = False

    def swap(self, other_marble: "Marble") -> None:
        if self.is_in_kennel() or other_marble.is_in_kennel():
            raise ValueError("Cannot swap positions with a marble in the kennel.")
        self.pos, other_marble.pos = other_marble.pos, self.pos
        print(f"Swapped marble {self} with marble {other_marble}")


class PlayerState(BaseModel):
    player_id: int
    list_card: List[Card] = Field(default_factory=list)
    list_marble: List[Marble] = Field(default_factory=list)
    is_active: bool = False
    is_started: bool = False

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["list_marble"] = [marble.to_dict() for marble in self.list_marble]
        return data

    def get_active_marble_positions(self) -> List[int]:
        """
        Get positions of all active (on-board) marbles.

        Returns:
            List[int]: List of positions of active marbles.
        """
        return [marble.pos for marble in self.list_marble if marble.pos is not None]

    def has_marble_in_kennel(self) -> bool:
        """
        Check if the player has any marble in the kennel.

        Returns:
            bool: True if any marble is in the kennel, False otherwise.
        """
        return any(marble.is_in_kennel() for marble in self.list_marble)

    def can_play_card(self, card: Card) -> bool:
        """
        Check if the player can play a given card.

        Args:
            card (Card): The card to check.

        Returns:
            bool: True if the player can play the card, False otherwise.
        """
        return any(marble.can_use_card(card.rank) for marble in self.list_marble)

    def add_card(self, card: Card) -> None:
        """
        Add a card to the player's hand.

        Args:
            card (Card): The card to add.
        """
        self.list_card.append(card)

    def remove_card(self, card: Card) -> bool:
        """
        Remove a specific card from the player's hand.

        Args:
            card (Card): The card to remove.

        Returns:
            bool: True if the card was successfully removed, False otherwise.
        """
        if card in self.list_card:
            self.list_card.remove(card)
            return True
        return False

    def get_marble_at_position(self, position: int) -> Optional[Marble]:
        """
        Get the marble at a specific position.

        Args:
            position (int): The position to check.

        Returns:
            Optional[Marble]: The marble at the position, or None if no marble is there.
        """
        for marble in self.list_marble:
            if marble.pos == position:
                return marble
        return None


class Action(BaseModel):
    card: Card
    pos_from: Optional[int]
    pos_to: Optional[int]
    card_swap: Optional[Card] = None

    def is_swap_action(self) -> bool:
        """
        Check if the action is a swap action (involving `card_swap`).

        Returns:
            bool: True if the action is a swap action, False otherwise.
        """
        return self.card_swap is not None

    def is_movement_action(self) -> bool:
        """
        Check if the action involves moving a marble.

        Returns:
            bool: True if the action involves moving a marble, False otherwise.
        """
        return self.pos_from is not None and self.pos_to is not None

    def is_kennel_exit_action(self) -> bool:
        """
        Check if the action involves exiting the kennel (from kennel to the start position).

        Returns:
            bool: True if the action is a kennel exit action, False otherwise.
        """
        return self.pos_from is None and self.pos_to is not None

    def validate_action(self):
        try:
            if self.is_swap_action():
                if self.pos_from is not None or self.pos_to is not None:
                    raise ValueError("Swap action cannot have pos_from or pos_to specified.")
            elif self.is_movement_action():
                if self.card_swap is not None:
                    raise ValueError("Movement action cannot involve a card swap.")
            elif self.is_kennel_exit_action():
                if self.pos_from is not None:
                    raise ValueError("Kennel exit action must have pos_from as None.")
            else:
                raise ValueError("Action is invalid: Must be a valid movement, swap, or kennel exit action.")
        except ValueError as e:
            print(f"Invalid action: {e}")
            raise

    def __str__(self):
        """
        Provide a string representation of the action.

        Returns:
            str: String representation of the action.
        """
        if self.is_swap_action():
            return f"Action: Swap {self.card} with {self.card_swap}"
        elif self.is_movement_action():
            return f"Action: Move from {self.pos_from} to {self.pos_to} using {self.card}"
        elif self.is_kennel_exit_action():
            return f"Action: Exit kennel to {self.pos_to} using {self.card}"
        return "Action: Invalid"

class GamePhase(str, Enum):
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    PAUSED = "PAUSED"

    def __str__(self):
        """
        Provide a string representation of the game phase.

        Returns:
            str: The name of the game phase.
        """
        return self.value

class GameState(BaseModel):
    cnt_player: int = 4
    list_player: List[PlayerState] = Field(default_factory=list)
    phase: GamePhase = GamePhase.RUNNING  # Add the phase field with a default value
    cnt_round: int = 0  # Add other necessary fields
    bool_game_finished: bool = False
    bool_card_exchanged: bool = False
    idx_player_started: int = 0
    idx_player_active: int = 0
    list_id_card_draw: List[Card] = Field(default_factory=list)
    list_id_card_discard: List[Card] = Field(default_factory=list)
    card_active: Optional[Card] = None

    def initialize_players(self, board_config) -> None:
        """Initialize players with marbles and cards."""
        start_cards = [Card(suit='♠', rank='A'), Card(suit='♥', rank='K'), Card(suit='', rank='JKR')]
        random.shuffle(start_cards)

        self.list_player = []
        for i in range(self.cnt_player):
            player_color = list(board_config.keys())[i]  # Assign colors to players in order
            home_positions = board_config[player_color]['home']

            # Ensure each player gets at least one start card
            player_cards = [start_cards[i % len(start_cards)]] + random.sample(self.LIST_CARD, 4)
            marbles = [Marble(player_id=i, pos=pos) for pos in
                       home_positions]  # Initialize marbles in the home positions

            self.list_player.append(
                PlayerState(
                    player_id=i,
                    list_card=player_cards,
                    list_marble=marbles
                )
            )

    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',      # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        # 3: Move 3 spots forward
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        # 4: Move 4 spots forward or back
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        # 5: Move 5 spots forward
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        # 6: Move 6 spots forward
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        # 7: Move 7 single steps forward
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        # 8: Move 8 spots forward
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        # 9: Move 9 spots forward
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        # 10: Move 10 spots forward
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        # Jake: A marble must be exchanged
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Queen: Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # King: Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # Ass: Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any other card you want
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2


    class Config:
        arbitrary_types_allowed = True




class Dog(Game):
    def __init__(self) -> None:
        """Game initialization (set_state call not necessary, we expect 4 players)."""
        self.board_numbers = list(range(0, 96))

        self.board = {
            "blue": {
                "home": self.board_numbers[64:68],
                "start": self.board_numbers[0],
                "finish": self.board_numbers[68:72],
            },
            "green": {
                "home": self.board_numbers[72:76],
                "start": self.board_numbers[16],
                "finish": self.board_numbers[76:80],
            },
            "yellow": {
                "home": self.board_numbers[88:92],
                "start": self.board_numbers[48],
                "finish": self.board_numbers[92:96],
            },
            "red": {
                "home": self.board_numbers[80:84],
                "start": self.board_numbers[32],
                "finish": self.board_numbers[84:88],
            },
        }
        self.state = None  # Placeholder for the current GameState

    def reload_deck(self) -> None:
        """Reload the deck when it is empty."""
        if not self.state.list_id_card_draw:  # Si el mazo está vacío
            print("Reloading deck from discard pile...")
            self.state.list_id_card_draw.extend(self.state.list_id_card_discard)
            random.shuffle(self.state.list_id_card_draw)
            self.state.list_id_card_discard.clear()

            if self.state.card_active:
                self.state.list_id_card_draw = [
                    card for card in self.state.list_id_card_draw if card != self.state.card_active
                ]

    def set_state(self, state: GameState) -> None:
        """Set the game to a given state."""
        self.state = state

    def get_state(self) -> GameState:
        """Get the complete, unmasked game state."""
        return self.state

    def print_state(self) -> None:
        """Print the current game state."""
        if self.state:
            print(self.state.model_dump_json(indent=4))  # Remove `ensure_ascii`
        else:
            print("Game state is not initialized.")

    def get_list_action(self) -> List[Action]:
        """Get a list of possible actions for the active player."""
        if not self.state:
            raise ValueError("Game state is not initialized.")

        actions = []
        active_player = self.state.list_player[self.state.idx_player_active]

        print(f"Active player {self.state.idx_player_active}:")
        print(f"  Cards: {active_player.list_card}")
        print(f"  Marbles: [{', '.join(str(marble.pos) for marble in active_player.list_marble)}]")

        for card in active_player.list_card:
            action_found = False  # Flag to stop processing additional marbles for this card
            for marble in active_player.list_marble:
                if marble.is_in_kennel():
                    # Only evaluate cards that allow exiting the kennel
                    if card.is_start_card():
                        start_position = self.board['blue']['start']  # Adjust for player-specific logic
                        print(f"  Valid action: Exit kennel to {start_position} using {card}")
                        actions.append(Action(card=card, pos_from=None, pos_to=start_position))
                        action_found = True  # Exit the loop for this card
                        break
                else:
                    # Marble is on the board, evaluate normal movement cards
                    movement = card.get_movement_value()
                    if movement is not None:
                        # Ensure marble.pos is valid before performing calculations
                        if marble.pos is not None:
                            new_pos = (marble.pos + movement) % len(self.board_numbers)
                            print(f"  Valid action: Move marble from {marble.pos} to {new_pos} with {card}")
                            actions.append(Action(card=card, pos_from=marble.pos, pos_to=new_pos))
                    elif card.is_swap_card():
                        # Logic for swapping marbles (e.g., Jack)
                        print(f"  Valid action: Swap using {card}")
                        # You can add logic for swap actions here
                    else:
                        # Skip invalid cards for movement
                        continue

            # Stop evaluating other marbles for the current card if an action was already found
            if action_found:
                continue

        if not actions:
            print(f"No valid actions for player {self.state.idx_player_active}.")

        return actions

    def apply_action(self, action: Action) -> None:
        active_player_color = ["blue", "green", "yellow", "red"][self.state.idx_player_active]
        start_pos = self.board[active_player_color]["start"]

        if not self.state:
            raise ValueError("Game state is not initialized.")

        active_player = self.state.list_player[self.state.idx_player_active]

        if action.is_kennel_exit_action():
            # Update the marble's position to the start position
            for marble in active_player.list_marble:
                if marble.is_in_kennel():
                    marble.leave_kennel(action.pos_to, action.card.rank)
                    break

        elif action.is_movement_action():
            for marble in active_player.list_marble:
                if marble.pos == action.pos_from:
                    marble.move(action.pos_to - marble.pos, len(self.board_numbers))
                    break

        active_player.list_card.remove(action.card)
        self.state.list_id_card_discard.append(action.card)

    def get_player_view(self, idx_player: int) -> GameState:
        """Get the masked state for the active player (e.g., the opponent's cards are face down)."""
        if not self.state:
            raise ValueError("Game state is not initialized.")

        masked_state = self.state.copy(deep=True)
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card(suit="?", rank="?")] * len(player.list_card)

        return masked_state

    def check_game_finished(self) -> bool:
        """
        Check if any player has finished the game (all marbles are in the finish zone).
        Updates the game state accordingly.
        """
        if not self.state:
            raise ValueError("Game state is not initialized.")

        for player in self.state.list_player:  # Access list_player via self.state
            if all(marble.finished for marble in player.list_marble):
                print(f"Player {player.player_id} has won the game!")
                self.state.bool_game_finished = True
                return True
        return False

class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Action:
        """
        Given masked game state and possible actions, select the next action.

        Args:
            state (GameState): The current (masked) game state.
            actions (List[Action]): The list of possible actions.

        Returns:
            Action: A randomly selected action, or None if no actions are available.
        """
        if actions:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    # Create the game instance
    game = Dog()

    # Initialize the game state
    initial_state = GameState(cnt_player=4)
    initial_state.initialize_players(game.board)  # Pass board configuration

    # Set additional game state parameters
    initial_state.phase = GamePhase.RUNNING

    # Set the game state in the Dog game instance
    game.set_state(initial_state)

    # Create players
    players = [RandomPlayer() for _ in range(initial_state.cnt_player)]

    max_rounds = 100
    print(f"Game setup complete. Players: {len(players)}")
    for _ in range(max_rounds):
        state = game.get_state()

        # Check if the game is finished
        if state.bool_game_finished or game.check_game_finished():
            print("Game over!")
            break

        # Get actions for the active player
        actions = game.get_list_action()
        if not actions:
            print(f"No valid actions for Player {state.idx_player_active}. Skipping turn.")
            state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
            continue

        # Player selects an action
        selected_action = players[state.idx_player_active].select_action(state, actions)
        if selected_action:
            print(f"Player {state.idx_player_active} selected action: {selected_action}")
            game.apply_action(selected_action)
        else:
            print(f"Player {state.idx_player_active} skipped their turn.")

        # Move to the next player
        state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
        state.cnt_round += 1

        # Check for maximum round limit
        if state.cnt_round >= max_rounds:
            print("Max rounds reached. Ending game.")
            state.bool_game_finished = True
            break

    # Print the final state
    game.print_state()
    print("Game finished!")