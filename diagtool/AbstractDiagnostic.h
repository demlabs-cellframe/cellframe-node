#ifndef ABSTRACTDIAGNOSTIC_H
#define ABSTRACTDIAGNOSTIC_H

#include <QObject>
#include "qtimer.h"
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QDebug>
#include <QUrl>
#include <QFileInfo>
#include <QCoreApplication>
#include <QProcess>
#include <QString>
#include <QRegularExpression>
#include <QSettings>
#include <QTime>

#include <QDir>
#include <QNetworkInterface>

class AbstractDiagnostic : public QObject
{
    Q_OBJECT
public:
    explicit AbstractDiagnostic(QObject * parent = nullptr);
    ~AbstractDiagnostic();

public:
    void start_diagnostic();
    void stop_diagnostic();
    void set_timeout(int timeout);
    quint64 get_file_size(QString flag, QString path);
    QString get_uptime_string(long sec);
    QString get_memory_string(long num);
    QJsonValue get_mac();

    QJsonDocument get_full_info(){return s_full_info;};

    QJsonObject roles_processing();

public:
    QTimer * s_timer_update;
    int s_timeout{1000};
    QJsonDocument s_full_info;
    QJsonValue s_mac;

signals:
    void data_updated(QJsonDocument);

};

#endif // ABSTRACTDIAGNOSTIC_H
