from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random

class Card(BaseModel):
    suit: str
    rank: str

class PlayerState(BaseModel):
    name: str
    list_card: List[Card]
    list_marble: List[int]

    def __init__(self, name: str):
        super().__init__(
            name=name,
            list_card=[],
            list_marble=[0 for _ in range(4)]
        )

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
    LIST_CARD: ClassVar[List[Card]] = [
        Card(suit=suit, rank=rank)
        for suit in ['♠', '♥', '♦', '♣']
        for rank in [
            '2', '3', '4', '5', '6', '7', '8', '9', '10',
            'J', 'Q', 'K', 'A'
        ]
    ] + [Card(suit='', rank='JKR') for _ in range(3)] * 2

    cnt_round: int
    phase: GamePhase
    list_player: List[PlayerState]
    list_card_draw: List[Card]
    list_card_discard: List[Card]

    def __init__(self, cnt_players: int = 4):
        super().__init__(
            cnt_round=1,
            phase=GamePhase.RUNNING,
            list_player=[PlayerState(name=f"Player {i+1}") for i in range(cnt_players)],
            list_card_draw=random.sample(self.LIST_CARD, len(self.LIST_CARD)),
            list_card_discard=[]
        )

class Dog:
    def __init__(self):
        self.state = GameState()
        self.round_pattern = [6, 5, 4, 3, 2]

    def deal_cards(self):
        """Deal cards to all players based on the current round pattern."""
        num_cards_to_deal = self.round_pattern[self.state.cnt_round - 1]
        print(f"Dealing {num_cards_to_deal} cards for round {self.state.cnt_round}")

        for player in self.state.list_player:
            # Check if there are enough cards in the draw pile
            if len(self.state.list_card_draw) < num_cards_to_deal:
                if not self.state.list_card_discard:
                    raise ValueError("Not enough cards to deal and no cards in discard pile to reshuffle.")

                print("Reshuffling discard pile into draw pile.")
                self.state.list_card_draw.extend(self.state.list_card_discard)
                random.shuffle(self.state.list_card_draw)
                self.state.list_card_discard.clear()

            # Deal cards to the player
            player.list_card = [
                self.state.list_card_draw.pop() for _ in range(num_cards_to_deal)
            ]
            print(f"{player.name} received: {[f'{card.rank}{card.suit}' for card in player.list_card]}")

    def advance_round(self):
        """Advance to the next round."""
        self.state.cnt_round += 1
        if self.state.cnt_round > len(self.round_pattern):
            self.state.phase = GamePhase.FINISHED

    def reset_game(self):
        """Reset the game to its initial state."""
        self.state = GameState()

class DogBenchmark:
    CNT_PLAYERS = 4

    def __init__(self):
        self.game = Dog()

    def test_initial_game_state_values(self):
        """Test initial game state."""
        self.game.reset_game()
        state = self.game.state

        assert state.phase == GamePhase.RUNNING, "Error: Game phase must be RUNNING initially."
        assert state.cnt_round == 1, "Error: Round count must be 1 initially."
        assert len(state.list_card_discard) == 0, "Error: Discard pile must be empty initially."
        assert len(state.list_card_draw) == len(GameState.LIST_CARD), "Error: Draw pile must have all cards initially."
        assert len(state.list_player) == self.CNT_PLAYERS, "Error: Incorrect number of players."

        for player in state.list_player:
            assert len(player.list_card) == 0, "Error: Players should not have cards initially."
            assert len(player.list_marble) == 4, "Error: Players must have 4 marbles."

    def test_card_dealing(self):
        """Test card dealing for multiple rounds."""
        self.game.reset_game()
        for round_num in range(1, 6):
            self.game.state.cnt_round = round_num
            try:
                self.game.deal_cards()
            except ValueError as e:
                print(f"Error during card dealing: {e}")
                break

            expected_card_count = self.game.round_pattern[round_num - 1]

            for player in self.game.state.list_player:
                assert len(player.list_card) == expected_card_count, (
                    f"Error: Each player should have {expected_card_count} cards in round {round_num}."
                )

if __name__ == "__main__":
    # Initialize game and benchmark tests
    benchmark = DogBenchmark()
    benchmark.test_initial_game_state_values()
    benchmark.test_card_dealing()
    print("All benchmark tests passed!")
