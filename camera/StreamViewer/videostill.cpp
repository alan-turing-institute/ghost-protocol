#include <QPainter>

#include "videostill.h"

VideoStill::VideoStill(QQuickItem *parent)
    : QQuickPaintedItem(parent)
{
    m_image = QImage();
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
}
