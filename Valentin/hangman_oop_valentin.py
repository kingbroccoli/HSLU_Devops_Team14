from typing import List, Optional
import random
from enum import Enum

from Valentin.hangman_game_valentin import chosen_word
from devops_project.server.py.game import Game, Player


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
        self.attempts = attempts


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
    game_state = HangmanGameState(
        word_to_guess=chosen_word,
        phase=GamePhase.SETUP,
        guesses=[],
        incorrect_guesses=[],
        attempts = 6
    )
    game.set_state(game_state)
    # Step 1: Select a word
    word_list = ["valentin", "beat", "dimi" ,"marcel", "Gross" ,"house", "tree", "superman", "worldwideweb", "banane"]
    chosen_word = random.choice(word_list)
    display = ["_" for _ in chosen_word]  # Creates a list of underscores for each letter
    attempts = 6  # Number of allowed incorrect attempts
    guessed_letters = []  # To keep track of guessed letters

    print("Welcome to Hangman!")
    print("Try to guess the word letter by letter.")

    # Game loop
    while attempts > 0:
        print("\nCurrent word:", " ".join(display))  # Show the current state of the word
        print(f"Remaining attempts: {attempts}")
        print("Guessed letters:", " ".join(guessed_letters))

        # Step 2: Get the player's guess
        guess = input("Guess a letter: ").lower()

        # Check if the letter was already guessed
        if guess in guessed_letters:
            print("You already guessed that letter. Try again.")
            continue

        guessed_letters.append(guess)  # Add the guess to the list of guessed letters

        # Step 3: Check if the guess is in the word
        if guess in chosen_word:
            print(f"Good job! {guess} is in the word.")
            # Reveal the correct guessed letters in the display
            for index, letter in enumerate(chosen_word):
                if letter == guess:
                    display[index] = guess
        else:
            print(f"Sorry, {guess} is not in the word.")
            attempts -= 1  # Decrease attempts if guess is incorrect

        # Step 4: Check if the player has guessed the whole word
        if "_" not in display:
            print("\nCongratulations! You've guessed the word:", chosen_word)
            break

    # Step 5: End game if out of attempts
    if attempts == 0:
        print("\nSorry, you've run out of attempts. The word was:", chosen_word)

