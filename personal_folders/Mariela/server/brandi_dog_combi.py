from typing import List, Optional, ClassVar, Dict, Tuple
from pydantic import BaseModel
from enum import Enum
import random

class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: int      # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved

    def move(self, steps: int) -> None:
        """ Move the marble by the specified number of steps """
        if not self.is_save:
            print("The marble is in the kennel and cannot be moved.")
            return
        self.pos += steps  # Move the marble by the specified steps
        if self.pos > 95:  # Marble does not go beyond position 95
            self.pos = 95
        print(f"Marble moved to position: {self.pos}")

    def reset_to_kennel(self) -> None:
        """Send the marble back to the kennel."""
        self.pos = 0
        self.is_save = False
        print("Marble returned to the kennel.")


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles

    def __init__(self, name: str):
        super().__init__(
            name=name,
            list_card=[],
            list_marble=[Marble(pos=0, is_save=False) for _ in range(4)]
        )

    def play_card(self, card: Card, marble_index: int = 0) -> None:
        """Execute the action of playing a card."""
        print(f"{self.name} plays the card: {card.rank}")

        if marble_index < 0 or marble_index >= len(self.list_marble):
            print("Invalid marble selection!")
            return

        if card.rank.isdigit():  # If the card represents a number
            steps = int(card.rank)
            self.list_marble[marble_index].move(steps)
        elif card.rank in ["A", "K"]:  # Start a marble
            if not self.list_marble[marble_index].is_save:
                self.list_marble[marble_index].is_save = True
                print(f"{self.name}'s marble {marble_index} is now in play!")
        else:
            print("Invalid card or functionality not fully implemented.")

    def exchange_card(self, card_to_exchange: Card, partner: "PlayerState") -> None:
        """Exchange a card with a partner."""
        if card_to_exchange not in self.list_card:
            print("Card not in hand!")
            return
        self.list_card.remove(card_to_exchange)
        partner.list_card.append(card_to_exchange)
        print(f"{self.name} exchanged {card_to_exchange.rank}{card_to_exchange.suit} with {partner.name}.")

class Action(BaseModel):
    card: Card
    marble_index: Optional[int] = None
    steps: Optional[int] = None
    # For Jacks or other special moves, might need extra info:
    # For 7, a sequence of moves or splitting steps
    # For Joker, which card rank it is emulating
    emulate_rank: Optional[str] = None
    marble_index_2: Optional[int] = None
    steps_2: Optional[int] = None
    jack_target_player_idx: Optional[int] = None
    jack_target_marble_index: Optional[int] = None

class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'

class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
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
    bool_game_finished: bool
    bool_card_exchanged: bool
    idx_player_started: int
    idx_player_active: int
    list_player: List[PlayerState]
    list_id_card_draw: List[Card]
    list_id_card_discard: List[Card]
    card_active: Optional[Card]


class Game:
    # Base game interface
    def set_state(self, state: GameState) -> None:
        raise NotImplementedError

    def get_state(self) -> GameState:
        raise NotImplementedError

    def get_list_action(self) -> List[Action]:
        raise NotImplementedError

    def apply_action(self, action: Action) -> None:
        raise NotImplementedError

    def get_player_view(self, idx_player: int) -> GameState:
        raise NotImplementedError

    def print_state(self) -> None:
        raise NotImplementedError

class Dog(Game):

    round_pattern = [6,5,4,3,2]

    def __init__(self) -> None:
        """ Game initialization """
        full_deck = GameState.LIST_CARD.copy()
        random.shuffle(full_deck)

        colors = ["blue", "green", "yellow", "red"]
        # Teams: (blue,yellow), (green,red) for example
        # We'll say team 0: blue,yellow; team 1: green,red
        # You can adjust the mapping as you like.
        team_map = {"blue":0,"yellow":0,"green":1,"red":1}

        self.board_numbers = list(range(0,96))
        self.board = {
            "blue": {
                "kennel": self.board_numbers[64:68],
                "start": self.board_numbers[0],
                "finish": self.board_numbers[68:72],
            },
            "green": {
                "kennel": self.board_numbers[72:76],
                "start": self.board_numbers[16],
                "finish": self.board_numbers[76:80],
            },
            "yellow": {
                "kennel": self.board_numbers[88:92],
                "start": self.board_numbers[48],
                "finish": self.board_numbers[92:96],
            },
            "red": {
                "kennel": self.board_numbers[80:84],
                "start": self.board_numbers[32],
                "finish": self.board_numbers[84:88],
            },
        }

        players = []
        for c in colors:
            marbles = [Marble(pos=p, is_save=False) for p in self.board[c]["kennel"]]
            p = PlayerState(
                name=c,
                list_card=[],
                list_marble=marbles,
                color=c,
                team_id=team_map[c]
            )
            players.append(p)

        initial_state = GameState(
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=1,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=players,
            list_id_card_draw=full_deck,
            list_id_card_discard=[],
            card_active=None
        )

        self.state = initial_state
        self.current_round_index = 0  # For round_pattern indexing

    def set_state(self, state: GameState) -> None:
        self.state = state

    def get_state(self) -> GameState:
        return self.state

    def print_state(self) -> None:
        s = self.state
        print(f"Phase: {s.phase}")
        print(f"Round: {s.cnt_round}, Active Player: {s.list_player[s.idx_player_active].name}")
        for p in s.list_player:
            cards_str = ", ".join([f"{c.rank}{c.suit}" for c in p.list_card])
            marbles_str = ", ".join([f"{m.pos}{'(F)' if m.finished else ''}" for m in p.list_marble])
            print(f"{p.name} (Team {p.team_id}): Cards[{cards_str}] Marbles[{marbles_str}]")

    def get_player_positions(self, color: str):
        return self.board[color]

    def deal_cards(self) -> None:
        """ Deal cards to all players based on the current round pattern """
        if self.state.phase == GamePhase.FINISHED:
            print("Game finished. No more dealing.")
            return

        num_cards = self.round_pattern[self.current_round_index]
        print(f"Dealing {num_cards} cards to each player for round {self.state.cnt_round}")

        for player in self.state.list_player:
            dealt = []
            for _ in range(num_cards):
                if len(self.state.list_id_card_draw) == 0:
                    # Reshuffle discard
                    self.state.list_id_card_draw = self.state.list_id_card_discard
                    random.shuffle(self.state.list_id_card_draw)
                    self.state.list_id_card_discard = []
                dealt.append(self.state.list_id_card_draw.pop())
            player.list_card.extend(dealt)
            print(f"{player.name} got {[c.rank+c.suit for c in dealt]}")

        self.current_round_index = (self.current_round_index+1) % len(self.round_pattern)
        self.state.cnt_round += 1

    def get_player_view(self, idx_player: int) -> GameState:
        # Return masked state
        masked_state = self.state.copy(deep=True)
        for i, p in enumerate(masked_state.list_player):
            if i != idx_player:
                p.list_card = [Card(suit='?', rank='?') for _ in p.list_card]
        return masked_state

    def move_marble(self, player: PlayerState, marble_index: int, steps: int) -> bool:
        """Move a marble forward (or backward if steps < 0) and apply rules:
           - If landing on another marble, send it back to kennel.
           - If passing start, increment laps.
           - If can enter finish (after 2 laps around the board).
        """
        marble = player.list_marble[marble_index]
        if marble.finished:
            print("Marble already finished, can't move.")
            return False
        if not marble.is_save:
            print("Marble not on board, can't move.")
            return False

        start_pos = self.get_player_positions(player.color)["start"]
        finish_range = self.get_player_positions(player.color)["finish"]
        old_pos = marble.pos
        new_pos = old_pos + steps

        # Check laps:
        # We assume passing start (exact position) increments laps.
        # The path is a loop of length 64 (?), marbles start after kennel on board pos.
        # For simplicity, let's say position 0 (blue start) is the start for blue,
        # similarly for others. If a marble passes its start position:
        board_length = 64  # The loop length (the rest are off-path finishes)
        # Actually, from the standard Brändi Dog: The main circle is likely 64 fields.
        # We'll assume 64 fields from 0 to 63 represent the loop.
        # The rest are finish and kennel fields outside the loop.
        # If going beyond 63, wrap around: new_pos = (new_pos % 64) when counting laps.
        # We'll track laps only if crossing the start field.

        # If marble moves beyond loop, wrap for lap counting:
        # Actually, the board might be arranged differently, but let's keep it simple:
        # We'll consider that any position < 64 is on the main loop.
        def loop_pos(pos):
            if pos < 64:
                return pos
            # If finish or kennel, no loops
            return None

        old_loop = loop_pos(old_pos)
        new_loop = None
        if steps > 0:
            # Check all intermediate positions if 7 (overtaking)
            # For now, just do final checks. (We'll handle overtaking with 7 separately)
            pass

        # Adjust for main loop wrapping
        if loop_pos(new_pos) is not None:
            new_loop = loop_pos(new_pos)
        else:
            # If entering a finish area, must ensure at least 2 laps
            # Player start must be passed at least twice
            # If not enough laps, can't enter finish -> clamp at last loop position
            if new_pos > 63:
                # Check if laps >= 2
                if marble.laps >= 2:
                    # Enter finish if within finish range
                    # If beyond finish range, clamp at last finish
                    if new_pos > finish_range[-1]:
                        new_pos = finish_range[-1]
                    # Mark finished if on finish fields
                    if new_pos in finish_range:
                        marble.finished = True
                        print(f"{player.name}'s marble {marble_index} finished!")
                else:
                    # Not enough laps, can't go into finish
                    new_pos = new_pos % 64
                    new_loop = new_pos
            else:
                # still on loop
                new_loop = new_pos % 64

        # Update laps if passing start
        if old_loop is not None and new_loop is not None and player.color in self.board:
            player_start = self.get_player_positions(player.color)["start"]
            # If we cross player_start between old_pos and new_pos, increment laps
            # Simple check: if going forward and we passed start_pos
            # start_pos must be < 64 for this logic to hold
            if start_pos < 64:
                # If we moved forward and passed the start:
                # A robust check would check each intermediate field, but we simplify:
                if steps > 0:
                    if old_loop <= start_pos <= new_loop or (old_loop > new_loop and start_pos <= new_loop):
                        marble.laps += 1
                else:
                    # If going backward over start, also count?
                    # The rules say passing start twice "whether backwards or forwards"
                    if new_loop <= start_pos <= old_loop:
                        marble.laps += 1

        # Perform the move
        marble.pos = new_pos

        # Check if landing on occupied space (not finish)
        # If landing on a space that is occupied by another marble (not finish), send it to kennel
        self.handle_collision(player, marble_index)

        return True

    def handle_collision(self, current_player: PlayerState, marble_index: int):
        # If two marbles land on the same space, the marble that was there first is sent home.
        # Also handle that marbles on the start field initially block others.
        # We must find if any other player's marble occupies the same pos.
        pos = current_player.list_marble[marble_index].pos
        for p in self.state.list_player:
            for i, m in enumerate(p.list_marble):
                if p is current_player and i == marble_index:
                    continue
                if m.pos == pos and not m.finished and m.is_save:
                    # send m back to kennel
                    self.send_to_kennel(p, i)

    def send_to_kennel(self, player: PlayerState, marble_index: int):
        # Move marble back to kennel
        color = player.color
        kennel_positions = self.get_player_positions(color)["kennel"]
        # Place in first free kennel position - in practice, kennel is static
        # We'll just pick the first kennel position and place it there
        player.list_marble[marble_index].pos = kennel_positions[0]
        player.list_marble[marble_index].is_save = False
        player.list_marble[marble_index].laps = 0
        player.list_marble[marble_index].finished = False
        print(f"{player.name}'s marble {marble_index} sent back to kennel.")

    def start_marble(self, player: PlayerState, marble_index: int):
        m = player.list_marble[marble_index]
        if m.is_save:
            print("Marble already on board.")
            return False
        start_pos = self.get_player_positions(player.color)["start"]
        # Check if start is free or blocked
        # If another marble is there from start, can't place?
        # In brandi dog, start marbles block passage but you can still place on start if empty
        for p in self.state.list_player:
            for marb in p.list_marble:
                if marb.pos == start_pos and marb.is_save and not marb.finished:
                    # Start blocked
                    print("Start position blocked, cannot start marble.")
                    return False
        m.pos = start_pos
        m.is_save = True
        print(f"{player.name} started marble {marble_index} at position {start_pos}")
        return True

    def apply_action(self, action: Action) -> None:
        s = self.state
        active_player = s.list_player[s.idx_player_active]

        # Check card in hand
        if action.card not in active_player.list_card:
            print("Card not in player's hand!")
            return

        # Remove card from hand
        active_player.list_card.remove(action.card)
        s.list_id_card_discard.append(action.card)
        print(f"{active_player.name} played {action.card.rank}{action.card.suit}")

        # Determine the rank to apply (for Joker)
        rank = action.emulate_rank if action.emulate_rank else action.card.rank

        # Implement logic for each card rank:
        # We'll assume action provides marble_index and steps as needed.
        # For A/K: start or move. For now, we assume if marble not on board, we start it,
        # else we move the given steps.
        # For A: 1 or 11 steps - we assume action.steps is given.
        # For K: 13 steps.
        # For Q: 12 steps.
        # For J: exchange marbles.
        # For 4: forward or backward.
        # For 7: split steps among two marbles if needed.
        # For number cards (2,3,5,6,8,9,10): move forward steps.

        def do_move(marble_idx, steps):
            return self.move_marble(active_player, marble_idx, steps)

        if rank == 'A':
            # Start or move 1/11
            m_i = action.marble_index or 0
            m = active_player.list_marble[m_i]
            if not m.is_save:
                self.start_marble(active_player, m_i)
                # If we wanted to move 11 after start, it's not normal brandi dog rule. Just start only.
            else:
                # Move steps (1 or 11)
                st = action.steps or 1
                do_move(m_i, st)

        elif rank == 'K':
            # Start or move 13
            m_i = action.marble_index or 0
            m = active_player.list_marble[m_i]
            if not m.is_save:
                self.start_marble(active_player, m_i)
            else:
                do_move(m_i, 13)

        elif rank == 'Q':
            # Move 12 forward
            m_i = action.marble_index or 0
            do_move(m_i, 12)

        elif rank == 'J':
            # Exchange marbles between players
            # Need: jack_target_player_idx and jack_target_marble_index
            # Swap positions of marbles (if allowed)
            # Conditions: cannot swap if marble in kennel, finished, or start first time
            target_p_idx = action.jack_target_player_idx
            target_m_i = action.jack_target_marble_index
            if target_p_idx is not None and target_m_i is not None:
                target_player = s.list_player[target_p_idx]
                m_i = action.marble_index or 0
                m1 = active_player.list_marble[m_i]
                m2 = target_player.list_marble[target_m_i]
                # Check if allowed to swap:
                if not (m1.is_save and not m1.finished):
                    print("Can't swap your marble, it's not on the board properly.")
                elif not (m2.is_save and not m2.finished):
                    print("Can't swap target marble.")
                else:
                    # swap positions
                    pos1, pos2 = m1.pos, m2.pos
                    m1.pos, m2.pos = pos2, pos1
                    print(f"{active_player.name} swapped marble {m_i} with {target_player.name}'s marble {target_m_i}")

        elif rank == 'JKR':
            # Joker acts like another card. Already handled by emulate_rank.
            # Just do what emulate_rank says.
            pass

        elif rank == '4':
            # Move 4 forward or backward (steps could be negative)
            m_i = action.marble_index or 0
            st = action.steps or 4
            do_move(m_i, st)

        elif rank == '7':
            # Split 7 steps among one or two marbles forward only.
            # action might have marble_index and steps, marble_index_2 and steps_2
            # All 7 steps must be used.
            total = 0
            if action.marble_index is not None and action.steps is not None:
                total += action.steps
            if action.marble_index_2 is not None and action.steps_2 is not None:
                total += action.steps_2
            if total != 7:
                print("7 steps must be fully used!")
            else:
                # Move first marble
                if action.marble_index is not None and action.steps is not None:
                    self.overtake_with_7(active_player, action.marble_index, action.steps)
                # Move second marble if any
                if action.marble_index_2 is not None and action.steps_2 is not None:
                    self.overtake_with_7(active_player, action.marble_index_2, action.steps_2)

        else:
            # Numeric cards 2,3,5,6,8,9,10
            if rank.isdigit() or rank == '10':
                m_i = action.marble_index or 0
                st = int(rank)
                do_move(m_i, st)

        # After action, check if team won
        self.check_win_condition()

        # Move to next player if game not finished
        if self.state.phase != GamePhase.FINISHED:
            s.idx_player_active = (s.idx_player_active + 1) % s.cnt_player

    def overtake_with_7(self, player: PlayerState, marble_index: int, steps: int):
        # With a 7, overtaking marbles sends them back to the kennel.
        # We should check all intermediate positions:
        m = player.list_marble[marble_index]
        if not m.is_save or m.finished:
            print("Marble can't move with 7.")
            return
        start = m.pos
        end = m.pos + steps
        direction = 1 if steps > 0 else -1
        for pos_check in range(start+direction, end+direction, direction):
            # Check each position for marbles to overtake
            for p in self.state.list_player:
                for i, marb in enumerate(p.list_marble):
                    if marb.is_save and not marb.finished and marb.pos == pos_check:
                        # Overtaken - send to kennel
                        self.send_to_kennel(p, i)
        # After overtaking, move marble finally
        self.move_marble(player, marble_index, steps)

    def send_team_help(self, team_id: int) -> bool:
        # If one player finished all marbles, they help partner
        # This logic is implicit: players always can move partner marbles after finishing theirs.
        # No specific code needed here unless you want to restrict actions.

        return True

    def check_win_condition(self):
        # Team wins when all their 8 marbles are finished (4 per player * 2 players)
        teams = {0:0, 1:0}
        for p in self.state.list_player:
            for m in p.list_marble:
                if m.finished:
                    teams[p.team_id] += 1
        for t, count in teams.items():
            if count == 8:
                print(f"Team {t} wins!")
                self.state.phase = GamePhase.FINISHED
                self.state.bool_game_finished = True

    def get_list_action(self) -> List[Action]:
        # Return possible actions for active player.
        # This could be complex. For now, we just return a placeholder.
        # In a real game, we'd consider what moves are possible from the player's cards and marble states.
        return []

if __name__ == '__main__':
    game = Dog()
    # Setup -> Deal cards -> Start running
    game.state.phase = GamePhase.RUNNING
    game.deal_cards()
    game.print_state()

    # Example: play an action with Ace to start marble 0 of blue
    # We assume blue is player 0:
    p0 = game.state.list_player[0]
    # Find an Ace card in player's hand
    ace_card = None
    for c in p0.list_card:
        if c.rank == 'A':
            ace_card = c
            break

    if ace_card:
        action = Action(card=ace_card, marble_index=0, steps=1)
        game.apply_action(action)
        game.print_state()

    # Continue as needed.
