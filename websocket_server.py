import asyncio
import requests
import websockets
import pandas as pd
import os
import streamlit as st

# URL to the raw content of the Excel file
url = 'https://raw.githubusercontent.com/MGardezi/WebSocketDStream/Master/air_beijing_data.xlsx'

# Make a GET request to download the file content
response = requests.get(url)

# Print out the first 500 characters of the received content
print(response.text[:500])

# Check if the response was successful
if response.ok:
    # If the content type is correct, save the file
    content_type = response.headers.get('Content-Type')
    if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
        with open('downloaded_file.xlsx', 'wb') as f:
            f.write(response.content)
        print('Excel file downloaded successfully.')
    else:
        print(f'Unexpected content type: {content_type}')
else:
    print(f'Failed to download the file. HTTP status code: {response.status_code}')

connected_clients = set()
shared_variable = None


async def handle_message(websocket, path):
    global shared_variable
    async for message in websocket:
        print("Received message:", message)
        if message == "stop":
            break

async def time_server(websocket, path):
    global shared_variable
    await register_client(websocket)
    print("Client connected.")
    try:
        for index in range(0, min(len(dataframe), 100), 5):
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

    # Run the WebSocket server
    loop = asyncio.get_event_loop()
    loop.run_until_complete(serve())
    loop.run_forever()

if __name__ == "__main__":
    main()
