import sys, asyncio, websockets

async def echo(websocket):
    async for message in websocket:
        await websocket.send(f"Echo: {message}")

async def start(port=8765):
    async with websockets.serve(echo, "localhost", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(start(int(sys.argv[1]) if len(sys.argv)>1 else 8765))
