# Camera tooling

This section of the repository provides tooling for interacting with the cameras.
This includes software for capturing video, streaming the video and calibrating positions.

## hackweek26

An application for Sailfish OS that captures video from the camera and sends it to the stream-filter daemon for further processing.

To build, ensure the Sailfish SDK is installed with a target of Sailfish OS 5.0.0 or later.
Then run the following to build the code and deploy the resulting packages to the device:

```sh
$ cd hackweek26
$ sfdk build -d
$ sfdk deploy --sdk
```

## stream-filter

A service for Sailfish OS that receives video frames from the hackweek26 app.
These frames are converted into the appropriate format for image recognition.

It can then either perform face tracking on these images directly, or stream them via a TCP connection to a separate application for face tracking and further processing.

To build, ensure the Sailfish SDK is installed with a target of Sailfish OS 5.0.0 or later.
Then run the following to build the code and deploy the resulting packages to the device:

```sh
$ cd stream-filter
$ sfdk build -d
$ sfdk deploy --sdk
```

## StreamViewer

This desktop app reads images from the stream-filter app over the network and displays them in a window.

The frames are shown in a window with various "landmarks" overlaid.

The WASD keys can then be used to alter the expected height and position of the camera.

The Q and E keys can be used to rotate teh camera around the vertical axis.

The "landmarks" move based on the reorientation and repositioning of the camera, allowing the actual camera's position in the real world to be established.

To build, ensure Qt5.15 and QtCreator are installed.
Open the project ni QtCreator and select the 'Build > Build project "StreamViewer"`.
Once built the application can also be run from the IDE using the `Build > Run`. menu item.

## network-test

A test tool that streams iamges from the stream-filter service as fast as possible. It doesn't do anything with the images it receives, just discarding the data before reading the next iamge.

To run, you can use the following:

```sh
$ cd network-test
$ python3 network-test.py
```
