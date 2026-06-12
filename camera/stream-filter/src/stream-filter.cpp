#include "service.h"
#include "server.h"
#include "facetracker.h"

#include <QCoreApplication>

int main(int argc, char *argv[])
{
  QCoreApplication app(argc, argv);

  FaceTracker faceTracker;

  Server server;

  Service srv(&server, &faceTracker);

  return app.exec();
}
