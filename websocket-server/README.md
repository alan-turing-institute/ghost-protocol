# Simple websocket server and test client

To run a websocket server, from this directory, run:
```
uv run ws_broadcast.py
```
It should then be listening on port 9000.   

To test, you can run a client, via the command:
```
uv run ws_client.py
```
(note that if the server is on a different machine, change from `localhost` to the host's IP address)
you can then use the "w", "a", "s", "d" keys, and the client should send messages in the format expected by the Unity app.
