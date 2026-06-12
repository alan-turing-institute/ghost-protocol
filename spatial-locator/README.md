# Locate a position in three-d

Given:

1. The x and y pixel locations on two images; and
2. Some kind of calibration data

Return:

An x, y, z position, in metres, from an origin fixed relative to the
screen.

## Running

Edit `config.rkt` to specify the address of the websocket server and run:

```sh
racket main.rkt
```

to start responding to messages.

Optional: also run `racket calibrate.rkt` to show a real-time top-down
view. Finally, `racket mock-cameras.rkt` generates synthetic
`faceResult` messages. (Run all in separate shells.)

## Racket

Install Racket

```sh
brew install racket
```

I forget which libraries are needed. But at least websockets:

```sh
raco pkg install rfc6455
```
