#include <QDebug>

#include <opencv2/imgcodecs.hpp>

#include "facetracker.h"

const float IOU_THRESHOLD = 0.3;

float FaceTracker::iou(QRectF box_a, QRectF box_b)
{
  float ax1 = box_a.x();
  float ay1 = box_a.y();
  float ax2 = ax1 + box_a.width();
  float ay2 = ay1 + box_a.height();
  float bx1 = box_b.x();
  float by1 = box_b.y();
  float bx2 = bx1 + box_b.width();
  float by2 = by1 + box_b.height();
  float inter_w = qMax(0.0f, qMin(ax2, bx2) - qMax(ax1, bx1));
  float inter_h = qMax(0.0f, qMin(ay2, by2) - qMax(ay1, by1));
  float inter = inter_w * inter_h;
  float uni = box_a.width() * box_a.height() + box_b.width() * box_b.height() - inter;
  return uni > 0.0f ? (inter / uni) : 0.0f;
}

FaceTracker::FaceTracker(QObject *parent) : QObject(parent)
{
  m_trackedBox = QRectF();
  cv::Size size = cv::Size(360, 480);

  m_detector = cv::FaceDetectorYN::create("/usr/share/stream-filter/models/face_detection_yunet_2023mar.onnx", "", size, 0.6, 0.3, 10);
}

void FaceTracker::update(QImage* frame) {
  int pos;
  float best;
  int found;
  QRectF box;
  float value;

  cv::Size size = cv::Size(frame->width(), frame->height());
  m_detector->setInputSize(size);
  m_frame = cv::Mat(size.height, size.width, CV_8UC3, (void*)frame->constBits());
  cv::Mat faces;
  m_detector->detect(m_frame, faces);

  int count = faces.size[0];
  if (count > 0) {
    if (m_trackedBox.isEmpty()) {
      best = 0;
      found = 0;
      for (pos = 0; pos < count; ++pos) {
        float value = faces.at<float>(pos, 2) * faces.at<float>(pos, 3);
        if (value > best) {
          best = value;
          found = pos;
        }
      }
      m_trackedBox = QRectF(faces.at<float>(found, 0), faces.at<float>(found, 1), faces.at<float>(found, 2), faces.at<float>(found, 3));
    }
    else {
      best = 0;
      found = 0;
      for (pos = 0; pos < count; ++pos) {
        box = QRectF(faces.at<float>(pos, 0), faces.at<float>(pos, 1), faces.at<float>(pos, 2), faces.at<float>(pos, 3));
        value = iou(box, m_trackedBox);
        if (value > best) {
          best = value;
          found = pos;
        }
      }

      box = QRectF(faces.at<float>(found, 0), faces.at<float>(found, 1), faces.at<float>(found, 2), faces.at<float>(found, 3));
      value = iou(box, m_trackedBox);
      if (abs(value) < IOU_THRESHOLD) {
        setTrackedBox(QRect());
      }
      else {
        setTrackedBox(box);
        qDebug() << "Bounds:" << found << ":" << m_trackedBox;
      }
    }
  }

  qDebug() << "Faces:" << count;
}

QRectF FaceTracker::trackedBox() const
{
  return m_trackedBox;
}

void FaceTracker::setTrackedBox(QRectF trackedBox) {
  if (m_trackedBox != trackedBox) {
    m_trackedBox = trackedBox;
    emit trackedBoxChanged();
  }
}
