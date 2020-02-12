# snack_game_core_test.py
import asyncio
import json
import logging
import websockets
import time;
from app import log_utils
import uuid
import threading
import random
import snack_game_core
import sys
import uvloop
logger = log_utils.get_logger(log_filename="app_ssnake_client_websocket.log", level=logging.INFO)

# logging.basicConfig()

# client_count = 1500; 
client_websocket_relations = dict()
client_room_relations = dict()

# server_uri = "ws://192.168.1.102:8763"
server_uri = "ws://127.0.0.1:8762"

login_action = {"action":"login"}



def make_move_event(room_id, player_id, to_go):

    make_move_action = {"action":"make_move",
                                                        "to_go":to_go,
                                                        "player_id":player_id,
                                                        "room_id":room_id};

    return snack_game_core.encode_data(make_move_action)


def create_room_event(room_id, player_id):

    actions = {"action":"create_room",
                            "player_id":player_id,
                            "room_name":"new_room",
                            "room_id":room_id}
    # logger.info(f"xxxx+" + json.dumps(actions))
    return snack_game_core.encode_data(actions)

def join_room_event(room_id, player_id):

    actions = {"action":"join_room",
                            "player_id":player_id,
                            "room_id":room_id}

    return snack_game_core.encode_data(actions)



async def startOneRoom(room_player_count=1):


    try:            
        # client_websocket = websockets.connect(server_uri)
        async with websockets.connect(server_uri) as client_websocket:

            #  login
            await client_websocket.send(json.dumps(login_action))
            login_result_str = await client_websocket.recv()
            login_result = json.loads(login_result_str)
            player_id = login_result['player_id']
            logger.debug("new player_id:" + player_id)
            client_websocket_relations[player_id] = client_websocket

            # create room 
            tmp_room_id = "room_" + str(uuid.uuid4())
            await client_websocket.send(create_room_event(tmp_room_id, player_id))
            create_room_result_str = await client_websocket.recv()
            logger.debug(create_room_result_str)
            create_room_result = json.loads(create_room_result_str)
            if ('room_id' in create_room_result):
                real_room_id = create_room_result['room_id']
                client_room_relations[player_id] = real_room_id    

            logger.debug(f"client create_room{real_room_id}_success...........................")

            for player_index in range(0,room_player_count-1):
                logger.info("player_index: " + str(player_index))
                single_room_client_thread = threading.Thread(target=async_room_client, args=(tmp_room_id,))
                single_room_client_thread.start()

            while True:
                sleep_time = random.randint(300,600);
                time.sleep(sleep_time/1000)
                logger.debug("make move for player: " + player_id)
                to_go = 1;
                await client_websocket.send(make_move_event(tmp_room_id, player_id, to_go))
                login_result_str = await client_websocket.recv()

    except Exception as e:
        raise
    else:
        pass
    finally:
        pass


async def client_make_move(room_id):

    async with websockets.connect(server_uri) as client_websocket:
        #  login
        await client_websocket.send(json.dumps(login_action))
        login_result_str = await client_websocket.recv()
        login_result = json.loads(login_result_str)
        player_id = login_result['player_id']
        logger.debug("new player_id:" + player_id)
        client_websocket_relations[player_id] = client_websocket

        # joinroom 
        await client_websocket.send(join_room_event(room_id, player_id))
        join_room_result_str = await client_websocket.recv()
        logger.debug(join_room_result_str)
        join_room_result = json.loads(join_room_result_str)
        if ('room_id' in join_room_result):
            real_room_id = join_room_result['room_id']
            client_room_relations[player_id] = real_room_id    
            logger.debug(f"client join_room{real_room_id}_success...........................")
    
        while True:
            sleep_time = random.randint(300,600);
            time.sleep(sleep_time/1000)
            logger.debug("make move for player: " + player_id)
            to_go = 1;
            await client_websocket.send(make_move_event(room_id, player_id, to_go))
            login_result_str = await client_websocket.recv()
            # logger.info(login_result_str)
            


def async_room_client(room_id):
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    #  this is more more important !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    new_loop.run_until_complete(client_make_move(room_id)) 
    # asyncio.run(client_make_move(room_id))

def async_start_room(room_player_count = 1):
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    #  this is more more important !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    new_loop.run_until_complete(startOneRoom(room_player_count))
    # asyncio.get_event_loop().run_until_complete(startOneClient())




if __name__ == '__main__':
    try:
        room_count = int(sys.argv[1])
        room_player_count = int(sys.argv[2])
        logger.info(f"room_count: {room_count}, room_player_count:{room_player_count}")
        for room_index in range (0, room_count) :
            single_room_thread = threading.Thread(target=async_start_room, args=(room_player_count,))
            single_room_thread.start()
           # asyncio.get_event_loop().run_until_complete(startClient())

    except Exception as e:
        raise
    else:
        pass
    finally:
        pass
    pass