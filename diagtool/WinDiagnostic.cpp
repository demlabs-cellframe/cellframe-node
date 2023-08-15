#include "WinDiagnostic.h"

WinDiagnostic::WinDiagnostic(AbstractDiagnostic *parent)
    : AbstractDiagnostic{parent}
{
    connect(s_timer_update, &QTimer::timeout,
            this, &WinDiagnostic::info_update,
            Qt::QueuedConnection);

    GetSystemTimes(&s_prev_idle, &s_prev_kernel, &s_prev_user);
}

void WinDiagnostic::info_update()
{
    QJsonObject proc_info;
    QJsonObject sys_info;
    QJsonObject cli_info;
    QJsonObject full_info;

    sys_info = get_sys_info();
    sys_info.insert("mac", s_mac);
//    sys_info.insert("disk", get_disk_info());

    QString jsonFilePath = QString("%1/etc/diagdata.json").arg(s_nodeDataPath);
    QFile file(jsonFilePath);
    if(file.open(QIODevice::ReadOnly | QIODevice::Text))
    {
        QJsonParseError err;
        QJsonDocument doc = QJsonDocument::fromJson(file.readAll(), &err);
        file.close();

        if(err.error == QJsonParseError::NoError && !doc.isEmpty())
            sys_info.insert("data", doc.object());
        else
            qWarning()<<err.errorString();
    }

    QJsonObject obj = sys_info["memory"].toObject();
    int mem = obj["total"].toString().toInt();;

    proc_info = get_process_info(mem);
    proc_info.insert("roles", roles_processing());

    if(s_node_status)
    {
        cli_info = get_cli_info();
        full_info.insert("cli_data", cli_info);
    }

    full_info.insert("system", sys_info);
    full_info.insert("process", proc_info);

    s_full_info.setObject(full_info);

    emit data_updated(s_full_info);
}

QJsonObject WinDiagnostic::get_sys_info()
{
    QJsonObject obj_sys_data, obj_cpu, obj_memory;

    // get CPU load
    FILETIME idle;
    FILETIME kernel;
    FILETIME user;

    GetSystemTimes(&idle, &kernel, &user);

    ULONGLONG sys = (ft2ull(user) - ft2ull(s_prev_user)) +
        (ft2ull(kernel) - ft2ull(s_prev_kernel));

    QString cpu_load = QString::number(int((sys - ft2ull(idle) + ft2ull(s_prev_idle)) * 100.0 / sys));
    obj_cpu.insert("load", cpu_load);

    s_prev_idle = idle;
    s_prev_kernel = kernel;
    s_prev_user = user;

    MEMORYSTATUSEX memory_status;
    ZeroMemory(&memory_status, sizeof(MEMORYSTATUSEX));
    memory_status.dwLength = sizeof(MEMORYSTATUSEX);
    GlobalMemoryStatusEx(&memory_status);

    QString memory, memory_used, memory_free;

    memory = QString::number(memory_status.ullTotalPhys / 1024);
    size_t total_value = memory_status.ullTotalPhys / 1024;
    size_t available_value = memory_status.ullAvailPhys / 1024;
    memory_free = QString::number(memory_status.ullAvailPhys / 1024);

    memory_used = QString::number((total_value - available_value) *100 / total_value);

    obj_memory.insert("total", memory);
    obj_memory.insert("free", memory_free);
    obj_memory.insert("load", memory_used);

    DWORD currentTime = GetTickCount();

    QString uptime = get_uptime_string(currentTime/1000);


    obj_sys_data.insert("uptime", uptime);
    obj_sys_data.insert("CPU", obj_cpu);
    obj_sys_data.insert("memory", obj_memory);
    return obj_sys_data;

}

long WinDiagnostic::get_memory_size(Qt::HANDLE hProc)
{
    PROCESS_MEMORY_COUNTERS pmcInfo;

    if (GetProcessMemoryInfo(hProc, &pmcInfo, sizeof(pmcInfo)))
        return pmcInfo.WorkingSetSize/1024;
    else return 0;

}

ULONGLONG WinDiagnostic::ft2ull(FILETIME &ft) {
    ULARGE_INTEGER ul;
    ul.HighPart = ft.dwHighDateTime;
    ul.LowPart = ft.dwLowDateTime;
    return ul.QuadPart;
}

void WinDiagnostic::refresh_win_snapshot()
{
    // Get the process list snapshot.
    hProcessSnapShot = CreateToolhelp32Snapshot(TH32CS_SNAPALL, 0);

    ProcessEntry.dwSize = sizeof( ProcessEntry );


    // Get the first process info.
    BOOL Return = FALSE;
    Return = Process32First( hProcessSnapShot,&ProcessEntry );

    // Getting process info failed.
    if( !Return )
    {
        qDebug()<<"Getting process info failed";
    }
}

QJsonObject WinDiagnostic::get_process_info(int totalRam)
{
    refresh_win_snapshot();

    hProcessSnapShot = CreateToolhelp32Snapshot(TH32CS_SNAPALL, 0);

    // vars for get process time
    FILETIME lpCreation, lpExit, lpKernel, lpUser;
    SYSTEMTIME stCreation, stExit, stKernel, stUser;
    long memory_size;

    HANDLE hSnapshot;
    PROCESSENTRY32 pe;
    long pid = 0;
    BOOL hResult;

    // snapshot of all processes in the system
    hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);

    // initializing size: needed for using Process32First
    pe.dwSize = sizeof(PROCESSENTRY32);

    // info about first process encountered in a system snapshot
    hResult = Process32First(hSnapshot, &pe);


    QString proc_name = "cellframe-node.exe";
    while (hResult) {
        // if we find the process: return process ID

        std::wstring string(pe.szExeFile);
        std::string str(string.begin(), string.end());
        QString s = QString::fromStdString(str);


        if(!proc_name.compare(s)){
            pid = pe.th32ProcessID;

            // get process descriptor
            HANDLE hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION , FALSE, pe.th32ProcessID);

            if(hProcess)
            {
                // get process times info
                if(GetProcessTimes(hProcess,&lpCreation, &lpExit, &lpKernel, &lpUser))
                {
                      FileTimeToSystemTime(&lpCreation, &stCreation);
                      FileTimeToSystemTime(&lpExit, &stExit);
                      FileTimeToSystemTime(&lpUser, &stUser);
                      FileTimeToSystemTime(&lpKernel, &stKernel);
                }

                memory_size = get_memory_size(hProcess);

                //TODO CPU processing

                CloseHandle(hProcess);
            }

            break;
        }
        hResult = Process32Next(hSnapshot, &pe);
    }

    CloseHandle( hProcessSnapShot );

    QJsonObject process_info;

    QString status = "Offline";
//    QString path = NODE_PATH;
    QString node_dir = QString("%1/cellframe-node/").arg(regGetUsrPath());

    QString log_size, db_size, chain_size;
    log_size = QString::number(get_file_size("log", node_dir) / 1024);
    db_size = QString::number(get_file_size("DB", node_dir) / 1024);
    chain_size = QString::number(get_file_size("chain", node_dir) / 1024);

    if(log_size.isEmpty()) log_size = "0";
    if(db_size.isEmpty()) db_size = "0";
    if(chain_size.isEmpty()) chain_size = "0";

    process_info.insert("log_size", log_size);
    process_info.insert("DB_size", db_size);
    process_info.insert("chain_size", chain_size);


    if(pid){

        QDateTime dateStart;
        dateStart.setMSecsSinceEpoch(0);
        dateStart = dateStart.addYears(stCreation.wYear - 1970);
        dateStart = dateStart.addMonths(stCreation.wMonth - 1);
        dateStart = dateStart.addDays(stCreation.wDay - 1);
        dateStart = dateStart.addSecs(stCreation.wHour * 60 * 60 + stCreation.wMinute * 60 + stCreation.wSecond);

        QDateTime dateNow = QDateTime::currentDateTime();

        quint64 sec_start = dateStart.toSecsSinceEpoch();
        quint64 sec_now = dateNow.toSecsSinceEpoch();

        long result_uptime = sec_now - sec_start;

        QString uptime = get_uptime_string(result_uptime);

        int precentUseRss = (memory_size * 100) / totalRam;
        QString memory_use_value = QString::number(memory_size);

        process_info.insert("memory_use",precentUseRss);
        process_info.insert("memory_use_value",memory_use_value);
        process_info.insert("uptime",uptime);
        process_info.insert("name","cellframe-node");

        status = "Online";

    }else{

        process_info.insert("memory_use",0);
        process_info.insert("memory_use_value","0 Kb");
        process_info.insert("uptime","00:00:00");
    }

    s_node_status = status == "Online" ? true : false;

    process_info.insert("status", status);
//    process_info.insert("path", path);


    return process_info;
}

