#ifndef VIDEOFILTERRUNNABLE_H
#define VIDEOFILTERRUNNABLE_H

#include "videofilter.h"

#include <QtDBus/QDBusUnixFileDescriptor>
#include <QtDBus/QDBusPendingReply>
#include <QVideoFilterRunnable>
#include <QElapsedTimer>

class VideoFilterRunnable : public QObject, public QVideoFilterRunnable
{
    Q_OBJECT
public:
    explicit VideoFilterRunnable(VideoFilter *filter);
    ~VideoFilterRunnable() override = default;

    QVideoFrame run(QVideoFrame *input, const QVideoSurfaceFormat &surfaceFormat,
                    RunFlags flags) override;

signals:
    void stringFound(const QString &result);

private:
    void analyze(QDBusUnixFileDescriptor fd, uint bufferSize,
                 QVideoSurfaceFormat surfaceFormat);
    VideoFilter *m_filter = nullptr;
    QDBusPendingReply<QString> m_reply;
    QElapsedTimer m_timer;
};

#endif // VIDEOFILTERRUNNABLE_H
