from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import random

from server.py.game import Game, Player



class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'

class Card(BaseModel):
    suit: str
    rank: str

class Marble(BaseModel):
    pos: int
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
        self._state: Optional[GameState] = None
        self.reset()

    def reset(self):
        LIST_SUIT = ['♠','♥','♦','♣']
        normal_ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        base_deck = [Card(suit=s, rank=r) for s in LIST_SUIT for r in normal_ranks]
        base_deck += [Card(suit='', rank='JKR')] * 3
        full_deck = base_deck * 2
        random.shuffle(full_deck)

        list_player = [
            PlayerState(
                name=f"Player {i+1}",
                list_card=[],
                list_marble=[Marble(pos=-1) for _ in range(4)]
            ) for i in range(4)
        ]

        for _ in range(6):
            for p in list_player:
                p.list_card.append(full_deck.pop())

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
        if self._state is None:
            raise ValueError("Game state has not been initialized.")
        return self._state

    def print_state(self) -> None:
        if self._state is None:
            print("No state to print. Initialize or reset the game.")
            return
        s = self._state
        print(f"Phase: {s.phase}, Round: {s.cnt_round}")
        print(f"Active Player: {s.idx_player_active}, Started Player: {s.idx_player_started}")
        for i, p in enumerate(s.list_player):
            cards_str = ", ".join([f"{c.rank}{c.suit}" for c in p.list_card])
            marbles_str = ", ".join([f"{m.pos}(save={m.is_save},laps={m.laps})" for m in p.list_marble])
            print(f"Player {i}: {p.name}, Cards: [{cards_str}], Marbles: [{marbles_str}]")
        print(f"Cards in draw pile: {len(s.list_id_card_draw)}, discard pile: {len(s.list_id_card_discard)}")

    def get_list_action(self) -> List[Action]:
        if self._state is None:
            raise ValueError("Game state has not been initialized.")

        state = self._state
        player = state.list_player[state.idx_player_active]
        actions = []

        if not state.bool_card_exchanged:
            for card in player.list_card:
                actions.append(Action(card=card, pos_from=-1, pos_to=-1))
            return actions

        for card in player.list_card:
            if card.rank == 'A':
                for marble in player.list_marble:
                    if marble.pos == -1:
                        actions.append(Action(card=card, pos_from=64, pos_to=0))

        return actions

    def apply_action(self, action: Optional[Action]) -> None:
        if self._state is None:
            raise ValueError("Game state has not been initialized.")

        state = self._state
        if action is None:
            state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
            return

        player = state.list_player[state.idx_player_active]

        if not state.bool_card_exchanged:
            state.bool_card_exchanged = True
            state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player
            return

        if action.pos_from == 64 and action.pos_to == 0:
            for marble in player.list_marble:
                if marble.pos == -1:
                    marble.pos = 0
                    marble.is_save = True
                    break
            state.list_id_card_discard.append(action.card)
            player.list_card.remove(action.card)
            state.idx_player_active = (state.idx_player_active + 1) % state.cnt_player

    def get_player_view(self, idx_player: int) -> GameState:
        if self._state is None:
            raise ValueError("Game state has not been initialized.")
        return self._state

class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None

if __name__ == '__main__':
    game = Dog()
    player = RandomPlayer()

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
