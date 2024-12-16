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


# ----- Dog -----

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