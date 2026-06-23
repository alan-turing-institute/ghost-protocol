#ifndef VIDEOSTILL_H
#define VIDEOSTILL_H

#include <QObject>
#include <QQuickPaintedItem>
#include <QImage>
#include <QTimer>

#include "project.h"

class VideoStill : public QQuickPaintedItem
{
    Q_OBJECT
    Q_PROPERTY(QImage still READ still WRITE setStill NOTIFY stillChanged)
    Q_PROPERTY(QRectF imageBox READ imageBox NOTIFY imageBoxChanged)
public:
    explicit VideoStill(QQuickItem *parent = nullptr);

public slots:
    QImage still() const;
    void setStill(QImage still);
    void updateImage();
    void renderPoint(QPainter* painter, QVector3D position, QString name);
    QRectF imageBox() const;

    void adjustCameraAngle(float angle);
    void adjustCameraHeight(float height);
    void adjustCameraPosition(float x, float y);

protected:
    void paint(QPainter* painter) override;

signals:
    void stillChanged();
    void imageBoxChanged();

private:
    void setImageBox(QRectF imageBox);

private:
    QImage m_image;
    Project m_project;
    QRectF m_imageBox;
};

#endif // VIDEOSTILL_H
