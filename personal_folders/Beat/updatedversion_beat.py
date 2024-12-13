from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
import random


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


class Marble(BaseModel):
    pos: str  # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str  # name of player
    list_card: List[Card]  # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card  # card to play
    pos_from: Optional[int]  # position to move the marble from
    pos_to: Optional[int]  # position to move the marble to
    card_swap: Optional[Card]  # optional card to swap ()


class GamePhase(str, Enum):
    SETUP = 'setup'  # before the game has started
    RUNNING = 'running'  # while the game is running
    FINISHED = 'finished'  # when the game is finished


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',  # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
                                          Card(suit='♠', rank='2'), Card(suit='♥', rank='2'),
                                          Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
                                          Card(suit='♠', rank='3'), Card(suit='♥', rank='3'),
                                          Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
                                          Card(suit='♠', rank='4'), Card(suit='♥', rank='4'),
                                          Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
                                          Card(suit='♠', rank='5'), Card(suit='♥', rank='5'),
                                          Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
                                          Card(suit='♠', rank='6'), Card(suit='♥', rank='6'),
                                          Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
                                          Card(suit='♠', rank='7'), Card(suit='♥', rank='7'),
                                          Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
                                          Card(suit='♠', rank='8'), Card(suit='♥', rank='8'),
                                          Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
                                          Card(suit='♠', rank='9'), Card(suit='♥', rank='9'),
                                          Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
                                          Card(suit='♠', rank='10'), Card(suit='♥', rank='10'),
                                          Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
                                          Card(suit='', rank='J'), Card(suit='', rank='Q'),
                                          Card(suit='', rank='K'), Card(suit='', rank='A'),
                                          Card(suit='', rank='JKR')
                                      ] * 2

    cnt_player: int = 4  # number of players (must be 4)
    phase: GamePhase  # current phase of the game
    cnt_round: int  # current round
    bool_game_finished: bool  # true if game has finished
    bool_card_exchanged: bool  # true if cards was exchanged in round
    idx_player_started: int  # index of player that started the round
    idx_player_active: int  # index of active player in round
    list_player: List[PlayerState]  # list of players
    list_id_card_draw: List[Card]  # list of cards to draw
    list_id_card_discard: List[Card]  # list of cards discarded
    card_active: Optional[Card]  # active card (for 7 and JKR with sequence of actions)


class Dog(Game):

    def __init__(self) -> None:
        self.reset()

    def reset(self):
        self.set_state(GameState(
            LIST_SUIT=['♠', '♥', '♦', '♣'],
            LIST_RANK=['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', 'JKR'],
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=1,
            bool_game_finished=False,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[PlayerState(name=f"Player {i}", list_card=[], list_marble=[]) for i in range(4)],
            deck=None,
        ))

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        print(f"Current game state:")
        print(f"Phase: {self.state.phase}")
        print(f"Round: {self.state.cnt_round}")
        print("Players:")
        for i, player in enumerate(self.state.list_player):
            print(f"Player {i + 1}:")
            print(f"  Hand: {[card.rank for card in player.list_card]}")
            print(f"  Marbles: {[marble.pos for marble in player.list_marble]}")

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        current_player = self.state.list_player[self.state.idx_player_active]
        possible_actions = []

        # Check if there are cards to draw
        if self.state.list_id_card_draw:
            possible_actions.append(Action(card=self.state.list_id_card_draw.pop(0)))

        # Check if there's an active card
        if self.state.card_active:
            possible_actions.append(Action(card=self.state.card_active))

        return possible_actions

    def apply_action(self, action: Action) -> None:
        """ Apply the given action to the game """
        current_player = self.state.list_player[self.state.idx_player_active]

        if self.state.phase == GamePhase.RUNNING:
            if action.card.rank == 'JKR':
                self.handle_joker_action(action, current_player)
            elif action.card.rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
                self.handle_number_card_action(action, current_player)
            elif action.card.rank in ['J', 'Q', 'K', 'A']:
                self.handle_special_card_action(action, current_player)
            else:
                raise ValueError(f"Unknown card rank: {action.card.rank}")
        else:
            raise ValueError("Game is not in RUNNING phase")

    def handle_joker_action(self, action: Action, current_player: PlayerState):
        # Joker action implementation
        print(f"{current_player.name} played Joker!")

        # Swap hands with another player
        other_players = self.state.list_player[:self.state.idx_player_active] + \
                        self.state.list_player[self.state.idx_player_active + 1:]
        swap_player = random.choice(other_players)
        current_player.list_card, swap_player.list_card = swap_player.list_card, current_player.list_card

        # Move marbles forward
        for marble in current_player.list_marble:
            marble.pos = min(95, int(marble.pos) + random.randint(1, 10))

        # Draw new cards
        self.state.deck.cards.extend([self.state.deck.cards.pop() for _ in range(random.randint(2, 5))])
        current_player.list_card.extend([self.state.deck.cards.pop() for _ in range(random.randint(2, 5))])

    def handle_number_card_action(self, action: Action, current_player: PlayerState):
        # Number card action implementation
        print(f"{current_player.name} played {action.card.rank}!")

        move_amount = int(action.card.rank)
        current_marble = next((marble for marble in current_player.list_marble if marble.is_save), None)

        if current_marble:
            new_pos = min(95, int(current_marble.pos) + move_amount)
            current_marble.pos = str(new_pos)

            # If marble reaches end, save it
            if new_pos == 95:
                current_marble.is_save = True

        # Move active card forward
        self.state.card_active = action.card

    def handle_special_card_action(self, action: Action, current_player: PlayerState):
        # Special card (J, Q, K, A) action implementation
        print(f"{current_player.name} played {action.card.rank}!")

        if action.pos_from:
            # Move marble back
            current_marble = next(
                (marble for marble in current_player.list_marble if str(marble.pos) == str(action.pos_from)), None)

            if current_marble:
                current_marble.pos = max(0, int(current_marble.pos) - 1)

        if action.pos_to:
            # Move marble forward
            current_marble = next(
                (marble for marble in current_player.list_marble if str(marble.pos) == str(action.pos_from)), None)

            if current_marble:
                move_amount = int(action.pos_to) - int(current_marble.pos)
                new_pos = min(95, int(current_marble.pos) + move_amount)
                current_marble.pos = str(new_pos)

                # If marble reaches end, save it
                if new_pos == 95:
                    current_marble.is_save = True

        # Draw new cards
        self.state.deck.cards.extend([self.state.deck.cards.pop() for _ in range(random.randint(1, 3))])
        current_player.list_card.extend([self.state.deck.cards.pop() for _ in range(random.randint(1, 3))])


if __name__ == '__main__':
    game = Dog()
