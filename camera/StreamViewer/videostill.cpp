#include <QPainter>

#include "videostill.h"

VideoStill::VideoStill(QQuickItem *parent)
    : QQuickPaintedItem(parent)
{
    m_image = QImage("/home/flypig/Pictures/Webcam/2022-01-22-215617.jpg");
}

void VideoStill::updateImage() {
    this->update();
}

QImage VideoStill::still() const
{
    return m_image;
}

void VideoStill::setStill(QImage still)
{
    m_image = still;
    emit stillChanged();
    this->update();
}

void VideoStill::paint(QPainter* painter)
{
    float width;
    float height;
    float xoffset;
    float yoffset;
    QVector2D point;

    width = this->width();
    height = ((float)m_image.height() / (float)m_image.width()) * this->width();
    xoffset = 0.0;
    yoffset = (this->height() - height) / 2.0;

    if (yoffset < 0) {
        height = this->height();
        width = ((float)m_image.width() / (float)m_image.height()) * this->height();
        xoffset = (this->width() - width) / 2.0;
        yoffset = 0.0;
    }

    painter->drawImage(QRectF(xoffset, yoffset, width, height), m_image);

    // Reception
    renderPoint(painter, QVector3D(-0.32, 7.26, 1.1), "Reception");
    // CCTV camera
    renderPoint(painter, QVector3D(1.14, 3.66, 2.48), "CCTV");
    // Main entrance framework
    renderPoint(painter, QVector3D(1.77, 9.4, 2.22), "Frame");
    // Tape
    renderPoint(painter, QVector3D(1.84, 3.71, 0), "Tape");
    // First aid kit
    renderPoint(painter, QVector3D(2.06, 9.12, 1.61), "First aid");
    // Bar
    renderPoint(painter, QVector3D(3.17, 7.10, 1.1), "Bar");
}

void VideoStill::renderPoint(QPainter* painter, QVector3D position, QString name)
{
    float width;
    float height;
    float xoffset;
    float yoffset;
    QVector2D point;
    QString text;

    width = this->width();
    height = ((float)m_image.height() / (float)m_image.width()) * this->width();
    xoffset = 0.0;
    yoffset = (this->height() - height) / 2.0;

    if (yoffset < 0) {
        height = this->height();
        width = ((float)m_image.width() / (float)m_image.height()) * this->height();
        xoffset = (this->width() - width) / 2.0;
        yoffset = 0.0;
    }

    point = m_project.convertSpaceToImage(position);
    //qDebug() << "Point:" << name << point;

    point = QVector2D(xoffset + (width / 2.0) + (width * (point.x() / 1920.0)), yoffset + (height / 2.0) - width * ((point.y() / 1920.0)));

    QPen pen(Qt::red);
    pen.setWidth(4.0);
    painter->setBrush(Qt::NoBrush);
    painter->setPen(pen);
    painter->drawEllipse(point.x(), point.y(), 8.0, 8.0);

    QFont font = painter->font();
    font.setPixelSize(32);
    painter->setFont(font);
    painter->drawText(point.x() + 12.0, point.y() + 16.0, name);

    pen = QPen(Qt::green);
    pen.setWidth(0.1);
    painter->setBrush(Qt::NoBrush);
    painter->setPen(pen);
    font.setPixelSize(24);
    painter->setFont(font);

    text = "θ: " + QString::number(m_project.angle(), 'f', 6);
    painter->drawText(32, 32, text);
    text = "n: " + QString::number(m_project.viewDirection().x(), 'f', 3) + ", " + QString::number(m_project.viewDirection().y(), 'f', 3) + ", " + QString::number(m_project.viewDirection().z(), 'f', 3);
    painter->drawText(32, 56, text);
    text = "u: " + QString::number(m_project.horizontal().x(), 'f', 3) + ", " + QString::number(m_project.horizontal().y(), 'f', 3) + ", " + QString::number(m_project.horizontal().z(), 'f', 3);
    painter->drawText(32, 80, text);
    text = "c: " + QString::number(m_project.cameraLocation().x(), 'f', 3) + ", " + QString::number(m_project.cameraLocation().y(), 'f', 3) + ", " + QString::number(m_project.cameraLocation().z(), 'f', 3);
    painter->drawText(32, 104, text);
}

void VideoStill::adjustCameraAngle(float angle)
{
    m_project.adjustCameraAngle(angle);
    m_project.outputCameraInfo();
    this->update();
}

void VideoStill::adjustCameraHeight(float height)
{
    m_project.adjustCameraHeight(height);
    m_project.outputCameraInfo();
    this->update();
}

void VideoStill::adjustCameraPosition(float x, float y)
{
    m_project.adjustCameraPosition(x, y);
    m_project.outputCameraInfo();
    this->update();
}
