import pytest
from server.py.dog import Dog  # Import the class/module you want to test

def test_dog_initial_state():
    game = Dog()
    state = game.get_state()
    assert state is not None  # Example: Check initial state exists

def test_dog_set_state():
    game = Dog()
    new_state = {"phase": "RUNNING", "player_turn": 1}  # Replace with real state object
    game.set_state(new_state)
    assert game.get_state() == new_state  # Verify state was set correctly

def test_dog_list_actions():
    game = Dog()
    actions = game.get_list_action()
    assert isinstance(actions, list)  # Verify it returns a list
    assert len(actions) > 0  # Ensure actions are available

