from typing import List, Optional
import random
from enum import Enum


class Game:
    """Base Game class, serves as a placeholder for game logic."""
    pass


class Player:
    """Base Player class, serves as a placeholder for player logic."""
    pass


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

    def get_player_view(self) -> HangmanGameState:
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
    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        if not actions:
            print("No more available actions.")
            return None

        print("\nWord to guess:", ''.join([char if char in state.guesses else '_' for char in state.word_to_guess]))
        print("Guessed letters:", ', '.join(state.guesses))
        print("Incorrect guesses:", ', '.join(state.incorrect_guesses))
        available_letters = [action.letter for action in actions]
        print("Available letters:", ', '.join(available_letters))

        while True:
            guess = input("Enter your guess (a single letter): ").lower()
            if len(guess) != 1 or not guess.isalpha():
                print("Invalid input. Please enter a single letter.")
            elif guess not in available_letters:
                print("Letter not available or already guessed. Try again.")
            else:
                return GuessLetterAction(guess)


def draw_next(mistake_count: int) -> None:
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
    ]
    print(hangman_stages[min(mistake_count, len(hangman_stages) - 1)])


if __name__ == "__main__":
    # Initialize the game
    game = Hangman()
    word = random.choice(['test', 'cat', 'dog', 'lamp']).lower()
    game_state = HangmanGameState(word_to_guess=word, phase=GamePhase.RUNNING, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)

    player = RandomPlayer()
    while game_state.phase == GamePhase.RUNNING:
        actions = game.get_list_action()
        action = player.select_action(game_state, actions)
        if action:
            game.apply_action(action)
            draw_next(len(game_state.incorrect_guesses))  # Draw Hangman based on mistakes
            game.print_state()
