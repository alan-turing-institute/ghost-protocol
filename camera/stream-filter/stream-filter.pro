# NOTICE:
#
# Application name defined in TARGET has a corresponding QML filename.
# If name defined in TARGET is changed, the following needs to be done
# to match new name:
#   - corresponding QML filename must be changed
#   - desktop icon filename must be changed
#   - desktop filename must be changed
#   - icon definition filename in desktop file must be changed
#   - translation filenames have to be changed

# The name of your application
TARGET = stream-filter

QT = core dbus multimedia
CONFIG += link_pkgconfig opencv4

PKGCONFIG += opencv4

HEADERS += src/service.h \
    src/facetracker.h \
    src/server.h

SOURCES += src/stream-filter.cpp src/service.cpp \
    src/facetracker.cpp \
    src/server.cpp

DISTFILES += models/face_detection_yunet_2023mar.onnx

models.path = /usr/share/$${TARGET}/models
models.files = models/*

INSTALLS += models

INCLUDEPATH += /usr/include/opencv4

OTHER_FILES = rpm/stream-filter.spec

target.path = /usr/libexec

DBUS_SERVICE_NAME=uk.ac.turing.stream

stream_dbus_adaptor.files = ./dbus/$${DBUS_SERVICE_NAME}.xml
stream_dbus_adaptor.source_flags = -c StreamAdaptor
DBUS_ADAPTORS += stream_dbus_adaptor

service.files = ./dbus/$${DBUS_SERVICE_NAME}.service
service.path = /usr/share/dbus-1/services/

INSTALLS += service target
