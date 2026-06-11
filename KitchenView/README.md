# Kitchen View

## Creating the Scene

The kitchen model was scanned with scaniverse and shared via SharePoint.
The original file should still be on SharePoint if it is needed.

The model was imported into Blender and then exported in .glb format.
Further edits to the model (particularly removing bits) are best done in Blender.
The TV wall was removed by creating a cube that intersected it and then creating a boolean difference modifier on the kitchen model.
Dont' forget to apply the modification before export.

The model can be imported into Unity by dragging the .glb file into the editor window.

## Unity Project

### Setup

There is a camera, a light source, the kitchen model and some other shapes used to get sizes and positions aligned
They are all dumb objects, except the camera, which has scripts for:
 
* Keyboard movement (note WASD for front-to-back and sideways movement and QE for vertical)
* Connecting to the websocket server (see the class defined at the top of the file)
* Perspective projection (see issues for remaining work)

### Building

1. Go to File -> Build Profiles and make sure it is set to WebGL.
2. Disable compression in the settings if we want to serve with Python's http.server.
3. Build with File -> Build and Run.

### Running

Go to the Build/<build-name> directory and run `python -m http.server` then open your browser to the URL listed in the server output.

