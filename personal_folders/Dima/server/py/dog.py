# dog.py
# from server.py.game import Game, Player
from game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel, field_validator
from enum import Enum
import random

LIST_SUIT = ['♠', '♥', '♦', '♣']
LIST_RANK = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', 'JKR']

class Card(BaseModel):
    suit: str  # card suit (color) or '' for Joker
    rank: str  # card rank (2,3,4,5,6,7,8,9,10,J,Q,K,A,JKR)


class Marble(BaseModel):
    pos: str       # position on board: '-1' for kennel, 'H' for home, or '0' to '95' for positions
    is_save: bool  # true if marble was moved out of kennel but not yet moved again


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from (if any)
    pos_to: Optional[int]      # position to move the marble to (if any)
    card_swap: Optional[Card]  # optional card to swap

    # Since Pydantic will handle parsing 'card' into a Card model if a dict is provided,
    # no additional field_validator is necessary.


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = LIST_SUIT
    LIST_RANK: ClassVar[List[str]] = LIST_RANK
    LIST_CARD: ClassVar[List[Card]] = (
        [Card(suit=s, rank=r) for s in LIST_SUIT for r in LIST_RANK if r != 'JKR'] +
        [Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')]
    ) * 2

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
        # Initialize with 4 players
        initial_players = []
        for i in range(4):
            player_state = PlayerState(
                name=f"Player {i+1}",
                list_card=[],
                list_marble=[
                    Marble(pos="-1", is_save=False),
                    Marble(pos="-1", is_save=False),
                    Marble(pos="-1", is_save=False),
                    Marble(pos="-1", is_save=False)
                ]
            )
            initial_players.append(player_state)

        deck = GameState.LIST_CARD.copy()
        random.shuffle(deck)

        self._state = GameState(
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=0,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=initial_players,
            list_id_card_draw=deck,
            list_id_card_discard=[],
            card_active=None
        )

        # Deal initial cards (for simplicity deal 5 cards each)
        self.deal_cards(5)

        # Exchange cards and start the game
        self.exchange_cards()
        self._state.phase = GamePhase.RUNNING

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
            marbles_str = ", ".join([f"pos={m.pos},save={m.is_save}" for m in p.list_marble])
            print(f"Player {i}: {p.name}, Cards: [{cards_str}], Marbles: [{marbles_str}]")
        print(f"Cards in draw pile: {len(s.list_id_card_draw)}, discard pile: {len(s.list_id_card_discard)}\n")

    def get_list_action(self) -> List[Action]:
        s = self._state
        if s.phase != GamePhase.RUNNING:
            return []
        active_player = s.list_player[s.idx_player_active]

        actions = []
        for card in active_player.list_card:
            possible_moves = self.get_moves_for_card(s.idx_player_active, card)
            for (pos_from, pos_to) in possible_moves:
                actions.append(Action(card=card, pos_from=pos_from, pos_to=pos_to, card_swap=None))
        return actions

    def apply_action(self, action: Action) -> None:
        s = self._state
        if s.phase != GamePhase.RUNNING:
            raise ValueError("Game is not running, cannot apply action.")

        if not self.is_action_valid(s.idx_player_active, action):
            raise ValueError("Invalid action")

        self.execute_move(s.idx_player_active, action)
        self.discard_card(s.idx_player_active, action.card)

        if self.check_win_condition():
            s.phase = GamePhase.FINISHED
            s.bool_game_finished = True
            return

        s.idx_player_active = (s.idx_player_active + 1) % s.cnt_player
        s.cnt_round += 1

        if all(len(p.list_card) == 0 for p in s.list_player):
            if len(s.list_id_card_draw) < 20:
                s.phase = GamePhase.FINISHED
                s.bool_game_finished = True
            else:
                self.deal_cards(5)
                self.exchange_cards()

    def get_player_view(self, idx_player: int) -> GameState:
        state_copy = self._state.copy(deep=True)
        # Mask other players' cards
        for i, p in enumerate(state_copy.list_player):
            if i != idx_player:
                p.list_card = [Card(suit="?", rank="?") for _ in p.list_card]
        return state_copy

    # ---------- Helper Methods ----------

    def deal_cards(self, num_cards: int):
        s = self._state
        for _ in range(num_cards):
            for p in s.list_player:
                if s.list_id_card_draw:
                    p.list_card.append(s.list_id_card_draw.pop())

    def exchange_cards(self):
        s = self._state
        if s.bool_card_exchanged:
            return
        if s.cnt_player != 4:
            return

        cards_to_pass = []
        for i, p in enumerate(s.list_player):
            if p.list_card:
                cards_to_pass.append((i, p.list_card.pop(0)))

        exchange_map = {0:2, 2:0, 1:3, 3:1}
        for (i, c) in cards_to_pass:
            partner = exchange_map[i]
            s.list_player[partner].list_card.append(c)
        s.bool_card_exchanged = True

    def check_win_condition(self) -> bool:
        s = self._state
        for p in s.list_player:
            if all(m.pos == 'H' for m in p.list_marble):
                return True
        return False

    def is_action_valid(self, idx_player: int, action: Action) -> bool:
        possible_actions = self.get_list_action()
        return any(a.card == action.card and a.pos_from == action.pos_from and a.pos_to == action.pos_to for a in possible_actions)

    def discard_card(self, idx_player: int, card: Card):
        s = self._state
        player = s.list_player[idx_player]
        for i, c in enumerate(player.list_card):
            if c.suit == card.suit and c.rank == card.rank:
                player.list_card.pop(i)
                break
        s.list_id_card_discard.append(card)

    def get_player_marble_positions(self, idx_player: int):
        s = self._state
        return [m.pos for m in s.list_player[idx_player].list_marble]

    def board_distance(self, start: int, steps: int) -> int:
        return (start + steps) % 96

    def find_marble_to_move(self, idx_player: int, pos_from: int):
        s = self._state
        for i, m in enumerate(s.list_player[idx_player].list_marble):
            if m.pos == str(pos_from):
                return i
        return None

    def execute_move(self, idx_player: int, action: Action):
        card = action.card
        rank = card.rank

        if rank in ['JKR', 'A', 'K', '4', '7', 'J']:
            # For special cards, logic is simplified in get_moves_for_card
            if rank == 'J':
                self.swap_marbles(idx_player, action.pos_from, action.pos_to)
            else:
                self.move_marble(idx_player, action.pos_from, action.pos_to)
        else:
            # Normal movement cards
            self.move_marble(idx_player, action.pos_from, action.pos_to)

        self.check_marble_home(idx_player)

    def check_marble_home(self, idx_player: int):
        # Placeholder for home logic
        pass

    def move_marble(self, idx_player: int, pos_from: int, pos_to: int):
        s = self._state
        player = s.list_player[idx_player]
        marble_idx = self.find_marble_to_move(idx_player, pos_from)
        if marble_idx is None:
            marble_idx = self.find_marble_in_kennel(idx_player)
            if marble_idx is None:
                return
        player.list_marble[marble_idx].pos = str(pos_to)
        player.list_marble[marble_idx].is_save = True
        self.handle_collision(pos_to, idx_player)

    def find_marble_in_kennel(self, idx_player: int):
        s = self._state
        for i, m in enumerate(s.list_player[idx_player].list_marble):
            if m.pos == '-1':
                return i
        return None

    def handle_collision(self, pos: int, current_player: int):
        s = self._state
        for p_idx, p_state in enumerate(s.list_player):
            if p_idx == current_player:
                continue
            for m in p_state.list_marble:
                if m.pos == str(pos):
                    # collision
                    m.pos = '-1'

    def swap_marbles(self, idx_player: int, pos_from: int, pos_to: int):
        s = self._state
        marble_idx_p = self.find_marble_to_move(idx_player, pos_from)
        if marble_idx_p is None:
            return
        for p_idx, p_state in enumerate(s.list_player):
            for m_idx, m in enumerate(p_state.list_marble):
                if m.pos == str(pos_to):
                    old_pos = s.list_player[idx_player].list_marble[marble_idx_p].pos
                    s.list_player[idx_player].list_marble[marble_idx_p].pos = m.pos
                    m.pos = old_pos
                    return

    from typing import List, Tuple

    def get_moves_for_card(self, idx_player: int, card: Card) -> List[Tuple[int, int]]:

        steps_map = {
            '2': 2, '3': 3, '5': 5, '6': 6, '8': 8, '9': 9, '10':10,
            'Q':12, 'K':13, 'A':1
        }
        s = self._state
        player = s.list_player[idx_player]
        moves = []

        if card.rank == 'JKR':
            for i, m in enumerate(player.list_marble):
                if m.pos.isdigit():
                    pos_from = int(m.pos)
                    pos_to = self.board_distance(pos_from, 1)
                    moves.append((pos_from, pos_to))
            kennel_idx = self.find_marble_in_kennel(idx_player)
            if kennel_idx is not None:
                start_pos = self.get_player_start_field(idx_player)
                moves.append((-1, start_pos))
            return moves

        if card.rank == 'A':
            kennel_idx = self.find_marble_in_kennel(idx_player)
            if kennel_idx is not None:
                start_pos = self.get_player_start_field(idx_player)
                moves.append((-1, start_pos))
            for i, m in enumerate(player.list_marble):
                if m.pos.isdigit():
                    pos_from = int(m.pos)
                    pos_to = self.board_distance(pos_from, 1)
                    moves.append((pos_from, pos_to))
            return moves

        if card.rank == 'K':
            kennel_idx = self.find_marble_in_kennel(idx_player)
            if kennel_idx is not None:
                start_pos = self.get_player_start_field(idx_player)
                moves.append((-1, start_pos))
            for i, m in enumerate(player.list_marble):
                if m.pos.isdigit():
                    pos_from = int(m.pos)
                    pos_to = self.board_distance(pos_from, 13)
                    moves.append((pos_from, pos_to))
            return moves

        if card.rank == '4':
            # move 4 steps backward
            for i, m in enumerate(player.list_marble):
                if m.pos.isdigit():
                    pos_from = int(m.pos)
                    pos_to = self.board_distance(pos_from, -4)
                    moves.append((pos_from, pos_to))
            return moves

        if card.rank == '7':
            # Just move 7 forward for simplicity
            for i, m in enumerate(player.list_marble):
                if m.pos.isdigit():
                    pos_from = int(m.pos)
                    pos_to = self.board_distance(pos_from, 7)
                    moves.append((pos_from, pos_to))
            return moves

        if card.rank == 'J':
            # swap with another marble
            your_marbles = [m for m in player.list_marble if m.pos.isdigit()]
            opp_positions = []
            for p_idx, p_state in enumerate(s.list_player):
                if p_idx != idx_player:
                    for m in p_state.list_marble:
                        if m.pos.isdigit():
                            opp_positions.append(int(m.pos))
            for ym in your_marbles:
                if ym.pos.isdigit():
                    pos_from = int(ym.pos)
                    for opp in opp_positions:
                        moves.append((pos_from, opp))
            return moves

        # Normal moves:
        steps = steps_map.get(card.rank, 0)
        for i, m in enumerate(player.list_marble):
            if m.pos.isdigit():
                pos_from = int(m.pos)
                pos_to = self.board_distance(pos_from, steps)
                moves.append((pos_from, pos_to))

        return moves

    def get_player_start_field(self, idx_player: int) -> int:
        # Arbitrary start positions
        return idx_player * 24


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    game = Dog()
    game.print_state()

    player = RandomPlayer()

    while game.get_state().phase != GamePhase.FINISHED:
        actions = game.get_list_action()
        if not actions:
            print("No actions left, game ends!")
            break
        view = game.get_player_view(game.get_state().idx_player_active)
        action = player.select_action(view, actions)
        game.apply_action(action)
        game.print_state()

    print("Game finished!")
