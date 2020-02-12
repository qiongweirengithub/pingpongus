# synchronizes_state.py


#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import queue
import threading
import time
import random
import uuid
# import gobang_games_action_center

from app import log_utils
logger = log_utils.get_logger("app_websocket.log")


rooms = dict()
rooms_moves = dict()
# rooms_moves['all'] = list()
# rooms_moves['frame2'] = list()
# rooms_moves['frame1'] = list()
# rooms_moves['next_start'] = 0
# rooms_moves['current_work_frame'] = 1
# 
# 
player_room_relations = dict()
player_socket_relations = dict()

circle_sync_list_len = 10
room_sync_delay_list = list()


def sync_frame_event(frame_array):
    return encode_data({"event_type": "sync_frame", "frame_array":frame_array})


def sched_sync_status() :
    asyncio.run(sched_sync_status_())


async def sched_sync_status_() :
    logger.info("started  schedule sync process") 
    cur_circle_index = 0
    try:

        while  True:
            time.sleep(0.02)

            if(len(room_sync_delay_list) <= 0) :
                continue
            need_sync_room_list = room_sync_delay_list[cur_circle_index]
            if(len(need_sync_room_list) > 0) :
                for room_id in need_sync_room_list  : 
                    if(room_id not in rooms):
                        need_sync_room_list.remove(room_id)
                        continue
                    await sync_room_status(room_id)
                    # await sync_room_status(room_id)
            else:
                # logger.info("need sync rooms for index:" + str(cur_circle_index) + " is empty")
                pass

            cur_circle_index = cur_circle_index + 1
            if(cur_circle_index  >= len(room_sync_delay_list)):
                cur_circle_index = 0

    except Exception as e:
        raise
    else:
        pass
    finally:
        pass


def start_sync_status() :

    if(len(room_sync_delay_list) > 0) :
        raise
    for sync_delay_list_size  in range(circle_sync_list_len):
        empty_sync_list = list()
        room_sync_delay_list.append(empty_sync_list)

    # asyncio.create_task(sched_sync_status())
    sync_thread = threading.Thread(target=sched_sync_status)
    sync_thread.start()
    logger.info("started  schedule sync thread") 



async def sync_room_status(room_id):
    next_need_sync_move_index = rooms_moves[room_id]['next_start'] 
    rooms_moves[room_id]['frame'] = rooms_moves[room_id]["all"][next_need_sync_move_index:] 
    rooms_moves[room_id]['next_start'] = len(rooms_moves[room_id]['all'])
    room_info =  rooms[room_id]

    new_frams = rooms_moves[room_id]['frame']
    if(len(new_frams) <= 0) :
        return
    # logger.info("roomid: " + room_id + "  all action : " + encode_data(rooms_moves[room_id]["all"]))

    logger.info("roomid: " + room_id + "  need sync frame : " + encode_data(new_frams))

    # logger.info(rooms_moves[room_id]['next_start'])

    if("player_1" in room_info) :
        player_1_id = room_info["player_1"]
        logger.info("player 1 : " + player_1_id)
        if(player_1_id in player_socket_relations) :
            logger.info("send msg to player1: " + player_1_id)
            player1_websocket = player_socket_relations[player_1_id] 
            # gobang_games_action_center.sync_frames(player1_websocket, rooms_moves[room_id]['frame'])
            await player1_websocket.send(sync_frame_event(rooms_moves[room_id]['frame']))

    if("player_2" in room_info) :
        player_2_id = room_info["player_2"]
        logger.info("player 2: " + player_2_id)
        if(player_2_id in player_socket_relations) :
            logger.info("send msg to player1: " + player_1_id)
            player2_websocket = player_socket_relations[player_2_id] 
            # gobang_games_action_center.sync_frames(player2_websocket, rooms_moves[room_id]['frame'])
            await player2_websocket.send(sync_frame_event(rooms_moves[room_id]['frame']))

    # logger.info("start sync room : " + room_id)


def encode_data(data):
    return json.dumps(data)

def decode_data(data):
    return json.loads(data)


def create_room(action_json):
    # validate user status
    room_id = "room_"+str(uuid.uuid4())
    if("room_id" in  action_json) :
        room_id = action_json['room_id']

    player_id = action_json['player_id']
    action_json['player_1'] = player_id
    room_name = action_json['room_name']

    if(room_id in rooms) :
        raise
    if(player_id in player_room_relations):
        raise

    # 
    sync_status_index = random.randint(0, circle_sync_list_len-1)
    room_sync_delay_list[sync_status_index].append(room_id)
    # 
    rooms[room_id] = action_json
    player_room_relations[player_id] = room_id

    # 
    rooms_moves[room_id] = dict()
    rooms_moves[room_id]["all"] = list()
    rooms_moves[room_id]["frame1"] = list()
    rooms_moves[room_id]["frame2"] = list()
    rooms_moves[room_id]["current_work_frame"] = 1
    rooms_moves[room_id]["next_start"]  = 0
    return room_id



def create_player_socket_relation(player_id, socket):
    player_socket_relations[player_id] = socket
    player_socket_relations[socket] = player_id


def del_player_socket_relation(player_id, socket):
    del player_socket_relations[player_id]
    del player_socket_relations[socket]





def login(action_json, websocket):
    if websocket: 
        if(websocket in player_socket_relations):
            return player_socket_relations[websocket]
        user_id = str(uuid.uuid4())
        create_player_socket_relation(user_id, websocket)
        return user_id

# handler for  join_room
# success: 
#     return  join status if s
# fail:
#     return error tips
def join_room(action_json):
    # validate 
    room_id = action_json['room_id']
    player_id = action_json['player_id']
    if(room_id  not  in rooms) :
        raise
    if(player_id in player_room_relations):
        raise


    room_info = rooms[room_id]
    room_info["player_2"] = player_id;
    rooms[room_id] = room_info;

    player_room_relations[player_id] = room_id
    return room_id

    



def exit_room(action_json):
    # validate
    room_id = action_json['room_id']
    player_id = action_json['player_id']
    if(room_id  not  in rooms) :
        raise
    if(player_id not in player_room_relations):
        raise
    room_id = action_json['room_id']
    player_id = action_json['player_id']

    del player_room_relations[player_id]
    


def room_over(action_json) :
    room_id = action_json['room_id']
    player_id = action_json['player_id']
    if(room_id  in rooms) :
        del rooms[room_id]

    if(player_id in player_room_relations):
        del player_room_relations[player_id]

    return "success"


def make_move(action_json):
    # validate
    room_id = action_json['room_id']
    player_id = action_json['player_id']
    if(room_id  not  in rooms) :
        raise

    if( (player_id.startswith( 'ai_' ))):
        pass
    elif(player_id  in player_room_relations):
        player_current_roomid = player_room_relations[player_id]
        if(player_current_roomid != room_id):
            raise
    else:
        raise

    poxi = action_json['poxi']
    poyi = action_json['poyi']
    rooms_moves[room_id]['all'].append(action_json)

    # current_work_frame = rooms_moves[room_id]['current_work_frame']
    # if(current_work_frame == 1) :
    #     rooms_moves[room_id]['frame1'].append(action_json)
    # elif (current_work_frame == 2) :
    #     rooms_moves[room_id]['frame1'].append(action_json)
    # else: 
    #     raise    
    return str(poxi) + "," + str(poyi)


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()



if __name__ == '__main__':
    user_action = dict()
    user_action["room_id"] = "test_room_id"
    user_action["player_id"] = "test_player1_id"
    user_action["room_name"] = "test_room_name"
    start_sync_status()

    create_room(user_action)

    user2_action = dict()
    user2_action["room_id"] = "test_room_id"
    user2_action["player_id"] = "test_player2_id"
    user2_action["room_name"] = "test_room_name"
    join_room(user2_action)



    user2_move_action = dict()
    user2_move_action["room_id"] = "test_room_id"
    user2_move_action["player_id"] = "test_player2_id"
    user2_move_action["room_name"] = "test_room_name"
    user2_move_action["poxi"] = 100
    user2_move_action["poyi"] = 12

    make_move(user2_move_action)
    time.sleep(1)
    make_move(user2_move_action)

    print("start main")
