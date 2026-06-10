#ifndef VIDEOSTILL_H
#define VIDEOSTILL_H

#include <QObject>
#include <QQuickPaintedItem>
#include <QImage>
#include <QTimer>

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

protected:
    void paint(QPainter* painter) override;

signals:
    void stillChanged();

private:
    QImage m_image;
};

#endif // VIDEOSTILL_H
