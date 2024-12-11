from typing import List, Optional, ClassVar
from pydantic import BaseModel, ValidationError
import random
from enum import Enum

class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: int  # position on board (0 to 95)
    is_safe: bool  # true if marble was moved out of the kennel and not yet moved

    def move_forward(self, board, distance: int):
        self.pos = (self.pos + distance) % 96

    def move_backward(self, board, distance: int):
        self.pos = (self.pos - distance) % 96

    def enter_play(self):
        self.is_safe = True
        self.pos = 0


class PlayerState(BaseModel):
    name: str
    list_card: List[Card]
    list_marble: List[Marble]


class Action(BaseModel):
    card: Card
    pos_from: Optional[int]
    pos_to: Optional[int]
    card_swap: Optional[Card]


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
                                          Card(suit=suit, rank=rank) for suit in LIST_SUIT for rank in LIST_RANK
                                      ] * 2

    cnt_player: int = 4
    phase: GamePhase
    cnt_round: int
    bool_game_finished: bool
    bool_card_exchanged: bool
    idx_player_started: int
    idx_player_active: int
    list_player: List[PlayerState]
    list_id_card_draw: List[Card]
    list_id_card_discard: List[Card]
    card_active: Optional[Card]

    def calculate_new_position(self, current_position: int, distance: int):
        return (current_position + distance) % 96


class Dog:
    def __init__(self):
        self.state = GameState(
            phase=GamePhase.SETUP,
            cnt_round=0,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[],
            list_id_card_draw=GameState.LIST_CARD.copy(),
            list_id_card_discard=[]
        )

    def set_state(self, state: GameState):
        self.state = state

    def get_state(self) -> GameState:
        return self.state

    def get_list_action(self) -> List[Action]:
        player = self.state.list_player[self.state.idx_player_active]
        actions = []
        for card in player.list_card:
            for marble in player.list_marble:
                if marble.is_safe:
                    actions.append(Action(card=card, pos_from=marble.pos, pos_to=(marble.pos + 1) % 96))
        return actions

    def apply_action(self, action: Action):
        try:
            player = self.state.list_player[self.state.idx_player_active]
            marble = next((m for m in player.list_marble if m.pos == action.pos_from), None)
            if marble and action.card.rank.isdigit():
                distance = int(action.card.rank)
                marble.move_forward(None, distance)
            elif marble and action.card.rank == 'J':
                # Swap logic placeholder
                pass
            elif marble and action.card.rank == 'Q':
                marble.move_forward(None, 12)
            elif marble and action.card.rank == 'K':
                marble.enter_play()
            elif marble and action.card.rank == 'A':
                marble.move_forward(None, 1)
            elif marble and action.card.rank == 'JKR':
                # Joker logic placeholder
                pass
            else:
                raise ValueError("Invalid card rank")

            print(f"Marble positions after action: {[m.pos for m in player.list_marble]}")
        except ValueError as e:
            print(f"Error applying action: {e}")


if __name__ == "__main__":
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

    actions = game.get_list_action()
    print("Possible actions:")
    for action in actions:
        print(action)

    print("\nApplying actions:")
    for action in actions:
        try:
            print(f"Applying action: {action}")
            game.apply_action(action)
        except ValueError as e:
            print(f"Error applying action: {e}")
