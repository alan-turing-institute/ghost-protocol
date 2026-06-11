import QtQuick 2.15
import QtQuick.Window 2.15
import uk.ac.turing.view 1.0

Window {
    width: 1280
    height: 960
    visible: true
    title: qsTr("Video still")
    color: "black"

    VideoStill {
        id: videoStill
        anchors.fill: parent
        focus: true

        Keys.onPressed: {
            switch (event.key) {
                case 87: {
                    // Up
                    adjustCameraHeight(0.02);
                }
                break;
                case 83: {
                    // Down
                    adjustCameraHeight(-0.02);
                }
                break;
                case 65: {
                    // Left
                    adjustCameraPosition(0.02, 0.0);
                }
                break;
                case 68: {
                    // Right
                    adjustCameraPosition(-0.02, 0.0);
                }
                break;
                case 81: {
                    // Rotate left
                    adjustCameraAngle(2.0 * 3.14159265 / 5760.0);
                }
                break;
                case 69: {
                    // Rotate right
                    adjustCameraAngle(-2.0 * 3.14159265 / 5760.0);
                }
                break;
            }
        }
    }
    Connections {
        target: client
        function onImageChanged() {
            videoStill.still = client.image;
            console.log("Image updated");
        }
    }
}
