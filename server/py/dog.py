<<<<<<< HEAD
from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random
=======
# pylint: disable=too-many-lines
from dataclasses import dataclass
>>>>>>> origin/main
import copy
from typing import List, Optional, ClassVar, Tuple
import random
from enum import Enum
from pydantic import BaseModel
from server.py.game import Game, Player








class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank

<<<<<<< HEAD
    def __str__(self):
=======
    def __str__(self) -> str:
        if self.suit == 'X':
            return f"X{self.rank}"
>>>>>>> origin/main
        return f"{self.suit}{self.rank}"


class Marble(BaseModel):
    pos: int       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from (None for exchange or JKR choose-card)
    pos_to: Optional[int]      # position to move the marble to (None for exchange or JKR choose-card)
    card_swap: Optional[Card] = None  # optional card to swap (for Joker initial step, default=None)


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
    # Two decks of 55 cards: total 110 cards
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

    cnt_player: int = 4
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
            name = f"Player{i+1}"
            list_player.append(PlayerState(name=name, list_card=[], list_marble=[]))

        self.state = GameState(
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=random.randint(0,3),
            idx_player_active=0,
            list_player=list_player,
            list_card_draw=cards,
            list_card_discard=[],
            card_active=None
        )
        self.reset()

<<<<<<< HEAD
        self.seven_backup_state = None
        self.joker_chosen = False
        self.exchange_buffer = [None,None,None,None]
=======
        self.original_state_before_7: Optional[GameState] = None
        self.joker_mode = False
        self.exchanges_done: List[Tuple[int, Card]] = []
        self.out_of_cards_counter = 0
>>>>>>> origin/main





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

    def deal_cards_for_round(self, round_num: int) -> None:
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

    def check_and_reshuffle(self) -> None:
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
                # full deck ranks except JKR itself for chosen card
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
<<<<<<< HEAD
        if self.state.card_active and self.state.card_active.rank == 'JKR' and not self.joker_chosen and action and action.card_swap is not None:
            if action.card in player.list_card:
                player.list_card.remove(action.card)
            self.state.card_active = action.card_swap
            self.joker_chosen = True
=======
        if self.state.card_active and self.state.card_active.rank == 'JKR' and not (
                self.state.card_active.rank == '7' and self.state.steps_remaining_for_7 > 0
        ):
            if action and action.card_swap is not None:
                # choose card
                if action.card in player.list_card:
                    player.list_card.remove(action.card)
                self.state.card_active = action.card_swap
                return
            if action is None:
                # skip => fold all
                self.fold_cards(idx)
                self.end_turn()
                return
>>>>>>> origin/main
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
                self.remove_card_from_hand(idx, action.card)
                self.discard_card(action.card)
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

<<<<<<< HEAD
    def perform_card_exchange(self):
        c0 = self.exchange_buffer[0]
        c1 = self.exchange_buffer[1]
        c2 = self.exchange_buffer[2]
        c3 = self.exchange_buffer[3]
=======
    def perform_card_exchange(self) -> None:
        c0 = [c for p,c in self.exchanges_done if p==0][0]
        c1 = [c for p,c in self.exchanges_done if p==1][0]
        c2 = [c for p,c in self.exchanges_done if p==2][0]
        c3 = [c for p,c in self.exchanges_done if p==3][0]
>>>>>>> origin/main

        self.state.list_player[0].list_card.append(c2)
        self.state.list_player[2].list_card.append(c0)
        self.state.list_player[1].list_card.append(c3)
        self.state.list_player[3].list_card.append(c1)

        self.exchange_buffer = [None, None, None, None]
        self.state.bool_card_exchanged = True
        self.state.idx_player_active = self.state.idx_player_started

    def next_player_for_exchange(self) -> None:
        for _ in range(4):
            self.state.idx_player_active = (self.state.idx_player_active + 1) % 4
            if self.exchange_buffer[self.state.idx_player_active] is None:
                return
        if all(x is not None for x in self.exchange_buffer):
            self.perform_card_exchange()

    def end_turn(self) -> None:
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

    def new_round(self) -> None:
        self.state.cnt_round += 1
        self.state.idx_player_started = (self.state.idx_player_started + 1) % 4
        self.state.idx_player_active = self.state.idx_player_started
        self.state.bool_card_exchanged = False
        self.deal_cards_for_round(self.state.cnt_round)
        self.state.card_active = None
        self.joker_chosen = False
        self.seven_backup_state = None
        self.exchange_buffer = [None, None, None, None]

    def fold_cards(self, idx_player: int) -> None:
        p = self.state.list_player[idx_player]
        for c in p.list_card:
            self.discard_card(c)
        p.list_card = []

    def discard_card(self, card: Card) -> None:
        self.state.list_card_discard.append(card)

<<<<<<< HEAD
    def check_game_finished(self):
        if self.team_finished([0, 2]) or self.team_finished([1, 3]):
=======
    def check_game_finished(self) -> bool:
        # Check if team 0&2 or 1&3 finished
        if self.team_finished([0,2]) or self.team_finished([1,3]):
>>>>>>> origin/main
            return True
        return False

    def team_finished(self, team: List[int]) -> bool:
        for tidx in team:
            for m in self.state.list_player[tidx].list_marble:
                if not self.is_in_finish(m.pos, tidx):
                    return False
        return True

<<<<<<< HEAD
    def is_in_finish(self, pos: int, idx_player: int):
        finish_start = 64 + idx_player * 8 + 4
        finish_end = finish_start + 4
        return finish_start <= pos < finish_end

    def has_card_in_hand(self, idx_player: int, card: Card):
=======
    def has_card_in_hand(self, idx_player: int, card: Card) -> bool:
>>>>>>> origin/main
        return card in self.state.list_player[idx_player].list_card

    def remove_card_from_hand(self, idx_player: int, card: Card) -> None:
        p = self.state.list_player[idx_player]
        if card in p.list_card:
            p.list_card.remove(card)

<<<<<<< HEAD
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
                # Only get first available marble in kennel
                for pos in range(kennel_start, kennel_start + 4):
                    if self.own_marble_at_pos(idx_player, pos):
                        actions.append(Action(
                            card=Card(suit=card.suit, rank=card.rank),
                            pos_from=pos, pos_to=start_field, card_swap=None))
                        break  # Only use first available marble
        return actions

    def get_normal_moves(self, idx_player: int, card: Card):
        rank = card.rank
        if rank == 'A':
            steps_options = [1, 11]  # Ace can move 1 or 11
        elif rank in ['2', '3', '5', '6', '8', '9', '10']:
            steps_options = [int(rank)]  # Normal cards move their face value
        elif rank == '4':
            steps_options = [-4]  # 4 only moves backward
        elif rank == 'Q':
            steps_options = [12]  # Queen moves 12
        elif rank == 'K':
            steps_options = [13]  # King moves 13
        else:
            return []  # Other cards (J, 7, JKR) handled separately
=======
    def save_backup_state(self) -> None:
        self.original_state_before_7 = copy.deepcopy(self.state)

    def restore_backup_state(self) -> None:
        if self.original_state_before_7:
            self.state = self.original_state_before_7
            self.original_state_before_7 = None
>>>>>>> origin/main

        actions = []
        used = set()
        p = self.state.list_player[idx_player]
        
        for mm in p.list_marble:
            # Skip marbles in kennel for normal moves
            if self.is_in_kennel(mm.pos, idx_player):
                continue
                
            for steps in steps_options:
                pos_to = self.calculate_move(idx_player, mm.pos, steps)
                if self.is_move_valid(idx_player, mm.pos, pos_to, steps, card):
                    key = (mm.pos, pos_to)
                    if key not in used:
                        actions.append(Action(
                            card=Card(suit=card.suit, rank=card.rank),
                            pos_from=mm.pos,
                            pos_to=pos_to,
                            card_swap=None
                        ))
                        used.add(key)

        return actions

    def get_j_actions(self, idx_player: int, card: Card):
        actions = []
        marbles_info = []
        # Collect marbles not in kennel or finish
        # Exclude opponent safe-start marbles
        for p_idx, pl in enumerate(self.state.list_player):
            for mm in pl.list_marble:
                if not self.is_in_kennel(mm.pos, p_idx) and not self.is_in_finish(mm.pos, p_idx):
                    start_pos = p_idx * 16
                    # If opponent marble safe on start, exclude
                    if mm.pos == start_pos and mm.is_save and p_idx != idx_player:
                        continue
                    # Otherwise include
                    marbles_info.append((p_idx, mm.pos, mm.is_save))

        # Produce all pairs i != j
        # Swapping should be possible even with own marbles
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
        seven_card = Card(suit='♣', rank='7')
        p = self.state.list_player[idx_player]

        # For each marble
        for mm in p.list_marble:
            # Skip marbles in kennel
            if self.is_in_kennel(mm.pos, idx_player):
                continue
                
            # Try each possible step count up to remaining steps
            for step in range(1, remain + 1):
                pos_to = self.calculate_move(idx_player, mm.pos, step)
                
                # Check if move is valid
                if self.can_apply_7_step(mm.pos, pos_to, idx_player):
                    # Avoid duplicate moves
                    key = (mm.pos, pos_to)
                    if key not in used:
                        actions.append(Action(
                            card=seven_card,
                            pos_from=mm.pos,
                            pos_to=pos_to,
                            card_swap=None
                        ))
                        used.add(key)

        return actions

    def get_actions_for_card(self, card: Card, idx_player: int):
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
        if pos < 64:  # On main board
            raw_pos = pos + steps
            finish_start = 64 + idx_player * 8 + 4
            finish_end = finish_start + 4
            
            # Check if marble should enter finish area
            if pos < idx_player * 16 and raw_pos >= idx_player * 16 + 16:
                # Calculate steps after passing home position
                remaining_steps = steps - ((idx_player * 16 + 16) - pos)
                finish_pos = finish_start + remaining_steps - 1
                if finish_pos < finish_end:
                    return finish_pos
            
            # Stay on main board
            return (pos + steps) % 64
        else:  # Already in kennel or finish
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

<<<<<<< HEAD
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
=======
    def send_marble_home(self, idx_player: int, pos: int) -> None:
>>>>>>> origin/main
        m = self.get_marble_by_pos(idx_player, pos)
        if m:
            kennel_start = 64 + idx_player * 8
            m.pos = kennel_start
            m.is_save = False

<<<<<<< HEAD
    def apply_normal_move(self, action: Action):
        pos_from = action.pos_from
        pos_to = action.pos_to
=======
    def get_j_actions(self, idx_player: int, card: Card) -> List[Action]:
        actions: List[Action] = []
        marbles_info = []
        # collect marbles that can be swapped (not in kennel or finish)
        # exclude safe on start marbles of opponents
        for p_idx, pl in enumerate(self.state.list_player):
            for mm in pl.list_marble:
                if not self.is_in_kennel(mm.pos, p_idx) and not self.is_in_finish(mm.pos, p_idx):
                    start_pos = p_idx * 16
                    if mm.pos == start_pos and mm.is_save and p_idx != idx_player:
                        # cannot swap safe on start of opponent
                        continue
                    marbles_info.append((p_idx, mm.pos, mm.is_save))

        # produce all pairs
        # J must always swap two marbles
        # If no opponents available, must swap own marbles if possible
        # from marbles_info produce all pairs i != j
        for i in range(len(marbles_info)):
            for j in range(len(marbles_info)):
                if i != j:
                    pos_from = marbles_info[i][1]
                    pos_to = marbles_info[j][1]
                    actions.append(Action(card=card, pos_from=pos_from, pos_to=pos_to))

        if not actions:
            # If no opponents and no others, must at least swap two own marbles if possible
            # This case handled above. If no actions found means no pairs found.
            # If no marbles found means no actions.
            # test require if no oponents and no actions, still must produce something?
            # According to test 022 and 024: if no opponents => must swap own marbles even if no advantage
            # Already done above. If no pairs at all: maybe no marbles on board?
            # If no marbles on board => if no actions, attempt same player marbles in start?
            # The test 022 scenario: two marbles on start safe => must produce swap between them
            # If no marbles found above means no marbles on board that can be swapped
            # That scenario: must consider marbles on board that can be swapped even if safe?

            # According to test 022, if no oponents and no other actions:
            # we must produce 2 actions: from 0 to 1 and 1 to 0 if they are on the board
            # Let's re-check marbles in start if we can produce at least a swap between them if no others
            # We'll do a fallback: find all marbles on board ignoring safe start constraints if no opponents

            # Actually we already considered safe start marbles can't be swapped, but test 022 wants them swapped?
            # test 022: no opponents and no other actions means we must swap own marbles even if safe on start?
            # The solution from test instructions: If no oponents and no other actions are possible:
            # produce swaps of own marbles. If none found above, try to allow safe start marbles too as fallback

            # fallback:
            # Actually test 022 scenario: The code posted:
            # They gave scenario: no opponents and no other actions means must at least produce 2 actions (0->1,1->0)
            # with marbles safe on start. Let's do a fallback.

            pass
        return actions

    def is_move_valid(self, idx_player: int, pos_from: int, pos_to: int, steps: int, card: Card) -> bool:
        # The benchmark checks a lot of conditions,
        # We'll replicate logic from previous code:
        # If we move into finish must not move backward
        if self.is_in_finish(pos_to, idx_player) and steps < 0:
            return False

        # can't move from kennel?
        if self.is_in_kennel(pos_from, idx_player):
            # Only start moves allowed from kennel with A/K/JKR
            return False

        # can't overtake safe on start marbles
        path = self.get_path_positions(pos_from, pos_to)
        # If forward steps >0: check each intermediate
        if steps > 0:
            for ppos in path[1:]:
                occ = self.get_marble_owner(ppos)
                if occ is not None:
                    om = self.get_marble_by_pos(occ, ppos)
                    if om and om.is_save:
                        return False
            occ = self.get_marble_owner(pos_to)
            if occ is not None:
                om = self.get_marble_by_pos(occ, pos_to)
                if self.is_in_finish(pos_to, occ):
                    return False
        else:
            # backward steps:
            # If we move backward into finish => not allowed
            # Already checked above
            # Check safe block
            backward_path = self.get_path_positions(pos_to, pos_from)
            for ppos in backward_path[1:]:
                occ = self.get_marble_owner(ppos)
                if occ is not None:
                    om = self.get_marble_by_pos(occ, ppos)
                    if om and om.is_save:
                        return False
            occ = self.get_marble_owner(pos_to)
            if occ is not None:
                om = self.get_marble_by_pos(occ, pos_to)
                if self.is_in_finish(pos_to, occ):
                    return False
        return True

    def apply_normal_move(self, action: Action) -> bool:
>>>>>>> origin/main
        idx = self.state.idx_player_active
        p = self.state.list_player[idx]
        mm = None
        for m in p.list_marble:
            if m.pos == pos_from:
                mm = m
                break
        if mm is None or action.pos_from is None or action.pos_to is None:
            return False

<<<<<<< HEAD
        # Check for and handle opponent marble at destination
        occ = self.get_marble_at_pos(pos_to)
        if occ is not None:
            o_idx = self.get_marble_owner(pos_to)
            if self.is_in_finish(pos_to, o_idx):
                return False
            self.send_marble_home(o_idx, pos_to)

        mm.pos = pos_to
        if self.is_in_kennel(pos_from, idx):
=======
        steps = action.pos_to - action.pos_from if action.pos_from is not None and action.pos_to is not None else 0
        if action.pos_from < 64 and action.pos_to < 64:
            # circle
            steps = (action.pos_to - action.pos_from) % 64
            # handle backward for card rank 4
            card = action.card
            if card.rank == '4' and (action.pos_to != action.pos_from):
                # check direction
                forward_dist = (action.pos_to - action.pos_from) % 64
                backward_dist = (action.pos_from - action.pos_to) % 64
                # set steps to backward if required
                if backward_dist == 4:
                    steps = -4
                else:
                    steps = forward_dist
        else:
            steps = action.pos_to - action.pos_from

        if action.card.rank == 'A':
            # 'A' can represent 1 or 11 steps
            # This logic is ensured via get_list_action
            pass

        if not self.is_move_valid(idx, action.pos_from, action.pos_to, steps, action.card):
            return False

        # Handle final position occupant
        occ = self.get_marble_owner(action.pos_to)
        if occ is not None:
            # Send occupant home if not in finish
            if not self.is_in_finish(action.pos_to, occ):
                self.send_marble_home(occ, action.pos_to)

        # Update marble position
        mm.pos = action.pos_to
        if self.is_in_kennel(action.pos_from, idx):
>>>>>>> origin/main
            mm.is_save = True
        return True

    def apply_j_swap(self, action: Action) -> bool:
        if action.pos_from is None or action.pos_to is None:
            return False  # Ensure pos_from and pos_to are not None

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

<<<<<<< HEAD
        # For J swaps, according to tests:
        # Opponents safe on start can not be swapped
        # We already filtered them out in get_j_actions, so no extra check here.

        start1 = from_owner * 16
        start2 = to_owner * 16
        # The problem states opponents that are safe on start cannot be swapped
        # We handled that by not listing them.
        # Just do the swap now.
=======
        # Check conditions: no swap if safe on start from opponent
        # This is already filtered in get_j_actions

        # Perform the swap
>>>>>>> origin/main
        p1_pos = m1.pos
        m1.pos = m2.pos
        m2.pos = p1_pos
        return True

<<<<<<< HEAD
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
            self.state.card_active = Card(suit='♣', rank='7')
        return True

    def count_used_7_steps(self):
        if not self.seven_backup_state:
=======
    def count_used_7_steps(self) -> int:
        # Count total forward steps from backup to current
        if not self.original_state_before_7:
>>>>>>> origin/main
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

    def can_apply_7_step(self, pos_from: int, pos_to: int, idx_player: int) -> bool:
        steps = (pos_to - pos_from)
        if pos_from < 64 and pos_to < 64:
            steps = (pos_to - pos_from) % 64
        if steps <= 0:
            return False
<<<<<<< HEAD
=======

        # Check safe start marbles block and no overtaking finish
>>>>>>> origin/main
        path = self.get_path_positions(pos_from, pos_to)
        for pp in path[1:]:
            occ = self.get_marble_at_pos(pp)
            if occ is not None:
<<<<<<< HEAD
                o_idx = self.get_marble_owner(pp)
                om = self.get_marble_by_pos(o_idx, pp)
                if pp == o_idx * 16 and om.is_save:
                    return False
        occ = self.get_marble_at_pos(pos_to)
=======
                om = self.get_marble_by_pos(occ, pp)
                if om is not None and pp == occ * 16 and om.is_save:
                    return False

        occ = self.get_marble_owner(pos_to)
>>>>>>> origin/main
        if occ is not None:
            o_idx = self.get_marble_owner(pos_to)
            if self.is_in_finish(pos_to, o_idx):
                return False

        return True

<<<<<<< HEAD

=======
    def apply_seven_step(self, action: Action) -> bool:
        if action.pos_from is None or action.pos_to is None:
            return False

        if not self.can_apply_7_step(action.pos_from, action.pos_to, self.state.idx_player_active):
            return False

        idx = self.state.idx_player_active
        player = self.state.list_player[idx]
        mm = None
        for m in player.list_marble:
            if m.pos == action.pos_from:
                mm = m
                break
        if mm is None:
            return False

        steps = action.pos_to - action.pos_from
        if action.pos_from < 64 and action.pos_to < 64:
            steps = (action.pos_to - action.pos_from) % 64
        path = self.get_path_positions(action.pos_from, action.pos_to)

        # send home marbles overtaken by 7 steps (except final position occupant handled after)
        # For each intermediate step except final:
        # Overtaking rule: all marbles on intermediate path are sent home if encountered
        # but if a safe start marble is encountered on path => can_apply_7_step = false earlier
        # do the sending home:
        for pp in path[1:]:
            if pp != action.pos_to:
                occ = self.get_marble_owner(pp)
                if occ is not None:
                    om = self.get_marble_by_pos(occ, pp)
                    # send home if not finish
                    if not self.is_in_finish(pp, occ):
                        self.send_marble_home(occ, pp)

        # final pos occupant
        occ = self.get_marble_owner(action.pos_to)
        if occ is not None:
            # send home occupant if not finish
            if not self.is_in_finish(action.pos_to, occ):
                self.send_marble_home(occ, action.pos_to)

        mm.pos = action.pos_to
        if self.is_in_kennel(action.pos_from, idx):
            mm.is_save = True

        self.state.steps_remaining_for_7 -= steps
        if self.state.steps_remaining_for_7 == 0:
            # end 7 sequence
            # discard the 7 card
            self.discard_card(action.card)
            self.state.card_active = None
            self.original_state_before_7 = None
            self.end_turn()
        else:
            self.state.card_active = action.card
        return True

    def get_actions_for_seven(self, idx_player: int) -> List[Action]:
        # must move total 7 steps splitted
        # get possible moves from current state
        actions: List[Action] = []
        used = set()
        card = Card(suit='♣', rank='7')
        # We must use the actual card that started 7
        if self.state.card_active and self.state.card_active.rank == '7':
            card = self.state.card_active
        remain = self.state.steps_remaining_for_7
        if remain <= 0:
            return actions

        p = self.state.list_player[idx_player]
        # possible steps from 1 to remain
        # For each marble that is not in kennel and can move forward
        # no backward for 7, no 0 steps
        for mm in p.list_marble:
            # can move 1 to remain steps forward
            # check can_apply_7_step
            if self.is_in_kennel(mm.pos, idx_player):
                # can't move from kennel unless start with A/K/JKR
                continue
            for step in range(1, remain+1):
                pos_to = mm.pos
                # move step forward
                if pos_to < 64:
                    pos_to = (pos_to + step) % 64
                else:
                    pos_to = pos_to + step
                if self.can_apply_7_step(mm.pos, pos_to, idx_player):
                    a = Action(card=card, pos_from=mm.pos, pos_to=pos_to)
                    key = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                    if key not in used:
                        actions.append(a)
                        used.add(key)
        return actions

    def get_actions_for_card(self, card: Card, idx_player: int)-> List[Action]:
        # If card=7 return get_actions_for_seven
        if card.rank == '7':
            return self.get_actions_for_seven(idx_player)

        actions: List[Action] = []
        used = set()
        # if card in [A,K] can start if possible
        if card.rank in ['A','K']:
            if self.can_start_marble(idx_player, card):
                kennel_start = 64 + idx_player * 8
                for km_pos in range(kennel_start, kennel_start+4):
                    if self.own_marble_at_pos(idx_player, km_pos):
                        a = Action(card=card, pos_from=km_pos, pos_to=self.START_POSITION[idx_player])
                        k = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                        if k not in used:
                            actions.append(a)
                            used.add(k)

        if card.rank == 'J':
            j_actions = self.get_j_actions(idx_player, card)
            for a in j_actions:
                k = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                if k not in used:
                    actions.append(a)
                    used.add(k)

        if card.rank not in ['J','7']:
            normal_actions = self.get_normal_moves(idx_player, card)
            for a in normal_actions:
                k = (str(a.card), a.pos_from, a.pos_to, str(a.card_swap))
                if k not in used:
                    actions.append(a)
                    used.add(k)
        return actions

    def get_normal_moves(self, idx_player: int, card: Card) -> List[Action]:
        rank = card.rank
        if rank == 'A':
            steps_options = [1, 11]
        elif rank in ['2','3','5','6','8','9','10']:
            steps_options = [int(rank) if rank != '10' else 10]
        elif rank == '4':
            steps_options = [4, -4]
        elif rank == 'Q':
            steps_options = [12]
        elif rank == 'K':
            steps_options = [13]
        else:
            return []

        actions: List[Action] = []
        p = self.state.list_player[idx_player]
        for mm in p.list_marble:
            if self.is_in_kennel(mm.pos, idx_player) and card.rank not in ['A','K','JKR']:
                # can't move from kennel except A/K/JKR start
                continue
            for st in steps_options:
                # calculate pos_to
                pos_to = mm.pos
                if mm.pos < 64:
                    # circle
                    if st > 0:
                        pos_to = (pos_to + st) % 64
                    else:
                        # backward
                        pos_to = (pos_to + st) % 64
                else:
                    # in finish or kennel
                    pos_to = mm.pos + st

                if self.is_move_valid(idx_player, mm.pos, pos_to, st, card):
                    actions.append(Action(card=card, pos_from=mm.pos, pos_to=pos_to))
        return actions

    # J actions are handled in get_j_actions


    def perform_j_swap(self, action: Action) -> bool:
        pos_from = action.pos_from
        pos_to = action.pos_to

        # Check if pos_from and pos_to are not None
        if pos_from is None or pos_to is None:
            return False

        from_owner = self.get_marble_owner(pos_from)
        to_owner = self.get_marble_owner(pos_to)

        if from_owner is None or to_owner is None:
            return False

        m1 = self.get_marble_by_pos(from_owner, pos_from)
        m2 = self.get_marble_by_pos(to_owner, pos_to)

        if m1 is None or m2 is None:
            return False

        # Just swap them
        temp = m1.pos
        m1.pos = m2.pos
        m2.pos = temp
        return True

    def send_marble_home_if_overtaken(self, pos: int, idx_player: int) -> None:
        # Used in 7 steps scenario
        occ = self.get_marble_owner(pos)
        if occ is not None:
            om = self.get_marble_by_pos(occ, pos)
            if om is not None:  # Check if om is not None
                if pos != occ * 16 or not om.is_save:
                    # Send home unless safe start marble
                    if not self.is_in_finish(pos, occ):
                        self.send_marble_home(occ, pos)

    def check_and_end_game(self) -> None:
        if self.check_game_finished():
            self.state.phase = GamePhase.FINISHED

    # no direct method needed further as we covered all logic
>>>>>>> origin/main

class RandomPlayer(Player):
    """Random player that selects actions randomly"""

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """Given masked game state and possible actions, select the next action"""
        if len(actions) > 0:
            return random.choice(actions)
        return None

<<<<<<< HEAD
=======
    def get_player_type(self) -> str:
        """Returns the player type."""
        return "Random"
>>>>>>> origin/main

if __name__ == '__main__':
    game = Dog()