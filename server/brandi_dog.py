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
        if self.pos > 96:  # Marble does not go beyond position 95
            self.pos = 95 # Set to 95 and not beyond
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
            list_marble=[Marble(pos= 0, is_save=False) for _ in range(4)]
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
            print("Invalid card or functionality not implemented.")

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
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):

    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',      # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        # 3: Move 3 spots forward
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        # 4: Move 4 spots forward or back
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        # 5: Move 5 spots forward
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        # 6: Move 6 spots forward
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        # 7: Move 7 single steps forward
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        # 8: Move 8 spots forward
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        # 9: Move 9 spots forward
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        # 10: Move 10 spots forward
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        # Jake: A marble must be exchanged
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Queen: Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # King: Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # Ass: Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any other card you want
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int = 4                # number of players (must be 4)
    phase: GamePhase                   # current phase of the game
    cnt_round: int                     # current round
    bool_game_finished: bool           # true if game has finished
    bool_card_exchanged: bool          # true if cards was exchanged in round
    idx_player_started: int            # index of player that started the round
    idx_player_active: int             # index of active player in round
    list_player: List[PlayerState]     # list of players
    list_id_card_draw: List[Card]      # list of cards to draw
    list_id_card_discard: List[Card]   # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)


class Dog(Game):

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """

        self.board_numbers = range(0, 96)
        self.board = {
            "blue": {
                "home": self.board_numbers[64:68],
                "start": self.board_numbers[0],
                "finish": self.board_numbers[68:72],
            },
            "green": {
                "home": self.board_numbers[72:76],
                "start": self.board_numbers[16],
                "finish": self.board_numbers[76:80],
            },
            "yellow": {
                "home": self.board_numbers[88:92],
                "start": self.board_numbers[48],
                "finish": self.board_numbers[92:96],
            },
            "red": {
                "home": self.board_numbers[80:84],
                "start": self.board_numbers[32],
                "finish": self.board_numbers[84:88],
            },
        }

    def get_player_positions(self, color: str) -> dict:

        return self.board.get(color, None)

    def init_players(self) -> List[PlayerState]:
        """ Initialize players with cards and marbles """
        colors = ["blue", "green", "yellow", "red"]
        return [PlayerState(name=color) for color in colors]

    def deal_cards(self) -> None:
        """ Deal cards to all players based on the current round """
        num_cards_to_deal = self.round_pattern[self.current_round_index]
        print(f"Dealing {num_cards_to_deal} cards to each player for round {self.current_round_index + 1}")

        for player in self.players:
            player.list_card = random.sample(self.card_deck, num_cards_to_deal)
            print(f"{player.name} received: {[f'{card.rank}{card.suit}' for card in player.list_card]}")

        # Advance to the next round
        self.current_round_index = (self.current_round_index + 1) % len(self.round_pattern)



    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        pass

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        pass

    def print_state(self) -> None:
        """ Print the current game state """
        pass

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':

    game = Dog()

    # Initialize the players
    players = game.init_players()

    # Example of game initialization with 4 players
    for player in players:
        print(f"Player: {player.name}")
        print(f"Cards: {player.list_card}")
        print(f"Marbles: {[marble.pos for marble in player.list_marble]}")

    # Example of fetching player positions
    red_positions = game.get_player_positions("red")
    print("Red player positions:", red_positions)

    # Dealing cards for rounds
    for round_num in range(1, 6):
        cards_to_deal = 6 - round_num
        deal_cards = random.sample(GameState.LIST_CARD, cards_to_deal)
        print(f"Round {round_num}: {deal_cards}")


    red_positions = game.get_player_positions("red")
    print("Red player positions:", red_positions)

    round = range(1,6)

#for each round we have to specify how many cards each player is dealed
    for round in round:
        if round == 1:
            deal_cards = random.sample(GameState.LIST_CARD, 6)
            print("1: ", deal_cards)
        if round == 2:
            deal_cards = random.sample(GameState.LIST_CARD, 5)
            print("2: ", deal_cards)
        if round == 3:
            deal_cards = random.sample(GameState.LIST_CARD, 4)
            print("3: ", deal_cards)
        if round == 4:
            deal_cards = random.sample(GameState.LIST_CARD, 3)
            print("4: ", deal_cards)
        if round == 5:
            deal_cards = random.sample(GameState.LIST_CARD, 2)
            print("4: ", deal_cards)
