#ifdef QT_QML_DEBUG
#include <QtQuick>
#endif

#include "service.h"
#include "server.h"

#include <QCoreApplication>

int main(int argc, char *argv[])
{
  QCoreApplication app(argc, argv);

  Server server;

  Service srv(&server);

  return app.exec();
}
