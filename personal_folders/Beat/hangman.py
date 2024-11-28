import random
from typing import List, Optional
from enum import Enum


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class HangmanGameState:
    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess.lower()
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses


class Hangman:
    def __init__(self, name: str) -> None:
        self.name = name  # A meaningful identifier for the game
        self.state: Optional[HangmanGameState] = None

    def set_state(self, state: HangmanGameState) -> None:
        self.state = state

    def get_state(self) -> HangmanGameState:
        if not self.state:
            raise ValueError("Game state is not initialized.")
        return self.state

    def print_state(self) -> None:
        if not self.state:
            raise ValueError("Game state is not initialized.")

        word_display = ''.join(
            [char if char in self.state.guesses else '_' for char in self.state.word_to_guess]
        )
        print("\nWord: ", word_display)
        print("Guesses: ", ', '.join(self.state.guesses))
        print("Incorrect guesses: ", ', '.join(self.state.incorrect_guesses))

    def draw_hangman(self, mistakes: int) -> None:
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
            ========='''
        ]
        print(hangman_stages[mistakes])

    def play_turn(self, guess: str) -> None:
        if not self.state or self.state.phase != GamePhase.RUNNING:
            raise ValueError("Game is not in a running state.")

        guess = guess.lower()
        if guess in self.state.word_to_guess:
            self.state.guesses.append(guess)
        else:
            self.state.incorrect_guesses.append(guess)

        if all(char in self.state.guesses for char in self.state.word_to_guess):
            self.state.phase = GamePhase.FINISHED
            print("You won! The word was:", self.state.word_to_guess)
        elif len(self.state.incorrect_guesses) >= 6:
            self.state.phase = GamePhase.FINISHED
            print("Game over! The word was:", self.state.word_to_guess)

    def start_game(self, word: str) -> None:
        self.set_state(HangmanGameState(word_to_guess=word, phase=GamePhase.RUNNING, guesses=[], incorrect_guesses=[]))
        while self.state.phase == GamePhase.RUNNING:
            self.print_state()
            self.draw_hangman(len(self.state.incorrect_guesses))
            guess = input("Enter your guess: ").strip().lower()
            if len(guess) != 1 or not guess.isalpha():
                print("Invalid input. Please enter a single letter.")
                continue
            if guess in self.state.guesses or guess in self.state.incorrect_guesses:
                print("You already guessed that letter!")
                continue
            self.play_turn(guess)
        self.print_state()
        self.draw_hangman(len(self.state.incorrect_guesses))


