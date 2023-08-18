#include "MacDiagnostic.h"

static unsigned long long _previousTotalTicks = 0;
static unsigned long long _previousIdleTicks = 0;

MacDiagnostic::MacDiagnostic(AbstractDiagnostic *parent)
    : AbstractDiagnostic{parent}
{
    connect(s_timer_update, &QTimer::timeout,
            this, &MacDiagnostic::info_update,
            Qt::QueuedConnection);
}

void MacDiagnostic::info_update()
{
//    qInfo()<<"MacDiagnostic::info_update ";

    QJsonObject proc_info;
    QJsonObject sys_info;
    QJsonObject cli_info;
    QJsonObject full_info;


    sys_info = get_sys_info();
    sys_info.insert("mac", s_mac);

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
    int mem = obj["total"].toString().toUInt();;

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

QJsonObject MacDiagnostic::get_sys_info()
{
//    qInfo()<<"MacDiagnostic::get_sys_info ";
    QJsonObject obj_sys_data, obj_cpu, obj_memory;

    //get memory data
    //total mem
    int mib[2];
    int64_t physical_memory;
    mib[0] = CTL_HW;
    mib[1] = HW_MEMSIZE;
    size_t length = sizeof(int64_t);
    sysctl(mib, 2, &physical_memory, &length, NULL, 0);



    //use mem

    vm_size_t page_size;
    mach_port_t mach_port;
    mach_msg_type_number_t count;
    vm_statistics64_data_t vm_stats;
    long long free_memory = 0;
//    long long used_memory = 0;

    mach_port = mach_host_self();
    count = sizeof(vm_stats) / sizeof(natural_t);
    if (KERN_SUCCESS == host_page_size(mach_port, &page_size) &&
        KERN_SUCCESS == host_statistics64(mach_port, HOST_VM_INFO,
                                        (host_info64_t)&vm_stats, &count))
    {
        free_memory = (int64_t)vm_stats.free_count * (int64_t)page_size;

//        used_memory = ((int64_t)vm_stats.active_count +
//                                 (int64_t)vm_stats.inactive_count +
//                                 (int64_t)vm_stats.wire_count) *  (int64_t)page_size;
    }

    QString memtotal = QString::number(physical_memory/1024);
    QString memfree  = QString::number(free_memory/1024);
//    QString memused = get_memory_string(used_memory/1024);

    QString memory_used = QString::number((physical_memory - free_memory) *100 / physical_memory);

    obj_memory.insert("total", memtotal);
    obj_memory.insert("free", memfree);
    obj_memory.insert("load", memory_used);

    //get cpu info

    host_cpu_load_info_data_t cpuinfo;
    float res = -1.0f;
    mach_msg_type_number_t counts = HOST_CPU_LOAD_INFO_COUNT;
    if (host_statistics(mach_host_self(), HOST_CPU_LOAD_INFO, (host_info_t)&cpuinfo, &count) == KERN_SUCCESS)
    {
       unsigned long long totalTicks = 0;
       for(int i=0; i<CPU_STATE_MAX; i++) totalTicks += cpuinfo.cpu_ticks[i];
       res =  calculate_cpu_load(cpuinfo.cpu_ticks[CPU_STATE_IDLE], totalTicks);
    }
    obj_cpu.insert("load", int(res*100));

    //get uptime system

    enum { NANOSECONDS_IN_SEC = 1000 * 1000 * 1000 };
    double multiply = 0;
    QString uptime = "00:00:00";
    if (multiply == 0)
    {
        mach_timebase_info_data_t s_timebase_info;
        if(mach_timebase_info(&s_timebase_info) == KERN_SUCCESS)
        {
            // multiply to get value in the nano seconds
            multiply = (double)s_timebase_info.numer / (double)s_timebase_info.denom;
            // multiply to get value in the seconds
            multiply /= NANOSECONDS_IN_SEC;
            uptime = get_uptime_string(mach_absolute_time() * multiply);
        }
    }


//    //-------

    obj_sys_data.insert("uptime", uptime);
    obj_sys_data.insert("CPU", obj_cpu);
    obj_sys_data.insert("memory", obj_memory);

    return obj_sys_data;
}

float MacDiagnostic::calculate_cpu_load(unsigned long long idleTicks, unsigned long long totalTicks)
{
//    qInfo()<<"MacDiagnostic::calculate_cpu_load ";
    unsigned long long totalTicksSinceLastTime = totalTicks-_previousTotalTicks;
    unsigned long long idleTicksSinceLastTime  = idleTicks-_previousIdleTicks;
    float ret = 1.0f-((totalTicksSinceLastTime > 0) ? ((float)idleTicksSinceLastTime)/totalTicksSinceLastTime : 0);
    _previousTotalTicks = totalTicks;
    _previousIdleTicks  = idleTicks;
    return ret;

}

/// ---------------------------------------------------------------
///        Process info
/// ---------------------------------------------------------------
QJsonObject MacDiagnostic::get_process_info(int totalRam)
{
//    qInfo()<<"MacDiagnostic::get_process_info ";
    QJsonObject process_info;

    QProcess proc;
    QString program = "ps";
    QStringList arguments;
    arguments << "-axm" << "-o" << "rss,pid,etime,comm";
    proc.start(program, arguments);
    proc.waitForFinished(1000);
    QString res = proc.readAll();

    QString string="";

    for(QString str : res.split("\n"))
    {
        if(str.contains("cellframe-node"))
        {
            string = str;
            break;
        }
    }

    QString status = "Offline";
    QString node_dir = s_nodeDataPath;

    QString log_size, db_size, chain_size;
    log_size   = QString::number(get_file_size("log", node_dir) / 1024);
    db_size    = QString::number(get_file_size("DB", node_dir) / 1024);
    chain_size = QString::number(get_file_size("chain", node_dir) / 1024);

    if(log_size.isEmpty()) log_size = "0";
    if(db_size.isEmpty()) db_size = "0";
    if(chain_size.isEmpty()) chain_size = "0";

    process_info.insert("log_size", log_size);
    process_info.insert("DB_size", db_size);
    process_info.insert("chain_size", chain_size);


    if(string.isEmpty())
    {
        process_info.insert("memory_use","0");
        process_info.insert("memory_use_value","0 Kb");
        process_info.insert("uptime","00:00:00");
    }
    else
    {
        status = "Online";

        int pid, rss;
        QString uptime, path;

        QStringList parseString = string.split(" ");
        parseString.removeAll("");

        rss = parseString[0].toInt();
        pid = parseString[1].toInt();
        uptime = parseString[2];
        path = parseString[3];

        QString memory_use_value = QString::number(rss);
        int precentUseRss = rss *100 / totalRam;

        process_info.insert("memory_use",precentUseRss);
        process_info.insert("memory_use_value",memory_use_value);
        process_info.insert("uptime",uptime);
        process_info.insert("name","cellframe-node");
        process_info.insert("path", path);
    }

    s_node_status = status == "Online" ? true : false;

    process_info.insert("status", status);


   return process_info;
}
