from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        self.letter = letter


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:

    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        pass

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        pass

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        pass

    def print_state(self) -> None:
        """ Print the current game state """
        pass

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps', phase=GamePhase.SETUP, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)
    

    # Initialize game data
    words = ['test', 'cat', 'dog', 'lamp']
    all_letters = list('abcdefghijklmnopqrstuvwxyz')  # All possible letters
    guessed_letters = []  # Store guessed letters
    word = random.choice(words)
    shown_word = ['_'] * len(word)

    # Functions
    def open_letter(letter, word, shown_word):
        """Update the shown word with the guessed letter."""
        for idx, char in enumerate(word):
            if char == letter:
                shown_word[idx] = letter
        return shown_word

    def draw_next(state):
        """Draw the Hangman based on the current state."""
        hangman_stages = [
            '''
              -----
                  |
                  |
                  | 
                  |
                  |
            =========''',
            '''
              -----
                  |
              O   |
                  |
                  |
                  |
            =========''',
            '''
              -----
                  |
              O   |
              |   |
                  |
                  |
            =========''',
            '''
              -----
                  |
              O   |
             /|   |
                  |
                  |
            =========''',
            '''
              -----
                  |
              O   |
             /|\\  |
                  |
                  |
            =========''',
            '''
              -----
                  |
              O   |
             /|\\  |
             /    |
                  |
            =========''',
            '''
              -----
                  |
              O   |
             /|\\  |
             / \\  |
                  |
            =========''',
            '''
              -----
              |   |
              O   |
             /|\\  |
             / \\  |
                  |
            ========='''
        ]
        print(hangman_stages[state])

    # Game loop
    state = 0
    # max_mistakes = len(all_letters) - len(word)
    while state < 8:
        print("\nWord:", ' '.join(shown_word))
        print("Guessed letters:", ' '.join(guessed_letters))
        print("Remaining letters:", ' '.join(all_letters))

        guess = input("Guess a letter: ").lower()

        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single valid letter.")
            continue

        if guess in guessed_letters:
            print("You already guessed that letter!")
            continue

        guessed_letters.append(guess)
        all_letters.remove(guess)  # Remove the guessed letter from the pool

        if guess in word:
            shown_word = open_letter(guess, word, shown_word)
            if '_' not in shown_word:
                print("Congrats! You guessed the word:", ''.join(shown_word))
                break
        else:
            state += 1
            print(f"Nope! You made {state} mistakes.")
            draw_next(state-1)

    if state == 8:
        print(f"Game over! The word was: {word}")
