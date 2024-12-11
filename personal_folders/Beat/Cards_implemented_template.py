from typing import List, Optional, ClassVar
from pydantic import BaseModel
import random
from enum import Enum

class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank

    def execute(self, marble, board, *args, **kwargs):
        raise NotImplementedError("Card logic not implemented for base Card.")

class Marble(BaseModel):
    pos: int       # position on board (0 to 95)
    is_safe: bool  # true if marble was moved out of kennel and was not yet moved

    def move_forward(self, board, distance):
        self.pos = (self.pos + distance) % 96

    def move_backward(self, board, distance):
        self.pos = (self.pos - distance) % 96

    def enter_play(self):
        self.is_safe = True
        self.pos = 0

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
        # Cards as defined
        Card(suit=suit, rank=rank) for suit in GameState.LIST_SUIT for rank in GameState.LIST_RANK
    ] * 2

    cnt_player: int = 4                # number of players (must be 4)
    phase: GamePhase                   # current phase of the game
    cnt_round: int                     # current round
    bool_game_finished: bool           # true if game has finished
    bool_card_exchanged: bool          # true if cards were exchanged in round
    idx_player_started: int            # index of player that started the round
    idx_player_active: int             # index of active player in round
    list_player: List[PlayerState]     # list of players
    list_id_card_draw: List[Card]      # list of cards to draw
    list_id_card_discard: List[Card]   # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)

    def calculate_new_position(self, current_position, distance):
        return (current_position + distance) % 96

class Dog:

    def __init__(self) -> None:
        self.state = GameState(
            phase=GamePhase.SETUP,
            cnt_round=0,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[],
            list_id_card_draw=[],
            list_id_card_discard=[]
        )

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        print(self.state)

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

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the opponent's cards are face down)"""
        pass

class RandomPlayer:

    def select_action(self, state: GameState, actions: List[Action]) -> Action:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None

if __name__ == '__main__':
    # Test Setup
    marble1 = Marble(pos=0, is_safe=True)
    marble2 = Marble(pos=10, is_safe=True)

    player = PlayerState(
        name="Player 1",
        list_card=[
            Card(suit='♠', rank='2'),
            Card(suit='♥', rank='4'),
            Card(suit='♦', rank='A'),
            Card(suit='♣', rank='Q')
        ],
        list_marble=[marble1, marble2]
    )

    game = Dog()
    game.state.list_player = [player]
    game.state.idx_player_active = 0

    # Test each card
    actions = game.get_list_action()
    print("Possible actions:")
    for action in actions:
        print(action)

    print("\nApplying actions:")
    for action in actions:
        print(f"Applying action: {action}")
        game.apply_action(action)
        print(f"Marble positions after action: {[m.pos for m in player.list_marble]}\n")
