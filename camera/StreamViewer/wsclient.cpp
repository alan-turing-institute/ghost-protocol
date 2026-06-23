#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QRectF>

#include "wsclient.h"

WsClient::WsClient(QObject *parent)
    : QObject{parent}
{
    m_webSocket = new QWebSocket();

    connect(m_webSocket, &QWebSocket::connected, this, &WsClient::connected);
    connect(m_webSocket, &QWebSocket::disconnected, this, &WsClient::disconnected);
    connect(m_webSocket, &QWebSocket::textMessageReceived, this, &WsClient::textMessageReceived);

    m_webSocket->open(QUrl("ws://127.0.0.1:9000"));

    m_faceBox = QRectF();
}

WsClient::~WsClient()
{
    m_webSocket->close();
}

void WsClient::connected()
{
    qDebug() << "Connected";
}

void WsClient::disconnected()
{
    qDebug() << "Disconnected";
}

QRectF WsClient::faceBox() const {
    return m_faceBox;
}

void WsClient::setFaceBox(QRectF faceBox) {
    if (m_faceBox != faceBox) {
        m_faceBox = faceBox;
        emit faceBoxChanged();
    }
}

void WsClient::textMessageReceived(QString const& message)
{
    QJsonDocument doc;
    // Format
    // {"faceResult":{"camera_0":{"bbox":[1448.1900776975926,1183.6299077162446,84.34225775255663,126.51338662883495],"frame_height":3000,"frame_width":4000,"left_eye":[1469.275642135732,1225.1449826261935],"right_eye":[1511.4467710120102,1226.4570905588525],"timestamp_ms":1781289049935},"camera_1":{"bbox":[1973.8731824650133,1234.8321425434383,61.614337772834915,92.42150665925237],"frame_height":3000,"frame_width":4000,"left_eye":[1989.276766908222,1266.335912471859],"right_eye":[2020.0839357946395,1264.9427103878525],"timestamp_ms":1781289049935}}}

    qDebug() << "Message received";
    doc = QJsonDocument::fromJson(message.toUtf8());

    if (doc.isObject() && doc.object().contains("faceResult") && doc.object()["faceResult"].isObject()) {
        QJsonObject result = doc.object()["faceResult"].toObject();
        if (result.contains("camera_0") && result["camera_0"].isObject()) {
            QJsonObject camera = result["camera_0"].toObject();
            if (camera["bbox"].isArray() && camera["bbox"].toArray().size() >= 4) {
                QJsonArray bboxArray = camera["bbox"].toArray();
                double width = camera["frame_width"].toDouble();
                double height = camera["frame_height"].toDouble();
                QRectF bbox = QRectF(bboxArray[0].toDouble() /  width, bboxArray[1].toDouble() / height, bboxArray[2].toDouble() / width, bboxArray[3].toDouble() / height);
                qDebug() << "[" << bbox << "]";
                setFaceBox(bbox);
            }
        }
    }
}

