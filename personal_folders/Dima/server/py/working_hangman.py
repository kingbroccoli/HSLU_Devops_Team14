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

    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str] = [], incorrect_guesses: List[str] = []) -> None:
        self.word_to_guess = word_to_guess
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman(Game):

    def __init__(self) -> None:
        """ Important: Game initialization also requires a set_state call to set the 'word_to_guess' """
        self.phase = None
        pass

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return self.state

        pass

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        self.state = state
        self.state.phase = GamePhase
        pass

    def print_state(self) -> None:
        """ Print the current game state """
        shown_word = ['_'] * len(game_state.word_to_guess)
        print("\nWord:", ' '.join(shown_word))
        print("Guessed letters:", ' '.join(game_state.guesses))
        print("Incorrect guesses letters:", ' '.join(game_state.incorrect_guesses))
        print("Remaining letters:", ' '.join(all_letters))
        

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
    # Initialize game data

    words = ['test', 'cat', 'dog', 'lamp']
    all_letters = list('abcdefghijklmnopqrstuvwxyz')  # All possible letters
    game_state = HangmanGameState(word_to_guess=random.choice(words), phase=GamePhase.RUNNING)
    game.set_state(game_state)
    game.print_state()
    
    shown_word = ['_'] * len(game_state.word_to_guess)

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
    while state < 8:
        print("\nWord:", ' '.join(shown_word))
        print("Guessed letters:", ' '.join(game_state.guesses))
        print("Incorrect guesses:", ' '.join(game_state.incorrect_guesses))
        print("Remaining letters:", ' '.join(all_letters))

        guess = input("Guess a letter: ").lower()

        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single valid letter.")
            continue

        if guess in game_state.guesses:
            print("You already guessed that letter!")
            continue

        game_state.guesses.append(guess)
        all_letters.remove(guess)  # Remove the guessed letter from the pool

        if guess in game_state.word_to_guess:
            shown_word = open_letter(guess, game_state.word_to_guess, shown_word)
            if '_' not in shown_word:
                print("Congrats! You guessed the word:", ''.join(shown_word))
                game.state.phase = GamePhase.FINISHED
                break

        else:
            state += 1
            game_state.incorrect_guesses.append(guess)
            print(f"Nope! You made {state} mistakes.")
            draw_next(state-1)

    if state == 8:
        print(f"Congrats! You lost. Gave over. The word was: {game_state.word_to_guess}")
        game.state.phase = GamePhase.FINISHED
