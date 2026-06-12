project(hackweek26 CXX)
cmake_minimum_required(VERSION 3.5)

find_package (Qt5 COMPONENTS Core Network Qml Gui Quick DBus Multimedia REQUIRED)

include(FindPkgConfig)
pkg_search_module(SAILFISH sailfishapp REQUIRED)
pkg_search_module(MULTIMEDIA REQUIRED Qt5Multimedia)
pkg_search_module(DBUS REQUIRED Qt5DBus)

set(CMAKE_AUTOMOC ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON)

add_executable(hackweek26 src/hackweek26.cpp src/videofilter.cpp src/videofilterrunnable.cpp)
target_compile_definitions(hackweek26 PRIVATE
    $<$<OR:$<CONFIG:Debug>,$<CONFIG:RelWithDebInfo>>:QT_QML_DEBUG>
)
target_include_directories(hackweek26 PRIVATE
    $<BUILD_INTERFACE:
    ${SAILFISH_INCLUDE_DIRS}
    ${MULTIMEDIA_INCLUDE_DIRS}
    ${DBUS_INCLUDE_DIRS}
>)
target_link_libraries(hackweek26
    Qt5::Quick
    ${SAILFISH_LDFLAGS}
    ${MULTIMEDIA_LDFLAGS}
    ${DBUS_LDFLAGS}
    librt.so
)

install(TARGETS hackweek26
    RUNTIME DESTINATION bin
)
install(DIRECTORY qml
    DESTINATION share/hackweek26
)
install(DIRECTORY translations
    DESTINATION share/hackweek26
    FILES_MATCHING PATTERN "*.qm"
)
install(FILES hackweek26.desktop
    DESTINATION share/applications
)
install(FILES icons/86x86/hackweek26.png
    DESTINATION share/icons/hicolor/86x86/apps
)
install(FILES icons/108x108/hackweek26.png
    DESTINATION share/icons/hicolor/108x108/apps
)
install(FILES icons/128x128/hackweek26.png
    DESTINATION share/icons/hicolor/128x128/apps
)
install(FILES icons/172x172/hackweek26.png
    DESTINATION share/icons/hicolor/172x172/apps
)

# Get the other files reachable from the project tree in Qt Creator
FILE(GLOB TsFiles "translations/*.ts")
add_custom_target(distfiles
    SOURCES
        hackweek26.desktop
        qml/hackweek26.qml
        qml/cover/CoverPage.qml
        qml/pages/FeedPage.qml
        rpm/hackweek26.changes.in
        rpm/hackweek26.changes.run.in
        rpm/hackweek26.spec
        rpm/hackweek26.yaml
        ${TsFiles})

# Tell Qt Creator where the application executable(s) would be located on the
# device.
#
# It is not necessary to list other deployables than executables (runtime
# targets) here. The deployment process of Sailfish OS projects is opaque to
# Qt Creator and the information contained in QtCreatorDeployment.txt is only
# used to locate the executable associated with the active run configuration
# on the device in order to run it.
#
# Search the Qt Creator Manual to learn about the QtCreatorDeployment.txt file
# format.
file(WRITE "${CMAKE_BINARY_DIR}/QtCreatorDeployment.txt"
    "${CMAKE_INSTALL_PREFIX}
${CMAKE_BINARY_DIR}/hackweek26:bin
")

