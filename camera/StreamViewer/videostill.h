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
public:
    explicit VideoStill(QQuickItem *parent = nullptr);

public slots:
    QImage still() const;
    void setStill(QImage still);
    void updateImage();
    void renderPoint(QPainter* painter, QVector3D position, QString name);

    void adjustCameraAngle(float angle);
    void adjustCameraHeight(float height);
    void adjustCameraPosition(float x, float y);

protected:
    void paint(QPainter* painter) override;

signals:
    void stillChanged();

private:
    QImage m_image;
    Project m_project;
};

#endif // VIDEOSTILL_H
