from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import random
from game import Game, Player

# from server.py.game import Game, Player

class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'

class Card(BaseModel):
    suit: str
    rank: str

class Marble(BaseModel):
    pos: str
    is_save: bool = False
    laps: int = 0
    steps: int = 0

class PlayerState(BaseModel):
    name: str
    list_card: List[Card]
    list_marble: List[Marble]

class Action(BaseModel):
    card: Card
    pos_from: Optional[int] = None
    pos_to: Optional[int] = None
    card_swap: Optional[Card] = None

class GameState(BaseModel):
    cnt_player: int
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

class Dog(Game):

    def __init__(self) -> None:
        self.reset()

    def reset(self):
        # Create a 110-card deck: 2 Bridge decks of 55 cards each
        LIST_SUIT = ['♠','♥','♦','♣']
        normal_ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        base_deck = []
        for s in LIST_SUIT:
            for r in normal_ranks:
                base_deck.append(Card(suit=s, rank=r))
        # 3 Jokers per deck
        for _ in range(3):
            base_deck.append(Card(suit='', rank='JKR'))
        # Double it for two decks = 110 cards total
        full_deck = base_deck * 2
        random.shuffle(full_deck)

        # Create players
        list_player = []
        for i in range(4):
            marbles = [Marble(pos='-1') for _ in range(4)]
            list_player.append(
                PlayerState(
                    name=f"Player {i+1}",
                    list_card=[],
                    list_marble=marbles
                )
            )

        # Deal 6 cards each (24 cards dealt)
        for _ in range(6):
            for p in list_player:
                p.list_card.append(full_deck.pop())

        # After dealing, 110-24=86 cards left in draw pile
        self._state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=list_player,
            list_id_card_draw=full_deck,
            list_id_card_discard=[],
            card_active=None
        )

    def set_state(self, state: GameState) -> None:
        self._state = state

    def get_state(self) -> GameState:
        return self._state

    def print_state(self) -> None:
        s = self._state
        print(f"Phase: {s.phase}, Round: {s.cnt_round}")
        print(f"Active Player: {s.idx_player_active}, Started Player: {s.idx_player_started}")
        for i, p in enumerate(s.list_player):
            cards_str = ", ".join([f"{c.rank}{c.suit}" for c in p.list_card])
            marbles_str = ", ".join([f"{m.pos}(save={m.is_save},laps={m.laps})" for m in p.list_marble])
            print(f"Player {i}: {p.name}, Cards: [{cards_str}], Marbles: [{marbles_str}]")
        print(f"Cards in draw pile: {len(s.list_id_card_draw)}, discard pile: {len(s.list_id_card_discard)}")

    def get_list_action(self) -> List[Action]:
        # Initially return empty. The benchmark will test initial conditions first.
        return []

    def apply_action(self, action: Optional[Action]) -> None:
        # If action is None or any action is given, do nothing for now.
        pass

    def get_player_view(self, idx_player: int) -> GameState:
        # Return full state without masking for now.
        return self._state

class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None

if __name__ == '__main__':
    game = Dog()
    player = RandomPlayer()

    # A simple loop to show that main works. This will end immediately since no actions.
    while game.get_state().phase != GamePhase.FINISHED:
        game.print_state()
        actions = game.get_list_action()
        if not actions:
            print("No actions left, game ends!")
            break
        action = player.select_action(game.get_player_view(game.get_state().idx_player_active), actions)
        if action:
            game.apply_action(action)
        else:
            print("No action chosen, folding.")
            break

    print("Game finished!")
