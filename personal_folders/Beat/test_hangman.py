import unittest
from hangman import Hangman, HangmanGameState, GamePhase


class TestHangman(unittest.TestCase):
    def setUp(self):
        self.game = Hangman("hangman")

    def test_initial_state(self):
        self.assertIsNone(self.game.state, "Initial game state should be None.")

    def test_set_and_get_state(self):
        state = HangmanGameState(
            word_to_guess="test",
            phase=GamePhase.RUNNING,
            guesses=["t"],
            incorrect_guesses=["x"]
        )
        self.game.set_state(state)
        retrieved_state = self.game.get_state()
        self.assertEqual(retrieved_state.word_to_guess, "test")
        self.assertEqual(retrieved_state.phase, GamePhase.RUNNING)
        self.assertEqual(retrieved_state.guesses, ["t"])
        self.assertEqual(retrieved_state.incorrect_guesses, ["x"])

    def test_game_win(self):
        state = HangmanGameState(
            word_to_guess="cat",
            phase=GamePhase.RUNNING,
            guesses=["c", "a", "t"],
            incorrect_guesses=[]
        )
        self.game.set_state(state)
        self.assertEqual(self.game.get_state().phase, GamePhase.FINISHED, "Game should be finished after correct guesses.")

    def test_game_loss(self):
        state = HangmanGameState(
            word_to_guess="dog",
            phase=GamePhase.RUNNING,
            guesses=["d"],
            incorrect_guesses=["x", "y", "z", "q", "w", "e"]
        )
        self.game.set_state(state)
        self.assertEqual(self.game.get_state().phase, GamePhase.FINISHED, "Game should be finished after 6 incorrect guesses.")


if __name__ == "__main__":
    unittest.main()
