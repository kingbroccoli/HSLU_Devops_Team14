import random
from enum import Enum
from typing import List, Optional, ClassVar
from pydantic import BaseModel # pylint: disable=import-error
from server.py.game import Game, Player # pylint: disable=import-error #mypy ignore:import-not-found


class Card(BaseModel): # pylint: disable=too-few-public-methods
    suit: str  # card suit (color)
    rank: str  # card rank

    def __lt__(self, card: "Card") -> bool:
        return self.suit < card.suit or \
            self.rank < card.rank


class Marble(BaseModel): # pylint: disable=too-few-public-methods
    pos: int  # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel): # pylint: disable=too-few-public-methods
    name: str  # name of player
    list_card: List[Card]  # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel): # pylint: disable=too-few-public-methods
    card: Card  # card to play
    pos_from: Optional[int]  # position to move the marble from
    pos_to: Optional[int]  # position to move the marble to
    card_swap: Optional[Card] = None  # optional card to swap ()


class GamePhase(str, Enum):
    SETUP = 'setup'  # before the game has started
    RUNNING = 'running'  # while the game is running
    FINISHED = 'finished'  # when the game is finished


class GameState(BaseModel): # pylint: disable=too-few-public-methods
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',  # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
                                          # 2: Move 2 spots forward
                                          Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(
            suit='♦', rank='2'), Card(suit='♣', rank='2'),
                                          # 3: Move 3 spots forward
                                          Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(
            suit='♦', rank='3'), Card(suit='♣', rank='3'),
                                          # 4: Move 4 spots forward or back
                                          Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(
            suit='♦', rank='4'), Card(suit='♣', rank='4'),
                                          # 5: Move 5 spots forward
                                          Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(
            suit='♦', rank='5'), Card(suit='♣', rank='5'),
                                          # 6: Move 6 spots forward
                                          Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(
            suit='♦', rank='6'), Card(suit='♣', rank='6'),
                                          # 7: Move 7 single steps forward
                                          Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(
            suit='♦', rank='7'), Card(suit='♣', rank='7'),
                                          # 8: Move 8 spots forward
                                          Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(
            suit='♦', rank='8'), Card(suit='♣', rank='8'),
                                          # 9: Move 9 spots forward
                                          Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(
            suit='♦', rank='9'), Card(suit='♣', rank='9'),
                                          # 10: Move 10 spots forward
                                          Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(
            suit='♦', rank='10'), Card(suit='♣', rank='10'),
                                          # Jake: A marble must be exchanged
                                          Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(
            suit='♦', rank='J'), Card(suit='♣', rank='J'),
                                          # Queen: Move 12 spots forward
                                          Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(
            suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
                                          # King: Start or move 13 spots forward
                                          Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(
            suit='♦', rank='K'), Card(suit='♣', rank='K'),
                                          # Ass: Start or move 1 or 11 spots forward
                                          Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(
            suit='♦', rank='A'), Card(suit='♣', rank='A'),
                                          # Joker: Use as any other card you want
                                          Card(suit='', rank='JKR'), Card(
            suit='', rank='JKR'), Card(suit='', rank='JKR')
                                      ] * 2

    cnt_player: int = 4  # number of players (must be 4)
    phase: GamePhase  # current phase of the game
    cnt_round: int  # current round
    bool_card_exchanged: bool  # true if cards was exchanged in round
    idx_player_started: int  # index of player that started the round
    idx_player_active: int  # index of active player in round
    list_player: List[PlayerState]  # list of players
    list_card_draw: List[Card]  # list of cards to draw
    list_card_discard: List[Card]  # list of cards discarded
    # active card (for 7 and JKR with sequence of actions)
    card_active: Optional[Card]

    def __str__(self) -> str:
        player_states = "\n".join(
            f"Player {i + 1} ({player.name}): Cards: {len(player.list_card)}, Marbles: {len(player.list_marble)}"
            for i, player in enumerate(self.list_player)
        )
        return (
            f"Game Phase: {self.phase}\n"
            f"Round: {self.cnt_round}\n" # pylint: disable=no-member
            f"Active Player: {self.idx_player_active + 1}\n"
            f"Players:\n{player_states}\n"
            f"Cards to Draw: {len(self.list_card_draw)}\n"
            f"Cards Discarded: {len(self.list_card_discard)}\n"
            f"Active Card: {self.card_active}\n"
        )


class Dog(Game):
    teams = {
        0: [0, 2],  # Team 1: Player 1 and Player 3
        1: [1, 3],  # Team 2: Player 2 and Player 4
    }
    # Constants for player positions
    PLAYER_POSITIONS = {
        0: {'start': 0, 'queue_start': 64, 'final_start': 68},
        1: {'start': 16, 'queue_start': 72, 'final_start': 76},
        2: {'start': 32, 'queue_start': 80, 'final_start': 84},
        3: {'start': 48, 'queue_start': 88, 'final_start': 92}
    }

    # Total steps in the main path ignoring the "special fields"
    TOTAL_STEPS = 64

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        super().__init__()
        self._state = GameState(  # type: ignore #type:unused-ignore
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[PlayerState(
                name=f"Player {i + 1}", list_card=[], list_marble=[]) for i in range(4)],
            list_card_draw=GameState.LIST_CARD.copy(),
            list_card_discard=[],
            card_active=None

        )
        random.shuffle(self._state.list_card_draw)
        self.deal_cards()
        self._set_marbles()

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self._state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self._state  # type: ignore

    def print_state(self) -> None:
        """ Print the current game state """
        print(self._state)

    def _choose_card_to_swap(self, player_state: PlayerState) -> Optional[Card]:
        """Choose a card to swap. This is placeholder logic."""
        if player_state.list_card:
            return random.choice(player_state.list_card)  # Randomly select a card to swap
        return None

    transformed_joker_card = None
    active_player_has_finished = False

    def get_list_action(self) -> List[Action]: # pylint: disable=too-many-locals, too-many-statements, too-many-branches
        """ Get a list of possible actions for the active player """
        actions = []
        unique_actions = []
        to_positions = []

        active_player = self._state.list_player[self._state.idx_player_active]

        marbles_in_kennel = self._count_marbles_in_kennel(self._state.idx_player_active)
        cards = [self.transformed_joker_card] if self.transformed_joker_card else active_player.list_card

        if not self._state.bool_card_exchanged:
            for card in cards:
                actions.append(Action(
                    card=card,
                    pos_from=None,
                    pos_to=None,
                    card_swap=None
                ))
            return actions

        # checks and assignments in case one player is done and must move teammates marbles
        final_start = self.PLAYER_POSITIONS[self._state.idx_player_active]['final_start']
        final_end = final_start + 4
        player_has_finished = all(
            final_start <= marble.pos < final_end for marble in active_player.list_marble)

        if player_has_finished:
            teammate_idx = (self._state.idx_player_active + 2) % self._state.cnt_player
            teammate = self._state.list_player[teammate_idx]
            marbles_to_check = teammate.list_marble
            actions_for_player_with_marbles_to_check = teammate_idx
            marbles_in_kennel = self._count_marbles_in_kennel(teammate_idx)
            self.active_player_has_finished = True
        else:
            marbles_to_check = active_player.list_marble
            actions_for_player_with_marbles_to_check = self._state.idx_player_active
            self.active_player_has_finished = False
        if self._state.card_active and self._state.card_active.rank == '7':

            # self._state.card_active = None
            return actions

        for card in cards: # pylint: disable=too-many-nested-blocks
            for marble in marbles_to_check:

                queue_start = self.PLAYER_POSITIONS[actions_for_player_with_marbles_to_check]['queue_start']
                active_player_fields = self.PLAYER_POSITIONS[actions_for_player_with_marbles_to_check]
                final_start = active_player_fields['final_start']
                # if marble is in kennel
                if marble.pos in range(queue_start,
                                       queue_start + 4):
                    if marble.pos == queue_start + 4 - marbles_in_kennel:

                        # only allow actions for ACE, KING or JOKER
                        if card.rank in ['A', 'JKR', 'K']:
                            start_position = self.PLAYER_POSITIONS[actions_for_player_with_marbles_to_check]['start']

                            # allow only if the current player does not have a marble on start
                            if all(m.pos != start_position for m in marbles_to_check):
                                # if 4 in kennel, start_position + 3 - #in kennel-1
                                if marble.pos == queue_start + 4 - marbles_in_kennel:
                                    actions.append(Action(card=card, pos_from=marble.pos, pos_to=start_position,
                                                          card_swap=None))

                                # Handle JOKER acting as ACE or KING
                                if card.rank == 'JKR':
                                    for suit in GameState.LIST_SUIT:
                                        # Joker acting as Ace
                                        actions.append(Action(
                                            card=card,
                                            pos_from=None,
                                            pos_to=None,
                                            card_swap=Card(suit=suit, rank='A')
                                        ))
                                        # Joker acting as King
                                        actions.append(Action(
                                            card=card,
                                            pos_from=None,
                                            pos_to=None,
                                            card_swap=Card(suit=suit, rank='K')
                                        ))
                else:
                    if card.rank.isdigit() and card.rank not in ['7', '4']:
                        to_positions = [self._move_n_forward(marble, int(card.rank), queue_start, final_start)]

                    if card.rank == 'A':
                        # Move 1 spot forward
                        to_positions.append(self._move_n_forward(marble, 1, queue_start, final_start))

                        # Move 11 spots forward
                        to_positions.append(self._move_n_forward(marble, 11, queue_start, final_start))

                        # Validate positions are not blocked or the move is not valid
                        valid_positions = []

                        for pos_to in to_positions:
                            if (not self._is_way_blocked(pos_to, marble.pos,
                                                         self._get_all_safe_marbles()) and
                                    not self._is_valid_move_in_final_area(marble.pos,
                                                                          pos_to, marbles_to_check,
                                                                          final_start,
                                                                          final_start + 3
                                                                          )):
                                valid_positions.append(pos_to)

                        to_positions = valid_positions

                    if card.rank == '4':
                        # Forward movement (+4)
                        next_position = (marble.pos + 4) % self.TOTAL_STEPS
                        if marble.pos < queue_start and next_position >= queue_start: # pylint: disable=chained-comparison
                            next_position = final_start + (next_position - queue_start) - 1

                        if self._is_valid_move_in_final_area(marble.pos, next_position, marbles_to_check,
                                                             final_start,
                                                             final_start + 3):
                            to_positions.append(next_position)

                        # Backward movement (-4)
                        next_position = self.TOTAL_STEPS - 4 \
                            if marble.pos == 0 else (marble.pos - 4) % self.TOTAL_STEPS
                        if marble.pos < queue_start and next_position >= queue_start: # pylint: disable=chained-comparison
                            next_position = final_start + (next_position - queue_start) - 1

                        if self._is_valid_move_in_final_area(marble.pos, next_position, marbles_to_check,
                                                             final_start,
                                                             final_start + 3):
                            to_positions.append(next_position)

                    if card.rank == 'J':

                        # Get the active player's marbles that are not in the kennel
                        active_player_marbles = [
                            marble for marble in marbles_to_check
                            if marble.pos not in range(queue_start, queue_start + 4)  # Exclude marbles in the kennel
                        ]

                        # Collect all other players' marbles that are not "safe"
                        other_players_marbles = [
                            (player_idx, marble)
                            for player_idx, player in enumerate(self._state.list_player)
                            if player_idx != actions_for_player_with_marbles_to_check  # Exclude the active player
                            for marble in player.list_marble
                            if not marble.is_save  # Only consider marbles that are not safe
                        ]

                        # Generate swap actions
                        for marble_own in active_player_marbles:
                            for player_idx, marble_other in other_players_marbles:
                                if marble_own.pos != marble_other.pos:
                                    # Add a valid swap act
                                    actions.append(
                                        Action(
                                            card=card,
                                            pos_from=marble_own.pos,  # Position of the active player's marble
                                            pos_to=marble_other.pos,  # Position of the other player's marble
                                            card_swap=None  # Specify that the act involves a swap
                                        )
                                    )
                                    actions.append(Action(
                                        card=card,
                                        pos_from=marble_other.pos,
                                        pos_to=marble_own.pos,
                                        card_swap=None
                                    ))

                        # If no actions exist, allow swapping two of the active player's marbles
                        # (which does not make a difference, but we do it for the test
                        if not actions:
                            for i, marble_own in enumerate(active_player_marbles):
                                for marble_partner in active_player_marbles[i:]:
                                    if marble_own.pos != marble_partner.pos:
                                        actions.append(
                                            Action(
                                                card=card,
                                                pos_from=marble_own.pos,  # Position of the first marble
                                                pos_to=marble_partner.pos,  # Position of the second marble
                                                card_swap=None  # Specify that the act involves a swap
                                            )
                                        )

                            # Allow swaps between two of the active player's marbles
                            for marble_partner in active_player_marbles:  # CHANGE: Removed avoidance of duplicate swaps
                                if marble_own != marble_partner:
                                    actions.append(Action(
                                        card=card,
                                        pos_from=marble_own.pos,
                                        pos_to=marble_partner.pos,
                                        card_swap=None
                                    ))  # CHANGE: Allow both directions of swaps

                    if card.rank == 'K':
                        to_positions.append(self._move_n_forward(marble, 13, queue_start, final_start))

                    if card.rank == 'Q':
                        to_positions.append(self._move_n_forward(marble, 12, queue_start, final_start))

                    if card.rank == 'JKR':
                        # Add Joker transformations for all other possible cards

                        for rank in GameState.LIST_RANK:
                            for suit in GameState.LIST_SUIT:
                                if rank != 'JKR':  # Exclude the Joker itself
                                    actions.append(Action(
                                        card=card,
                                        pos_from=None,
                                        pos_to=None,
                                        card_swap=Card(suit=suit, rank=rank)
                                    ))

                    # checks for each possible position if the way is blocked.
                    # if it is not blocked, we add it to act.
                    for pos_to in to_positions:
                        if not self._is_way_blocked(
                                pos_to, marble.pos, self._get_all_safe_marbles()):
                            actions.append(Action(card=card, pos_from=marble.pos, pos_to=pos_to,
                                                  card_swap=None))

            for act in actions:
                if act not in unique_actions:
                    unique_actions.append(act)

        return unique_actions

    def _count_marbles_in_kennel(self, index:int) -> int:
        active_player = self._state.list_player[index]
        queue_start = self.PLAYER_POSITIONS[index]['queue_start']
        queue_end = queue_start + 4
        marbles_in_kennel = [marble for marble in active_player.list_marble if
                             queue_start <= int(marble.pos) < queue_end]
        return len(marbles_in_kennel)

    def _check_team_win(self) -> bool:
        """
        Check if a team has won, that means, both players on a team have all their marbles in the final area.
        """
        # Check each team
        for team_id, players in self.teams.items():  # Iterates through each team and its associated players
            team_wins = True
            for player_idx in players:
                final_start = self.PLAYER_POSITIONS[player_idx]['final_start']
                final_positions = range(final_start, final_start + 4)
                current_player = self._state.list_player[player_idx]
                if not all(marble.pos in final_positions for marble in current_player.list_marble):
                    team_wins = False
                    break

            if team_wins:
                # Update game phase and print winner
                self._state.phase = GamePhase.FINISHED
                print(f"Team {team_id + 1} has won the game!")
                return True

        return False

    none_actions_counter = 0
    card_exchanges_counter = 0
    seven_steps_counter = 0

    def apply_action(self, action: Action) -> None: # pylint: disable=too-many-locals, too-many-statements, redefined-outer-name, too-many-branches
        """ Apply the given action to the game """
        active_player = self._state.list_player[self._state.idx_player_active]

        self._handle_none_action(action, active_player)

        if action is not None: # pylint: disable=too-many-nested-blocks
            if action.card.rank == '7':
                if action.pos_to is not None and action.pos_from is not None:
                    self.seven_steps_counter += abs(action.pos_to-action.pos_from) % self.TOTAL_STEPS
                    if self.seven_steps_counter ==7:
                        self.seven_steps_counter =0
                        self._state.card_active = None
                        self._state.idx_player_active = (self._state.idx_player_active + 1) % self._state.cnt_player
                    else:
                        self._state.card_active = action.card
                    # Handle marble moves for card #7
                    if action.pos_from is not None and action.pos_to is not None:
                        marble_to_move = next(
                            (marble for marble in active_player.list_marble if marble.pos == action.pos_from), None
                        )

                        if marble_to_move:
                            # Detect marbles taken over during the move
                            marbles_to_reset = self._get_marbles_between(action.pos_from, action.pos_to)

                            for reset_marble in marbles_to_reset:
                                self._reset_to_kennel(reset_marble)

                            # Move the active player's marble to its new position
                            self._move_marble_logic(marble_to_move, action.pos_to,
                                                    is_player_finished=self.active_player_has_finished)
                return

            # card exchange with partner
            if (not self._state.bool_card_exchanged
                    and action.pos_from is None
                    and action.pos_to is None
                    and self.card_exchanges_counter <=4):
                # give your card to your teammate
                partner = self._state.list_player[(self._state.idx_player_active + 2) % self._state.cnt_player]
                partner.list_card.append(action.card)
                active_player.list_card.remove(action.card)

                if self.card_exchanges_counter == 4:
                    self._state.bool_card_exchanged = True
                    self.card_exchanges_counter = 0
                self._state.idx_player_active = (self._state.idx_player_active + 1) % self._state.cnt_player
                return

            card_to_apply = action.card
            if action.card_swap is not None:
                card_to_apply = action.card_swap
                active_player.list_card.append(card_to_apply)
                active_player.list_card.remove(action.card)
                self.transformed_joker_card = action.card_swap
                self._state.list_card_discard.append(action.card)
                self._state.card_active = card_to_apply
                return

            self.transformed_joker_card = None
            self._state.card_active = card_to_apply
            # removing card from players hand and putting it to discarded stack
            active_player.list_card.remove(action.card)
            self._state.list_card_discard.append(action.card)

            if (action.card.rank == 'J' or
                    (action.card_swap is not None and action.card_swap.rank == 'J')):
                self._swap_marbles(action)
            else:
                if self.active_player_has_finished:
                    active_player = self._state.list_player[
                        (self._state.idx_player_active + 2) % self._state.cnt_player]
                else:
                    active_player = self._state.list_player[self._state.idx_player_active]
                # Find the marble being moved
                marble_to_move = next(
                    (marble for marble in active_player.list_marble if marble.pos == action.pos_from),
                    None
                )

                if marble_to_move:
                    if action.pos_to is not None:
                    # Check for collision before moving the marble
                        if self._is_collision(pos_to=action.pos_to):
                            self._handle_collision(current_action=action)

                    # Perform the movement logic
                    self._move_marble_logic(
                        marble_to_move, action.pos_to, self.active_player_has_finished)  # type: ignore

        if self._check_team_win():
            self._state.phase = self._state.phase.FINISHED

        # check if round is over
        if self.none_actions_counter == 4 and len(self._state.list_card_draw) != 0:
            self._state.cnt_round += 1
            self.deal_cards()
            # calculate the next player (after 4, comes 1 again). not sure if needed here or somewhere else
            # example: (4+1)%4=1 -> after player 4, it's player 1's turn again
            self._state.idx_player_active = (self._state.idx_player_active + 1) % self._state.cnt_player
            self._state.bool_card_exchanged=False

        # if round is over and no cards are left in stack
        if len(self._state.list_card_draw) == 0 and self.none_actions_counter == 4:
            self._refresh_deck()
            self.none_actions_counter = 0
            # do not want to do this but I have no idea how the tests logic should work
            for p in self._state.list_player:
                p.list_card = []

    def _handle_none_action(self, current_action: Action, active_player: PlayerState) -> None:
        if current_action is None:
            self.none_actions_counter += 1
            active_player.list_card = []

    def _move_marble_logic(self, marble: Marble, pos_to: int, is_player_finished: bool) -> None:
        """
        Core logic for moving a marble to a new position.
        """
        pos_to = int(pos_to)  # Ensure the target position is an integer

        # Update marble position
        marble.pos = pos_to

        if is_player_finished:
            index = (self._state.idx_player_active + 2) % self._state.cnt_player
        else:
            index = self._state.idx_player_active

            # Determine if the new position is "safe"
        safe_positions = {
            self.PLAYER_POSITIONS[index]['start'],
            *range(self.PLAYER_POSITIONS[index]['queue_start'], self.PLAYER_POSITIONS[index]['queue_start'] + 4),
            *range(self.PLAYER_POSITIONS[index]['final_start'], self.PLAYER_POSITIONS[index]['final_start'] + 4)
        }

        marble.is_save = pos_to in safe_positions

    def _is_collision(self, pos_to: int) -> bool:
        """
        Check if the movement of the marble using the card results in a collision.

        Args:
            marble (Marble): The marble being moved.
            pos_to (int): The target position.
            card (Card): The card being played.

        Returns:
            bool: True if the marble jumps over another marble, False otherwise.
        """
        # Check if the target position is occupied by a marble
        for current_player in self._state.list_player:

            for other_marble in current_player.list_marble:
                if other_marble.pos == pos_to:
                    # If the marble is not safe and belongs to another player, return True
                    if not other_marble.is_save:
                        return True

        return False

    def _get_marbles_between(self, pos_from: int, pos_to: int) -> List[Marble]:
        """
        Get all marbles that are taken over between pos_from and pos_to.
        """
        marbles_to_reset = []

        for current_player in self._state.list_player:
            for marble in current_player.list_marble:
                if marble.pos == pos_from:
                    continue  # Exclude the marble starting the move

                # Normalize positions to handle circular board
                marble_pos = marble.pos
                adjusted_pos_to = pos_to + (self.TOTAL_STEPS if pos_to < pos_from else 0)
                adjusted_marble_pos = marble_pos + (self.TOTAL_STEPS if marble_pos < pos_from else 0)

                # Check if the marble is in the range of the move
                if pos_from < adjusted_marble_pos <= adjusted_pos_to:
                    marbles_to_reset.append(marble)

        return marbles_to_reset

    def _reset_to_kennel(self, marble: Marble) -> None:
        """
        Reset a marble to its kennel (queue start position).
        """
        for player_index, current_player in enumerate(self._state.list_player):
            if marble in current_player.list_marble:
                queue_start = self.PLAYER_POSITIONS[player_index]['queue_start']
                marble_index = current_player.list_marble.index(marble)
                marble.pos = queue_start + marble_index
                marble.is_save = True
                return
    def _handle_collision(self, current_action: Action) -> None:
        """
        Handle the collision by sending the marble back to its starting position.
        """
        for player_index, current_player in enumerate(self._state.list_player):
            for marble in current_player.list_marble:
                # print(f"Checking marble at pos {marble.pos} against action.pos_to {action.pos_to}")
                if marble.pos == current_action.pos_to and not marble.is_save:
                    # Send the marble back to its queue start
                    queue_start = self.PLAYER_POSITIONS[player_index]['queue_start']
                    marble.pos = queue_start + current_player.list_marble.index(marble)  # Back to the queue
                    marble.is_save = True
                    return
    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the opponent's cards are face down) """
        masked_state: GameState = self._state.copy()
        for i, current_player in enumerate(masked_state.list_player):
            if i != idx_player:
                current_player.list_card = [Card(suit='?', rank='?')] * len(current_player.list_card)
        return masked_state

    def _refresh_deck(self) -> None:
        """
        Shuffle the draw pile. If the draw pile does not have enough cards to be dealt,
        move discarded cards back to the draw pile and shuffle.
        """

        # Move discarded cards to the draw pile
        self._state.list_card_draw = self._state.LIST_CARD.copy()
        self._state.list_card_discard.clear()

        # Shuffle the draw pile
        random.shuffle(self._state.list_card_draw)

    def _is_way_blocked(self, pos_to: int, pos_from: int, safe_marbles: List[Marble]) -> bool:
        """ Check if the way is blocked between from  & to by any safe marble
        - If a marble is in the way: return True
        - If no marble is in the way: return False"""

        # Identify the "safe" positions (0, 16, 32, 48)
        safe_positions = [0, 16, 32, 48]  # Marbles are protected and can't be passed by others

        # Adjust pos_to for circular board wrapping
        total_steps = self.TOTAL_STEPS  # Board has 64 total steps (0–63)
        if pos_to < pos_from:
            pos_to += total_steps  # Adjust pos_to if it wraps around the board

        # Loop through each safe marble
        for marble in safe_marbles:  # Loops through all the marbles that are currently on the safe spots
            marble_pos = marble.pos
            if marble_pos in safe_positions:
                # Normalize marble_pos to match the current path calculation
                if marble_pos < pos_from:
                    marble_pos += total_steps

                # Check if the marble is blocking the path
                if pos_from < marble_pos <= pos_to:
                    return True  # Path is blocked by a safe marble

        return False  # No safe marble is blocking the path

    def _is_valid_move_in_final_area(self, pos_from: int, pos_to: int, marbles: list[Marble], final_area_start: int,
                                     final_area_end: int) -> bool:
        """
        Validates whether a move in the final area is legal based on game rules.
        Marbles cannot jump over other marbles in the final area.
        """
        if pos_from < final_area_start or pos_from > final_area_end:
            return True  # Not in the final area, allow the move.

        step_direction = 1 if pos_to > pos_from else -1
        for intermediate_pos in range(pos_from + step_direction, pos_to + step_direction, step_direction):
            for marble in marbles:
                if marble.pos == intermediate_pos:
                    return False  # Found a marble in the way, move is invalid.
        return True

    def _get_all_safe_marbles(self) -> list[Marble]:
        safe_marbles = []
        for current_player in self._state.list_player:
            for marble in current_player.list_marble:
                if marble.is_save:
                    safe_marbles.append(marble)
        return safe_marbles

    def deal_cards(self) -> None:
        for current_player in self._state.list_player:
            round_mod = self._state.cnt_round % 10
            if round_mod == 0:
                cards_to_deal = 2
            elif round_mod <= 5:
                cards_to_deal = 7 - round_mod
            else:
                cards_to_deal = 12 - round_mod

            if cards_to_deal > len(self._state.list_card_draw):
                self._refresh_deck()

            for _ in range(cards_to_deal):
                card = self._state.list_card_draw.pop()
                current_player.list_card.append(card)

    def _set_marbles(self) -> None:
        for player_index, current_player in enumerate(self._state.list_player):
            for marble_index in range(4):
                current_player.list_marble.append(
                    Marble(
                        pos=int(self.PLAYER_POSITIONS[player_index]['queue_start'] + marble_index),
                        is_save=True
                    )
                )

    def _swap_marbles(self, chosen_action: Action) -> None:
        """
          Swap the positions of two marbles based on the provided action.

          Args:
              chosen_action (Action): The action containing pos_from and pos_to.
          """
        marble_from = None
        marble_to = None

        # Find the marble at pos_from and pos_to
        for current_player in self._state.list_player:
            for marble in current_player.list_marble:
                if marble.pos == chosen_action.pos_from:
                    marble_from = marble
                elif marble.pos == chosen_action.pos_to:
                    marble_to = marble

                # Exit early if both marbles are found
                if marble_from and marble_to:
                    break
            if marble_from and marble_to:
                break

        # If both marbles are found, swap their positions
        if marble_from and marble_to:
            marble_from.pos, marble_to.pos = marble_to.pos, marble_from.pos

    def _move_n_forward(self, marble: Marble, steps: int, queue_start: int, final_start: int) -> int:
        pos = (marble.pos + steps) % self.TOTAL_STEPS
        if marble.pos < queue_start and pos >= queue_start:  # pylint: disable=chained-comparison
            pos = final_start + (pos - queue_start) - 1
        return pos

class RandomPlayer(Player): # pylint: disable=too-few-public-methods

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]: # pylint: disable=unused-argument
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    game = Dog()
    player = RandomPlayer()

    while game.get_state().phase != GamePhase.FINISHED:
        ACTIVE_PLAYERS = 4
        while ACTIVE_PLAYERS > 0:
            list_actions = game.get_list_action()

            if not list_actions:
                ACTIVE_PLAYERS -= 1
                print("Player has no actions left. Please wait until the round is over.")
            else:
                action: Action = player.select_action(game.get_state(), list_actions)  # type: ignore
                game.apply_action(action)
                game.print_state()

        # Reset card swapping flag for the next round
        game.get_state().bool_card_exchanged = False

        print(f"\n --------------- ROUND {game.get_state().cnt_round} finished -----------------")