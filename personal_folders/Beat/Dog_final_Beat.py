from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
import random

class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank

class Marble(BaseModel):
    pos: str       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved

class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles

    def __init__(self, name: str):
        super().__init__(
            name=name,
            list_card=[],
            list_marble=[Marble(pos='0', is_save=False) for _ in range(4)]
        )

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
        # Jack: A marble must be exchanged
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Queen: Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # King: Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # Ace: Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any other card you want
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_round: int = 1                     # current round
    phase: GamePhase = GamePhase.RUNNING  # current phase of the game
    list_player: List[PlayerState]        # list of players
    list_card_draw: List[Card]            # list of cards to draw
    list_card_discard: List[Card]         # list of cards discarded

    def __init__(self, cnt_players: int = 4):
        super().__init__(
            list_player=[PlayerState(name=f"Player {i+1}") for i in range(cnt_players)],
            list_card_draw=random.sample(self.LIST_CARD, len(self.LIST_CARD)),
            list_card_discard=[]
        )

class Dog(Game):

    def __init__(self) -> None:
        self.state = GameState()
        self.round_pattern = [6, 5, 4, 3, 2]

    def deal_cards(self) -> None:
        """Deal cards to all players based on the current round pattern."""
        num_cards_to_deal = self.round_pattern[self.state.cnt_round - 1]
        print(f"Dealing {num_cards_to_deal} cards for round {self.state.cnt_round}")

        for player in self.state.list_player:
            if len(self.state.list_card_draw) < num_cards_to_deal:
                if not self.state.list_card_discard:
                    raise ValueError("Not enough cards to deal and no cards in discard pile to reshuffle.")

                print("Reshuffling discard pile into draw pile.")
                self.state.list_card_draw.extend(self.state.list_card_discard)
                random.shuffle(self.state.list_card_draw)
                self.state.list_card_discard.clear()

            player.list_card = [
                self.state.list_card_draw.pop() for _ in range(num_cards_to_deal)
            ]
            print(f"{player.name} received: {[f'{card.rank}{card.suit}' for card in player.list_card]}")

    def advance_round(self) -> None:
        """Advance to the next round."""
        self.state.cnt_round += 1
        if self.state.cnt_round > len(self.round_pattern):
            self.state.phase = GamePhase.FINISHED

    def reset_game(self) -> None:
        """Reset the game to its initial state."""
        self.state = GameState()

    def set_state(self, state: GameState) -> None:
        """Set the game to a given state."""
        self.state = state

    def get_state(self) -> GameState:
        """Get the complete, unmasked game state."""
        return self.state

    def print_state(self) -> None:
        """Print the current game state."""
        print(self.state)

if __name__ == "__main__":
    game = Dog()

    # Reset and start the game
    game.reset_game()

    # Play through the rounds
    for round_num in range(1, 6):
        game.state.cnt_round = round_num
        try:
            game.deal_cards()
        except ValueError as e:
            print(f"Error during card dealing: {e}")
            break

        print(f"Round {round_num} completed.")

    print("Game finished.")
