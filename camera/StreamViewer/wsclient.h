#ifndef WSCLIENT_H
#define WSCLIENT_H

#include <QObject>
#include <QtWebSockets/QWebSocket>
#include <QRectF>

class WsClient : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QRectF faceBox READ faceBox NOTIFY faceBoxChanged)
public:
    explicit WsClient(QObject *parent = nullptr);
    ~WsClient();

    void setFaceBox(QRectF faceBox);

public slots:
    void connected();
    void disconnected();
    void textMessageReceived(QString const& message);
    QRectF faceBox() const;

signals:
    void faceBoxChanged();

private:
    QWebSocket* m_webSocket;
    QRectF m_faceBox;
};

#endif // WSCLIENT_H
