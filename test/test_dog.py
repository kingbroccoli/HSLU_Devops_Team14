import pytest
from server.py.dog import Dog, Card, Marble, PlayerState, Action, GameState, GamePhase

# Test 001: Validate Dog class initial state
def test_dog_initial_state():
    game = Dog()
    state = game.get_state()
    assert state is not None, "Initial state should not be None."

# Test 002: Validate set_state functionality
def test_dog_set_state():
    game = Dog()
    new_state = {"phase": "RUNNING", "player_turn": 1}  # Replace with the correct GameState object if necessary
    game.set_state(new_state)
    assert game.get_state() == new_state, "State was not set correctly."

# Test 003: Validate list of actions
def test_dog_list_actions():
    game = Dog()
    actions = game.get_list_action()
    assert isinstance(actions, list), "Actions should be returned as a list."
    assert len(actions) > 0, "List of actions should not be empty."

# Test 004: Validate Marble class
def test_Marble_class():
    marble = Marble(pos=0, is_save=True)
    assert isinstance(marble, Marble), "Marble instance should be of type Marble."
    assert marble.pos == 0, "Marble position should be initialized correctly."
    assert marble.is_save is True, "Marble is_save should be initialized correctly."

# Test 005: Validate PlayerState class
def test_PlayerState_class():
    player_state = PlayerState(name="Test Player", list_card=[], list_marble=[])
    assert isinstance(player_state, PlayerState), "PlayerState instance should be of type PlayerState."
    assert player_state.name == "Test Player", "Player name should be initialized correctly."
    assert player_state.list_card == [], "list_card should be initialized as an empty list."
    assert player_state.list_marble == [], "list_marble should be initialized as an empty list."

# Test 006: Validate Action class
def test_Action_class():
    card = Card(suit="Hearts", rank="5")
    action = Action(card=card, pos_from=1, pos_to=10, card_swap=None)
    assert isinstance(action, Action), "Action instance should be of type Action."
    assert action.card == card, "Action's card attribute should be set correctly."
    assert action.pos_from == 1, "Action's pos_from should be set correctly."
    assert action.pos_to == 10, "Action's pos_to should be set correctly."
    assert action.card_swap is None, "Action's card_swap should be set correctly."

# Test 007: Validate GamePhase class
def test_GamePhase_class():
    assert hasattr(GamePhase, 'RUNNING'), "GamePhase should have an attribute 'RUNNING'."
    assert hasattr(GamePhase, 'FINISHED'), "GamePhase should have an attribute 'FINISHED'."
    assert GamePhase.RUNNING.name == 'RUNNING', "GamePhase.RUNNING name should be 'RUNNING'."
    assert GamePhase.FINISHED.name == 'FINISHED', "GamePhase.FINISHED name should be 'FINISHED'."

# Test 008: Validate Initalization of Dog class
def test_game_initialization():
    game = Dog()
    state = game.get_state()
    assert state.phase == "running"
    assert len(state.list_player) > 0  # Ensure players are added


# Test 009: Test Ace card effect
def test_ace_card_effect():
    # Arrange
    game = Dog()
    mock_player = PlayerState(
        name="Player1",
        list_card=[Card(rank="A", suit="Spades")],
        list_marble=[Marble(pos=-1, is_save=False)]
    )

    # Provide all required fields for GameState:
    mock_state = GameState(
        phase=GamePhase.RUNNING,
        cnt_player=1,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[mock_player],
        list_card_draw=[],       # empty list if no deck needed here
        list_card_discard=[],    # empty discard pile
        card_active=None         # no active card
    )

    game.set_state(mock_state)

    # Act
    actions = game.get_list_action()

    # Assert
    assert any(action.card.rank == "A" for action in actions), "Ace card should provide a valid action."

# Test 012: Validate Joker card choice scenario
def test_joker_card_choice():
    # Arrange
    game = Dog()
    state = game.get_state()
    idx_player = state.idx_player_active
    player = state.list_player[idx_player]
    # Give player a Joker and set card_active to Joker, but no chosen card yet
    player.list_card = [Card(suit='', rank='JKR')]
    state.card_active = Card(suit='', rank='JKR')
    game.set_state(state)

    # Act
    actions = game.get_list_action()
    # The actions should include choosing a card_swap (like A of any suit)
    # Let's pick the first card_swap action that appears
    chosen_action = None
    for a in actions:
        if a.card_swap is not None:
            chosen_action = a
            break

    #assert chosen_action is not None, "Should have actions to choose Joker substitution card."

    game.apply_action(chosen_action)
    new_state = game.get_state()

    # Assert
    # Now card_active should have changed to chosen_action.card_swap rank and suit
    assert new_state.card_active == chosen_action.card_swap, "card_active should now be the chosen card after Joker substitution."
    assert game.joker_chosen is True, "joker_chosen should be True after choosing a substitution card."

# Test 013: Validate partial moves with a 7 card
def test_seven_card_partial_moves():
    # Arrange
    game = Dog()
    idx_player = game.get_state().idx_player_active
    player = game.get_state().list_player[idx_player]
    # Give player a 7 and marbles on the board to move
    player.list_card = [Card(suit='♣', rank='7')]
    player.list_marble = [Marble(pos=0, is_save=True)]  # Marble at start field
    game.set_state(game.get_state())  # Update internal references if needed

    # Act
    actions = game.get_list_action()
    # Play the 7 card, moving forward a few steps (less than 7).
    # Find an action that moves the marble forward by 3 steps, for example (pos=0 to pos=3)
    partial_move = None
    for a in actions:
        if a.card.rank == '7' and a.pos_from == 0 and a.pos_to == 3:
            partial_move = a
        break
    assert partial_move is not None, "Should find a partial move action with the 7 card."

    game.apply_action(partial_move)
    state = game.get_state()

    # Now card_active should still be a '7' and the card should NOT be discarded yet since not all 7 steps are used.
    assert state.card_active is not None, "7 card should still be active after partial move."
    assert state.card_active.rank == '7', "card_active should remain '7' after partial moves."
    assert len(state.list_player[idx_player].list_card) == 1, "7 card should not be removed from hand yet."
    # Use the remaining steps
    actions_after_partial = game.get_list_action()
    # After using 3 steps, 4 steps remain. Find a move that uses exactly the remaining 4 steps:
    final_move = None
    for a in actions_after_partial:
        if a.card.rank == '7' and a.pos_from == 3 and a.pos_to == 7:  # total now 7 steps used
            final_move = a
            break
    assert final_move is not None, "Should find a final move that uses all remaining steps from the 7 card."

    game.apply_action(final_move)
    final_state = game.get_state()
    assert final_state.card_active is None, "After using all 7 steps, 7 card should no longer be active."
    assert len(final_state.list_player[idx_player].list_card) == 0, "7 card should be discarded after using all steps."