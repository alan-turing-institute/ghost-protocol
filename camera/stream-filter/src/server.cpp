#include <QThread>
#include <QBuffer>
#include <QElapsedTimer>

#include "server.h"

Server::Server(QObject *parent) : QObject(parent)
{
  qint32 pos;
  m_server = new QTcpServer(this);

  connect(m_server, &QTcpServer::newConnection, this, &Server::newConnection);

  if (!m_server->listen(QHostAddress::Any, 9991)) {
    qDebug() << "Server failed to start";
  }
  else {
    qDebug() << "Server started";
  }

  m_imageBuffer = (QImage**)malloc(m_imageBufferSize * sizeof(QImage*));
  for (pos = 0; pos < m_imageBufferSize; ++pos) {
    m_imageBuffer[pos] = new QImage();
  }
}

void Server::newConnection()
{
  QTcpSocket* socket = m_server->nextPendingConnection();
  qDebug() << "Connected";

  connect(socket, &QTcpSocket::readyRead, this, &Server::readyRead);
  connect(socket, &QTcpSocket::readChannelFinished, this, &Server::readChannelFinished);

  sendNextImage(socket);
}

void Server::readyRead()
{
  QByteArray read;
  QTcpSocket* socket = (QTcpSocket*)sender();

  read = socket->readLine();
  qDebug() << "Reply: " << QString(read);

  sendNextImage(socket);
}

void Server::readChannelFinished()
{
  QTcpSocket* socket = (QTcpSocket*)sender();

  disconnect(socket, &QTcpSocket::readyRead, this, &Server::readyRead);
  disconnect(socket, &QTcpSocket::readChannelFinished, this, &Server::readChannelFinished);

  socket->close();
  qDebug() << "Connection closed";
}

void Server::sendNextImage(QTcpSocket* socket)
{
  char szValue[4];
  quint32 uValue;

  QByteArray data;
  QBuffer buffer(&data);
  buffer.open(QIODevice::WriteOnly);

  m_setNextImage.lock();
  m_imageBuffer[0]->save(&buffer, "JPG");
  // Save a copy of the image for debugging purposes
  //m_imageBuffer[0]->save("/home/defaultuser/image.jpg", 0);
  m_setNextImage.unlock();

  uValue = data.size();
  szValue[0] = (uValue >> 24) & 0xff;
  szValue[1] = (uValue >> 16) & 0xff;
  szValue[2] = (uValue >> 8) & 0xff;
  szValue[3] = (uValue >> 0) & 0xff;
  socket->write(szValue, 4);
  socket->flush();

  socket->write(data);
  socket->flush();
}

void Server::setNextImage(QImage* image)
{
  qint32 pos;
  QImage* oldBuffer;

  m_setNextImage.lock();

  oldBuffer = m_imageBuffer[0];

  for (pos = 1; pos < m_imageBufferSize; ++pos) {
    m_imageBuffer[pos - 1] = m_imageBuffer[pos];
  }
  m_imageBuffer[(m_imageBufferSize - 1)] = image;

  m_setNextImage.unlock();

  delete oldBuffer;
}
