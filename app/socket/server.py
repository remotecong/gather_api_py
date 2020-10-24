""" web socket server """
import asyncio
import websockets
import json

worker_id = 0
workers = set()

def get_id(websocket):
    """ find id """
    for worker_id, worker in workers:
        if worker is websocket:
            return worker_id


def add_worker(websocket):
    """ add worker to pile """
    global worker_id
    if not get_id(websocket):
        worker_id += 1
        workers.add((worker_id, websocket))
        return worker_id


def remove_worker(websocket):
    """ remove worker from pile """
    worker_id = get_id(websocket)
    if worker_id:
        workers.remove((worker_id, websocket))


async def handler(websocket, path):
    """ handler for all ws communications """
    global worker_id

    try:
        async for message in websocket:
            add_worker(websocket)
            data = json.loads(message)
            action = data.get("action", None)
            if action == "connect":
                await websocket.send(str(worker_id))
            else:
                print(f"not sure what u mean by {action}")
    except json.JSONDecodeError:
        print(f"not sure what to do with {message}")
    except websockets.exceptions.ConnectionClosedError:
        workers.remove((get_id(websocket), websocket))
    except websockets.exceptions.ConnectionClosedOK:
        workers.remove((get_id(websocket), websocket))


asyncio.get_event_loop().run_until_complete(websockets.serve(handler, "localhost", 8765))
asyncio.get_event_loop().run_forever()

