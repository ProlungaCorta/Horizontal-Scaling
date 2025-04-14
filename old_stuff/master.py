import asyncio

# Function to handle communication with each agent
async def handle_client(reader, writer):
    data = await reader.read(1024)  # Read up to 1024 bytes
    message = data.decode('utf8')  # Decode the message into a string
    addr = writer.get_extra_info('peername')  # Get the client's address

    print(f"Received data: {message} from {addr}")

    # Send a response back to the agent
    response = f"Received your data, {addr}!"
    writer.write(response.encode())  # Send a response back to the agent
    await writer.drain()  # Wait for the data to be sent completely

    print("Closing the connection")
    writer.close()  # Close the connection

# Function to start the server
async def start_master_server():
    server = await asyncio.start_server(
        handle_client, '127.0.0.1', 6969)  # Bind to localhost and port 12345
    
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    # Start the server to accept connections and handle them
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(start_master_server())

