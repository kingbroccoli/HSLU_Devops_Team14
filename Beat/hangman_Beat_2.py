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

    class Hangman(Game):
        def __init__(self) -> None:
            self.state: Optional[HangmanGameState] = None

        def get_state(self) -> HangmanGameState:
            if not self.state:
                raise ValueError("Game state is not initialized.")
            return self.state

        def set_state(self, state: HangmanGameState) -> None:
            self.state = state

        def print_state(self) -> None:
            if not self.state:
                raise ValueError("Game state is not initialized.")

            word_display = ''.join(
                [char if char in self.state.guesses else '_' for char in self.state.word_to_guess]
            )
            print(f"Word: {word_display}")
            print(f"Guesses: {', '.join(self.state.guesses)}")
            print(f"Incorrect guesses: {', '.join(self.state.incorrect_guesses)}")

        def get_list_action(self) -> List[GuessLetterAction]:
            if not self.state or self.state.phase != GamePhase.RUNNING:
                return []

            all_letters = set('abcdefghijklmnopqrstuvwxyz')
            guessed_letters = set(self.state.guesses + self.state.incorrect_guesses)
            available_letters = all_letters - guessed_letters
            return [GuessLetterAction(letter) for letter in available_letters]

        def apply_action(self, action: GuessLetterAction) -> None:
            if not self.state or self.state.phase != GamePhase.RUNNING:
                raise ValueError("Cannot play at this stage of the game.")

            letter = action.letter.lower()
            if letter in self.state.word_to_guess:
                self.state.guesses.append(letter)
            else:
                self.state.incorrect_guesses.append(letter)

            if all(char in self.state.guesses for char in self.state.word_to_guess):
                self.state.phase = GamePhase.FINISHED
                print("You won! The word was:", self.state.word_to_guess)
            elif len(self.state.incorrect_guesses) >= 6:
                self.state.phase = GamePhase.FINISHED
                print("Game over! The word was:", self.state.word_to_guess)

        def get_player_view(self, idx_player: int) -> HangmanGameState:
            if not self.state:
                raise ValueError("Game state is not initialized.")

            masked_word = ''.join(
                [char if char in self.state.guesses else '_' for char in self.state.word_to_guess]
            )
            return HangmanGameState(
                word_to_guess=masked_word,
                phase=self.state.phase,
                guesses=self.state.guesses,
                incorrect_guesses=self.state.incorrect_guesses,
            )

class RandomPlayer(Player):
    class RandomPlayer(Player):

        def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[
            GuessLetterAction]:
            """
            Given the current game state and possible actions, prompt the user to select the next action.
            This assumes that the player is a human user.
            """
            if not actions:
                print("No more available actions.")
                return None

            # Display masked word to the player
            print("\nWord to guess:", state.word_to_guess)
            print("Guessed letters:", ', '.join(state.guesses))
            print("Incorrect guesses:", ', '.join(state.incorrect_guesses))

            # Show available actions (letters left to guess)
            available_letters = [action.letter for action in actions]
            print("Available letters:", ', '.join(available_letters))

            while True:
                guess = input("Enter your guess (a single letter): ").lower()

                # Ensure input is valid and available
                if len(guess) != 1 or not guess.isalpha():
                    print("Invalid input. Please enter a single letter.")
                elif guess not in available_letters:
                    print("Letter not available or already guessed. Try again.")
                else:
                    return GuessLetterAction(guess)


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
        pr