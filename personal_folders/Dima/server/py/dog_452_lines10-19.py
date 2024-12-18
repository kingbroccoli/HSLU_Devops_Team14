from server.py.game import (Game, Player)
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random


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
    pos_from: Optional[int] = None
    pos_to: Optional[int] = None
    card_swap: Optional[Card] = None


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


class GameState(BaseModel):
    # ... (previous code remains the same)

    LIST_CARD: ClassVar[List[Card]] = [
        # Regular cards (no multiplication by 2 to maintain 86 cards)
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
    ]

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
        """Initialize new game"""
        self.reset()

    def reset(self) -> None:
        """Reset game to initial state"""
        initial_deck = list(GameState.LIST_CARD)
        random.shuffle(initial_deck)

        self.state = GameState(
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[
                PlayerState(
                    name=f"Player{i + 1}",
                    list_card=[],
                    list_marble=[Marble(pos=64 + i * 8 + j, is_save=False) for j in range(4)]
                ) for i in range(4)
            ],
            list_card_draw=initial_deck,
            list_card_discard=[],
            card_active=None
        )
        self._deal_cards()

    def set_state(self, state: GameState) -> None:
        """Set game state"""
        self.state = state

    def get_state(self) -> GameState:
        """Get current game state"""
        return self.state

    def print_state(self) -> None:
        """Print current game state"""
        print(f"Round: {self.state.cnt_round}")
        print(f"Phase: {self.state.phase}")
        print(f"Active Player: {self.state.idx_player_active}")
        for idx, player in enumerate(self.state.list_player):
            print(f"\nPlayer {idx}:")
            print(f"Cards: {[f'{c.suit}{c.rank}' for c in player.list_card]}")
            print(f"Marbles: {[m.pos for m in player.list_marble]}")

    def get_list_action(self) -> List[Action]:
        """Get list of possible actions for active player"""
        actions = []
        player = self.state.list_player[self.state.idx_player_active]

        # Card exchange phase at start of round
        if not self.state.bool_card_exchanged:
            for card in player.list_card:
                actions.append(Action(
                    card=card,
                    card_swap=card
                ))
            return actions

        # Handle active Joker
        if self.state.card_active and self.state.card_active.rank == 'JKR':
            return self._get_joker_actions()

        # Normal play phase
        for card in player.list_card:
            if card.rank == 'JKR' and not self.state.card_active:
                # First Joker action - specify card to imitate
                for rank in GameState.LIST_RANK[:-1]:  # Exclude Joker
                    for suit in GameState.LIST_SUIT:
                        actions.append(Action(
                            card=card,
                            card_swap=Card(suit=suit, rank=rank)
                        ))
                continue

            # Get card-specific actions
            if card.rank in ['A', 'K']:
                actions.extend(self._get_start_actions(card))
            if card.rank == 'J':
                actions.extend(self._get_swap_actions(card))
            elif card.rank == '7':
                actions.extend(self._get_seven_actions(card))
            elif card.rank == '4':
                actions.extend(self._get_movement_actions(card, allow_backward=True))
            else:
                actions.extend(self._get_movement_actions(card))

        # Remove duplicates while preserving order
        return list({str(a.dict()): a for a in actions}.values())

    def apply_action(self, action: Action) -> None:
        """Apply action to game state"""
        if action is None:
            self._handle_no_action()
            return

        player = self.state.list_player[self.state.idx_player_active]
        initial_total_cards = self._count_total_cards()

        # Handle card exchange
        if not self.state.bool_card_exchanged and action.card_swap:
            self._handle_card_exchange(action)
            return

        # Handle Joker first action
        if action.card.rank == 'JKR' and action.card_swap and not self.state.card_active:
            self.state.card_active = action.card_swap
            return

        # Apply marble movement
        if action.pos_from is not None and action.pos_to is not None:
            self._move_marble(action)

        # Remove used card
        if action.card in player.list_card:
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)

        # Reset active card
        self.state.card_active = None

        # Verify card count hasn't changed
        assert initial_total_cards == self._count_total_cards(), "Card count mismatch"

        # Move to next player
        self._next_player()

    def get_player_view(self, idx_player: int) -> GameState:
        """Get masked state for specified player"""
        masked_state = self.state.copy(deep=True)

        # Hide other players' cards
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = [Card(suit='?', rank='?') for _ in player.list_card]

        return masked_state

    def _deal_cards(self) -> None:
        """Deal cards to players"""
        cards_per_player = 7 - ((self.state.cnt_round - 1) % 5)

        # Reshuffle if needed
        if len(self.state.list_card_draw) < cards_per_player * 4:
            self.state.list_card_draw.extend(self.state.list_card_discard)
            self.state.list_card_discard = []
            random.shuffle(self.state.list_card_draw)

        # Deal cards
        for player in self.state.list_player:
            player.list_card = []
            for _ in range(cards_per_player):
                if self.state.list_card_draw:
                    player.list_card.append(self.state.list_card_draw.pop())

    def _get_movement_actions(self, card: Card, allow_backward: bool = False) -> List[Action]:
        """Get possible movement actions for a card"""
        actions = []
        player = self.state.list_player[self.state.idx_player_active]

        # Get movement distance based on card rank
        distances = []
        if card.rank.isdigit():
            distances = [int(card.rank)]
        elif card.rank == 'Q':
            distances = [12]
        elif card.rank == 'K':
            distances = [13]
        elif card.rank == 'A':
            distances = [1, 11]

        # Add backward movement for 4
        if allow_backward:
            distances.extend([-d for d in distances])

        # Check each marble for possible moves
        for marble in player.list_marble:
            if marble.pos < 64:  # Only move marbles on the board
                for dist in distances:
                    new_pos = (marble.pos + dist) % 64
                    if self._is_valid_move(marble.pos, new_pos):
                        actions.append(Action(
                            card=card,
                            pos_from=marble.pos,
                            pos_to=new_pos
                        ))

        return actions

    def _get_start_actions(self, card: Card) -> List[Action]:
        """Get possible actions to move out of kennel"""
        actions = []
        player = self.state.list_player[self.state.idx_player_active]
        start_pos = (self.state.idx_player_active * 16) % 64  # Starting position for current player

        # Check each marble in kennel
        for marble in player.list_marble:
            if marble.pos >= 64:  # Marble is in kennel
                if self._is_valid_move(marble.pos, start_pos):
                    actions.append(Action(
                        card=card,
                        pos_from=marble.pos,
                        pos_to=start_pos
                    ))

        return actions

    def _get_seven_actions(self, card: Card) -> List[Action]:
        """Get possible actions for seven card"""
        actions = []
        player = self.state.list_player[self.state.idx_player_active]
        remaining_steps = 7 if not self.state.card_active else int(self.state.card_active.rank)

        for marble in player.list_marble:
            if marble.pos < 64:  # Only move marbles on the board
                for steps in range(1, remaining_steps + 1):
                    new_pos = (marble.pos + steps) % 64
                    if self._is_valid_move(marble.pos, new_pos):
                        actions.append(Action(
                            card=card,
                            pos_from=marble.pos,
                            pos_to=new_pos
                        ))

        return actions

    def _get_swap_actions(self, card: Card) -> List[Action]:
        """Get possible swap actions for Jack"""
        actions = []
        player = self.state.list_player[self.state.idx_player_active]

        # Check each marble for possible swaps
        for marble in player.list_marble:
            if marble.pos < 64:  # Only swap marbles on the board
                # Check other players' marbles
                for other_player in self.state.list_player:
                    if other_player != player:
                        for other_marble in other_player.list_marble:
                            if other_marble.pos < 64 and not other_marble.is_save:
                                actions.append(Action(
                                    card=card,
                                    pos_from=marble.pos,
                                    pos_to=other_marble.pos
                                ))

        return actions

    def _get_joker_actions(self) -> List[Action]:
        """Get possible actions for active Joker"""
        if not self.state.card_active:
            return []

        # Get actions as if it were the imitated card
        if self.state.card_active.rank in ['A', 'K']:
            return self._get_start_actions(self.state.card_active)
        elif self.state.card_active.rank == 'J':
            return self._get_swap_actions(self.state.card_active)
        elif self.state.card_active.rank == '7':
            return self._get_seven_actions(self.state.card_active)
        elif self.state.card_active.rank == '4':
            return self._get_movement_actions(self.state.card_active, allow_backward=True)
        else:
            return self._get_movement_actions(self.state.card_active)

    def _is_valid_move(self, from_pos: int, to_pos: int) -> bool:
        """Check if move is valid"""
        # Check if target position is occupied by teammate's marble
        player = self.state.list_player[self.state.idx_player_active]
        partner = self.state.list_player[(self.state.idx_player_active + 2) % 4]

        for marble in player.list_marble + partner.list_marble:
            if marble.pos == to_pos:
                return False

        return True

    def _move_marble(self, action: Action) -> None:
        """Move marble and handle consequences"""
        # Find and move the marble
        for marble in self.state.list_player[self.state.idx_player_active].list_marble:
            if marble.pos == action.pos_from:
                marble.pos = action.pos_to
                marble.is_save = self._is_position_safe(action.pos_to)
                break

        # Handle marble elimination
        self._handle_marble_elimination(action.pos_to)

        # Check win condition
        if self._check_win():
            self.state.phase = GamePhase.FINISHED

    def _handle_marble_elimination(self, pos: int) -> None:
        """Handle marble elimination at position"""
        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.pos == pos and not marble.is_save:
                    # Return marble to kennel
                    marble.pos = 64 + self.state.list_player.index(player) * 8
                    marble.is_save = False

    def _is_position_safe(self, pos: int) -> bool:
        """Check if position is safe"""
        return pos % 16 == 0 or pos >= 64  # Starting positions and kennel are safe

    def _check_win(self) -> bool:
        """Check if current team has won"""
        player = self.state.list_player[self.state.idx_player_active]
        partner = self.state.list_player[(self.state.idx_player_active + 2) % 4]

        return (all(m.pos >= 64 for m in player.list_marble) and
                all(m.pos >= 64 for m in partner.list_marble))

    def _count_total_cards(self) -> int:
        """Count total cards in game"""
        return (len(self.state.list_card_draw) +
                len(self.state.list_card_discard) +
                sum(len(p.list_card) for p in self.state.list_player))

    def _handle_no_action(self) -> None:
        """Handle case when no action is possible"""
        player = self.state.list_player[self.state.idx_player_active]
        self.state.list_card_discard.extend(player.list_card)
        player.list_card = []
        self._next_player()

    def _next_player(self) -> None:
        """Move to next player or round"""
        if all(len(p.list_card) == 0 for p in self.state.list_player):
            self._start_new_round()
        else:
            self.state.idx_player_active = (self.state.idx_player_active + 1) % 4

    def _start_new_round(self) -> None:
        """Start a new round"""
        self.state.cnt_round += 1
        self.state.bool_card_exchanged = False
        self.state.idx_player_started = (self.state.idx_player_started + 1) % 4
        self.state.idx_player_active = self.state.idx_player_started
        self._deal_cards()

    def _handle_card_exchange(self, action: Action) -> None:
        """Handle card exchange at start of round"""
        player = self.state.list_player[self.state.idx_player_active]
        partner_idx = (self.state.idx_player_active + 2) % 4
        partner = self.state.list_player[partner_idx]

        player.list_card.remove(action.card)
        partner.list_card.append(action.card)

        if self.state.idx_player_active == (self.state.idx_player_started + 3) % 4:
            self.state.bool_card_exchanged = True

        self.state.idx_player_active = (self.state.idx_player_active + 1) % 4


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    game = Dog()
    player = RandomPlayer()

    while game.get_state().phase != GamePhase.FINISHED:
        actions = game.get_list_action()
        action = player.select_action(game.get_state(), actions)
        if action:
            game.apply_action(action)
        game.print_state()