from typing import List, Optional
import string
import random
from enum import Enum
from pydantic import BaseModel, field_validator
from server.py.game import Game, Player

class GuessLetterAction(BaseModel):
    letter: str

class GamePhase(str, Enum):
    SETUP = 'setup'            
    RUNNING = 'running'        
    FINISHED = 'finished'      

class HangmanGameState(BaseModel):
    word_to_guess: str = ""
    phase: GamePhase = GamePhase.SETUP
    guesses: List[str] = []
    incorrect_guesses: List[str] = []

    def updateincorrect_guesses(self) -> None:
        self.incorrect_guesses = [letter for letter in self.guesses if letter not in self.word_to_guess]

    def get_masked_state(self):
        if self.phase == GamePhase.FINISHED:
            masked_word = self.word_to_guess
        else:
            masked_word = ''.join([letter if letter in self.guesses else '_' for letter in self.word_to_guess])
        return HangmanGameState(
            word_to_guess=masked_word,
            phase=self.phase,
            guesses=self.guesses,
            incorrect_guesses=self.incorrect_guesses
        )

    def check_if_finished(self) -> None:
        if len(set(self.word_to_guess).difference(set(self.guesses))) == 0:
            self.phase = GamePhase.FINISHED
        if len(set(self.guesses).difference(set(self.word_to_guess))) > 7:
            self.phase = GamePhase.FINISHED

    def apply_action(self, action: GuessLetterAction) -> None:
        self.guesses.append(action.letter)
        self.updateincorrect_guesses()
        self.check_if_finished()


class Hangman(Game):

    def __init__(self) -> None:
        self.state = HangmanGameState()

    def get_state(self) -> HangmanGameState:
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        self.state = state
        self.state.phase = GamePhase.RUNNING

    def print_state(self) -> None:
        state = self.state.get_masked_state()
        num_wrong = len(self.state.incorrect_guesses)
        print(num_worng)
        print(f"Guesses: {' '.join(self.state.guesses)}")

    def get_list_action(self) -> List[GuessLetterAction]:
        if self.state.phase == GamePhase.FINISHED:
            return []
        all_letters = string.ascii_uppercase
        return [GuessLetterAction(letter=letter) for letter in all_letters if letter not in self.state.guesses]

    def apply_action(self, action: GuessLetterAction) -> None:
        if self.state.phase == GamePhase.FINISHED:
            raise ValueError("fin")
        self.state.apply_action(action)

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        return self.state.get_masked_state()

class RandomPlayer(Player):
    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        if len(actions) > 0:
            return random.choice(actions)
        return None

if __name__ == "__main__":
    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DEVOPS')
    game.set_state(game_state)
    player = RandomPlayer()
    for _ in range(26):
        if game.state.phase == GamePhase.FINISHED:
            break
        act = player.select_action(game.get_state(), game.get_list_action())
        game.apply_action(act)
        game.print_state()
        print("\n-")

