# -runcmd: cd ../.. & venv\Scripts\python server/py/uno.py
# runcmd: cd ../.. & venv\Scripts\python benchmark/benchmark_uno.py python uno.Uno

from server.py.game import Game, Player
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import random


class Card(BaseModel):
    color: Optional[str] = None   # color of the card (see LIST_COLOR)
    number: Optional[int] = None  # number of the card (if not a symbol card)
    symbol: Optional[str] = None  # special cards (see LIST_SYMBOL)


class Action(BaseModel):
    card: Optional[Card] = None  # the card to play
    color: Optional[str] = None  # the chosen color to play (for wild cards)
    draw: Optional[int] = None   # the number of cards to draw for the next player
    uno: bool = False            # true to announce "UNO" with the second last card


class PlayerState(BaseModel):
    name: Optional[str] = None
    list_card: List[Card] = []


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class GameState(BaseModel):
    # constants
    CNT_HAND_CARDS: int = 7
    LIST_COLOR: List[str] = ['red', 'green', 'yellow', 'blue', 'any']
    LIST_SYMBOL: List[str] = ['skip', 'reverse', 'draw2', 'wild', 'wilddraw4']

    # total deck definition is not strictly needed, we handle in code
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
        # Fill missing fields with defaults
        # The tests create states with minimal info, we must fill the rest
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

        # If CNT_HAND_CARDS not changed, it should remain 7, no problem.

        # If phase=setup, we do setup
        if self.state.phase == GamePhase.SETUP:
            # Ensure correct number of players if not set
            if len(self.state.list_player) < self.state.cnt_player:
                self.state.list_player = [PlayerState(name=f"Player{i+1}", list_card=[]) for i in range(self.state.cnt_player)]

            # If list_card_draw empty, create a full deck
            if len(self.state.list_card_draw) == 0:
                self.state.list_card_draw = self._create_full_deck()
                random.shuffle(self.state.list_card_draw)

            # Deal cards if they don't have 7 cards yet
            for p in self.state.list_player:
                if len(p.list_card) < self.state.CNT_HAND_CARDS:
                    needed = self.state.CNT_HAND_CARDS - len(p.list_card)
                    self._draw_cards(p, needed)

            # If discard empty, flip starting card
            if len(self.state.list_card_discard) == 0:
                self._flip_starting_card()

            if self.state.idx_player_active is None:
                # choose random player
                if self.state.cnt_player > 0:
                    self.state.idx_player_active = random.randint(0, self.state.cnt_player - 1)
                else:
                    self.state.idx_player_active = 0

            # Apply start card rules
            self._apply_start_card_rules()

            # Now phase is running
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

        # If game finished, no actions
        if self.state.phase == GamePhase.FINISHED:
            return []

        top_card = self._get_top_discard()

        # If must draw due to special cards
        if self.state.cnt_to_draw > 0:
            # The only action is to draw cnt_to_draw cards
            return [Action(draw=self.state.cnt_to_draw)]

        # If normal turn and not forced draw
        playable = self._get_playable_cards(player.list_card, top_card, self.state.color)
        actions = []

        hand_count = len(player.list_card)
        for c in playable:
            if c.symbol in ['wild', 'wilddraw4']:
                possible_colors = [col for col in self.state.LIST_COLOR if col != 'any']
                draw_count = 4 if c.symbol == 'wilddraw4' else None
                for col in possible_colors:
                    if hand_count == 2:
                        actions.append(Action(card=c, color=col, draw=draw_count))
                        actions.append(Action(card=c, color=col, draw=draw_count, uno=True))
                    else:
                        actions.append(Action(card=c, color=col, draw=draw_count))
            else:
                draw_for_next = self._calc_draw_for_card(c)
                if hand_count == 2:
                    actions.append(Action(card=c, color=c.color, draw=draw_for_next))
                    actions.append(Action(card=c, color=c.color, draw=draw_for_next, uno=True))
                else:
                    actions.append(Action(card=c, color=c.color, draw=draw_for_next))

        # Player can always choose to draw one card if no forced draw is pending
        # (unless forced draw is pending, which we handled above)
        actions.append(Action(draw=1))

        return actions

    def apply_action(self, action: Action) -> None:
        if self.state.phase != GamePhase.RUNNING:
            return

        idx = self.state.idx_player_active
        player = self.state.list_player[idx]

        if action.draw is not None:
            # Drawing cards
            n = action.draw
            self._draw_cards(player, n)
            if n in [2,4]:
                # forced draw from draw2 or wilddraw4
                self.state.cnt_to_draw = 0
                # after forced draw in 2 player game, turn returns to player who caused it
                if self.state.cnt_player == 2:
                    # revert turn to previous player
                    self.state.idx_player_active = (idx - self.state.direction) % self.state.cnt_player
                else:
                    # normal rotate after forced draw
                    self._advance_turn()
            else:
                # normal draw of 1 card
                # player now has drawn card, can potentially play it
                # has_drawn = True means if they don't play now, turn passes next call
                self.state.has_drawn = True
            return

        if action.card is not None:
            # playing a card
            card_to_play = self._find_card_in_hand(player, action.card)
            if card_to_play is None:
                # invalid action?
                return

            had_two_cards = (len(player.list_card) == 2)
            player.list_card.remove(card_to_play)

            # set color if wild
            if card_to_play.symbol in ['wild', 'wilddraw4']:
                self.state.color = action.color
            else:
                # use card color unless it's 'any'
                if card_to_play.color != 'any':
                    self.state.color = card_to_play.color

            self.state.list_card_discard.append(card_to_play)
            self.state.has_drawn = False

            # Apply card effects
            if card_to_play.symbol == 'skip':
                if self.state.cnt_player == 2:
                    # skip acts like immediate extra turn for you
                    # do nothing, same player continues
                    pass
                else:
                    # skip next player
                    self._advance_turn()
                    self._advance_turn()
            elif card_to_play.symbol == 'reverse':
                if self.state.cnt_player == 2:
                    # acts like skip in 2 player game
                    # same player continues
                    pass
                else:
                    self.state.direction = -self.state.direction
                    self._advance_turn()
            elif card_to_play.symbol == 'draw2':
                self.state.cnt_to_draw += 2
                if self.state.cnt_player == 2:
                    self._advance_turn()  # next player draws2 and we come back
                else:
                    self._advance_turn()
            elif card_to_play.symbol == 'wilddraw4':
                self.state.cnt_to_draw += 4
                if self.state.cnt_player == 2:
                    self._advance_turn()
                else:
                    self._advance_turn()
            else:
                # normal or wild card
                self._advance_turn()

            # Check if player finished their cards => game ends
            if len(player.list_card) == 0:
                self.state.phase = GamePhase.FINISHED
                self.state.idx_player_active = idx
                return

            # UNO penalty if had two cards and didn't say UNO
            if had_two_cards and not action.uno:
                # draw 4 penalty
                self._draw_cards(player, 4)

    def get_player_view(self, idx_player: int) -> GameState:
        # mask opponents cards
        masked_state = self._copy_state()
        for i, p in enumerate(masked_state.list_player):
            if i != idx_player:
                p.list_card = [Card() for _ in p.list_card]
        return masked_state

    # ---------------- Internal helper methods ----------------

    def _create_full_deck(self) -> List[Card]:
        colors = ['red', 'green', 'yellow', 'blue']
        deck = []
        # 0 cards: one of each color
        for c in colors:
            deck.append(Card(color=c, number=0))
        # 1-9 twice each color
        for c in colors:
            for num in range(1,10):
                deck.append(Card(color=c, number=num))
                deck.append(Card(color=c, number=num))
        # skip, reverse, draw2 each twice per color
        for c in colors:
            deck.append(Card(color=c, symbol='skip'))
            deck.append(Card(color=c, symbol='skip'))
            deck.append(Card(color=c, symbol='reverse'))
            deck.append(Card(color=c, symbol='reverse'))
            deck.append(Card(color=c, symbol='draw2'))
            deck.append(Card(color=c, symbol='draw2'))
        # wild, wilddraw4 4 each
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
        # draw until we get a non-wilddraw4 card
        tries = 0
        while True:
            if len(self.state.list_card_draw) == 0:
                self._reshuffle_discard_into_draw()
            if len(self.state.list_card_draw) == 0:
                break
            card = self.state.list_card_draw.pop()
            if card.symbol == 'wilddraw4':
                # put it at the bottom and continue
                self.state.list_card_draw.insert(0, card)
                tries += 1
                if tries > 200: # safeguard
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

        # If symbol on first card has special effect
        # skip: skip first player
        # reverse: if more than 2 players, just reverse direction. if 2 players, skip first player
        # draw2: first player must draw2
        # wild: first player chooses color and plays normally
        # wilddraw4: shouldn't appear at start (we handled that)

        if top_card.symbol == 'skip':
            # skip first player
            self._advance_turn()
        elif top_card.symbol == 'reverse':
            if self.state.cnt_player == 2:
                # acts like skip
                self._advance_turn()
            else:
                self.state.direction = -1
        elif top_card.symbol == 'draw2':
            # first player must draw2
            self.state.cnt_to_draw = 2
        elif top_card.symbol == 'wild':
            # just means first player chooses color next action
            # no immediate effect needed
            pass
        # wilddraw4 never at start by construction

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
                # wilddraw4 only if no card of top_color (if top_color != 'any')
                if c.symbol == 'wilddraw4' and top_color != 'any':
                    if any((cc.color == top_color and cc.color != 'any') for cc in hand if cc != c):
                        continue
                playable.append(c)
            else:
                # must match color or number/symbol
                if top_color == 'any':
                    # any card playable
                    playable.append(c)
                else:
                    same_color = (c.color == top_color)
                    same_number = (c.number is not None and c.number == top_number)
                    same_symbol = (c.symbol is not None and c.symbol == top_symbol)
                    if same_color or same_number or same_symbol:
                        playable.append(c)
        return playable

    def _calc_draw_for_card(self, card: Card) -> Optional[int]:
        # If stacking draw2 on top of another draw, it accumulates
        if card.symbol == 'draw2':
            return self.state.cnt_to_draw + 2 if self.state.cnt_to_draw > 0 else 2
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
