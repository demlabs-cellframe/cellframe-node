#ifndef MACDIAGNOSTIC_H
#define MACDIAGNOSTIC_H

#include "AbstractDiagnostic.h"

#include <sys/sysctl.h>
#include <sys/types.h>
#include <mach/vm_statistics.h>
#include <mach/mach_types.h>
#include <mach/mach_init.h>
#include <mach/mach_host.h>
#include <time.h>
#include <mach/mach_time.h>

using namespace std;


class MacDiagnostic : public AbstractDiagnostic
{
    Q_OBJECT
public:
    explicit MacDiagnostic(AbstractDiagnostic * parent = nullptr);

private:
    QJsonObject get_sys_info();
    QJsonObject get_process_info(int totalRam);

    //cpu
    float calculate_cpu_load(unsigned long long idleTick, unsigned long long totakTicks );

private slots:
    void info_update();

};

#endif // MACDIAGNOSTIC_H
