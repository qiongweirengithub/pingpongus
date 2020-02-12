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
import queue
import logging
import uvloop
from concurrent.futures import ThreadPoolExecutor
# import gobang_games_action_center

from app import log_utils
logger = log_utils.get_logger(log_filename="app_snake_websocket.log", level=logging.INFO)


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
player_msg_queue_relations = dict()

circle_sync_list_len = 10
circle_sync_interval = 0.005
room_sync_delay_list = list()
sync_frame_executor = ThreadPoolExecutor(max_workers=500)



def sync_frame_event(frame_array):
    return encode_data({"event_type": "sync_frame", "frame_array":frame_array})



def sched_sync_status_upgrade() :
    logger.debug("started  schedule sync process") 
    cur_circle_index = 0
    try:
        while  True:
            time.sleep(circle_sync_interval)

            if(len(room_sync_delay_list) <= 0) :
                continue
            need_sync_room_list = room_sync_delay_list[cur_circle_index]

            sync_tasks = list();

            if(len(need_sync_room_list) > 0) :
                
                for room_id in need_sync_room_list  : 
                    if(room_id not in rooms):
                        need_sync_room_list.remove(room_id)
                        continue

                    sync_tasks.append(room_id);

                if(len(sync_tasks) > 0):
                    async_sync_handler(sync_tasks)    # version2 - upgrade
                    pass
                    # version-2 end

            else:
                # logger.debug("need sync rooms for index:" + str(cur_circle_index) + " is empty")
                pass

            cur_circle_index = cur_circle_index + 1
            if(cur_circle_index  >= len(room_sync_delay_list)):
                cur_circle_index = 0

    except Exception :
        logger.error("sched_sync_status_upgrade", exc_info = True)
    else:
        pass
    finally:
        pass

    

def async_sync_handler(sync_tasks):
    if(len(sync_tasks) <= 0) :
        return
    for room_id in sync_tasks:
        push_player_msg(room_id);


def start_sync_status() :

    if(len(room_sync_delay_list) > 0) :
        raise
    for sync_delay_list_size  in range(circle_sync_list_len):
        empty_sync_list = list()
        room_sync_delay_list.append(empty_sync_list)
    # asyncio.create_task(sched_sync_status())
    sync_thread = threading.Thread(target=sched_sync_status_upgrade)
    sync_thread.start()
    statistic_thread = threading.Thread(target=statistic_room_status)
    statistic_thread.start()
    logger.debug("started  schedule sync thread") 

def statistic_room_status():
    while  True:
        time.sleep(3)
        logger.info(f"client count:{len(player_socket_relations)}", )
        pass


def push_player_msg(room_id):
    start_time = time.time()
    try:
        next_need_sync_move_index = rooms_moves[room_id]['next_start'] 
        rooms_moves[room_id]['frame'] = rooms_moves[room_id]["all"][next_need_sync_move_index:] 
        rooms_moves[room_id]['next_start'] = len(rooms_moves[room_id]['all'])
        room_info =  rooms[room_id]

        new_frams = rooms_moves[room_id]['frame']
        if(len(new_frams) <= 0) :
            return
        # logger.debug("roomid: " + room_id + "  all action : " + encode_data(rooms_moves[room_id]["all"]))
        start_time = time.time()

        logger.debug("roomid: " + room_id + "  need sync frame : " + encode_data(new_frams))

        # logger.debug(rooms_moves[room_id]['next_start'])
        room_player_count = 0;
        if("player_1" in room_info) :
            room_player_count+=1;
            player_1_id = room_info["player_1"]
            if(player_1_id in player_socket_relations) :
                logger.debug("send msg to player1: " + player_1_id)
                player1_websocket = player_socket_relations[player_1_id] 
                if(player_1_id in player_msg_queue_relations) :
                    player_msg_queue_relations[player_1_id].put(new_frams)
            else:
                pass

        if("player_2" in room_info) :
            room_player_count+=1;
            player_2_id = room_info["player_2"]
            logger.debug("player 2: " + player_2_id)
            if(player_2_id in player_socket_relations) :
                logger.debug("send msg to player1: " + player_2_id)
                player2_websocket = player_socket_relations[player_2_id] 
                if(player_2_id in player_msg_queue_relations) :
                    player_msg_queue_relations[player_2_id].put(new_frams)

        if(room_player_count == 0):
            logger.debug("room has no player yet, remove from sync queue")
            del rooms[room_id]
        end_time = time.time()
        logger.debug(f"add to room player queue cost:{end_time-start_time}")
    except Exception as e:
        logger.error(e)
    else:
        pass
    finally:
        pass
  

def start_player_msg_push_thread(player_id):
    new_loop = asyncio.new_event_loop()
    try:
        t = threading.Thread(target=start_player_msg_push_loop, args=(new_loop, player_id))
        t.start()
        pass
    except Exception as e:
        logger.error("submit sync task exception", exc_info=True)
    finally:
        pass


def start_player_msg_push_loop(loop, player_id):
    # asyncio.***  的操作是基于当前 loop 环境的,
    # 因此需要这行下面的设置 loop 环境, 
    asyncio.set_event_loop(loop)
    #  this is more more important !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop.run_until_complete(handling_player_msg(player_id)) 

    
async def handling_player_msg(player_id):
    if(player_id not in player_msg_queue_relations):
        raise
    player_msg_queue = player_msg_queue_relations[player_id]
    logger.debug("handing player msg process start, player:" + player_id)
    if(player_id  not in player_socket_relations) :
        logger.error(f"player: {player_id} has no websocket find")
        raise
    player_websocket = player_socket_relations[player_id]

    while  True:
        new_frame = player_msg_queue.get(block=True, timeout=None)
        logger.debug(f"new frame {new_frame} for player:{player_id}")
        start_time = time.time()
        try:
            await player_websocket.send(sync_frame_event(new_frame))
        except Exception :
            logger.error(f"send new frame for player:{player_id} exceptions", exc_info=True)
            clean_player(player_id)
        else:
            pass
        finally:
            end_time = time.time()
            logger.debug(f"send msg to player cost:{end_time-start_time}")
            pass

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
    rooms_moves[room_id]["current_work_frame"] = 1
    rooms_moves[room_id]["next_start"]  = 0
    return room_id


def clean_player(player_id):
    if(player_id not in player_room_relations):
        return
    room_id = player_room_relations[player_id]    
    if(room_id not in rooms):
        logger.error(f"room:{room_id} not exist")

    room_player_count = 0;
    room_info = rooms[room_id];
    if("player_1" in room_info) :
        room_player_count+=1
        player_1_id = room_info["player_1"]
        if(player_1_id == player_id):
            del rooms[room_id]["player_1"]
            room_player_count-=1
            

    if("player_2" in room_info) :
        room_player_count+=1
        player_2_id = room_info["player_2"]
        if(player_2_id == player_id):
            del rooms[room_id]["player_2"]
            room_player_count+=1

    if(room_player_count == 0) :
        del rooms[room_id]
            



def create_player_socket_relation(player_id, socket):
    player_socket_relations[player_id] = socket
    player_socket_relations[socket] = player_id


def del_player_socket_relation(player_id, socket):
    del player_socket_relations[player_id]
    del player_socket_relations[socket]


def init_player_msg_queue_relation(player_id):
    player_msg_queue_relations[player_id] = queue.Queue()



def login(action_json, websocket):
    if websocket: 
        if(websocket in player_socket_relations):
            return player_socket_relations[websocket]
        user_id = str(uuid.uuid4())
        create_player_socket_relation(user_id, websocket)
        init_player_msg_queue_relation(user_id)
        start_player_msg_push_thread(user_id)
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

    to_go = action_json['to_go']
    #  减少传输信息量
    del action_json['room_id']
    del action_json['action']

    rooms_moves[room_id]['all'].append(action_json)

    # current_work_frame = rooms_moves[room_id]['current_work_frame']
    # if(current_work_frame == 1) :
    #     rooms_moves[room_id]['frame1'].append(action_json)
    # elif (current_work_frame == 2) :
    #     rooms_moves[room_id]['frame1'].append(action_json)
    # else: 
    #     raise    
    return str(to_go)


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



def task_split_test(sync_tasks):

    task_len = len(sync_tasks)
    depart_task_len = 5
    depart_task_count = int(task_len/depart_task_len)
    if depart_task_count > 0 :

        start = 0
        page = 1
        end = (page-1)*depart_task_len
        for depart_task_id in range(0, depart_task_count) :
            page += 1
            start = end
            end = (page-1)*depart_task_len
            print(json.dumps(sync_tasks[start:end]))

            
                        
        print(json.dumps(sync_tasks[end:]))
    

    else:
        new_loop = asyncio.new_event_loop()
        t = threading.Thread(target=start_loop, args=(new_loop,sync_tasks))
        t.start()

if __name__ == '__main__':

    # user_action = dict()
    # user_action["room_id"] = "test_room_id"
    # user_action["player_id"] = "test_player1_id"
    # user_action["room_name"] = "test_room_name"
    # start_sync_status()

    # create_room(user_action)

    # user2_action = dict()
    # user2_action["room_id"] = "test_room_id"
    # user2_action["player_id"] = "test_player2_id"
    # user2_action["room_name"] = "test_room_name"
    # join_room(user2_action)



    # user2_move_action = dict()
    # user2_move_action["room_id"] = "test_room_id"
    # user2_move_action["player_id"] = "test_player2_id"
    # user2_move_action["room_name"] = "test_room_name"
    # user2_move_action["to_go"] = 100

    # make_move(user2_move_action)
    # time.sleep(1)
    # make_move(user2_move_action)

    # print("start main")
    sync_tasks = list()
    count = random.randint(1,50)
    for task_index in range(0, count):
        sync_tasks.append(task_index)
    task_split_test(sync_tasks)

