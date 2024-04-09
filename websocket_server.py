import asyncio
from urllib.parse import parse_qs, urlparse
import websockets
import pandas as pd
import os

# Load the Excel data
# path_to_file = os.path.join('C:\\', 'Users', 'muhammad', 'Desktop', 'Pyhton', 'Pyhton', 'py', 'data.xlsx')
#path_to_file = os.path.join('C:\\', 'Users', 'muhammad', 'Desktop', 'Pyhton', 'Pyhton', 'py', 'data.xlsx')
path_to_file = os.path.join(os.path.dirname(__file__), 'data', 'air_beijing_data.xlsx')
dataframe = pd.read_excel(path_to_file)

connected_clients = set()

async def handle_message(websocket, path):
    async for message in websocket:
        print("Received message:", message)
        if message == "stop":
            break

async def time_server(websocket, path):
    await register_client(websocket)
    print("Client connected.")
    try:
        # Get the start index from the query parameters
        query = parse_qs(urlparse(path).query)
        start_index = int(query.get('start', [0])[0])

        for index in range(start_index, min(len(dataframe), 4000), 5):
            window_data = dataframe.iloc[index:index+5].to_json(orient='records')
            await websocket.send(window_data)
            print(f"Sent data window starting at index {index}")
            await asyncio.sleep(2)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await unregister_client(websocket)
        print("Client disconnected.")

async def register_client(websocket):
    connected_clients.add(websocket)

async def unregister_client(websocket):
    connected_clients.remove(websocket)

async def serve():
    start_server = websockets.serve(time_server, "localhost", 42424)
    await start_server

asyncio.get_event_loop().run_until_complete(serve())
asyncio.get_event_loop().run_forever()
