# -runcmd: cd ../.. & venv\Scripts\python server/py/uno.py
# runcmd: cd ../.. & venv\Scripts\python benchmark/benchmark_uno.py python uno.Uno

from server.py.game import Game, Player
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import random


class Card(BaseModel):
    color: Optional[str] = None
    number: Optional[int] = None
    symbol: Optional[str] = None


class Action(BaseModel):
    card: Optional[Card] = None
    color: Optional[str] = None
    draw: Optional[int] = None
    uno: bool = False

    def __eq__(self, other):
        if not isinstance(other, Action):
            return False
        return (self._sort_key() == other._sort_key())

    def __lt__(self, other):
        if not isinstance(other, Action):
            return False
        return (self._sort_key() < other._sort_key())

    def _sort_key(self):
        # Create a tuple that can be compared
        # card fields
        c_color = self.card.color if self.card and self.card.color is not None else ''
        c_number = self.card.number if self.card and self.card.number is not None else -1
        c_symbol = self.card.symbol if self.card and self.card.symbol is not None else ''
        # chosen color
        chosen_color = self.color if self.color else ''
        draw = self.draw if self.draw is not None else -1
        uno = 1 if self.uno else 0
        return (c_color, c_number, c_symbol, chosen_color, draw, uno)


class PlayerState(BaseModel):
    name: Optional[str] = None
    list_card: List[Card] = []


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class GameState(BaseModel):
    CNT_HAND_CARDS: int = 7
    LIST_COLOR: List[str] = ['red', 'green', 'yellow', 'blue', 'any']
    LIST_SYMBOL: List[str] = ['skip', 'reverse', 'draw2', 'wild', 'wilddraw4']
    LIST_CARD: List[Card] = [
        Card(color='red', number=0), Card(color='green', number=0), Card(color='yellow', number=0), Card(color='blue', number=0),
        Card(color='red', number=1), Card(color='green', number=1), Card(color='yellow', number=1), Card(color='blue', number=1),
        Card(color='red', number=2), Card(color='green', number=2), Card(color='yellow', number=2), Card(color='blue', number=2),
        Card(color='red', number=3), Card(color='green', number=3), Card(color='yellow', number=3), Card(color='blue', number=3),
        Card(color='red', number=4), Card(color='green', number=4), Card(color='yellow', number=4), Card(color='blue', number=4),
        Card(color='red', number=5), Card(color='green', number=5), Card(color='yellow', number=5), Card(color='blue', number=5),
        Card(color='red', number=6), Card(color='green', number=6), Card(color='yellow', number=6), Card(color='blue', number=6),
        Card(color='red', number=7), Card(color='green', number=7), Card(color='yellow', number=7), Card(color='blue', number=7),
        Card(color='red', number=8), Card(color='green', number=8), Card(color='yellow', number=8), Card(color='blue', number=8),
        Card(color='red', number=9), Card(color='green', number=9), Card(color='yellow', number=9), Card(color='blue', number=9),
        Card(color='red', symbol='skip'), Card(color='green', symbol='skip'), Card(color='yellow', symbol='skip'), Card(color='blue', symbol='skip'),
        Card(color='red', symbol='reverse'), Card(color='green', symbol='reverse'), Card(color='yellow', symbol='reverse'), Card(color='blue', symbol='reverse'),
        Card(color='red', symbol='draw2'), Card(color='green', symbol='draw2'), Card(color='yellow', symbol='draw2'), Card(color='blue', symbol='draw2'),
        Card(color='any', symbol='wild'), Card(color='any', symbol='wild'),
        Card(color='any', symbol='wilddraw4'), Card(color='any', symbol='wilddraw4')
    ]

    list_card_draw: Optional[List[Card]] = None
    list_card_discard: Optional[List[Card]] = None
    list_player: Optional[List[PlayerState]] = None
    phase: Optional[GamePhase] = None
    cnt_player: int
    idx_player_active: Optional[int] = None
    direction: Optional[int] = None
    color: Optional[str] = None
    cnt_to_draw: Optional[int] = None
    has_drawn: Optional[bool] = None


class Uno(Game):
    def __init__(self) -> None:
        self.state = GameState(cnt_player=0)

    def set_state(self, state: GameState) -> None:
        self.state = state

        if self.state.phase is None:
            self.state.phase = GamePhase.SETUP
        if self.state.list_card_draw is None:
            self.state.list_card_draw = []
        if self.state.list_card_discard is None:
            self.state.list_card_discard = []
        if self.state.list_player is None:
            self.state.list_player = []
        if self.state.direction is None:
            self.state.direction = 1
        if self.state.color is None:
            self.state.color = 'any'
        if self.state.cnt_to_draw is None:
            self.state.cnt_to_draw = 0
        if self.state.has_drawn is None:
            self.state.has_drawn = False

        if self.state.phase == GamePhase.SETUP:
            if len(self.state.list_player) < self.state.cnt_player:
                self.state.list_player = [PlayerState(name=f"Player{i+1}", list_card=[]) for i in range(self.state.cnt_player)]

            if len(self.state.list_card_draw) == 0:
                self.state.list_card_draw = self._create_full_deck()
                random.shuffle(self.state.list_card_draw)

            for p in self.state.list_player:
                if len(p.list_card) < self.state.CNT_HAND_CARDS:
                    needed = self.state.CNT_HAND_CARDS - len(p.list_card)
                    self._draw_cards(p, needed)

            if len(self.state.list_card_discard) == 0:
                self._flip_starting_card()

            if self.state.idx_player_active is None:
                if self.state.cnt_player > 0:
                    self.state.idx_player_active = random.randint(0, self.state.cnt_player - 1)
                else:
                    self.state.idx_player_active = 0

            self._apply_start_card_rules()

            self.state.phase = GamePhase.RUNNING

    def get_state(self) -> GameState:
        return self.state

    def print_state(self) -> None:
        print("phase:", self.state.phase)
        print("active player idx:", self.state.idx_player_active)
        print("direction:", self.state.direction)
        print("color:", self.state.color)
        print("cnt_to_draw:", self.state.cnt_to_draw)
        if len(self.state.list_card_discard) > 0:
            print("top discard:", self.state.list_card_discard[-1])
        for i, p in enumerate(self.state.list_player):
            print(f"player {i}: {p.name}, cards: {len(p.list_card)}")

    def get_list_action(self) -> List[Action]:
        if self.state.phase != GamePhase.RUNNING:
            return []

        idx = self.state.idx_player_active
        player = self.state.list_player[idx]

        if self.state.phase == GamePhase.FINISHED:
            return []

        top_card = self._get_top_discard()

        # If stacking scenario (cnt_to_draw>0), can either draw or stack a draw card
        if self.state.cnt_to_draw > 0:
            # Player must either draw the cnt_to_draw cards or stack another draw card
            actions = []
            # find draw2 or wilddraw4 in hand to stack
            draw_stack_cards = [c for c in player.list_card if c.symbol in ['draw2', 'wilddraw4']]
            # For each possible stack card
            for c in draw_stack_cards:
                # If playing draw2: new draw = cnt_to_draw + 2
                # If playing wilddraw4: new draw = cnt_to_draw + 4
                draw_value = self.state.cnt_to_draw + (4 if c.symbol == 'wilddraw4' else 2)
                if c.symbol == 'wilddraw4':
                    # choose any color except 'any'
                    for col in ['red', 'green', 'yellow', 'blue']:
                        actions.append(Action(card=c, color=col, draw=draw_value))
                else:
                    # draw2 color must be card's color
                    # We do not need color choice for draw2. Just use c.color
                    actions.append(Action(card=c, color=c.color, draw=draw_value))
            # Always add the option to just draw
            actions.append(Action(draw=self.state.cnt_to_draw))
            return actions

        # Normal scenario (cnt_to_draw=0)
        playable = self._get_playable_cards(player.list_card, top_card, self.state.color)
        actions = []
        hand_count = len(player.list_card)
        for c in playable:
            draw_for_next = self._calc_draw_for_card(c)
            if c.symbol in ['wild', 'wilddraw4']:
                possible_colors = ['red', 'green', 'yellow', 'blue']
                for col in possible_colors:
                    if hand_count == 2:
                        actions.append(Action(card=c, color=col, draw=draw_for_next))
                        actions.append(Action(card=c, color=col, draw=draw_for_next, uno=True))
                    else:
                        actions.append(Action(card=c, color=col, draw=draw_for_next))
            else:
                if hand_count == 2:
                    actions.append(Action(card=c, color=c.color, draw=draw_for_next))
                    actions.append(Action(card=c, color=c.color, draw=draw_for_next, uno=True))
                else:
                    actions.append(Action(card=c, color=c.color, draw=draw_for_next))

        # Can also choose to draw 1 card
        actions.append(Action(draw=1))
        return actions

    def apply_action(self, action: Action) -> None:
        if self.state.phase != GamePhase.RUNNING:
            return

        idx = self.state.idx_player_active
        player = self.state.list_player[idx]

        if action.draw is not None:
            n = action.draw
            self._draw_cards(player, n)
            if n in [2,4]:
                # forced draw from previous player
                self.state.cnt_to_draw = 0
                if self.state.cnt_player == 2:
                    # return turn to previous player
                    self.state.idx_player_active = (idx - self.state.direction) % self.state.cnt_player
                else:
                    self._advance_turn()
            else:
                # normal draw of 1 card
                self.state.has_drawn = True
            return

        if action.card is not None:
            card_to_play = self._find_card_in_hand(player, action.card)
            if card_to_play is None:
                return

            had_two_cards = (len(player.list_card) == 2)
            player.list_card.remove(card_to_play)

            # set color if wild
            if card_to_play.symbol in ['wild', 'wilddraw4']:
                self.state.color = action.color
            else:
                if card_to_play.color != 'any':
                    self.state.color = card_to_play.color

            self.state.list_card_discard.append(card_to_play)
            self.state.has_drawn = False

            if card_to_play.symbol == 'skip':
                # at start of turn normal skip:
                if self.state.cnt_player == 2:
                    # skip acts like immediate next turn to same player
                    pass
                else:
                    self._advance_turn()
                    self._advance_turn()
            elif card_to_play.symbol == 'reverse':
                # always direction = -self.direction in normal play
                # for 2 player it's skip effect (but from instructions we implemented in get_list_action)
                # The rules say in normal play reverse flips direction
                if self.state.cnt_player == 2:
                    # acts like skip, same player continues
                    pass
                else:
                    self.state.direction = -self.state.direction
                    self._advance_turn()
            elif card_to_play.symbol == 'draw2':
                self.state.cnt_to_draw += 2
                if self.state.cnt_player == 2:
                    self._advance_turn()
                else:
                    self._advance_turn()
            elif card_to_play.symbol == 'wilddraw4':
                self.state.cnt_to_draw += 4
                if self.state.cnt_player == 2:
                    self._advance_turn()
                else:
                    self._advance_turn()
            else:
                self._advance_turn()

            if len(player.list_card) == 0:
                self.state.phase = GamePhase.FINISHED
                self.state.idx_player_active = idx
                return

            if had_two_cards and not action.uno:
                self._draw_cards(player, 4)

    def get_player_view(self, idx_player: int) -> GameState:
        masked_state = self._copy_state()
        for i, p in enumerate(masked_state.list_player):
            if i != idx_player:
                p.list_card = [Card() for _ in p.list_card]
        return masked_state

    def _create_full_deck(self) -> List[Card]:
        colors = ['red', 'green', 'yellow', 'blue']
        deck = []
        for c in colors:
            deck.append(Card(color=c, number=0))
        for c in colors:
            for num in range(1,10):
                deck.append(Card(color=c, number=num))
                deck.append(Card(color=c, number=num))
        for c in colors:
            deck.append(Card(color=c, symbol='skip'))
            deck.append(Card(color=c, symbol='skip'))
            deck.append(Card(color=c, symbol='reverse'))
            deck.append(Card(color=c, symbol='reverse'))
            deck.append(Card(color=c, symbol='draw2'))
            deck.append(Card(color=c, symbol='draw2'))
        for _ in range(4):
            deck.append(Card(color='any', symbol='wild'))
        for _ in range(4):
            deck.append(Card(color='any', symbol='wilddraw4'))
        return deck

    def _draw_cards(self, player: PlayerState, n: int):
        for _ in range(n):
            if len(self.state.list_card_draw) == 0:
                self._reshuffle_discard_into_draw()
            if len(self.state.list_card_draw) == 0:
                break
            c = self.state.list_card_draw.pop()
            player.list_card.append(c)

    def _reshuffle_discard_into_draw(self):
        if len(self.state.list_card_discard) > 1:
            top = self.state.list_card_discard.pop()
            self.state.list_card_draw = self.state.list_card_discard[:]
            self.state.list_card_discard = [top]
            random.shuffle(self.state.list_card_draw)

    def _flip_starting_card(self):
        tries = 0
        while True:
            if len(self.state.list_card_draw) == 0:
                self._reshuffle_discard_into_draw()
            if len(self.state.list_card_draw) == 0:
                break
            card = self.state.list_card_draw.pop()
            if card.symbol == 'wilddraw4':
                self.state.list_card_draw.insert(0, card)
                tries += 1
                if tries > 200:
                    break
            else:
                self.state.list_card_discard.append(card)
                if card.color != 'any':
                    self.state.color = card.color
                break

    def _apply_start_card_rules(self):
        top_card = self._get_top_discard()
        if top_card is None:
            return

        if top_card.symbol == 'skip':
            self._advance_turn()
        elif top_card.symbol == 'reverse':
            # According to test_008, direction should be -1 at start
            self.state.direction = -1
        elif top_card.symbol == 'draw2':
            self.state.cnt_to_draw = 2
        elif top_card.symbol == 'wild':
            # no immediate effect needed
            pass

    def _advance_turn(self):
        self.state.idx_player_active = (self.state.idx_player_active + self.state.direction) % self.state.cnt_player
        self.state.has_drawn = False

    def _get_top_discard(self):
        if len(self.state.list_card_discard) == 0:
            return None
        return self.state.list_card_discard[-1]

    def _get_playable_cards(self, hand: List[Card], top_card: Card, current_color: str) -> List[Card]:
        if top_card is None:
            return hand[:]

        playable = []
        top_color = current_color
        top_number = top_card.number
        top_symbol = top_card.symbol

        for c in hand:
            if c.symbol in ['wild', 'wilddraw4']:
                # wild always playable
                # wilddraw4 playable only if no card of top_color in hand (if top_color != 'any')
                if c.symbol == 'wilddraw4' and top_color != 'any':
                    if any((cc.color == top_color and cc.symbol not in ['wild','wilddraw4']) for cc in hand if cc != c):
                        continue
                playable.append(c)
            else:
                same_color = (c.color == top_color)
                same_number = (c.number is not None and c.number == top_number)
                same_symbol = (c.symbol is not None and c.symbol == top_symbol)
                if top_color == 'any':
                    # any card playable if no other restriction
                    playable.append(c)
                else:
                    if same_color or same_number or same_symbol:
                        playable.append(c)
        return playable

    def _calc_draw_for_card(self, card: Card) -> Optional[int]:
        if card.symbol == 'draw2':
            return 2 if self.state.cnt_to_draw == 0 else self.state.cnt_to_draw+2
        if card.symbol == 'wilddraw4':
            return 4
        return None

    def _find_card_in_hand(self, player: PlayerState, card: Card) -> Optional[Card]:
        for c in player.list_card:
            if c.color == card.color and c.number == card.number and c.symbol == card.symbol:
                return c
        return None

    def _copy_state(self) -> GameState:
        import copy
        return copy.deepcopy(self.state)


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    uno = Uno()
    state = GameState(cnt_player=3)
    uno.set_state(state)
