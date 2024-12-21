from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import json
import asyncio

import server.py.hangman as hangman
import server.py.battleship as battleship

import random

app = FastAPI()

app.mount("/inc/static", StaticFiles(directory="server/inc/static"), name="static")

templates = Jinja2Templates(directory="server/inc/templates")


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ----- Hangman -----

@app.get("/hangman/singleplayer/local/", response_class=HTMLResponse)
async def hangman_singleplayer(request: Request):
    return templates.TemplateResponse("game/hangman/singleplayer_local.html", {"request": request})

@app.websocket("/hangman/singleplayer/ws")
async def hangman_singleplayer_ws(websocket: WebSocket):
    await websocket.accept()

    idx_player_you = 0

    try:

        game = hangman.Hangman()

        words = []
        with open('server/py/hangman_words.json') as fin:
            words = json.load(fin)
        word_to_guess = random.choice(words)

        state = hangman.HangmanGameState(word_to_guess=word_to_guess, phase=hangman.GamePhase.RUNNING, guesses=[], incorrect_guesses=[])
        game.set_state(state)

        while True:

            state = game.get_player_view(idx_player_you)

            game.print_state()

            state = game.get_player_view(idx_player_you)
            list_action = game.get_list_action()
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = [action.model_dump() for action in list_action]
            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)

            if state.phase == hangman.GamePhase.FINISHED:
                break

            if len(list_action) == 0:
                game.apply_action(None)
            else:
                data = await websocket.receive_json()
                if data['type'] == 'action':
                    action = hangman.GuessLetterAction.model_validate(data['action'])
                    game.apply_action(action)
                    print(action)

            continue
            state = game.get_player_view(idx_player_you)
            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []

            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)

    except WebSocketDisconnect:
        print('DISCONNECTED')


# ----- Battleship -----

@app.get("/battleship/simulation/", response_class=HTMLResponse)
async def battleship_simulation(request: Request):
    return templates.TemplateResponse("game/battleship/simulation.html", {"request": request})


@app.websocket("/battleship/simulation/ws")
async def battleship_simulation_ws(websocket: WebSocket):
    await websocket.accept()

    idx_player_you = 0

    try:
        game = battleship.Battleship()
        player = battleship.RandomPlayer()

        while True:

            state = game.get_state()
            list_action = game.get_list_action()
            action = None
            if len(list_action) > 0:
                action = player.select_action(state, list_action)

            dict_state = state.model_dump()
            dict_state['idx_player_you'] = idx_player_you
            dict_state['list_action'] = []
            dict_state['selected_action'] = None if action is None else action.model_dump()
            data = {'type': 'update', 'state': dict_state}
            await websocket.send_json(data)

            if state.phase == battleship.GamePhase.FINISHED:
                break

            data = await websocket.receive_json()

            if data['type'] == 'action':
                action = battleship.BattleshipAction.model_validate(data['action'])
                game.apply_action(action)

    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.get("/battleship/singleplayer", response_class=HTMLResponse)
async def battleship_singleplayer(request: Request):
    return templates.TemplateResponse("game/battleship/singleplayer.html", {"request": request})


@app.websocket("/battleship/singleplayer/ws")
async def battleship_singleplayer_ws(websocket: WebSocket):
    await websocket.accept()

    idx_player_you = 0

    try:

        game = battleship.Battleship()
        player = battleship.RandomPlayer()

        while True:

            state = game.get_state()
            if state.phase == battleship.GamePhase.FINISHED:
                break

            #game.print_state()

            if state.idx_player_active == idx_player_you:

                state = game.get_player_view(idx_player_you)
                list_action = game.get_list_action()
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = [action.model_dump() for action in list_action]
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)

                if len(list_action) == 0:
                    game.apply_action(None)
                else:
                    data = await websocket.receive_json()
                    if data['type'] == 'action':
                        action = battleship.BattleshipAction.model_validate(data['action'])
                        game.apply_action(action)
                        print(action)

                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []

                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)

            else:

                state = game.get_player_view(state.idx_player_active)
                list_action = game.get_list_action()
                action = player.select_action(state, list_action)
                if action is not None:
                    await asyncio.sleep(1)
                game.apply_action(action)
                state = game.get_player_view(idx_player_you)
                dict_state = state.model_dump()
                dict_state['idx_player_you'] = idx_player_you
                dict_state['list_action'] = []
                data = {'type': 'update', 'state': dict_state}
                await websocket.send_json(data)

    except WebSocketDisconnect:
        print('DISCONNECTED')


# ----- UNO -----

@app.get("/uno/simulation/", response_class=HTMLResponse)
async def uno_simulation(request: Request):
    return templates.TemplateResponse("game/uno/simulation.html", {"request": request})


@app.websocket("/uno/simulation/ws")
async def uno_simulation_ws(websocket: WebSocket):
    await websocket.accept()

    try:

        pass

    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.get("/uno/singleplayer", response_class=HTMLResponse)
async def uno_singleplayer(request: Request):
    return templates.TemplateResponse("game/uno/singleplayer.html", {"request": request})


@app.websocket("/uno/singleplayer/ws")
async def uno_singleplayer_ws(websocket: WebSocket):
    await websocket.accept()

    try:

        pass

    except WebSocketDisconnect:
        print('DISCONNECTED')


@app.websocket("/uno/random_player/ws")
async def uno_random_player_ws(websocket: WebSocket):
    await websocket.accept()

    try:

        pass

    except WebSocketDisconnect:
        print('DISCONNECTED')


# ----- Dog ----- Initial version, commented out to try Marcel's implementation


# @app.get("/dog/simulation/", response_class=HTMLResponse)
# async def dog_simulation(request: Request):
#     return templates.TemplateResponse("game/dog/simulation.html", {"request": request})


# @app.websocket("/dog/simulation/ws")
# async def dog_simulation_ws(websocket: WebSocket):
#     await websocket.accept()

#     try:

#         pass

#     except WebSocketDisconnect:
#         print('DISCONNECTED')


# @app.get("/dog/singleplayer", response_class=HTMLResponse)
# async def dog_singleplayer(request: Request):
#     return templates.TemplateResponse("game/dog/singleplayer.html", {"request": request})


# @app.websocket("/dog/singleplayer/ws")
# async def dog_singleplayer_ws(websocket: WebSocket):
#     await websocket.accept()

#     try:

#         pass

#     except WebSocketDisconnect:
#         print('DISCONNECTED')


# @app.websocket("/dog/random_player/ws")
# async def dog_random_player_ws(websocket: WebSocket):
#     await websocket.accept()

#     try:

#         pass

#     except WebSocketDisconnect:
#         print('DISCONNECTED')




# ----- Dog ----- Marcel's Dog --  Should should be redone, because even for uno it shows something and for dog — nothing


@app.get("/dog/simulation/", response_class=HTMLResponse)
async def dog_simulation(request: Request):
    return templates.TemplateResponse("game/dog/simulation.html", {"request": request})


@app.websocket("/dog/simulation/ws")
async def dog_simulation_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        # Initialize or retrieve game state for simulation
        game = dog_game.DogGame()  # Create an instance of the game
        game_state = game.initialize_game()  # Initialize the game

        while True:
            # Receive player actions (e.g., play a card, move a marble)
            message = await websocket.receive_text()  # Receive message from client
            action = json.loads(message)  # Deserialize JSON action

            # Process the action (move a marble, play a card, etc.)
            updated_state = game.process_action(action, game_state)

            # Send updated game state back to the client
            await websocket.send_text(json.dumps(updated_state))  # Send updated state

            if game.check_game_over(updated_state):
                break  # End the game if a player has won

    except WebSocketDisconnect:
        print('DISCONNECTED')



@app.get("/dog/singleplayer", response_class=HTMLResponse)
async def dog_singleplayer(request: Request):
    return templates.TemplateResponse("game/dog/singleplayer.html", {"request": request})


@app.websocket("/dog/singleplayer/ws")
async def dog_singleplayer_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        # Initialize the game for singleplayer mode
        game = dog_game.DogGame()
        game_state = game.initialize_singleplayer_game()  # Initialize for single player

        while True:
            # Receive player's move (e.g., move a marble, play a card)
            message = await websocket.receive_text()
            action = json.loads(message)  # Deserialize action

            # Process the player's action (move a marble or play a card)
            updated_game_state = game.process_singleplayer_action(action, game_state)

            # Send the updated game state to the client
            await websocket.send_text(json.dumps(updated_game_state))

            if game.check_game_over(updated_game_state):
                break  # End the game if player has finished

    except WebSocketDisconnect:
        print('DISCONNECTED')



@app.websocket("/dog/random_player/ws")
async def dog_random_player_ws(websocket: WebSocket):
    await websocket.accept()

    try:
        # Initialize the game and set up the random player
        game = dog_game.DogGame()
        game_state = game.initialize_singleplayer_game()
        random_player = RandomPlayer()  # Assume you have a RandomPlayer class

        while True:
            # Random player selects an action
            action = random_player.select_action(game_state, game.get_possible_actions(game_state))

            # Process the action selected by the random player
            updated_game_state = game.process_action(action, game_state)

            # Send the updated state back to the client
            await websocket.send_text(json.dumps(updated_game_state))

            # End the game if the game over condition is met
            if game.check_game_over(updated_game_state):
                break

    except WebSocketDisconnect:
        print('DISCONNECTED')
