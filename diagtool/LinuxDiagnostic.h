#ifndef LINUXDIAGNOSTIC_H
#define LINUXDIAGNOSTIC_H


#include "AbstractDiagnostic.h"
#include <unistd.h>
#include <fcntl.h>
#include <vector>

#include <fstream>
#include <numeric>
#include <vector>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <locale.h>
#include <signal.h>
#include <dirent.h>

#include <sys/sysinfo.h>

using namespace std;


class LinuxDiagnostic : public AbstractDiagnostic
{
    Q_OBJECT
public:
    explicit LinuxDiagnostic(AbstractDiagnostic * parent = nullptr);

private:
    QJsonObject get_sys_info();
    bool get_cpu_times(size_t &idle_time, size_t &total_time);
    std::vector<size_t> get_cpu_times();
    long get_pid();
    QString get_running(char* pid);
    QString get_proc_path(long pid);
    QJsonObject get_process_info(long pid, int totalRam);
    QJsonObject get_disk_info();
    QJsonObject get_cli_info();


    //CLI

    QStringList get_networks();
    QJsonObject get_net_info(QString net);
    QJsonObject get_mempool_count(QString net);
    QJsonObject get_ledger_count(QString net);
    QJsonObject get_blocks_count(QString net);
    QJsonObject get_events_count(QString net);

private slots:
    void info_update();

private:
    size_t previous_idle_time{0}, previous_total_time{0};
    bool s_node_status{false};

};

#endif // LINUXDIAGNOSTIC_H
