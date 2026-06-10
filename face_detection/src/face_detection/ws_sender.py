"""WebSocket forwarder for face detection results.

Usage (single stream)::

    sender = WebSocketClient("ws://host:port")
    run_tcp_stream(host, port, on_face=sender)

Usage (stereo stream)::

    sender = WebSocketClient("ws://host:port")
    run_tcp_stereo_stream(host_0, port_0, host_1, port_1, on_stereo=sender)

Single-stream messages contain a flat FaceResult dict.
Stereo messages contain ``{"camera_0": ..., "camera_1": ...}``
where each camera value is a FaceResult dict (with its own timestamp_ms) or null.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import threading
from collections.abc import Callable

import websockets
import websockets.asyncio.client

from face_detection.detector import FaceResult, StereoResult


class WebSocketClient:
    """Forwards face detection results to a remote WebSocket server.

    Connects to an existing WebSocket server in a background thread.
    Pass the instance as on_face (single stream) or on_stereo (stereo stream).
    """

    def __init__(self, uri: str) -> None:
        self._uri = uri
        self._ws: websockets.asyncio.client.ClientConnection | None = None
        self._loop = asyncio.new_event_loop()
        self._ready = threading.Event()

        t = threading.Thread(target=self._run_loop, daemon=True)
        t.start()
        self._ready.wait()
        print(f"WebSocket client connected to {uri}")

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect())

    async def _connect(self) -> None:
        async with websockets.asyncio.client.connect(self._uri) as ws:
            self._ws = ws
            self._ready.set()
            await ws.wait_closed()

    def __call__(self, result: FaceResult | StereoResult) -> None:
        if isinstance(result, StereoResult) and (
            result.camera_0 is None or result.camera_1 is None
        ):
            return
        payload = json.dumps({"faceResult": dataclasses.asdict(result)})
        asyncio.run_coroutine_threadsafe(self._send(payload), self._loop)

    async def _send(self, payload: str) -> None:
        if self._ws is not None:
            await self._ws.send(payload)

    @property
    def on_face(self) -> Callable[[FaceResult], None]:
        return self  # type: ignore[return-value]

    @property
    def on_stereo(self) -> Callable[[StereoResult], None]:
        return self  # type: ignore[return-value]
