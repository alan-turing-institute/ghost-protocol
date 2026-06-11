#ifndef PROJECT_H
#define PROJECT_H

#include <QObject>
#include <QVector3D>
#include <QVector2D>

class Project : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QVector3D cameraLocation READ cameraLocation WRITE setCameraLocation NOTIFY cameraLocationChanged)
    Q_PROPERTY(QVector3D viewDirection READ viewDirection WRITE setViewDirection NOTIFY viewDirectionChanged)
    Q_PROPERTY(QVector3D horizontal READ horizontal WRITE setHorizontal NOTIFY horizontalChanged)
    Q_PROPERTY(float focalLength READ focalLength WRITE setFocalLength NOTIFY focalLengthChanged)
public:
    explicit Project(QObject *parent = nullptr);
    void outputCameraInfo() const;
    float angle() const;

public slots:
    QVector3D cameraLocation() const;
    QVector3D viewDirection() const;
    QVector3D horizontal() const;
    float focalLength() const;

    void setCameraLocation(QVector3D cameraLocation);
    void setViewDirection(QVector3D viewDirection);
    void setHorizontal(QVector3D horizontal);
    void setFocalLength(float flocaLLength);

    QVector2D convertSpaceToImage(QVector3D position) const;

    void adjustCameraAngle(float angle);
    void adjustCameraHeight(float height);
    void adjustCameraPosition(float x, float y);

signals:
    void cameraLocationChanged();
    void viewDirectionChanged();
    void horizontalChanged();
    void focalLengthChanged();

private:
    QVector3D m_cameraLocation;
    QVector3D m_viewDirection;
    QVector3D m_horizontal;
    float m_focalLength;
    float m_angle;
};

#endif // PROJECT_H
