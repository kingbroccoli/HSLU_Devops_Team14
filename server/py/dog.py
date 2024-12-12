# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: str       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from
    pos_to: Optional[int]      # position to move the marble to
    card_swap: Optional[Card]  # optional card to swap ()


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):

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

    cnt_player: int = 4                # number of players (must be 4)
    phase: GamePhase                   # current phase of the game
    cnt_round: int                     # current round
    bool_game_finished: bool           # true if game has finished
    bool_card_exchanged: bool          # true if cards was exchanged in round
    idx_player_started: int            # index of player that started the round
    idx_player_active: int             # index of active player in round
    list_player: List[PlayerState]     # list of players
    list_id_card_draw: List[Card]      # list of cards to draw
    list_id_card_discard: List[Card]   # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)


class Dog(Game):

    def __init__(self) -> None:
        """Game initialization."""
        # Shuffle the full card deck to create the draw pile
        shuffled_deck = random.sample(GameState.LIST_CARD, len(GameState.LIST_CARD))

        # Define the game board with positions
        self.board_numbers = range(0, 96)
        self.board = {
            "blue": {
                "kennel": self.board_numbers[64:68],
                "start": self.board_numbers[0],
                "finish": self.board_numbers[68:72],
            },
            "green": {
                "kennel": self.board_numbers[72:76],
                "start": self.board_numbers[16],
                "finish": self.board_numbers[76:80],
            },
            "red": {
                "kennel": self.board_numbers[80:84],
                "start": self.board_numbers[32],
                "finish": self.board_numbers[84:88],
            },
            "yellow": {
                "kennel": self.board_numbers[88:92],
                "start": self.board_numbers[48],
                "finish": self.board_numbers[92:96],
            },
        }

        # Initialize players and assign marbles based on the board configuration
        colors = ["blue", "green", "red", "yellow"]
        players = []
        for i, color in enumerate(colors):
            marbles = [
                Marble(pos=str(position), is_save=False)
                for position in self.board[color]["kennel"]
            ]
            players.append(PlayerState(name=f"Player {i + 1}", list_card=[], list_marble=marbles))

        # Define the initial game state
        initial_state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=1,  # Start with round 1
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=players,
            list_id_card_draw=shuffled_deck,
            list_id_card_discard=[],
            card_active=None
        )

        # Set the initial game state
        self.set_state(initial_state)

        # Initialize players and assign marbles based on the board configuration
        colors = ["blue", "green", "red", "yellow"]
        players = []
        for i, color in enumerate(colors):
            marbles = [
                Marble(pos=str(position), is_save=False)
                for position in self.board[color]["kennel"]
            ]
            players.append(PlayerState(name=f"Player {i + 1}", list_card=[], list_marble=marbles))

        # Update the game state with the initialized players
        self.state.list_player = players
        self.state.list_id_card_draw = shuffled_deck

    def deal_cards(self) -> None:
        """Deal cards to players based on the round count, continue until phase == FINISHED."""
        if self.state.phase == GamePhase.FINISHED:
            print("Game is finished. No more cards to deal.")
            return

        # Number of cards to deal per round
        cards_per_round = {1: 6, 2: 5, 3: 4, 4: 3, 5: 2}

        # Determine the round for card distribution
        effective_round = (self.state.cnt_round - 1) % 5 + 1  # Map to 1, 2, 3, 4, 5
        deal_count = cards_per_round.get(effective_round, 0)
        print(f"Dealing {deal_count} cards for Round {self.state.cnt_round} (Effective Round {effective_round}).")

        for player in self.state.list_player:
            # Check if enough cards are available in the draw pile
            if len(self.state.list_id_card_draw) < deal_count:
                print("Re-shuffling discard pile into draw pile.")
                self.state.list_id_card_draw.extend(self.state.list_id_card_discard)
                random.shuffle(self.state.list_id_card_draw)
                self.state.list_id_card_discard.clear()

            # Deal cards to the player
            dealt_cards = self.state.list_id_card_draw[:deal_count]
            self.state.list_id_card_draw = self.state.list_id_card_draw[deal_count:]
            player.list_card.extend(dealt_cards)

            print(f"Player {player.name} was dealt: {dealt_cards}")

        # Increment the overall round counter
        self.state.cnt_round += 1

    def set_state(self, state: GameState) -> None:
        """Set the game to a given state."""
        self.state = state
        # Debug statement
        print(f"Game state set: {self.state}")

    def get_state(self) -> GameState:
        """Get the complete, unmasked game state."""
        # Debug statement
        print(f"Getting state: {self.state}")
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        print(self.state)

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass

######## added part Beat

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        # Placeholder logic for possible actions
        active_player = self.state.list_player[self.state.idx_player_active]
        actions = []
        for card in active_player.list_card:
            for marble in active_player.list_marble:
                if marble.is_safe:
                    actions.append(Action(card=card, pos_from=marble.pos, pos_to=marble.pos + 1))
        return actions

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        active_player = self.state.list_player[self.state.idx_player_active]
        marble = next((m for m in active_player.list_marble if m.pos == action.pos_from), None)
        if not marble:
            print("Invalid action: Marble not found.")
            return

        if action.card.rank == '2':
            marble.move_forward(self.state, 2)
        elif action.card.rank == '3':
            marble.move_forward(self.state, 3)
        elif action.card.rank == '4':
            marble.move_forward(self.state, 4)
        elif action.card.rank == '5':
            marble.move_forward(self.state, 5)
        elif action.card.rank == '6':
            marble.move_forward(self.state, 6)
        elif action.card.rank == '7':
            marble.move_forward(self.state, 7)  # Simplified for now
        elif action.card.rank == '8':
            marble.move_forward(self.state, 8)
        elif action.card.rank == '9':
            marble.move_forward(self.state, 9)
        elif action.card.rank == '10':
            marble.move_forward(self.state, 10)
        elif action.card.rank == 'J':
            pass  # Implement swap logic
        elif action.card.rank == 'Q':
            marble.move_forward(self.state, 12)
        elif action.card.rank == 'K':
            marble.enter_play()
        elif action.card.rank == 'A':
            marble.move_forward(self.state, 1)  # Implement "1 or 11"
        elif action.card.rank == 'JKR':
            pass  # Implement Joker logic

#### Part Beat


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()
    # Fetch the initialized state
    game_state = game.get_state()

    # Test the number of players
    print("Number of Players:", len(game_state.list_player))
    for idx, player in enumerate(game_state.list_player):
        print(f"Player {idx + 1} Marbles:", player.list_marble)

    # Test the card deck
    print("\nNumber of Cards in Draw Pile:", len(game_state.list_id_card_draw))
    print("Sample Cards in Draw Pile:", game_state.list_id_card_draw[:5])  # Display first 5 cards

    # Test the board setup
    print("\nGame Board Configuration:")
    for color, positions in game.board.items():
        print(f"{color.capitalize()} Kennel: {positions['kennel']}")
        print(f"{color.capitalize()} Start: {positions['start']}")
        print(f"{color.capitalize()} Finish: {positions['finish']}")

    # Test phase and round
    print("\nInitial Game Phase:", game_state.phase)
    print("Initial Round Count:", game_state.cnt_round)

    # Start the game
    game.state.phase = GamePhase.RUNNING

    for _ in range(8):
        game.deal_cards()

    # Change the phase to FINISHED and test
    game.state.phase = GamePhase.FINISHED
    game.deal_cards()

