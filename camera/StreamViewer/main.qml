import QtQuick 2.15
import QtQuick.Window 2.15
import uk.ac.turing.view 1.0

Window {
    width: 640
    height: 480
    visible: true
    title: qsTr("Video still")

    VideoStill {
        id: videoStill
        anchors.fill: parent
    }
    Connections {
        target: client
        function onImageChanged() {
            videoStill.still = client.image;
            console.log("Image updated");
        }
    }
}
