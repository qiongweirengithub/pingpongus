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

circle_sync_list_len = 10
circle_sync_interval = 0.01
room_sync_delay_list = list()
sync_frame_executor = ThreadPoolExecutor(max_workers=500)



def sync_frame_event(frame_array):
    return encode_data({"event_type": "sync_frame", "frame_array":frame_array})


def sched_sync_status() :
    asyncio.run(sched_sync_status_())


async def sched_sync_status_() :
    logger.debug("started  schedule sync process") 
    cur_circle_index = 0
    try:

        while  True:
            asyncio.sleep(circle_sync_interval)

            if(len(room_sync_delay_list) <= 0) :
                continue
            need_sync_room_list = room_sync_delay_list[cur_circle_index]

            sync_tasks = list();

            if(len(need_sync_room_list) > 0) :
                
                for room_id in need_sync_room_list  : 
                    if(room_id not in rooms):
                        need_sync_room_list.remove(room_id)
                        continue
                    #  version-1 start
                    # await sync_room_status(room_id)
                    #  version-1 end

                    # version-2 start
                    sync_tasks.append(asyncio.ensure_future(sync_room_status(room_id)));

                if(len(sync_tasks) > 0):
                    # logger.debug("sync task size: " + str(len(sync_tasks)))
                    await asyncio.wait(sync_tasks)
                    pass
                    # version-2 end

            else:
                # logger.debug("need sync rooms for index:" + str(cur_circle_index) + " is empty")
                pass

            cur_circle_index = cur_circle_index + 1
            if(cur_circle_index  >= len(room_sync_delay_list)):
                cur_circle_index = 0

    except Exception as e:
        logger.error(exc_info=True)
    else:
        pass
    finally:
        pass



def sched_sync_status_upgrade() :
    logger.debug("started  schedule sync process") 
    cur_circle_index = 0
    try:
        while  True:
            time.sleep(0.02)

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




def start_loop(loop, sync_tasks):
    if(len(sync_tasks) <= 0) :
        return
    # asyncio.***  的操作是基于当前 loop 环境的,
    # 因此需要这行下面的设置 loop 环境, 
    # QW, 启动新的loop，必须执行此句,  后续生成的task以及wait等操作才是基于此loop的, 
    # 如果没有这句话,  asyncio.ensure_future 是其他loop 环境的, 
    #                                  会导致本函数的loop.run_until_complete(asyncio.wait)  提示   ”loop argument must agree with Future“
    #                                  https://stackoverflow.com/questions/46806174/python-3-6-and-valueerror-loop-argument-must-agree-with-future 
    asyncio.set_event_loop(loop)

    future_tasks = list();
    for room_id in sync_tasks:
        future_tasks.append(asyncio.ensure_future(sync_room_status(room_id)));
    
    #  this is more more important !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    # future = asyncio.ensure_future(_sync_handler(future_tasks))  # 将协程对象包装成带未来值的对象
    # task = loop.create_task(_sync_handler(future_tasks))
    loop.run_until_complete(asyncio.wait(future_tasks)) # wait()里面加一个可迭代对象

def start_loop2(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever() # wait()里面加一个可迭代对象


def async_sync_handler_upgrade(sync_tasks):

    task_len = len(sync_tasks)
    logger.debug("task len : " + str(task_len))

    depart_task_len = 5
    depart_task_count = int(task_len/depart_task_len)
    logger.debug("depart_task_count: " + str(depart_task_count))
    if depart_task_count > 0 :
        start = 0
        page = 1
        end = (page-1)*depart_task_len
        for depart_task_id in range(0, depart_task_count) :
            page+=1
            start = end
            end = (page-1)*depart_task_len
            new_loop = asyncio.new_event_loop()
            logger.debug("depart task len: " + str(len(sync_tasks[start:end])))

            sync_frame_task = sync_frame_executor.submit(start_loop, new_loop,sync_tasks[start:end])
            # t = threading.Thread(target=start_loop, args=(new_loop,sync_tasks[start:end]))
            # t.start()            

        logger.debug("depart task len: " + str(len(sync_tasks[end:])))
        new_loop = asyncio.new_event_loop()
        sync_frame_task = sync_frame_executor.submit(start_loop, new_loop,sync_tasks[end:])

        # t = threading.Thread(target=start_loop, args=(new_loop,sync_tasks[end:]))
        # t.start()            

    else:
        new_loop = asyncio.new_event_loop()
        sync_frame_task = sync_frame_executor.submit(start_loop, new_loop,sync_tasks)
        # t = threading.Thread(target=start_loop, args=(new_loop,sync_tasks))
        # t.start()

    #  method1 is perfect ....................................................................

def async_sync_handler(sync_tasks):
    logger.debug("sync task len: " + str(len(sync_tasks)))

    #  method1 is perfect ....................................................................
    new_loop = asyncio.new_event_loop()
    try:
        # sync_frame_executor.submit(start_loop, new_loop,sync_tasks)
        t = threading.Thread(target=start_loop, args=(new_loop,sync_tasks))
        t.start()
        pass
    except Exception as e:
        logger.error("submit sync task exception", exc_info=True)
    finally:
        pass
    #  method1 is perfect ....................................................................

    #  method2 can not work............................................................
    # new_loop = asyncio.new_event_loop()
    # t = threading.Thread(target=start_loop2, args=(new_loop,))
    # t.start()
    # new_loop.call_soon_threadsafe(__sync_handler, sync_tasks, new_loop)
    # asyncio.run_coroutine_threadsafe(__sync_handler(sync_tasks, new_loop), new_loop)
    #  method2 can not work............................................................


    #  method3 is low ....................................................................
    # sync_thread = threading.Thread(target=sync_handler, args=(sync_tasks,))
    # sync_thread.start()
    #  method3 is low ....................................................................


def sync_handler(sync_tasks):
    #  开启新 asyncio 环境
    asyncio.run(___sync_handler(sync_tasks))


def __sync_handler(sync_tasks, loop):
    logger.debug("sync task size: " + str(len(sync_tasks)))
    # asyncio.set_event_loop(loop)
    # future_tasks = list();
    # for room_id in sync_tasks:
    #     future_tasks.append(asyncio.ensure_future(sync_room_status(room_id)));
    # await asyncio.wait(future_tasks)

async def ___sync_handler(sync_tasks):
    future_tasks = list();
    for room_id in sync_tasks:
        future_tasks.append(asyncio.ensure_future(sync_room_status(room_id)));
    await asyncio.wait(future_tasks)


async def _sync_handler(sync_futures):
    await asyncio.wait(sync_futures)

def start_sync_status() :

    if(len(room_sync_delay_list) > 0) :
        raise
    for sync_delay_list_size  in range(circle_sync_list_len):
        empty_sync_list = list()
        room_sync_delay_list.append(empty_sync_list)
    # asyncio.create_task(sched_sync_status())
    sync_thread = threading.Thread(target=sched_sync_status_upgrade)
    sync_thread.start()
    logger.debug("started  schedule sync thread") 



async def sync_room_status(room_id):
    try:
        next_need_sync_move_index = rooms_moves[room_id]['next_start'] 
        rooms_moves[room_id]['frame'] = rooms_moves[room_id]["all"][next_need_sync_move_index:] 
        rooms_moves[room_id]['next_start'] = len(rooms_moves[room_id]['all'])
        room_info =  rooms[room_id]

        new_frams = rooms_moves[room_id]['frame']
        if(len(new_frams) <= 0) :
            return
        # logger.debug("roomid: " + room_id + "  all action : " + encode_data(rooms_moves[room_id]["all"]))

        logger.debug("roomid: " + room_id + "  need sync frame : " + encode_data(new_frams))

        # logger.debug(rooms_moves[room_id]['next_start'])
        room_player_count = 0;
        if("player_1" in room_info) :
            room_player_count+=1;
            player_1_id = room_info["player_1"]
            if(player_1_id in player_socket_relations) :
                logger.debug("send msg to player1: " + player_1_id)
                player1_websocket = player_socket_relations[player_1_id] 
            try:
                    # gobang_games_action_center.sync_frames(player1_websocket, rooms_moves[room_id]['frame'])
                    await player1_websocket.send(sync_frame_event(rooms_moves[room_id]['frame']))
            except Exception as e:
                del room_info['player_1']
                room_player_count-=1;
                logger.error(e)
            else:
                pass
            finally:
                pass

        if("player_2" in room_info) :
            room_player_count+=1;
            player_2_id = room_info["player_2"]
            logger.debug("player 2: " + player_2_id)
            if(player_2_id in player_socket_relations) :
                logger.debug("send msg to player1: " + player_1_id)
                player2_websocket = player_socket_relations[player_2_id] 
                try:
                    await player2_websocket.send(sync_frame_event(rooms_moves[room_id]['frame']))
                except Exception as e:
                    del room_info['player_2']
                    room_player_count-=1;
                    logger.error(e)
                else:
                    pass
                finally:
                    pass
        if(room_player_count == 0):
            logger.debug("room has no player yet, remove from sync queue")
            del rooms[room_id]
    except Exception as e:
        logger.error(e)
    else:
        pass
    finally:
        pass
    

def encode_data(data, type='str_ori'):
    if('str_ori' == type):
        return json.dumps(data)
    elif('proto_buffer' == type):
        raise 'unsupport decode type'



def decode_data(data, type='str_ori'):
    if('str_ori' == type):
        return json.loads(data)
    elif('proto_buffer' == type):
        raise 'unsupport decode type'
    



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
    player_room_relations[room_id + 'player_1'] = player_id

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

