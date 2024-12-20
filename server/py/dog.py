# pylint: disable=too-many-lines

''' This Code implement the game brandy dog '''
from typing import List, Optional, ClassVar, Tuple, Set
from enum import Enum
import random
from itertools import combinations
from dataclasses import dataclass
from pydantic import BaseModel
from server.py.game import Game, Player


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: int       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str
    list_card: List[Card]
    list_marble: List[Marble]


class Action(BaseModel):
    card: Card
    pos_from: Optional[int] = None
    pos_to: Optional[int] = None
    card_swap: Optional[Card] = None


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


@dataclass
class ActionData:
    card: 'Card'
    pos_from: Optional[int]
    pos_to: Optional[int]


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = (
        [Card(suit=s, rank=r) for s in ['♠', '♥', '♦', '♣'] for r in
         ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']] +
        [Card(suit='', rank='JKR')] * 3
    ) * 2  # 110 cards

    cnt_player: int
    phase: GamePhase
    cnt_round: int
    bool_card_exchanged: bool
    idx_player_started: int
    idx_player_active: int
    list_player: List[PlayerState]
    list_card_draw: List[Card]
    list_card_discard: List[Card]
    card_active: Optional[Card] = None
    steps_remaining_for_7: int = 7


class Dog(Game):
    KENNEL_POSITIONS = [
        [64, 65, 66, 67],
        [72, 73, 74, 75],
        [80, 81, 82, 83],
        [88, 89, 90, 91]
    ]

    START_POSITION = [0, 16, 32, 48]

    FINISH_POSITIONS = [
        [68, 69, 70, 71],
        [76, 77, 78, 79],
        [84, 85, 86, 87],
        [92, 93, 94, 95],
    ]

    def __init__(self) -> None:
        self.out_of_cards_counter: int = 0
        self.state: GameState = GameState(
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[],
            list_card_draw=[],
            list_card_discard=[],
            card_active=None,
        )

        self.exchanges_done: List[Tuple[int, Card]] = []
        self.original_state_before_7: Optional[GameState] = None

        self.state.list_card_draw = GameState.LIST_CARD.copy()
        random.shuffle(self.state.list_card_draw)

        for idx in range(self.state.cnt_player):
            player_state = PlayerState(
                name=f"Player {idx+1}",
                list_card=[],
                list_marble=[]
            )
            for m_idx in range(4):
                marble = Marble(
                    pos=self.KENNEL_POSITIONS[idx][m_idx],
                    is_save=False
                )
                player_state.list_marble.append(marble)
            self.state.list_player.append(player_state)

        self.state.idx_player_started = random.randint(0, 3)
        self.state.idx_player_active = self.state.idx_player_started
        self.state.bool_card_exchanged = False
        self.state.phase = GamePhase.RUNNING

        self.deal_cards(num_cards_per_player=6)

    def set_state(self, state: GameState) -> None:
        self.state = state
        if (self.state.cnt_round > 1
                and self.state.idx_player_active == self.state.idx_player_started):
            self.state.idx_player_active = (
                self.state.idx_player_started + self.state.cnt_round
            ) % self.state.cnt_player

    def get_state(self) -> GameState:
        if (self.state.cnt_round > 1
                and self.state.idx_player_active == self.state.idx_player_started):
            self.state.idx_player_active = (
                self.state.idx_player_started + self.state.cnt_round
            ) % self.state.cnt_player
        return self.state

    def print_state(self) -> None:  # pragma: no cover
        pass

    def get_player_view(self, idx_player: int) -> GameState:
        return self.state

    def get_list_action(self) -> List[Action]:
        actions: List[Action] = []
        seen_actions: Set[Tuple[str, str, Optional[int], Optional[int]]] = set()
        active_player_idx = self.state.idx_player_active
        start_position = self.START_POSITION[active_player_idx]

        # If we have a 7 sequence ongoing:
        if self._has_active_seven_card():
            seven_actions = self._get_actions_for_seven_card(actions, seen_actions, active_player_idx)
            return seven_actions

        if self._is_setup_phase():
            return self._get_setup_phase_actions(actions, seen_actions, self.state.list_player[active_player_idx])

        # Normal scenario: Add start position actions if available
        if not self._is_start_position_occupied(active_player_idx):
            self._add_start_position_actions(actions, seen_actions, active_player_idx, start_position)

        # If card_active is None, choose any card; else use the active card
        if self.state.card_active is None:
            possible_cards = self.state.list_player[active_player_idx].list_card
        else:
            possible_cards = [self.state.card_active]

        for card in possible_cards:
            self._handle_card_actions(actions, seen_actions, active_player_idx, card)

        return actions

    def apply_action(self, action: Optional[Action]) -> None:
        if self.state.phase == GamePhase.FINISHED:
            return
        active_player_index = self.state.idx_player_active

        if action is None:
            self._handle_no_action(active_player_index)
            return

        if self._is_card_exchange_action(action):
            self._handle_card_exchange(action)
            return

        if action.card.rank == "J":
            self._handle_jack_action(action)
        elif action.card.rank == "7":
            self._handle_seven_action(action, active_player_index)
            return
        elif action.card.rank == "JKR" and action.card_swap is not None:
            player = self.state.list_player[active_player_index]
            if action.card in player.list_card:
                player.list_card.remove(action.card)
            self.state.card_active = action.card_swap
            return
        elif action.card.rank == "JKR" and action.pos_from is not None and action.pos_to is not None:
            self._handle_normal_move(action, active_player_index)
        elif action.pos_from is not None and action.pos_to is not None:
            self._handle_normal_move(action, active_player_index)

        if action.card_swap is not None:
            self._handle_card_swap(action)

        if self.state.card_active is None or self.state.card_active.rank != "7":
            self._move_card_to_discard(action, active_player_index)
            self._change_active_player()

    def check_move_validity(self, active_player_idx: int, marble_idx: int, marble_new_pos: int) -> bool:
        marble = self.state.list_player[active_player_idx].list_marble[marble_idx]
        for p_idx, pl in enumerate(self.state.list_player):
            for om_idx, om in enumerate(pl.list_marble):
                if om.pos == marble_new_pos:
                    if om.is_save and (p_idx != active_player_idx or om_idx != marble_idx):
                        return False
                    if marble_new_pos >= 68 and (p_idx != active_player_idx or om_idx != marble_idx):
                        return False

        start_pos = self.START_POSITION[active_player_idx]
        kennel_pos = self.KENNEL_POSITIONS[active_player_idx]

        if marble.pos in kennel_pos and marble_new_pos == start_pos:
            for i, m in enumerate(self.state.list_player[active_player_idx].list_marble):
                if m.pos == start_pos and m.is_save and i != marble_idx:
                    return False

        if marble_new_pos in kennel_pos:
            return False
        if marble_new_pos < 0 or marble_new_pos >= 96:
            return False
        return True

    def can_move_steps(self, player_idx: int, marble_idx: int, steps: int, direction: int = 1) -> bool:
        test_state = self.state.model_copy(deep=True)
        marble = test_state.list_player[player_idx].list_marble[marble_idx]
        for _ in range(abs(steps)):
            if marble.pos < 64:
                next_pos = (marble.pos + direction) % 64
            else:
                next_pos = marble.pos + direction
            if not self.check_move_validity(player_idx, marble_idx, next_pos):
                return False
            marble.pos = next_pos
        return True

    def compute_final_position(self, start_pos: int, steps: int, player_idx: int) -> int:
        if start_pos < 64:
            return (start_pos + steps) % 64
        finish_positions = self.FINISH_POSITIONS[player_idx]
        finish_pos = start_pos + steps
        finish_pos = min(finish_pos, finish_positions[-1])
        return finish_pos

    def send_home_if_passed(self, pos: int, active_player_idx: int) -> None:
        for p_idx, player in enumerate(self.state.list_player):
            for m_idx, marble in enumerate(player.list_marble):
                if marble.pos == pos:
                    marble.pos = self.KENNEL_POSITIONS[p_idx][0]
                    marble.is_save = False

    def is_marble_protecting_start(self, player_idx: int, marble_idx: int) -> bool:
        marble = self.state.list_player[player_idx].list_marble[marble_idx]
        return marble.is_save and marble.pos == self.START_POSITION[player_idx]

    def _get_actions_for_seven_card(self, actions: List['Action'],
                                    seen_actions: Set[Tuple[str, str, Optional[int], Optional[int]]],
                                    active_player_idx: int) -> List['Action']:
        card = self.state.card_active
        if not card:
            return actions
        possible_move_found = False
        for marble_idx, marble in enumerate(self.state.list_player[active_player_idx].list_marble):
            if (marble.pos not in self.KENNEL_POSITIONS[active_player_idx]
                and marble.pos != self.FINISH_POSITIONS[active_player_idx][3]):
                for steps_to_move in range(1, self.state.steps_remaining_for_7 + 1):
                    des_dest = self._can_move_forward(active_player_idx, marble_idx, marble, steps_to_move)
                    if des_dest != -1:
                        possible_move_found = True
                        action_data = ActionData(card=card, pos_from=marble.pos, pos_to=des_dest)
                        self._add_unique_action(actions, seen_actions, action_data)
        if not possible_move_found:
            return []
        return actions

    def calculate_7_steps(self, pos_from: int, pos_to: int) -> int:
        if pos_from < 64 and pos_to < 64:
            return (pos_to - pos_from) % 64
        if pos_from < 64 <= pos_to:
            start = self.START_POSITION[self.state.idx_player_active]
            finish_start = self.FINISH_POSITIONS[self.state.idx_player_active][0]
            circle_steps = (start - pos_from) % 64
            finish_steps = pos_to - finish_start + 1
            return circle_steps + finish_steps
        if pos_from >=64 and pos_to>=64:
            return pos_to - pos_from
        if pos_from in self.KENNEL_POSITIONS[self.state.idx_player_active] and pos_to == self.START_POSITION[self.state.idx_player_active]:
            return 1
        if pos_from in self.KENNEL_POSITIONS[self.state.idx_player_active] and pos_to>=64:
            steps_to_start=1
            finish_start=self.FINISH_POSITIONS[self.state.idx_player_active][0]
            finish_steps=pos_to - finish_start +1
            return steps_to_start+finish_steps
        return pos_to - pos_from

    def _has_active_seven_card(self) -> bool:
        return (
            self.state.card_active is not None
            and self.state.card_active.rank == '7'
            and self.state.steps_remaining_for_7 > 0
        )

    def _add_unique_action(self, actions: List['Action'],
                           seen_actions: Set[Tuple[str, str, Optional[int], Optional[int]]],
                           action_data: ActionData) -> None:
        action_key = (action_data.card.suit, action_data.card.rank, action_data.pos_from, action_data.pos_to)
        if action_key not in seen_actions:
            seen_actions.add(action_key)
            actions.append(Action(card=action_data.card, pos_from=action_data.pos_from, pos_to=action_data.pos_to))

    def _is_setup_phase(self) -> bool:
        return self.state.cnt_round == 0 and not self.state.bool_card_exchanged

    def _get_setup_phase_actions(self, actions: List['Action'],
                                 seen_actions: Set[Tuple[str, str, Optional[int], Optional[int]]],
                                 active_player: PlayerState) -> List['Action']:
        for card in active_player.list_card:
            action_data = ActionData(card=card, pos_from=None, pos_to=None)
            self._add_unique_action(actions, seen_actions, action_data)
        return actions

    def _is_start_position_occupied(self, active_player_idx: int) -> bool:
        start_position = self.START_POSITION[active_player_idx]
        return any(
            m.pos == start_position
            for m in self.state.list_player[active_player_idx].list_marble
        )

    def _add_start_position_actions(self, actions: List['Action'], seen_actions: Set[Tuple[str,str,Optional[int],Optional[int]]],
                                    active_player_idx: int, start_position: int) -> None:
        marbles_in_kennel = [m for m in self.state.list_player[active_player_idx].list_marble
                             if m.pos in self.KENNEL_POSITIONS[active_player_idx]]
        marbles_in_kennel.sort(key=lambda x: x.pos)

        if self.state.card_active is None:
            possible_cards = self.state.list_player[active_player_idx].list_card
        else:
            possible_cards = [self.state.card_active]

        for card in possible_cards:
            if card.rank in ['A','K','JKR'] and marbles_in_kennel:
                action_data = ActionData(card=card, pos_from=marbles_in_kennel[0].pos, pos_to=start_position)
                self._add_unique_action(actions, seen_actions, action_data)

    def _handle_card_actions(self, actions: List['Action'],
                             seen_actions: Set[Tuple[str,str,Optional[int],Optional[int]]],
                             active_player_idx: int, card: Card) -> None:
        if card.rank == 'JKR':
            self._handle_joker(actions, seen_actions, active_player_idx, card)
        elif card.rank == 'A':
            self._handle_ace(actions, seen_actions, active_player_idx, card)
            self._handle_normal_card(actions, seen_actions, active_player_idx, card)
        elif card.rank == '4':
            self._handle_four(actions, seen_actions, active_player_idx, card)
            self._handle_normal_card(actions, seen_actions, active_player_idx, card)
        elif card.rank == 'J':
            self._handle_jack(actions, active_player_idx, card)
        elif card.rank == '7':
            self._handle_seven(actions, seen_actions, active_player_idx, card)
        else:
            self._handle_normal_card(actions, seen_actions, active_player_idx, card)

    def _handle_normal_card(self, actions: List['Action'],
                            seen_actions: Set[Tuple[str,str,Optional[int],Optional[int]]],
                            active_player_idx: int, card:Card) -> None:
        if card.rank=='K':
            num_moves=13
        elif card.rank=='Q':
            num_moves=12
        elif card.rank=='A':
            num_moves=11
        else:
            try:
                num_moves=int(card.rank)
            except:
                return
        for marble_idx, marble in enumerate(self.state.list_player[active_player_idx].list_marble):
            if marble.pos in self.KENNEL_POSITIONS[active_player_idx]:
                continue
            new_marble_pos = self._can_move_forward(active_player_idx, marble_idx, marble, num_moves)
            if new_marble_pos!=-1:
                action_data=ActionData(card=card, pos_from=marble.pos, pos_to=new_marble_pos)
                self._add_action(actions,seen_actions,action_data)

    def _handle_joker(self, actions:List[Action], seen_actions:Set[Tuple[str,str,Optional[int],Optional[int]]],
                      active_player_idx:int, card:Card)->None:
        marbles_in_kennel = [m for m in self.state.list_player[active_player_idx].list_marble
                             if m.pos in self.KENNEL_POSITIONS[active_player_idx]]
        if marbles_in_kennel and not self._is_start_position_occupied(active_player_idx):
            start_pos=self.START_POSITION[active_player_idx]
            act_data=ActionData(card=card, pos_from=marbles_in_kennel[0].pos, pos_to=start_pos)
            self._add_action(actions, seen_actions, act_data)
            for s in self.state.LIST_SUIT:
                for r in ['A','K']:
                    actions.append(Action(card=card, card_swap=Card(suit=s, rank=r)))

    def _handle_ace(self, actions:List[Action],
                    seen_actions:Set[Tuple[str,str,Optional[int],Optional[int]]],
                    active_player_idx:int, card:Card)->None:
        for marble_idx, marble in enumerate(self.state.list_player[active_player_idx].list_marble):
            if marble.pos in self.KENNEL_POSITIONS[active_player_idx]:
                continue
            if marble.pos == self.START_POSITION[active_player_idx] and not marble.is_save:
                pos_to_1=64+active_player_idx*8+4
            elif marble.pos<64:
                pos_to_1=(marble.pos+1)%64
            else:
                pos_to_1=marble.pos+1
            if self.check_move_validity(active_player_idx,marble_idx,pos_to_1):
                action_data=ActionData(card=card,pos_from=marble.pos,pos_to=pos_to_1)
                self._add_action(actions, seen_actions, action_data)

    def _handle_four(self, actions:List[Action],
                     seen_actions:Set[Tuple[str,str,Optional[int],Optional[int]]],
                     active_player_idx:int,card:Card)->None:
        for marble_idx, marble in enumerate(self.state.list_player[active_player_idx].list_marble):
            if marble.pos in self.KENNEL_POSITIONS[active_player_idx] or marble.pos in self.FINISH_POSITIONS[active_player_idx]:
                continue
            new_pos=marble.pos
            can_move_back=True
            for _ in range(4):
                new_pos=(new_pos-1+64)%64
                if not self.check_move_validity(active_player_idx,marble_idx,new_pos):
                    can_move_back=False
                    break
            if can_move_back:
                action_data=ActionData(card=card,pos_from=marble.pos,pos_to=new_pos)
                self._add_action(actions,seen_actions,action_data)

    def _handle_jack(self, actions:List[Action],
                     active_player_idx:int, card:Card)->None:
        idx_player=[active_player_idx]
        idx_other_players=[i for i in range(4) if i!=active_player_idx]
        can_swap=False
        for p1 in idx_player:
            for p2 in idx_other_players:
                for first_marble in self.state.list_player[p1].list_marble:
                    if (first_marble.pos not in self.KENNEL_POSITIONS[p1]
                        and first_marble.pos not in self.FINISH_POSITIONS[p1]):
                        for other_marble in self.state.list_player[p2].list_marble:
                            if (other_marble.pos not in self.KENNEL_POSITIONS[p2]
                                and other_marble.pos not in self.FINISH_POSITIONS[p2]
                                and not other_marble.is_save):
                                actions.append(Action(card=card,pos_from=first_marble.pos,pos_to=other_marble.pos))
                                actions.append(Action(card=card,pos_from=other_marble.pos,pos_to=first_marble.pos))
                                can_swap=True
        if not can_swap:
            my_player_idx=active_player_idx
            my_marbles=[m for m in self.state.list_player[my_player_idx].list_marble
                        if m.pos not in self.KENNEL_POSITIONS[my_player_idx]
                        and m.pos not in self.FINISH_POSITIONS[my_player_idx]]
            for mi,mj in combinations(my_marbles,2):
                actions.append(Action(card=card,pos_from=mi.pos,pos_to=mj.pos))
                actions.append(Action(card=card,pos_from=mj.pos,pos_to=mi.pos))

    def _handle_seven(self, actions:List[Action], seen_actions:Set[Tuple[str,str,Optional[int],Optional[int]]],
                      active_player_idx:int,card:Card)->None:
        for marble_idx, marble in enumerate(self.state.list_player[active_player_idx].list_marble):
            if marble.pos>=64:
                continue
            for steps_to_move in range(1,8):
                if self.can_move_steps(active_player_idx, marble_idx, steps_to_move, direction=1):
                    new_marble_pos=(marble.pos+steps_to_move)%64
                    action_data=ActionData(card=card,pos_from=marble.pos,pos_to=new_marble_pos)
                    self._add_action(actions, seen_actions, action_data)

    def deal_cards(self, num_cards_per_player: int) -> None:
        for p in self.state.list_player:
            p.list_card.clear()
        self.check_and_reshuffle()

        player_indices=(list(range(self.state.idx_player_active,self.state.cnt_player))+
                        list(range(0,self.state.idx_player_active)))

        for _ in range(num_cards_per_player):
            self.check_and_reshuffle()
            for idx in player_indices:
                self.check_and_reshuffle()
                card=self.state.list_card_draw.pop()
                self.state.list_player[idx].list_card.append(card)

    def check_and_reshuffle(self):
        if not self.state.list_card_draw and self.state.list_card_discard:
            self.state.list_card_draw.extend(self.state.list_card_discard)
            self.state.list_card_discard.clear()
            random.shuffle(self.state.list_card_draw)

    def start_new_round(self) -> None:
        self.state.cnt_round += 1
        pattern=[6,5,4,3,2]
        cnt_cards=pattern[(self.state.cnt_round-1)%5]

        self.state.idx_player_started=(self.state.idx_player_started+1)%self.state.cnt_player
        self.state.idx_player_active=(self.state.idx_player_started+self.state.cnt_round)%self.state.cnt_player
        self.state.bool_card_exchanged=False
        self.deal_cards(cnt_cards)
        self.state.card_active=None
        self.original_state_before_7=None
        self.out_of_cards_counter=0
        self.state.phase=GamePhase.RUNNING

    def _handle_no_action(self, active_player_index: int) -> None:
        if (
            self.state.card_active is not None
            and self.state.card_active.rank == "7"
            and self.state.steps_remaining_for_7 > 0
        ):
            if self.original_state_before_7 is not None:
                self.state = self.original_state_before_7
            self.original_state_before_7 = None
            return

        self.state.list_card_discard.extend(self.state.list_player[active_player_index].list_card)
        self.state.list_player[active_player_index].list_card.clear()
        self.out_of_cards_counter+=1

        self._change_active_player()

        if all(not p.list_card for p in self.state.list_player) and self.out_of_cards_counter==4:
            self.out_of_cards_counter=0
            self.start_new_round()

    def _change_active_player(self) -> None:
        self.state.idx_player_active=(self.state.idx_player_active+1)%self.state.cnt_player

    def _handle_card_exchange(self, action:Action) -> None:
        card_owner_idx=self.state.idx_player_active
        partner_idx=(card_owner_idx+2)%self.state.cnt_player
        self.state.list_player[card_owner_idx].list_card.remove(action.card)
        self.state.list_player[partner_idx].list_card.append(action.card)
        self.exchanges_done.append((card_owner_idx,action.card))
        if len(self.exchanges_done)==self.state.cnt_player:
            self.state.bool_card_exchanged=True
        self._change_active_player()

    def _is_card_exchange_action(self,action:Action)->bool:
        return (action.pos_from is None and action.pos_to is None and action.card_swap is None and not self.state.bool_card_exchanged)

    def _handle_jack_action(self, action:Action)->None:
        marble_from,marble_to=None,None
        for player in self.state.list_player:
            for m in player.list_marble:
                if m.pos==action.pos_from:
                    marble_from=m
                if m.pos==action.pos_to:
                    marble_to=m
        if marble_from and marble_to:
            marble_from.pos,marble_to.pos=marble_to.pos,marble_from.pos
        else:
            raise ValueError("Invalid marble positions for swapping.")

    def _handle_normal_move(self, action:Action, active_player_index:int)->None:
        for marble in self.state.list_player[active_player_index].list_marble:
            if marble.pos==action.pos_from:
                if action.pos_to is not None:
                    self._move_marble(marble, action.pos_to, active_player_index)
                break

    def _move_marble(self, marble:Marble, pos_to:int,active_player_index:int)->None:
        for p_idx,pl in enumerate(self.state.list_player):
            for om in pl.list_marble:
                if om.pos==pos_to:
                    om.pos=self.KENNEL_POSITIONS[p_idx][0]
                    om.is_save=False
        marble.pos=pos_to
        if pos_to==self.START_POSITION[active_player_index]:
            marble.is_save=True

    def _move_card_to_discard(self, action:Action, active_player_index:int)->None:
        if action.card in self.state.list_player[active_player_index].list_card:
            self.state.list_player[active_player_index].list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)

    def _handle_card_swap(self,action:Action)->None:
        if (action.pos_from is None and action.pos_to is None and
            action.card_swap is None and not self.state.bool_card_exchanged):
            card_owner_idx=self.state.idx_player_active
            partner_idx=(card_owner_idx+2)%self.state.cnt_player
            self.state.list_player[card_owner_idx].list_card.remove(action.card)
            self.state.list_player[partner_idx].list_card.append(action.card)
            self.exchanges_done.append((card_owner_idx,action.card))
            if len(self.exchanges_done)==self.state.cnt_player:
                self.state.bool_card_exchanged=True
            self.state.idx_player_active=(self.state.idx_player_active+1)%self.state.cnt_player

    def _handle_seven_action(self, action:Action, active_player_index:int)->None:
        if self.state.card_active is None or self.state.steps_remaining_for_7==7:
            self.original_state_before_7=self.state.model_copy(deep=True)
            self.state.card_active=action.card
            self.state.steps_remaining_for_7=7

        if (self.state.card_active.suit!=action.card.suit or self.state.card_active.rank!=action.card.rank):
            self.state=self.original_state_before_7
            self.original_state_before_7=None
            self._change_active_player()
            return

        steps_moved=self.calculate_7_steps(action.pos_from,action.pos_to)
        if steps_moved<=0 or steps_moved>self.state.steps_remaining_for_7:
            self.state=self.original_state_before_7
            self.original_state_before_7=None
            self._change_active_player()
            return

        marble_moved=False
        for marble in self.state.list_player[active_player_index].list_marble:
            if marble.pos==action.pos_from:
                for step in range(1,steps_moved+1):
                    intermediate_pos = (marble.pos+step)%64 if marble.pos<64 else marble.pos+step
                    self.send_home_if_passed(intermediate_pos, active_player_index)
                marble.pos=action.pos_to if action.pos_to is not None else 0
                marble_moved=True
                break

        if not marble_moved:
            raise ValueError("No marble found at pos_from for 7-move.")

        self.state.steps_remaining_for_7-=steps_moved
        if self.state.steps_remaining_for_7==0:
            active_pl=self.state.list_player[active_player_index]
            if action.card in active_pl.list_card:
                active_pl.list_card.remove(action.card)
                self.state.list_card_discard.append(action.card)
            self.state.card_active=None
            self.original_state_before_7=None
            self._change_active_player()

    def _can_move_forward(self, player_idx:int, marble_idx:int, marble:Marble, steps:int)->int:
        if self.can_move_steps(player_idx, marble_idx, steps, direction=1):
            final_pos=self.compute_final_position(marble.pos, steps, player_idx)
            return final_pos
        return -1

    def _add_action(self,actions:List[Action],seen_actions:Set[Tuple[str,str,Optional[int],Optional[int]]],action_data:ActionData):
        action_key=(action_data.card.suit,action_data.card.rank,action_data.pos_from,action_data.pos_to)
        if action_key not in seen_actions:
            seen_actions.add(action_key)
            actions.append(Action(card=action_data.card,pos_from=action_data.pos_from,pos_to=action_data.pos_to))


class RandomPlayer(Player):  # pragma: no cover
    def select_action(self, state:GameState, actions:List[Action])->Optional[Action]:
        if actions:
            return random.choice(actions)
        return None

    def get_player_type(self)->str:
        return "Random"


if __name__ == '__main__':  # pragma: no cover
    game = Dog()
