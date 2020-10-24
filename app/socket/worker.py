""" web socket worker """

import asyncio
import websockets

async def hello(uri):
    """ test """
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                print(message)
    except websockets.exceptions.ConnectionClosedError:
        print("goodbye!")


asyncio.get_event_loop().run_until_complete(hello("ws://localhost:8765"))
asyncio.get_event_loop().run_forever()
