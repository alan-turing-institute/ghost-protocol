import QtQuick 2.0
import Sailfish.Silica 1.0
import QtMultimedia 5.6
import uk.ac.turing.stream 1.0

Page {
    id: page

    // The effective value will be restricted by ApplicationWindow.allowedOrientations
    allowedOrientations: Orientation.All

    Camera {
          id: camera
          flash.mode: Camera.FlashOff
          focus.focusMode: Camera.FocusContinuous
    }

    SilicaFlickable {
        anchors.fill: parent
        contentHeight: column.height + Theme.paddingLarge
        flickableDirection: Flickable.VerticalFlick

        Column {
            id: column
            width: parent.width
            spacing: Theme.paddingLarge

            VideoOutput {
                source:  camera
                filters: [ qrFilter ]
                width: Screen.width
                height: Screen.height
            }

            VideoFilter {
                id: qrFilter
            }
        }
    }
}
