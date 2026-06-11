#ifndef WSCLIENT_H
#define WSCLIENT_H

#include <QObject>
#include <QtWebSockets/QWebSocket>

class WsClient : public QObject
{
    Q_OBJECT
public:
    explicit WsClient(QObject *parent = nullptr);

signals:

private:
    QWebSocket* m_webSocket;
};

#endif // WSCLIENT_H
