import asyncio
import websockets
import socket
import sys


def get_local_ip():
    # Connect to an external address (no data sent) to find the active interface IP
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "unknown"

connected = set()


async def handler(websocket):
    connected.add(websocket)
    addr = websocket.remote_address
    print(f"[+] {addr} connected  ({len(connected)} total)")
    try:
        async for message in websocket:
            print(f"[>] {addr}: {message}")
            others = connected - {websocket}
            if others:
                websockets.broadcast(others, message)
    finally:
        connected.discard(websocket)
        print(f"[-] {addr} disconnected  ({len(connected)} total)")


async def serve(port):
    local_ip = get_local_ip()

    print(f"WebSocket broadcast server running")
    print(f"  Local:   ws://localhost:{port}")
    print(f"  Network: ws://{local_ip}:{port}")
    print()
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    asyncio.run(serve(port))


if __name__ == "__main__":
    main()
