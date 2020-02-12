# echoserver.py

#!/usr/bin/env python

import asyncio
import websockets
from app import log_utils
import time

logger = log_utils.get_logger("app_websocket.log")

# list connected_sockets = [];

async def echo(websocket, path):
	try:
	    async for message in websocket:
	    	logger.info("recieve msg: " + message)
	    	await websocket.send(message)
	except Exception as e:
		logger.error(e)
	else:
		pass
	finally:
		pass


async def push_event():
	try:
	    async for message in websocket:
	    	logger.info("recieve msg: " + message)
	    	await websocket.send(message)
	except Exception as e:
		logger.error(e)
	else:
		pass
	finally:
		pass




if __name__ == '__main__':
	asyncio.get_event_loop().run_until_complete(websockets.serve(echo, '127.0.0.1', 8765))
	asyncio.get_event_loop().run_forever()


