#ifndef DIAGNOSTICWORKER_H
#define DIAGNOSTICWORKER_H

#include <QObject>
#include <QTimer>
#include <QElapsedTimer>
#include <QSettings>

#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "LinuxDiagnostic.h"


class DiagnosticWorker : public QObject
{
    Q_OBJECT
public:
    explicit DiagnosticWorker(QObject *parent = nullptr);
    ~DiagnosticWorker();

private:
    QString m_node_version{""};
    QSettings m_settings;
    AbstractDiagnostic* m_diagnostic;

    QTimer *s_uptime_timer;
    QElapsedTimer *s_elapsed_timer;
    QString s_uptime{"00:00:00"};

private slots:
    void slot_diagnostic_data(QJsonDocument);
    void slot_uptime();

private:
    void write_data(QJsonDocument);

};

#endif // DIAGNOSTICWORKER_H
