from typing import List, Any
from abc import ABCMeta, abstractmethod

GameState = Any
GameAction = Any


class Game(metaclass=ABCMeta):

    @abstractmethod
    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        pass

    @abstractmethod
    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        pass

    @abstractmethod
    def print_state(self) -> None:
        """ Print the current game state """
        pass

    @abstractmethod
    def get_list_action(self) -> List[GameAction]:
        """ Get a list of possible actions for the active player """
        pass

    @abstractmethod
    def apply_action(self, action: GameAction) -> None:
        """ Apply the given action to the game """
        pass

    @abstractmethod
    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class Player(metaclass=ABCMeta):

    @abstractmethod
    def select_action(self, state: GameState, actions: List[GameAction]) -> GameAction:
        """ Given masked game state and possible actions, select the next action """
        pass
