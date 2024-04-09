import asyncio
from urllib.parse import parse_qs, urlparse
import requests
import websockets
import pandas as pd
import streamlit as st
import io

def download_and_load_excel(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
    except (requests.RequestException, pd.errors.ParserError) as e:
        st.error(f"Failed to download or load the Excel file: {e}")
        return None

# URL to the raw content of the Excel file
url = 'https://raw.githubusercontent.com/MGardezi/StreamingData/Master/data.xlsx'

# Attempt to download and load the Excel file into a DataFrame
dataframe = download_and_load_excel(url)
if dataframe is None:
    raise Exception("Failed to download or load the Excel file.")

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
    #start_server = websockets.serve(time_server, "localhost", 42424)
    start_server = websockets.serve(time_server, "0.0.0.0", 42424)
    await start_server

asyncio.get_event_loop().run_until_complete(serve())
asyncio.get_event_loop().run_forever()

