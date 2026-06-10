#include "videofilter.h"
#include "videofilterrunnable.h"

VideoFilter::VideoFilter(QObject *parent)
    : QAbstractVideoFilter(parent)
{
}

QVideoFilterRunnable *VideoFilter::createFilterRunnable()
{
    if (!isActive()) {
        return nullptr;
    }
    return new VideoFilterRunnable(this);
}

QString VideoFilter::result() const
{
    return m_result;
}

void VideoFilter::setResult(const QString &result)
{
    if (m_result == result)
        return;

    m_result = result;
    emit resultChanged(m_result);
}

void VideoFilter::clearResult()
{
    setResult(QString());
}
