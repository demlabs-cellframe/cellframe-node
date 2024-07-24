 #ifdef WIN32 

#include "service.h"
#include "../commands/abstractcommand.h"
#include <windows.h>
#include <windowsx.h>
#include <shlobj.h>


#include <windows.h>
#include <tlhelp32.h>
#include <tchar.h>

bool isProcessRunning(const TCHAR* const executableName) {
    PROCESSENTRY32 entry;
    entry.dwSize = sizeof(PROCESSENTRY32);

    const auto snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);

    if (!Process32First(snapshot, &entry)) {
        CloseHandle(snapshot);
        return false;
    }

    do {
        
        if (!_tcsicmp(entry.szExeFile, executableName)) {
            
            CloseHandle(snapshot);
            return true;
        }
    } while (Process32Next(snapshot, &entry));

    CloseHandle(snapshot);
    return false;
}

int runShellAdmin(std::string app, std::string cmd)
{
    // Launch itself as admin
    SHELLEXECUTEINFO sei = { sizeof(sei) };
    sei.lpVerb = "runas";
    sei.lpFile = app.c_str();
    sei.lpParameters = cmd.c_str();
    sei.hwnd = NULL;
    sei.nShow = SW_HIDE;

    if (!ShellExecuteEx(&sei))
    {
        DWORD dwError = GetLastError();
        if (dwError == ERROR_CANCELLED)
        {
            std::cout << "End user did not allow elevation" << std::endl;
            return -1;
        }

        std::cout << "Exec failed" << dwError<< std::endl;

    }
    WaitForSingleObject(sei.hProcess,INFINITE);
    long unsigned int rc;
    GetExitCodeProcess(sei.hProcess, &rc);
    return rc;
}


bool CServiceControl::enable()
{
    auto nodebinpath = std::filesystem::path{variable_storage["NODE_BINARY_PATH"]}/"cellframe-node.exe";
    std::string cmd = std::string("/Create /F /RL highest /SC onlogon /TR \"'") + nodebinpath.string() + "'\" /TN CellframeNode";
    long unsigned int res = runShellAdmin("schtasks.exe", cmd);
    return res == 0 ? true : false;
}

bool CServiceControl::disable()
{
    std::string cmd = std::string("/Delete  /TN CellframeNode /f");
    long unsigned int res = runShellAdmin("schtasks.exe", cmd);
    return res == 0 ? true : false;
}

unsigned int CServiceControl::serviceStatus()
{
    unsigned int status = 0;
    
    std::string cmd = std::string("schtasks /query  /TN CellframeNode");
    int res = std::system(cmd.c_str());
    
    if (res == 0)
    {
        status |= SERVICE_ENABLED;
    }
    
    if (isProcessRunning("cellframe-node.exe"))
    {
        std::cout << "proc running" << std::endl;
        status |= PROCESS_RUNNING;
    }
    
    return (unsigned)status;
}

bool CServiceControl::start()
{
    std::string cmd = std::string("/run  /TN CellframeNode");
    long unsigned int res = runShellAdmin("schtasks.exe", cmd);
    return res==0 ? true : false;
}

bool CServiceControl::stop()
{
    std::string cmd = std::string("/IM cellframe-node.exe  /F");
    long unsigned int res = runShellAdmin("taskkill.exe", cmd);
    return res==0 ? true : false;
}

bool CServiceControl::restart()
{
    stop();
    start();
    return true;
}    
 #endif