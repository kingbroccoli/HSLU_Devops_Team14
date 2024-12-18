from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random
import copy


class Card(BaseModel):
    suit: str
    rank: str


class Marble(BaseModel):
    pos: int
    is_save: bool


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
        '2', '3', '4', '5', '6', '7', '8', '9', '10',
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    BASE_DECK: ClassVar[List[Card]] = [
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int
    phase: GamePhase
    cnt_round: int
    bool_card_exchanged: bool
    idx_player_started: int
    idx_player_active: int
    list_player: List[PlayerState]
    list_card_draw: List[Card]
    list_card_discard: List[Card]
    card_active: Optional[Card]


class Dog(Game):

    def __init__(self) -> None:
        cards = GameState.BASE_DECK.copy()
        list_player = []
        for i in range(4):
            list_player.append(PlayerState(name=f"Player{i+1}", list_card=[], list_marble=[]))

        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=random.randint(0, 3),
            idx_player_active=0,
            list_player=list_player,
            list_card_draw=cards,
            list_card_discard=[],
            card_active=None
        )

        self.seven_backup_state = None
        self.joker_chosen = False
        self.exchange_buffer = [None, None, None, None]

        self.reset()

    def reset(self):
        for i, p in enumerate(self.state.list_player):
            p.list_marble = []
            kennel_start = 64 + i * 8
            for k in range(4):
                p.list_marble.append(Marble(pos=kennel_start + k, is_save=False))

        self.state.phase = GamePhase.RUNNING
        self.state.cnt_round = 1
        self.state.bool_card_exchanged = False
        self.state.card_active = None
        self.joker_chosen = False
        self.seven_backup_state = None
        self.exchange_buffer = [None, None, None, None]

        self.state.idx_player_active = self.state.idx_player_started
        self.state.list_card_draw = GameState.BASE_DECK.copy()
        random.shuffle(self.state.list_card_draw)
        self.state.list_card_discard = []
        self.deal_cards_for_round(self.state.cnt_round)

    def set_state(self, state: GameState) -> None:
        self.state = state

    def get_state(self) -> GameState:
        return self.state

    def print_state(self) -> None:
        pass

    def get_player_view(self, idx_player: int) -> GameState:
        masked_state = self.state.copy(deep=True)
        if masked_state.phase != GamePhase.FINISHED:
            for i, p in enumerate(masked_state.list_player):
                if i != idx_player:
                    p.list_card = [Card(suit='X', rank='X') for _ in p.list_card]
        return masked_state

    def deal_cards_for_round(self, round_num: int):
        pattern = [6, 5, 4, 3, 2]
        idx = (round_num - 1) % 5
        cnt_cards = pattern[idx]
        self.check_and_reshuffle()
        for p in self.state.list_player:
            p.list_card = []
        for i in range(self.state.cnt_player):
            for _ in range(cnt_cards):
                if not self.state.list_card_draw:
                    self.check_and_reshuffle()
                self.state.list_player[i].list_card.append(self.state.list_card_draw.pop(0))

    def check_and_reshuffle(self):
        if not self.state.list_card_draw and self.state.list_card_discard:
            self.state.list_card_draw = self.state.list_card_discard.copy()
            self.state.list_card_discard = []
            random.shuffle(self.state.list_card_draw)

    def get_list_action(self) -> List[Action]:
        if self.state.phase == GamePhase.FINISHED:
            return []

        idx = self.state.idx_player_active
        player = self.state.list_player[idx]

        # card exchange phase if cnt_round=0
        if self.state.cnt_round == 0 and not self.state.bool_card_exchanged:
            if self.exchange_buffer[idx] is None:
                return [Action(card=Card(suit=c.suit, rank=c.rank), pos_from=None, pos_to=None, card_swap=None) for c in player.list_card]
            else:
                if all(x is not None for x in self.exchange_buffer):
                    self.perform_card_exchange()
                return []

        # If card_active=7 partial steps
        if self.state.card_active and self.state.card_active.rank == '7':
            return self.get_actions_for_seven(idx)

        # If card_active=JKR chosen card:
        if self.state.card_active and self.joker_chosen and self.state.card_active.rank != '7':
            return self.get_actions_for_card(self.state.card_active, idx)

        # If card_active=JKR but no chosen card yet
        if self.state.card_active and self.state.card_active.rank == 'JKR' and not self.joker_chosen:
            return []

        actions = []
        used = set()
        for c in player.list_card:
            base_card = Card(suit=c.suit, rank=c.rank)
            if c.rank == 'JKR':
                # start actions
                start_actions = self.get_start_actions(idx, c)
                for a in start_actions:
                    key = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                    if key not in used:
                        actions.append(a)
                        used.add(key)

                # card_swap actions for JKR
                if self.state.cnt_round == 1 and all(self.is_in_kennel(m.pos, idx) for m in player.list_marble):
                    LIST_SUIT = self.state.LIST_SUIT
                    for s in LIST_SUIT:
                        for r in ['A', 'K']:
                            swap_card = Card(suit=s, rank=r)
                            a = Action(card=Card(suit=c.suit, rank=c.rank), pos_from=None, pos_to=None, card_swap=swap_card)
                            key = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                            if key not in used:
                                actions.append(a)
                                used.add(key)
                else:
                    LIST_SUIT = self.state.LIST_SUIT
                    full_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
                    for s in LIST_SUIT:
                        for r in full_ranks:
                            swap_card = Card(suit=s, rank=r)
                            a = Action(card=Card(suit=c.suit, rank=c.rank), pos_from=None, pos_to=None, card_swap=swap_card)
                            key = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                            if key not in used:
                                actions.append(a)
                                used.add(key)
            elif c.rank == 'J':
                j_actions = self.get_j_actions(idx, c)
                for a in j_actions:
                    key = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                    if key not in used:
                        actions.append(a)
                        used.add(key)
            else:
                if c.rank in ['A', 'K']:
                    start_actions = self.get_start_actions(idx, c)
                    for a in start_actions:
                        key = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                        if key not in used:
                            actions.append(a)
                            used.add(key)
                normal_actions = self.get_normal_moves(idx, c)
                for a in normal_actions:
                    key = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                    if key not in used:
                        actions.append(a)
                        used.add(key)
        return actions

    def apply_action(self, action: Optional[Action]) -> None:
        if self.state.phase == GamePhase.FINISHED:
            return

        idx = self.state.idx_player_active
        player = self.state.list_player[idx]

        # card exchange
        if self.state.cnt_round == 0 and not self.state.bool_card_exchanged:
            if action is None:
                return
            if not any((action.card == c for c in player.list_card)):
                return
            self.exchange_buffer[idx] = action.card
            player.list_card.remove(action.card)
            self.next_player_for_exchange()
            return

        # card_active=JKR no chosen card yet
        if self.state.card_active and self.state.card_active.rank == 'JKR' and not self.joker_chosen and action and action.card_swap is not None:
            if action.card in player.list_card:
                player.list_card.remove(action.card)
            self.state.card_active = action.card_swap
            self.joker_chosen = True
            return

        # card_active=7 partial move
        if self.state.card_active and self.state.card_active.rank == '7':
            if action is None:
                self.restore_backup_state()
                self.end_turn()
                return
            if action.card.rank == '7':
                if self.seven_backup_state is None:
                    self.save_backup_state()
                success = self.apply_seven_step(action)
                if not success:
                    self.restore_backup_state()
                    self.end_turn()
                return
            else:
                return

        # card_active=JKR chosen card scenario:
        if self.state.card_active and self.joker_chosen and self.state.card_active.rank != '7':
            if action is None:
                self.end_turn()
                return
            if self.apply_normal_move(action):
                self.state.card_active = None
                self.joker_chosen = False
                self.end_turn()
            return

        # No card_active normal scenario
        if action is None:
            self.fold_cards(idx)
            self.end_turn()
            return

        if action.card.rank == 'J':
            if not self.has_card_in_hand(idx, action.card):
                return
            if self.apply_j_swap(action):
                self.remove_card_from_hand(idx, action.card)
                self.discard_card(action.card)
                self.end_turn()
            return

        if action.card.rank == '7':
            if not self.has_card_in_hand(idx, action.card):
                return
            self.save_backup_state()
            success = self.apply_seven_step(action)
            if not success:
                self.restore_backup_state()
                self.end_turn()
            return

        if action.card.rank == 'JKR' and action.pos_from is not None:
            if not self.has_card_in_hand(idx, action.card):
                return
            if self.apply_normal_move(action):
                self.remove_card_from_hand(idx, action.card)
                self.discard_card(action.card)
                self.end_turn()
            return

        if action.card.rank in ['A', '2', '3', '4', '5', '6', '8', '9', '10', 'Q', 'K']:
            if not self.has_card_in_hand(idx, action.card):
                return
            if self.apply_normal_move(action):
                self.remove_card_from_hand(idx, action.card)
                self.discard_card(action.card)
                self.end_turn()
            return

    def perform_card_exchange(self):
        c0 = self.exchange_buffer[0]
        c1 = self.exchange_buffer[1]
        c2 = self.exchange_buffer[2]
        c3 = self.exchange_buffer[3]

        self.state.list_player[0].list_card.append(c2)
        self.state.list_player[2].list_card.append(c0)
        self.state.list_player[1].list_card.append(c3)
        self.state.list_player[3].list_card.append(c1)

        self.exchange_buffer = [None, None, None, None]
        self.state.bool_card_exchanged = True
        self.state.idx_player_active = self.state.idx_player_started

    def next_player_for_exchange(self):
        for _ in range(4):
            self.state.idx_player_active = (self.state.idx_player_active + 1) % 4
            if self.exchange_buffer[self.state.idx_player_active] is None:
                return
        if all(x is not None for x in self.exchange_buffer):
            self.perform_card_exchange()

    def end_turn(self):
        if self.check_game_finished():
            self.state.phase = GamePhase.FINISHED
            return
        for _ in range(4):
            self.state.idx_player_active = (self.state.idx_player_active + 1) % 4
            if self.state.card_active is not None:
                return
            if self.state.list_player[self.state.idx_player_active].list_card:
                return
        self.new_round()

    def new_round(self):
        self.state.cnt_round += 1
        self.state.idx_player_started = (self.state.idx_player_started + 1) % 4
        self.state.idx_player_active = self.state.idx_player_started
        self.state.bool_card_exchanged = False
        self.deal_cards_for_round(self.state.cnt_round)
        self.state.card_active = None
        self.joker_chosen = False
        self.seven_backup_state = None
        self.exchange_buffer = [None, None, None, None]

    def fold_cards(self, idx_player: int):
        p = self.state.list_player[idx_player]
        for c in p.list_card:
            self.discard_card(c)
        p.list_card = []

    def discard_card(self, card: Card):
        self.state.list_card_discard.append(card)

    def check_game_finished(self):
        if self.team_finished([0, 2]) or self.team_finished([1, 3]):
            return True
        return False

    def team_finished(self, team: List[int]):
        for tidx in team:
            for m in self.state.list_player[tidx].list_marble:
                if not self.is_in_finish(m.pos, tidx):
                    return False
        return True

    def is_in_finish(self, pos: int, idx_player: int):
        finish_start = 64 + idx_player * 8 + 4
        finish_end = finish_start + 4
        return finish_start <= pos < finish_end

    def has_card_in_hand(self, idx_player: int, card: Card):
        return card in self.state.list_player[idx_player].list_card

    def remove_card_from_hand(self, idx_player: int, card: Card):
        p = self.state.list_player[idx_player]
        if card in p.list_card:
            p.list_card.remove(card)

    def get_start_actions(self, idx_player: int, card: Card):
        start_field = idx_player * 16
        kennel_start = 64 + idx_player * 8
        actions = []
        if card.rank in ['A', 'K', 'JKR']:
            can_start = False
            occupant = self.get_marble_at_pos(start_field)
            if occupant is None:
                if self.has_marble_in_kennel(idx_player):
                    can_start = True
            else:
                o_idx = self.get_marble_owner(start_field)
                om = self.get_marble_by_pos(o_idx, start_field)
                if start_field == o_idx * 16 and om.is_save:
                    can_start = False
                else:
                    if self.has_marble_in_kennel(idx_player):
                        can_start = True
            if can_start:
                kennel_positions = range(kennel_start, kennel_start + 4)
                for km_pos in kennel_positions:
                    if self.own_marble_at_pos(idx_player, km_pos):
                        actions.append(Action(
                            card=Card(suit=card.suit, rank=card.rank),
                            pos_from=km_pos, pos_to=start_field, card_swap=None))
        return actions

    def get_normal_moves(self, idx_player: int, card: Card):
        rank = card.rank
        if rank == 'A':
            steps_options = [1, 11]
        elif rank in ['2', '3', '5', '6', '8', '9', '10']:
            if rank == '10':
                steps_options = [10]
            else:
                steps_options = [int(rank)]
        elif rank == '4':
            steps_options = [4, -4]
        elif rank == 'Q':
            steps_options = [12]
        elif rank == 'K':
            steps_options = [13]
        else:
            return []

        actions = []
        p = self.state.list_player[idx_player]
        for mm in p.list_marble:
            for st in steps_options:
                pos_to = self.calculate_move(idx_player, mm.pos, st)
                if self.is_move_valid(idx_player, mm.pos, pos_to, st, card):
                    actions.append(Action(
                        card=Card(suit=card.suit, rank=card.rank),
                        pos_from=mm.pos, pos_to=pos_to, card_swap=None))
        return actions

    def get_j_actions(self, idx_player: int, card: Card):
        actions = []
        marbles_info = []
        for p_idx, pl in enumerate(self.state.list_player):
            for mm in pl.list_marble:
                if not self.is_in_kennel(mm.pos, p_idx) and not self.is_in_finish(mm.pos, p_idx):
                    start_pos = p_idx * 16
                    if mm.pos == start_pos and mm.is_save:
                        continue
                    marbles_info.append((p_idx, mm.pos, mm.is_save))

        for i in range(len(marbles_info)):
            for j in range(len(marbles_info)):
                if i != j:
                    pos_from = marbles_info[i][1]
                    pos_to = marbles_info[j][1]
                    actions.append(Action(
                        card=Card(suit=card.suit, rank=card.rank),
                        pos_from=pos_from, pos_to=pos_to, card_swap=None))
        return actions

    def get_actions_for_seven(self, idx_player: int):
        remain = 7 - self.count_used_7_steps()
        if remain <= 0:
            return []
        actions = []
        used = set()
        # always create a new 7-card:
        seven_card = Card(suit='♣', rank='7')
        p = self.state.list_player[idx_player]
        for mm in p.list_marble:
            for step in range(1, remain + 1):
                pos_to = self.calculate_move(idx_player, mm.pos, step)
                if self.can_apply_7_step(mm.pos, pos_to, idx_player):
                    a = Action(card=Card(suit=seven_card.suit, rank=seven_card.rank), pos_from=mm.pos, pos_to=pos_to, card_swap=None)
                    key = (a.pos_from, a.pos_to)
                    if key not in used:
                        actions.append(a)
                        used.add(key)
        return actions

    def get_actions_for_card(self, card: Card, idx_player: int):
        # create fresh card instance
        ccard = Card(suit=card.suit, rank=card.rank)
        if card.rank == '7':
            return self.get_actions_for_seven(idx_player)

        actions = []
        used = set()
        if ccard.rank in ['A', 'K']:
            start_actions = self.get_start_actions(idx_player, ccard)
            for a in start_actions:
                k = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                if k not in used:
                    actions.append(a)
                    used.add(k)

        if ccard.rank == 'J':
            j_actions = self.get_j_actions(idx_player, ccard)
            for a in j_actions:
                k = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                if k not in used:
                    actions.append(a)
                    used.add(k)

        if ccard.rank not in ['J', '7']:
            normal_actions = self.get_normal_moves(idx_player, ccard)
            for a in normal_actions:
                k = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                if k not in used:
                    actions.append(a)
                    used.add(k)
        return actions

    def is_in_kennel(self, pos: int, idx_player: int):
        kennel_start = 64 + idx_player * 8
        return kennel_start <= pos < kennel_start + 4

    def get_marble_at_pos(self, pos: int):
        for p_idx, p in enumerate(self.state.list_player):
            for mm in p.list_marble:
                if mm.pos == pos:
                    return pos
        return None

    def get_marble_owner(self, pos: int):
        for p_idx, p in enumerate(self.state.list_player):
            for mm in p.list_marble:
                if mm.pos == pos:
                    return p_idx
        return None

    def get_marble_by_pos(self, p_idx: int, pos: int):
        p = self.state.list_player[p_idx]
        for mm in p.list_marble:
            if mm.pos == pos:
                return mm
        return None

    def own_marble_at_pos(self, idx_player: int, pos: int):
        p = self.state.list_player[idx_player]
        for mm in p.list_marble:
            if mm.pos == pos:
                return True
        return False

    def has_marble_in_kennel(self, idx_player: int):
        kennel_start = 64 + idx_player * 8
        p = self.state.list_player[idx_player]
        for mm in p.list_marble:
            if kennel_start <= mm.pos < kennel_start + 4:
                return True
        return False

    def calculate_move(self, idx_player: int, pos: int, steps: int):
        if pos < 64:
            raw_pos = pos + steps
            finish_start = 64 + idx_player * 8 + 4
            finish_end = finish_start + 4
            if finish_start <= raw_pos < finish_end:
                return raw_pos
            else:
                return (pos + steps) % 64
        else:
            return pos + steps

    def get_path_positions(self, start: int, end: int):
        if start < 64 and end < 64:
            if end >= start:
                return list(range(start, end + 1))
            else:
                return list(range(start, 64)) + list(range(0, end + 1))
        else:
            if start <= end:
                return list(range(start, end + 1))
            else:
                return list(range(end, start + 1))

    def is_move_valid(self, idx_player: int, pos_from: int, pos_to: int, steps: int, card: Card):
        if self.is_in_kennel(pos_from, idx_player):
            return False
        if self.is_in_finish(pos_to, idx_player) and steps < 0:
            return False
        if steps > 0:
            forward_path = self.get_path_positions(pos_from, pos_to)
            for ppos in forward_path[1:]:
                occ = self.get_marble_at_pos(ppos)
                if occ is not None:
                    o_idx = self.get_marble_owner(ppos)
                    om = self.get_marble_by_pos(o_idx, ppos)
                    if ppos == o_idx * 16 and om.is_save:
                        return False
            occ = self.get_marble_at_pos(pos_to)
            if occ is not None:
                o_idx = self.get_marble_owner(pos_to)
                if self.is_in_finish(pos_to, o_idx):
                    return False
        else:
            backward_path = self.get_path_positions(pos_to, pos_from)
            for ppos in backward_path[1:]:
                occ = self.get_marble_at_pos(ppos)
                if occ is not None:
                    o_idx = self.get_marble_owner(ppos)
                    om = self.get_marble_by_pos(o_idx, ppos)
                    if ppos == o_idx * 16 and om.is_save:
                        return False
            occ = self.get_marble_at_pos(pos_to)
            if occ is not None:
                o_idx = self.get_marble_owner(pos_to)
                if self.is_in_finish(pos_to, o_idx):
                    return False
        return True

    def send_marble_home(self, idx_player: int, pos: int):
        m = self.get_marble_by_pos(idx_player, pos)
        if m:
            kennel_start = 64 + idx_player * 8
            m.pos = kennel_start
            m.is_save = False

    def apply_normal_move(self, action: Action):
        pos_from = action.pos_from
        pos_to = action.pos_to
        idx = self.state.idx_player_active
        p = self.state.list_player[idx]
        mm = None
        for m in p.list_marble:
            if m.pos == pos_from:
                mm = m
                break
        if mm is None:
            return False

        occ = self.get_marble_at_pos(pos_to)
        if occ is not None:
            o_idx = self.get_marble_owner(pos_to)
            if self.is_in_finish(pos_to, o_idx):
                return False
            self.send_marble_home(o_idx, pos_to)

        mm.pos = pos_to
        if self.is_in_kennel(pos_from, idx):
            mm.is_save = True
        return True

    def apply_j_swap(self, action: Action):
        pos_from = action.pos_from
        pos_to = action.pos_to
        from_owner = self.get_marble_owner(pos_from)
        to_owner = self.get_marble_owner(pos_to)
        if from_owner is None or to_owner is None:
            return False
        m1 = self.get_marble_by_pos(from_owner, pos_from)
        m2 = self.get_marble_by_pos(to_owner, pos_to)
        if m1 is None or m2 is None:
            return False

        if self.is_in_kennel(m1.pos, from_owner) or self.is_in_finish(m1.pos, from_owner):
            return False
        if self.is_in_kennel(m2.pos, to_owner) or self.is_in_finish(m2.pos, to_owner):
            return False

        start1 = from_owner * 16
        start2 = to_owner * 16
        if (m1.pos == start1 and m1.is_save) or (m2.pos == start2 and m2.is_save):
            return False

        p1_pos = m1.pos
        m1.pos = m2.pos
        m2.pos = p1_pos
        return True

    def save_backup_state(self):
        self.seven_backup_state = copy.deepcopy(self.state)

    def restore_backup_state(self):
        if self.seven_backup_state:
            self.state = self.seven_backup_state
            self.seven_backup_state = None

    def apply_seven_step(self, action: Action):
        steps = action.pos_to - action.pos_from
        if action.pos_to < 64 and action.pos_from < 64:
            steps = (action.pos_to - action.pos_from) % 64
        if steps <= 0:
            return False
        idx = self.state.idx_player_active
        if not self.has_card_in_hand(idx, action.card):
            return False
        if not self.can_apply_7_step(action.pos_from, action.pos_to, idx):
            return False

        p = self.state.list_player[idx]
        mm = None
        for m in p.list_marble:
            if m.pos == action.pos_from:
                mm = m
                break
        if mm is None:
            return False

        path = self.get_path_positions(action.pos_from, action.pos_to)
        for pp in path[1:]:
            occ = self.get_marble_at_pos(pp)
            if occ is not None:
                o_idx = self.get_marble_owner(pp)
                om = self.get_marble_by_pos(o_idx, pp)
                if pp == o_idx * 16 and om.is_save:
                    return False
                if pp != action.pos_to:
                    self.send_marble_home(o_idx, pp)

        occ = self.get_marble_at_pos(action.pos_to)
        if occ is not None:
            o_idx = self.get_marble_owner(action.pos_to)
            if self.is_in_finish(action.pos_to, o_idx):
                return False
            self.send_marble_home(o_idx, action.pos_to)

        mm.pos = action.pos_to
        if self.is_in_kennel(action.pos_from, idx):
            mm.is_save = True

        used_steps = self.count_used_7_steps()
        if used_steps == 7:
            self.remove_card_from_hand(idx, action.card)
            self.discard_card(action.card)
            self.seven_backup_state = None
            self.state.card_active = None
            self.end_turn()
        else:
            # ensure card_active is set to '7'
            self.state.card_active = Card(suit='♣', rank='7')
        return True

    def count_used_7_steps(self):
        if not self.seven_backup_state:
            return 0
        old_p = self.seven_backup_state.list_player[self.state.idx_player_active]
        new_p = self.state.list_player[self.state.idx_player_active]
        old_pos = sorted([m.pos for m in old_p.list_marble])
        new_pos = sorted([m.pos for m in new_p.list_marble])
        steps_used = 0
        for i in range(4):
            op = old_pos[i]
            np = new_pos[i]
            if op < 64 and np < 64:
                fw_steps = (np - op) % 64
            else:
                fw_steps = (np - op)
            if fw_steps > 0:
                steps_used += fw_steps
        return steps_used

    def can_apply_7_step(self, pos_from: int, pos_to: int, idx_player: int):
        steps = (pos_to - pos_from)
        if pos_from < 64 and pos_to < 64:
            steps = (pos_to - pos_from) % 64
        if steps <= 0:
            return False
        path = self.get_path_positions(pos_from, pos_to)
        for pp in path[1:]:
            occ = self.get_marble_at_pos(pp)
            if occ is not None:
                o_idx = self.get_marble_owner(pp)
                om = self.get_marble_by_pos(o_idx, pp)
                if pp == o_idx * 16 and om.is_save:
                    return False
        occ = self.get_marble_at_pos(pos_to)
        if occ is not None:
            o_idx = self.get_marble_owner(pos_to)
            if self.is_in_finish(pos_to, o_idx):
                return False
        return True


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    game = Dog()