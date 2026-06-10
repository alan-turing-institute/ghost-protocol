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

#include <unistd.h>
#include <sys/mman.h>

const char *SERVICE_NAME = "uk.ac.turing.stream";
const char *OBJECT_PATH = "/uk/ac/turing/stream";
const char *INTERFACE = "uk.ac.turing.stream";
const QDBusConnection::RegisterOption flags = QDBusConnection::ExportAllSlots;

Service::Service(Server* server, QObject *parent)
    : QObject(parent),
      QDBusContext()
{
  m_server = server;
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
          uchar* rgbbuf = (uchar*)malloc(height * width * 4);
          // QVideoFrame::Format_BGRA32
          // The frame is stored using a 32-bit BGRA format (0xBBGGRRAA).
          for (int nPos = 0; nPos < (height * width * 4); nPos += 4) {
            uint16_t uRed = buf[nPos + 2];
            uint16_t uGreen = buf[nPos + 1];
            uint16_t uBlue = buf[nPos + 0];

            // QVideoFrame::Format_ARGB32
            // 32-bit RGB format (0xffRRGGBB). This is equivalent to QImage::Format_RGB32
            rgbbuf[nPos + 0] = uRed;
            rgbbuf[nPos + 1] = uGreen;
            rgbbuf[nPos + 2] = uBlue;
            rgbbuf[nPos + 3] = 0xff;
          }
          format = QImage::Format_ARGB32;

          image = new QImage(rgbbuf, width, height, format, Service::imageCleanupHandler, (void*)rgbbuf);
        }
        else {
          format = QVideoFrame::imageFormatFromPixelFormat((QVideoFrame::PixelFormat)pixelFormat);
          image = new QImage(buf, width, height, format);
        }
        QImage* scaled = new QImage(image->scaled(width / 4.0, height / 4.0));
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
