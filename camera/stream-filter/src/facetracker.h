#ifndef FACETRACKER_H
#define FACETRACKER_H

#include <QObject>
#include <QRectF>
#include <QImage>

#include <opencv4/opencv2/objdetect/face.hpp>

class FaceTracker : public QObject
{
  Q_OBJECT
  Q_PROPERTY(QRectF trackedBox READ trackedBox WRITE setTrackedBox NOTIFY trackedBoxChanged)
public:
  explicit FaceTracker(QObject *parent = nullptr);
  void update(QImage* frame);
  static float iou(QRectF first, QRectF second);

public slots:
  QRectF trackedBox() const;
  void setTrackedBox(QRectF trackedBox);

signals:
  void trackedBoxChanged();

private:
  QRectF m_trackedBox;
  cv::Ptr<cv::FaceDetectorYN> m_detector;
  cv::Mat m_frame;
};

#endif // FACETRACKER_H
