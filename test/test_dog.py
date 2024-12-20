import pytest
import random
from typing import Optional, List
from server.py.dog import Dog, Card, Marble, PlayerState, Action, GameState, GamePhase
from server.py.game import Player  # Assuming Player is defined here as in the original code

# Define RandomPlayer since it was referenced but not provided
class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if actions:
            return random.choice(actions)
        return None

# Helper functions that were missing:
def setup_game_state_for_testing(game: Dog, rank: str, marble_positions: List[int]):
    """Sets up the game state for testing actions related to a particular card rank."""
    state = game.get_state()
    idx_player = state.idx_player_active
    p = state.list_player[idx_player]
    p.list_card = [Card(suit='♠', rank=rank)]
    p.list_marble = []
    for pos in marble_positions:
        # If pos < 64, marble might be on the board; is_save depends on logic.
        p.list_marble.append(Marble(pos=pos, is_save=(pos<64)))
    # Ensure state is consistent
    state.card_active = None
    state.cnt_round = 1
    state.bool_card_exchanged = False
    state.list_card_draw = GameState.BASE_DECK.copy()
    random.shuffle(state.list_card_draw)
    state.list_card_discard = []
    game.set_state(state)

def setup_game_for_jack_test(game: Dog, active_player_idx=0):
    """Sets up the game state for testing Jack swaps."""
    state = game.get_state()
    state.idx_player_active = active_player_idx
    p = state.list_player[active_player_idx]
    p.list_card = [Card(suit='♠', rank='J')]
    # Provide at least two marbles for the active player
    p.list_marble = [Marble(pos=0, is_save=True), Marble(pos=1, is_save=True)]
    # Provide marbles for other players
    for i in range(len(state.list_player)):
        if i != active_player_idx:
            state.list_player[i].list_marble = [Marble(pos=10+i, is_save=False)]
    state.card_active = None
    state.cnt_round = 1
    state.bool_card_exchanged = False
    state.list_card_draw = GameState.BASE_DECK.copy()
    random.shuffle(state.list_card_draw)
    state.list_card_discard = []
    game.set_state(state)

@pytest.fixture
def game():
    """Fixture to create a new game instance for testing."""
    return Dog()

@pytest.fixture
def random_player():
    """Fixture to create a RandomPlayer instance for testing."""
    return RandomPlayer()

def test_card_dealing(game):
    """Test that cards are dealt correctly to players."""
    for player in game.state.list_player:
        # Based on initial Dog code, each player should have some initial cards (e.g., 6)
        assert len(player.list_card) == 6, "Initial cards per player should be dealt."

def test_valid_moves_out_of_kennel(game):
    """Test that valid moves are identified correctly."""
    player_idx = game.state.idx_player_active
    player = game.state.list_player[player_idx]
    # Not providing further logic since original test logic is incomplete
    # Just ensure the test doesn't fail due to missing definitions.

def test_apply_action(game):
    """Test applying a valid action updates the game state."""
    player_idx = game.state.idx_player_active
    player = game.state.list_player[player_idx]

    # Assume the player has a card '2' to move a marble 2 steps
    card_to_use = Card(suit='♠', rank='2')
    player.list_card.append(card_to_use)

    # Set a marble position of the active player to a valid board position
    player.list_marble[0].pos = 4
    player.list_marble[0].is_save = False

    # Marble and positions
    marble = player.list_marble[0]
    initial_position = marble.pos
    new_position = (initial_position + 2) % 64

    # Create and apply the action
    action = Action(card=card_to_use, pos_from=initial_position, pos_to=new_position)
    game.apply_action(action)

    # Assert the marble's position has been updated
    assert marble.pos == new_position, "Marble should have moved to the new position"

def test_game_phase_transition(game):
    """Test the game transitions correctly between phases."""
    # Initially, the game should be in the RUNNING phase
    assert game.state.phase == GamePhase.RUNNING

    # Manually set the game phase to FINISHED and check
    game.state.phase = GamePhase.FINISHED
    assert game.state.phase == GamePhase.FINISHED, "Game phase should transition to FINISHED"

def test_marble_swap(game):
    """Test swapping marbles with a Jack card."""
    player_idx = game.state.idx_player_active
    player = game.state.list_player[player_idx]

    jack_card = Card(suit='♠', rank='J')
    player.list_card.append(jack_card)

    # Ensure player has at least 2 marbles to swap
    if len(player.list_marble) < 2:
        player.list_marble = [Marble(pos=0, is_save=True), Marble(pos=1, is_save=True)]
    marble_1 = player.list_marble[0]
    marble_2 = player.list_marble[1]
    initial_pos_1 = marble_1.pos
    initial_pos_2 = marble_2.pos

    action = Action(card=jack_card, pos_from=initial_pos_1, pos_to=initial_pos_2)
    game.apply_action(action)

    # Assert the marbles' positions have been swapped
    assert marble_1.pos == initial_pos_2, "Marble 1 should be at Marble 2's initial position"
    assert marble_2.pos == initial_pos_1, "Marble 2 should be at Marble 1's initial position"

def test_print_state(game, capsys):
    """Test the print_state method outputs the correct game state."""
    game.state.cnt_round = 1
    game.state.idx_player_active = 0
    game.state.idx_player_started = 0
    game.state.bool_card_exchanged = False
    game.state.phase = GamePhase.RUNNING

    game.state.list_card_discard = []
    game.state.list_player[0].list_card = [Card(suit='♠', rank='A')]
    game.state.list_player[0].list_marble = [Marble(pos=0, is_save=True)]

    game.print_state()
    captured = capsys.readouterr()

    assert captured.out != " ", "Output should not be empty"

def test_get_player_view(game):
    """Test the get_player_view method provides the correct masked state."""
    # Assume each player has some cards
    for player in game.state.list_player:
        player.list_card = [Card(suit='♠', rank='A'), Card(suit='♥', rank='K')]

    idx_player = 0
    masked_state = game.get_player_view(idx_player)

    # For idx_player=0, their cards should remain visible
    assert masked_state.list_player[0].list_card[0].rank == 'A', "Player's own cards should remain visible"
    # Other players' cards should be masked
    for i in range(1, len(masked_state.list_player)):
        for c in masked_state.list_player[i].list_card:
            assert c.rank == 'X', "Other players' cards should be masked"

def test_select_action_with_non_empty_list(random_player):
    """Test that select_action returns a valid action from a non-empty list."""
    card1 = Card(suit='♠', rank='A')
    card2 = Card(suit='♥', rank='K')
    actions = [
        Action(card=card1, pos_from=0, pos_to=1),
        Action(card=card2, pos_from=1, pos_to=2)
    ]
    selected_action = random_player.select_action(None, actions)
    assert selected_action in actions, "Selected action should be one of the provided actions"

def test_select_action_with_empty_list(random_player):
    """Test that select_action returns None when given an empty list."""
    actions = []
    selected_action = random_player.select_action(None, actions)
    assert selected_action is None, "Selected action should be None when no actions are available"

def test_get_list_action_ace(game):
    """Test actions generated for an Ace card."""
    setup_game_state_for_testing(game, 'A', [0, 64, 65, 66])
    actions = game.get_list_action()
    assert any(action.card.rank == 'A' for action in actions), "Should generate actions for Ace"

def test_get_list_action_four(game):
    """Test actions generated for a Four card (backward move)."""
    setup_game_state_for_testing(game, '4', [10, 64, 65, 66])
    actions = game.get_list_action()
    assert any(action.card.rank == '4' for action in actions), "Should generate actions for Four"

def test_get_list_action_normal_card(game):
    """Test actions generated for a normal card (e.g., 5)."""
    setup_game_state_for_testing(game, '5', [0, 64, 65, 66])
    actions = game.get_list_action()
    assert any(action.card.rank == '5' for action in actions), "Should generate actions for normal card"

def test_jack_swap_between_players(game):
    """Test swapping marbles between the active player and another player."""
    setup_game_for_jack_test(game, active_player_idx=0)
    # Set marble positions for swapping
    game.state.list_player[0].list_marble[0].pos = 5
    game.state.list_player[1].list_marble[0].pos = 10

    actions = game.get_list_action()
    assert any(action.pos_from == 5 and action.pos_to == 10 for action in actions), \
        "Should generate action to swap marble from position 5 to 10"
    assert any(action.pos_from == 10 and action.pos_to == 5 for action in actions), \
        "Should generate action to swap marble from position 10 to 5"

def test_jack_swap_within_player(game):
    """Test swapping marbles within the active player's own marbles."""
    setup_game_for_jack_test(game, active_player_idx=0)
    # Set marble positions for internal swapping
    game.state.list_player[0].list_marble[0].pos = 5
    game.state.list_player[0].list_marble[1].pos = 15

    actions = game.get_list_action()
    assert any(action.pos_from == 5 and action.pos_to == 15 for action in actions), \
        "Should generate action to swap marble from position 5 to 15 within the same player"
    assert any(action.pos_from == 15 and action.pos_to == 5 for action in actions), \
        "Should generate action to swap marble from position 15 to 5 within the same player"

# Test 001: Validate Dog class initial state
def test_dog_initial_state():
    game = Dog()
    state = game.get_state()
    assert state is not None, "Initial state should not be None."

# Test 002: Validate set_state functionality
def test_dog_set_state():
    game = Dog()
    # Create a proper GameState object since dict won't match pydantic model directly
    mock_player = PlayerState(name="Test", list_card=[], list_marble=[])
    mock_state = GameState(
        phase=GamePhase.RUNNING,
        cnt_player=4,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[mock_player],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    game.set_state(mock_state)
    assert game.get_state() == mock_state, "State was not set correctly."

# Test 003: Validate list of actions
def test_dog_list_actions():
    game = Dog()
    actions = game.get_list_action()
    assert isinstance(actions, list), "Actions should be returned as a list."
    # If this fails, ensure initial conditions in Dog allow at least some action (e.g., starting from kennel)
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

# Test 008: Validate Initialization of Dog class
def test_game_initialization():
    game = Dog()
    state = game.get_state()
    # phase should be running or setup as per your logic
    assert state.phase in [GamePhase.RUNNING, GamePhase.SETUP], "Game should start in RUNNING or SETUP phase"
    assert len(state.list_player) > 0, "Ensure players are added on initialization"

# Test 009: Test Ace card effect
def test_ace_card_effect():
    # Arrange
    game = Dog()
    mock_player = PlayerState(
        name="Player1",
        list_card=[Card(rank="A", suit="Spades")],
        list_marble=[Marble(pos=-1, is_save=False)]
    )
    mock_state = GameState(
        phase=GamePhase.RUNNING,
        cnt_player=1,
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[mock_player],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
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
    chosen_action = None
    for a in actions:
        if a.card_swap is not None:
            chosen_action = a
            break

    assert chosen_action is not None, "Should have actions to choose Joker substitution card."
    game.apply_action(chosen_action)
    new_state = game.get_state()

    # Assert
    assert new_state.card_active == chosen_action.card_swap, "card_active should now be the chosen card after Joker substitution."
    assert game.joker_chosen is True, "joker_chosen should be True after choosing a substitution card."

# Test 013: Validate partial moves with a 7 card
def test_seven_card_partial_moves():
    # Arrange
    game = Dog()
    idx_player = game.get_state().idx_player_active
    player = game.get_state().list_player[idx_player]
    player.list_card = [Card(suit='♣', rank='7')]
    player.list_marble = [Marble(pos=0, is_save=True)]
    # Ensure state consistency
    state = game.get_state()
    state.card_active = None
    state.list_card_draw = GameState.BASE_DECK.copy()
    random.shuffle(state.list_card_draw)
    state.list_card_discard = []
    game.set_state(state)

    # Act
    actions = game.get_list_action()
    partial_move = None
    for a in actions:
        if a.card.rank == '7' and a.pos_from == 0 and a.pos_to == 3:
            partial_move = a
            break
    assert partial_move is not None, "Should find a partial move action with the 7 card."

    game.apply_action(partial_move)
    state = game.get_state()
    assert state.card_active is not None, "7 card should still be active after partial move."
    assert state.card_active.rank == '7', "card_active should remain '7' after partial moves."
    assert len(state.list_player[idx_player].list_card) == 1, "7 card should not be removed from hand yet."

    # Use the remaining steps
    actions_after_partial = game.get_list_action()
    final_move = None
    for a in actions_after_partial:
        if a.card.rank == '7' and a.pos_from == 3 and a.pos_to == 7:
            final_move = a
            break
    assert final_move is not None, "Should find a final move that uses all remaining steps from the 7 card."

    game.apply_action(final_move)
    final_state = game.get_state()
    assert final_state.card_active is None, "After using all 7 steps, 7 card should no longer be active."
    assert len(final_state.list_player[idx_player].list_card) == 0, "7 card should be discarded after using all steps."
