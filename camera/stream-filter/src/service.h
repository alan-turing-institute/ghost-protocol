#ifndef SERVICE_H
#define SERVICE_H

#include <QDBusContext>
#include <QDBusUnixFileDescriptor>
#include <QTimer>

#include "server.h"

class Service: public QObject, public QDBusContext
{
    Q_OBJECT

public:
    explicit Service(Server* server, QObject *parent = nullptr);
    virtual ~Service();

public slots:
    QString decodeFromDescriptor(QDBusUnixFileDescriptor fd, uint size, int width, int height, int pixelFormat);
    void quit();

private:
    static void imageCleanupHandler(void *info);

private:
    Server* m_server;
};

#endif // SERVICE_H
