# synchronizes_state.py


#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from app import log_utils
logger = log_utils.get_logger("app_websocket.log")
import gobang_games_core

# logging.basicConfig()

STATE = {"value": 0}

USERS = set()

gobang_games_core.start_sync_status()

def login_event(player_id):
    return gobang_games_core.encode_data({"event_type": "login_success", "player_id":player_id})

def create_room_event(room_id):
    return gobang_games_core.encode_data({"event_type": "create_room_success", "room_id":room_id})


def join_room_event(room_id):
    return gobang_games_core.encode_data({"event_type": "join_room_success", "room_id":room_id})


def make_move_event(move_info):
    return gobang_games_core.encode_data({"event_type": "make_move_success", "move_info":move_info})

def room_over_event(room_over_info):
    return gobang_games_core.encode_data({"event_type": "room_over_success", "room_over_info":room_over_info})


def sync_frames_event(frame_info):
    return gobang_games_core.encode_data({"event_type": "sync_frams", "framw_info":frame_info})


async def notify_login(user_websocket, user_id):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        login_msg = login_event(user_id)
        logger.info(login_msg)
        await asyncio.wait([user_websocket.send(login_msg)])

async def notify_create_room(user_websocket, room_id):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        create_room_msg = create_room_event(room_id)
        logger.info(create_room_msg)
        await asyncio.wait([user_websocket.send(create_room_msg)])

async def notify_join_room(user_websocket, room_id):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        join_room_msg = join_room_event(room_id)
        logger.info(join_room_msg)
        await asyncio.wait([user_websocket.send(join_room_msg)])

async def notify_make_move(user_websocket, move_info):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        make_move_msg = make_move_event(move_info)
        logger.info(make_move_msg)
        await asyncio.wait([user_websocket.send(make_move_msg)])


async def sync_frames(user_websocket,  frame_info):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        frame_msg = sync_frames_event(frame_info)
        logger.info(frame_msg)
        await asyncio.wait([user_websocket.send(frame_msg)])

async def notify_room_over(user_websocket,  room_over):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        room_over_msg = room_over_event(room_over)
        logger.info(room_over_msg)
        await asyncio.wait([user_websocket.send(room_over_msg)])        


# user action  core hanlder
# see gobang_game_readme.md
async def event_router(websocket, path):
    try:
        # await websocket.send(state_event())
        async for action_str in websocket:
            logger.info('new message: ' + action_str)
            action_data = gobang_games_core.decode_data(action_str)

            if(action_data["action"] == "login"):
                user_id = gobang_games_core.login(action_data,  websocket)
                await notify_login(websocket, user_id)
                pass
            
            elif(action_data["action"] == "create_room"):
                room_id = gobang_games_core.create_room(action_data)
                await notify_create_room(websocket, room_id)
                pass
            
            elif (action_data["action"] == "join_room"):
                room_id  = gobang_games_core.join_room(action_data)
                await notify_join_room(websocket, room_id)
                pass

            elif (action_data["action"] == "exit_room"):
                gobang_games_core.exit_room(action_data)
                pass

            elif (action_data["action" ]== "make_move"):
                move_info = gobang_games_core.make_move(action_data)
                await notify_make_move(websocket, move_info)
                pass

            elif (action_data["action" ]== "room_over"):
                room_over_info = gobang_games_core.room_over(action_data)
                await notify_room_over(websocket, room_over_info)
                pass

            else:
                logger.error("invalid action : " + action_str);

    except Exception as e:
        logger.error(e)
    finally:
        # await gobang_games_core.unregister(websocket)
        pass

logger.info("start servering")

start_server = websockets.serve(event_router, "0.0.0.0", 8764 )

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()