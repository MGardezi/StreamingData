import asyncio
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
        for index in range(0, min(len(dataframe), 4000), 5):
            window_data = dataframe.iloc[index:index+5].to_json(orient='records')
            await websocket.send(window_data)
            print(f"Sent data window starting at index {index}")
            await asyncio.sleep(1)
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
    # Let the system choose a random available port
    start_server = websockets.serve(time_server, "0.0.0.0", 42424)
    # 0.0.0.0 means that the server will be accessible to any IP address
    await start_server

# Streamlit app
def main():
    st.title("WebSocket Server")
    st.write("This app runs a WebSocket server.")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(serve())
    loop.run_forever()

if __name__ == "__main__":
    main()
