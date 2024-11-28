# server/py/hangman.py
from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        self.letter = letter.upper()


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:

    def __init__(self, word_to_guess: str, guesses: List[str], phase: GamePhase) -> None:
        self.word_to_guess = word_to_guess.upper()
        self.guesses = guesses
        self.phase = phase
        self.incorrect_guesses = 0  # Track incorrect guesses


class Hangman(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        self.state: Optional[HangmanGameState] = None

    def get_state(self) -> HangmanGameState:
        """ Get the complete, unmasked game state """
        if not self.state:
            raise ValueError("Game state is not set.")
        return self.state

    def set_state(self, state: HangmanGameState) -> None:
        """ Set the game to a given state """
        self.state = state
        self.state.phase = GamePhase.RUNNING

    def print_state(self) -> None:
        """ Print the current game state """
        if not self.state:
            raise ValueError("Game state is not set.")
        word_to_show = ''.join(
            letter if letter in self.state.guesses else '_'
            for letter in self.state.word_to_guess
        )
        print(f"Word to guess: {word_to_show}")
        print(f"Guesses: {', '.join(self.state.guesses)}")
        print(f"Incorrect guesses: {self.state.incorrect_guesses}")
        print(f"Phase: {self.state.phase}")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        if not self.state:
            raise ValueError("Game state is not set.")
        return [GuessLetterAction(letter) for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if letter not in self.state.guesses]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        if not self.state:
            raise ValueError("Game state is not set.")
        guess = action.letter.upper()
        if guess in self.state.guesses:
            print(f"Letter '{guess}' was already guessed.")
            return
        self.state.guesses.append(guess)
        if guess not in self.state.word_to_guess:
            print(f"Letter '{guess}' is incorrect.")
            self.state.incorrect_guesses += 1
        if all(letter in self.state.guesses for letter in self.state.word_to_guess):
            self.state.phase = GamePhase.FINISHED
            print("Congratulations! You've guessed the word.")
        elif self.state.incorrect_guesses >= 8:
            self.state.phase = GamePhase.FINISHED
            print("Game over! You've made 8 incorrect guesses.")

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player """
        if not self.state:
            raise ValueError("Game state is not set.")
        return HangmanGameState(
            word_to_guess=self.state.word_to_guess,
            guesses=self.state.guesses,
            phase=self.state.phase,
        )


class RandomPlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    game = Hangman()
    words = ['devops', 'python', 'hangman', 'software']
    game_state = HangmanGameState(word_to_guess=random.choice(words), guesses=[], phase=GamePhase.SETUP)
    game.set_state(game_state)

    print("Welcome to Hangman!")
    while game_state.phase == GamePhase.RUNNING:
        game.print_state()
        actions = game.get_list_action()
        guess = input("Guess a letter: ").upper()
        if len(guess) == 1 and guess.isalpha():
            action = GuessLetterAction(guess)
            game.apply_action(action)
        else:
            print("Please guess a valid letter.")
    print(f"Game over! The word was: {game_state.word_to_guess}")