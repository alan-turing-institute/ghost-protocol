#include "client.h"

Client::Client(QObject *parent)
    : QObject{parent}
{
    m_data.clear();
    m_length = 0;
    m_socket = new QTcpSocket(this);
    m_socket->connect(m_socket, &QTcpSocket::readyRead, this, &Client::readyRead);
    qDebug() << "Connecting";
    m_socket->connectToHost("10.10.100.154", 9991);
}

void Client::readyRead()
{
    if (m_length == 0) {
        QByteArray lengthData;
        lengthData = m_socket->read(4);
        m_length = ((uint8_t)lengthData[0] << 24) + ((uint8_t)lengthData[1] << 16) + ((uint8_t)lengthData[2] << 8) + ((uint8_t)lengthData[3]);
        qDebug() << "Data length:" << m_length;
    }

    m_data += m_socket->read(m_length - m_data.length());

    if (m_data.length() == m_length) {

        QImage image;
        bool loaded = image.loadFromData(m_data, "JPG");
        if (loaded) {
            setImage(image);
        }
        m_socket->write("Done\n");
        m_length = 0;
        m_data.clear();
        qDebug() << "Size:" << image.width() << image.height();
    }
}

QImage Client::image() const
{
    return m_image;
}

void Client::setImage(QImage image)
{
    m_image = image;
    emit imageChanged();
}
