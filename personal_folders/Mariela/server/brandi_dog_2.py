# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
from server.py.game import Game, Player
from typing import List, Optional, ClassVar
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
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from
    pos_to: Optional[int]      # position to move the marble to
    card_swap: Optional[Card]  # optional card to swap ()


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


class Dog(Game):

    def __init__(self) -> None:
        """ Game initialization """
        self.round_pattern = [6, 5, 4, 3, 2]  # repeating pattern for dealing cards
        self.current_round_index = 0

        self.board_numbers = range(0, 96)
        self.board = {
            "blue": {
                "home": list(self.board_numbers)[64:68],
                "start": list(self.board_numbers)[0],
                "finish": list(self.board_numbers)[68:72],
            },
            "green": {
                "home": list(self.board_numbers)[72:76],
                "start": list(self.board_numbers)[16],
                "finish": list(self.board_numbers)[76:80],
            },
            "yellow": {
                "home": list(self.board_numbers)[88:92],
                "start": list(self.board_numbers)[48],
                "finish": list(self.board_numbers)[92:96],
            },
            "red": {
                "home": list(self.board_numbers)[80:84],
                "start": list(self.board_numbers)[32],
                "finish": list(self.board_numbers)[84:88],
            },
        }

        players = self.init_players()
        # Initial full deck to draw from
        full_deck = GameState.LIST_CARD.copy()
        random.shuffle(full_deck)

        self.state = GameState(
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

        # Handy references
        self.players = self.state.list_player
        self.card_deck = self.state.list_id_card_draw

    def get_player_positions(self, color: str) -> dict:
        return self.board.get(color, None)

    def init_players(self) -> List[PlayerState]:
        colors = ["blue", "green", "yellow", "red"]
        return [PlayerState(name=color) for color in colors]

    def deal_cards(self) -> None:
        """ Deal cards to all players for the current round """
        num_cards_to_deal = self.round_pattern[self.current_round_index]
        print(f"Dealing {num_cards_to_deal} cards to each player for round {self.current_round_index + 1}")

        # Draw cards from the card deck
        for player in self.players:
            dealt_cards = []
            for _ in range(num_cards_to_deal):
                if len(self.card_deck) == 0:
                    # If deck is empty, reshuffle discard
                    self.card_deck.extend(self.state.list_id_card_discard)
                    self.state.list_id_card_discard.clear()
                    random.shuffle(self.card_deck)
                dealt_cards.append(self.card_deck.pop())
            player.list_card = dealt_cards
            print(f"{player.name} received: {[f'{card.rank}{card.suit}' for card in player.list_card]}")

        # Advance to the next round
        self.current_round_index = (self.current_round_index + 1) % len(self.round_pattern)

    def set_state(self, state: GameState) -> None:
        self.state = state

    def get_state(self) -> GameState:
        return self.state

    def print_state(self) -> None:
        print("Game State:")
        print(f" Phase: {self.state.phase}")
        print(f" Round: {self.state.cnt_round}")
        print(f" Active Player: {self.players[self.state.idx_player_active].name if self.state.idx_player_active < len(self.players) else 'None'}")
        for p in self.players:
            card_list = ", ".join([f"{c.rank}{c.suit}" for c in p.list_card])
            marble_positions = ", ".join([str(m.pos) for m in p.list_marble])
            print(f" Player: {p.name}, Cards: [{card_list}], Marbles: [{marble_positions}]")

    def get_list_action(self) -> List[Action]:
        # This should return valid actions for the active player.
        # For now, we return an empty list or a dummy action.
        # Implementing full action logic will depend on the game rules.
        # E.g., checking which marbles can move, which cards can be played, etc.
        active_player = self.players[self.state.idx_player_active]
        actions = []
        # Example: For each card, maybe propose a move for marble 0
        for card in active_player.list_card:
            # Just a placeholder action
            actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=None))
        return actions

    def apply_action(self, action: Action) -> None:
        # Apply the action chosen by the active player.
        # This will involve updating the position of a marble, discarding cards, etc.
        # Placeholder logic:
        active_player = self.players[self.state.idx_player_active]

        if action.card in active_player.list_card:
            # Remove the card from the player's hand
            active_player.list_card.remove(action.card)
            self.state.list_id_card_discard.append(action.card)
            print(f"{active_player.name} played {action.card.rank}{action.card.suit}")

            # If there's a move associated (pos_from/pos_to), you'd implement that here.
            # For now, just a placeholder print:
            if action.pos_from is not None and action.pos_to is not None:
                # Move a marble from pos_from to pos_to, if logic is implemented.
                # You'd need to find which marble corresponds, etc.
                pass

        # Move to next player's turn
        self.state.idx_player_active = (self.state.idx_player_active + 1) % len(self.players)

    def get_player_view(self, idx_player: int) -> GameState:
        # Return a masked view of the GameState for player at idx_player.

        # Instead of using copy(), use model_copy()
        masked_state = self.state.model_copy(deep=True)

        # For all players except idx_player, hide their cards
        for i, p in enumerate(masked_state.list_player):
            if i != idx_player:
                p.list_card = [Card(suit='?', rank='?') for _ in p.list_card]

        return masked_state


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()

    # Initialize the players
    players = game.players
    for player in players:
        print(f"Player: {player.name}")
        print(f"Cards: {player.list_card}")
        print(f"Marbles: {[marble.pos for marble in player.list_marble]}")

    # Example of fetching player positions
    red_positions = game.get_player_positions("red")
    print("Red player positions:", red_positions)

    # Deal the initial round of cards
    game.deal_cards()
    game.print_state()

    # Example of taking player view
    player_view = game.get_player_view(0)
    print("Player 0 view (masked):")
    for p in player_view.list_player:
        card_list = ", ".join([f"{c.rank}{c.suit}" for c in p.list_card])
        print(f"  {p.name} Cards: [{card_list}]")
