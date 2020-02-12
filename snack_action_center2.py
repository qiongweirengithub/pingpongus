# synchronizes_state.py


#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets
from app import log_utils
# import snack_game_core_v2
import snack_game_core_v2
import concurrent.futures
import uvloop   
import time

_logger = log_utils.get_logger("app_snake_websocket.log", logging.INFO)
_logger.debug("start servering")


# logging.basicConfig()

STATE = {"value": 0}

USERS = set()

snack_game_core_v2.start_sync_status()

def login_event(player_id):
    return snack_game_core_v2.encode_data({"event_type": "login_success", "player_id":player_id})

def create_room_event(room_id):
    return snack_game_core_v2.encode_data({"event_type": "create_room_success", "room_id":room_id})


def join_room_event(room_id):
    return snack_game_core_v2.encode_data({"event_type": "join_room_success", "room_id":room_id})


def make_move_event(move_info):
    return snack_game_core_v2.encode_data({"event_type": "make_move_success", "move_info":move_info})

def room_over_event(room_over_info):
    return snack_game_core_v2.encode_data({"event_type": "room_over_success", "room_over_info":room_over_info})


def sync_frames_event(frame_info):
    return snack_game_core_v2.encode_data({"event_type": "sync_frams", "framw_info":frame_info})


async def notify_login(user_websocket, user_id):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        login_msg = login_event(user_id)
        _logger.debug(login_msg)
        await asyncio.wait([user_websocket.send(login_msg)])

async def notify_create_room(user_websocket, room_id):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        create_room_msg = create_room_event(room_id)
        _logger.debug(create_room_msg)
        await asyncio.wait([user_websocket.send(create_room_msg)])

async def notify_join_room(user_websocket, room_id):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        join_room_msg = join_room_event(room_id)
        _logger.debug(join_room_msg)
        await asyncio.wait([user_websocket.send(join_room_msg)])

async def notify_make_move(user_websocket, move_info):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        make_move_msg = make_move_event(move_info)
        _logger.debug(make_move_msg)
        await asyncio.wait([user_websocket.send(make_move_msg)])


async def sync_frames(user_websocket,  frame_info):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        frame_msg = sync_frames_event(frame_info)
        _logger.debug(frame_msg)
        await asyncio.wait([user_websocket.send(frame_msg)])

async def notify_room_over(user_websocket,  room_over):
    if user_websocket:  # asyncio.wait doesn't accept an empty list
        room_over_msg = room_over_event(room_over)
        _logger.debug(room_over_msg)
        await asyncio.wait([user_websocket.send(room_over_msg)])        


# user action  core hanlder
# see gobang_game_readme.md
async def event_router(websocket, path):
    try:
        # await websocket.send(state_event())
        async for action_str in websocket:
            _logger.debug('new message: ' + action_str)
            action_data = snack_game_core_v2.decode_data(action_str)

            if(action_data["action"] == "login"):
                user_id = snack_game_core_v2.login(action_data,  websocket)
                await notify_login(websocket, user_id)
                pass
            
            elif(action_data["action"] == "create_room"):
                room_id = snack_game_core_v2.create_room(action_data)
                await notify_create_room(websocket, room_id)
                pass
            
            elif (action_data["action"] == "join_room"):
                room_id  = snack_game_core_v2.join_room(action_data)
                await notify_join_room(websocket, room_id)
                pass

            elif (action_data["action"] == "exit_room"):
                snack_game_core_v2.exit_room(action_data)
                pass

            elif (action_data["action" ]== "make_move"):
                action_data['start_process_request'] = time.time()
                snack_game_core_v2.make_move(action_data)
                # await notify_make_move(websocket, move_info)
                pass

            elif (action_data["action" ]== "room_over"):
                room_over_info = snack_game_core_v2.room_over(action_data)
                await notify_room_over(websocket, room_over_info)
                pass

            else:
                _logger.error("invalid action : " + action_str);

    except Exception as e:
        _logger.error("event router run exception", exc_info=True)
    finally:
        # await snack_game_core_v2.unregister(websocket)
        pass




if __name__ == '__main__':

    try:
        start_server = websockets.serve(event_router, host="0.0.0.0", port=8762, read_limit=1024 )
        # _logger.info("start servering")
        # async def start_websocket_server():
        #     loop = asyncio.get_running_loop()
        #     with concurrent.futures.ThreadPoolExecutor() as pool:
        #             result = await loop.run_in_executor(pool, start_server)

        loop = asyncio.get_event_loop()
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        # pool =  concurrent.futures.ThreadPoolExecutor(max_workers=1)
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=2000)
        # with concurrent.futures.ProcessPoolExecutor() as pool:
        #     _logger.info("init main loop pool")
        loop.set_default_executor(pool)
        loop.run_until_complete(start_server)
        loop.run_forever()

    except Exception as e:
        raise
    else:
        pass
    finally:
        pass
    pass


