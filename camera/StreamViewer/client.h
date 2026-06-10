#ifndef CLIENT_H
#define CLIENT_H

#include <QObject>
#include <QTcpSocket>
#include <QImage>

class Client : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QImage image READ image WRITE setImage NOTIFY imageChanged)
public:
    explicit Client(QObject *parent = nullptr);

public slots:
    void readyRead();
    QImage image() const;
    void setImage(QImage image);

signals:
    void imageChanged();

private:
    QTcpSocket* m_socket;
    QImage m_image;
    QByteArray m_data;
    quint32 m_length;
};

#endif // CLIENT_H
