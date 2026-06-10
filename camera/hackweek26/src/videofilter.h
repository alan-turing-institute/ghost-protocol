#ifndef VIDEOFILTER_H
#define VIDEOFILTER_H

#include <QAbstractVideoFilter>

class VideoFilter : public QAbstractVideoFilter
{
    Q_OBJECT
    Q_PROPERTY(QString result READ result NOTIFY resultChanged)

public:
    explicit VideoFilter(QObject *parent = nullptr);
    virtual ~VideoFilter() override = default;

    QVideoFilterRunnable *createFilterRunnable() override;
    QString result() const;
    void setResult(const QString &result);

    Q_INVOKABLE void clearResult();

signals:
    void decodeFinished(const QString &result);
    void resultChanged(const QString &result);

private:
    QString m_result;
    friend class VideoFilterRunnable;
};

#endif // VIDEOFILTER_H
