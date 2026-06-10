#ifndef SERVER_H
#define SERVER_H

#include <QObject>
#include <QTcpSocket>
#include <QTcpServer>
#include <QImage>
#include <QMutex>

class Server : public QObject
{
  Q_OBJECT
public:
  explicit Server(QObject *parent = nullptr);
  void sendNextImage(QTcpSocket* socket);

signals:

public slots:
  void newConnection();
  void setNextImage(QImage* image);
  void readyRead();
  void readChannelFinished();

private:
  const qint32 m_imageBufferSize = 2;
  QTcpServer* m_server;
  QImage** m_imageBuffer;
  QMutex m_setNextImage;
};

#endif // SERVER_H
