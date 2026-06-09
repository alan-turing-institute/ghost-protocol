# ghost-protocol

This project is a REG hackweek project.

The goal is to show a "3D" image on a large display as it would appear from the viewers actual location in the space in front of the screen. The image should move as the viewer moves around. E.g. similar to the eye tracking display used in Mission Impossible - Ghost Protocol when they break into the Kremlin.

The steps will be:
1. Set up two cameras at two locations,
2. Stream the camera feeds to a device running an face detection model,
3. Identify location of persons head/eyes as pixel coordinates,
4. Use pixel coordiantes from both cameras to locate person in 3D space,
5. Adjust image on screen according to persons view point.

