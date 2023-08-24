#ifndef WINDIAGNOSTIC_H
#define WINDIAGNOSTIC_H

#include "AbstractDiagnostic.h"

#include <windows.h>
#include <psapi.h>
#include <tlhelp32.h>
#include "registry.h"
#include "pdh.h"


enum PLATFORM { WINNT1, WIN2K_XP1, WIN9X1, UNKNOWN1 };

class WinDiagnostic : public AbstractDiagnostic {
    Q_OBJECT
public:
    explicit WinDiagnostic(AbstractDiagnostic* parent = nullptr);

private:
    QJsonObject get_sys_info();
    QJsonObject get_process_info(int totalRam);

    long get_memory_size(HANDLE hProc);
    ULONGLONG ft2ull(FILETIME &ft);

private:

    HANDLE hProcessSnapShot;
    PROCESSENTRY32 ProcessEntry;
    FILETIME s_prev_idle, s_prev_kernel, s_prev_user;

private slots:
    void refresh_win_snapshot();
    void info_update();
};

#endif  // WINDIAGNOSTIC_H
