#include "math.h"
#include <QDebug>
#include "project.h"

Project::Project(QObject *parent)
    : QObject{parent}
{
    m_angle = -2.0 / 33.0;
    m_cameraLocation = QVector3D(-0.3, 0.1, 1.39); // c
    m_viewDirection = QVector3D(sin(-2.0 * M_PI * m_angle), cos(2.0 * M_PI * m_angle), 0.0); // n
    m_horizontal = QVector3D(cos(2.0 * M_PI * m_angle), sin(2.0 * M_PI * m_angle), 0.0); // u
    m_focalLength = float((3326.0 / 4000.0) * 1920.0); // f
}

QVector2D Project::convertSpaceToImage(QVector3D position) const
{
    QVector3D relativePosition;
    float distance;
    QVector2D projection;

    relativePosition = position - m_cameraLocation;
    distance = QVector3D::dotProduct(relativePosition, m_viewDirection);
    projection.setX(QVector3D::dotProduct(relativePosition, m_horizontal) * m_focalLength / distance);
    projection.setY(QVector3D::dotProduct(relativePosition, QVector3D::crossProduct(m_horizontal, m_viewDirection)) * m_focalLength / distance);

    return projection;
}

QVector3D Project::cameraLocation() const
{
    return m_cameraLocation;
}

QVector3D Project::viewDirection() const
{
    return m_viewDirection;
}

QVector3D Project::horizontal() const
{
    return m_horizontal;
}

float Project::focalLength() const
{
    return m_focalLength;
}

void Project::setCameraLocation(QVector3D cameraLocation)
{
    if (m_cameraLocation != cameraLocation) {
        m_cameraLocation = cameraLocation;
        emit cameraLocationChanged();
    }
}

void Project::setViewDirection(QVector3D viewDirection)
{
    if (m_viewDirection != viewDirection) {
        m_viewDirection = viewDirection;
        emit viewDirectionChanged();
    }
}

void Project::setHorizontal(QVector3D horizontal)
{
    if (m_horizontal != horizontal) {
        m_horizontal = horizontal;
        emit horizontalChanged();
    }
}

void Project::setFocalLength(float focalLength)
{
    if (m_focalLength != focalLength) {
        m_focalLength = focalLength;
        emit focalLengthChanged();
    }
}

void Project::adjustCameraAngle(float angle)
{
    m_angle += angle;

    setViewDirection(QVector3D(sin(-2.0 * M_PI * m_angle), cos(2.0 * M_PI * m_angle), 0.0));
    setHorizontal(QVector3D(cos(2.0 * M_PI * m_angle), sin(2.0 * M_PI * m_angle), 0.0));
}

void Project::adjustCameraHeight(float height)
{
    QVector3D cameraLocation = this->cameraLocation();
    cameraLocation.setZ(cameraLocation.z() + height);
    setCameraLocation(cameraLocation);
}

void Project::adjustCameraPosition(float x, float y)
{
    QVector3D cameraLocation = this->cameraLocation();
    cameraLocation.setX(cameraLocation.x() + x);
    cameraLocation.setY(cameraLocation.y() + y);
    setCameraLocation(cameraLocation);
}

float Project::angle() const
{
    return m_angle;
}

void Project::outputCameraInfo() const
{
    qDebug() << "Camera angle:" << m_angle;
    qDebug() << "ViewDirection:" << m_viewDirection;
    qDebug() << "Horizontal:" << m_horizontal;
    qDebug() << "Camera location:" << m_cameraLocation;
    qDebug() << "";
}
