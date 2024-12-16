import pytest
from hangman import Hangman, HangmanGameState, GuessLetterAction, GamePhase


@pytest.fixture
def setup_game():
    """Fixture to initialize the game and state."""
    game = Hangman()
    state = HangmanGameState(word_to_guess="PYTHON")
    game.set_state(state)
    return game


def test_initial_state(setup_game):
    """Test the initial game state."""
    game = setup_game
    state = game.get_state()
    assert state.word_to_guess == "PYTHON"
    assert state.phase == GamePhase.RUNNING
    assert state.guesses == []
    assert state.incorrect_guesses == []


def test_guess_correct_letter(setup_game):
    """Test guessing a correct letter."""
    game = setup_game
    action = GuessLetterAction(letter="P")
    game.apply_action(action)
    state = game.get_state()
    assert "P" in state.guesses
    assert "P" not in state.incorrect_guesses
    assert state.phase == GamePhase.RUNNING


def test_guess_incorrect_letter(setup_game):
    """Test guessing an incorrect letter."""
    game = setup_game
    action = GuessLetterAction(letter="Z")
    game.apply_action(action)
    state = game.get_state()
    assert "Z" in state.incorrect_guesses
    assert state.phase == GamePhase.RUNNING


def test_game_finish_correct_guesses(setup_game):
    """Test game finishes when all correct letters are guessed."""
    game = setup_game
    for letter in "PYTHON":
        action = GuessLetterAction(letter=letter)
        game.apply_action(action)
    state = game.get_state()
    assert state.phase == GamePhase.FINISHED


def test_game_finish_incorrect_guesses(setup_game):
    """Test game finishes after too many incorrect guesses."""
    game = setup_game
    for letter in "ABCDEFGH":
        action = GuessLetterAction(letter=letter)
        game.apply_action(action)
    state = game.get_state()
    assert state.phase == GamePhase.FINISHED


def test_masked_state(setup_game):
    """Test the masked representation of the game state."""
    game = setup_game
    for letter in "PY":
        action = GuessLetterAction(letter=letter)
        game.apply_action(action)
    masked_state = game.get_state().get_masked_state()
    assert masked_state.word_to_guess == "PY____"
    assert masked_state.phase == GamePhase.RUNNING
