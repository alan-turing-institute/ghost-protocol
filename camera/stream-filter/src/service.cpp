#include "service.h"

#include <QDBusContext>
#include <QDBusConnectionInterface>
#include <QDBusReply>
#include <QDBusMessage>
#include <QDebug>
#include <QFile>
#include <QVideoSurfaceFormat>
#include <QImage>
#include <QCoreApplication>
#include <QPainter>

#include <unistd.h>
#include <sys/mman.h>

const char *SERVICE_NAME = "uk.ac.turing.stream";
const char *OBJECT_PATH = "/uk/ac/turing/stream";
const char *INTERFACE = "uk.ac.turing.stream";
const QDBusConnection::RegisterOption flags = QDBusConnection::ExportAllSlots;

Service::Service(Server* server, FaceTracker* facetracker, QObject *parent)
    : QObject(parent),
      QDBusContext()
{
  m_server = server;
  m_facetracker = facetracker;
  qDebug() << "Creating connection";
  QDBusConnection connection = QDBusConnection::sessionBus();
  if (!connection.registerObject(OBJECT_PATH, INTERFACE, this, flags)) {
      qFatal("Cannot register object at %s", OBJECT_PATH);
  }

  if (!connection.registerService(SERVICE_NAME)) {
      qFatal("Cannot register D-Bus service at %s", SERVICE_NAME);
  }
  qDebug() << "Created connection";
}

Service::~Service()
{
}

void Service::imageCleanupHandler(void *info)
{
  uchar* rgbbuf = (uchar*)info;
  free(rgbbuf);
}

QString Service::decodeFromDescriptor(QDBusUnixFileDescriptor fd, uint size, int width, int height, int pixelFormat)
{
  QString response = "Image not saved";
  QFile mf;
  QImage* image;

  if (mf.open(fd.fileDescriptor(), QIODevice::ReadOnly)) {
      uchar *buf = mf.map(0, size);

      if (buf != nullptr) {
        QImage::Format format;
        if (pixelFormat == 8) {
          uchar* rgbbuf = (uchar*)malloc(height * width * 3);
          // QVideoFrame::Format_BGRA32
          // The frame is stored using a 32-bit BGRA format (0xBBGGRRAA).
          int nPrePos = 0;
          for (int nPos = 0; nPos < (height * width * 3); nPos += 3) {
            uint8_t uRed = buf[nPrePos + 0];
            uint8_t uGreen = buf[nPrePos + 1];
            uint8_t uBlue = buf[nPrePos + 1];
            nPrePos += 4;

            // QVideoFrame::Format_ARGB32
            // 32-bit RGB format (0xffRRGGBB). This is equivalent to QImage::Format_RGB32
            rgbbuf[nPos + 0] = uRed;
            rgbbuf[nPos + 1] = uGreen;
            rgbbuf[nPos + 2] = uBlue;
          }
          format = QImage::Format_RGB888;

          image = new QImage(rgbbuf, width, height, format, Service::imageCleanupHandler, (void*)rgbbuf);
        }
        else {
          format = QVideoFrame::imageFormatFromPixelFormat((QVideoFrame::PixelFormat)pixelFormat);
          image = new QImage(buf, width, height, format);
        }
        QImage* scaled = new QImage(image->scaled(800, 800 * height / width));
//        QImage* scaled = image;
//        m_facetracker->update(scaled);
//        if (!m_facetracker->trackedBox().isEmpty()) {
//          QPainter painter(scaled);
//          QPen pen(Qt::red);
//          pen.setWidth(4.0);
//          painter.setBrush(Qt::NoBrush);
//          painter.setPen(pen);
//          painter.drawRect(m_facetracker->trackedBox());
//          painter.end();
//        }
        m_server->setNextImage(scaled);
        delete image;

        response = "Image saved";
      } else {
          qWarning() << "map():" << mf.error();
      }
  } else {
      qWarning() << "open():" << mf.error();
  }

  return response;
}

void Service::quit()
{
  QCoreApplication::quit();
}
