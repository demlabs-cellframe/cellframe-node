#include "LinuxDiagnostic.h"
#include <sys/vfs.h>
#include <sys/stat.h>

LinuxDiagnostic::LinuxDiagnostic(AbstractDiagnostic *parent)
    : AbstractDiagnostic{parent}
{
    connect(s_timer_update, &QTimer::timeout,
            this, &LinuxDiagnostic::info_update,
            Qt::QueuedConnection);
}


void LinuxDiagnostic::info_update(){

    // QSettings config("/opt/cellframe-node/etc/cellframe-node.cfg",
    //                    QSettings::IniFormat);

    // bool isEnabled = config.value("Diagnostic/enabled",false).toBool();

    if(true) //isEnabled
    {
        QJsonObject proc_info;
        QJsonObject sys_info;
        QJsonObject cli_info;
        QJsonObject full_info;

        sys_info = get_sys_info();
        sys_info.insert("mac", s_mac);
        sys_info.insert("disk", get_disk_info());

        QFile file("/opt/cellframe-node/etc/diagdata.json");
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
        int mem = obj["total"].toInt();

        proc_info = get_process_info(get_pid(), mem);
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
}

QJsonObject LinuxDiagnostic::get_disk_info()
{
    QString path = "/opt/cellframe-node";

    QString apath = QDir(path).absolutePath();

    struct statfs stfs;

    if (::statfs(apath.toLocal8Bit(),&stfs) == -1)
    {
        QJsonObject diskObj;
        diskObj.insert("total",     -1);
        diskObj.insert("free",      -1);
        diskObj.insert("available", -1);
        diskObj.insert("used",      -1);

        return diskObj;
    }

    quint64 total     = stfs.f_blocks * stfs.f_bsize;
    quint64 free      = stfs.f_bfree  * stfs.f_bsize;
    quint64 available = stfs.f_bavail * stfs.f_bsize;
    quint64 used      = total - free;

    QJsonObject diskObj;
    diskObj.insert("total",     QString::number(total));
    diskObj.insert("free",      QString::number(free));
    diskObj.insert("available", QString::number(available));
    diskObj.insert("used",      QString::number(used));

    return diskObj;
}


long LinuxDiagnostic::get_pid()
{
    long pid;
    QString path = QString("%1/var/run/cellframe-node.pid").arg("/opt/cellframe-node/");

    QFile file(path);
    QByteArray data;
    if (!file.open(QIODevice::ReadOnly))
        return 0;
    data = file.readAll();
    pid = data.toLong();

    return pid;
}

/// ---------------------------------------------------------------
///        Sys info
/// ---------------------------------------------------------------
QJsonObject LinuxDiagnostic::get_sys_info()
{
    QJsonObject obj_sys_data, obj_cpu, obj_memory;

    ifstream stat_stream;
    string buff;

    //-------

    //get cpu info
    size_t idle_time, total_time;
    get_cpu_times(idle_time, total_time);

    const float idle_time_delta = idle_time - previous_idle_time;
    const float total_time_delta = total_time - previous_total_time;
    const float utilization = 100.0 * (1.0 - idle_time_delta / total_time_delta);

    previous_idle_time = idle_time;
    previous_total_time = total_time;

    stat_stream.open("/proc/cpuinfo");
    for(int i = 0; i < 16;i++) stat_stream >> buff;
    getline(stat_stream,buff);

    obj_cpu.insert("load", (int)utilization);
    obj_cpu.insert("model", QString::fromStdString(buff));
    stat_stream.close();

    //get uptime system
    stat_stream.open("/proc/uptime");
    stat_stream >> buff;
    QString uptime = get_uptime_string(atoi(buff.c_str()));
    stat_stream.close();

    //get memory data
    stat_stream.open("/proc/meminfo");
    QString memory, memory_used, memory_free;
    string total,free,available;
    stat_stream >> buff >> total >> buff >> buff >> free >> buff >> buff >> available;
    stat_stream.close();

    int total_value = atoi(total.c_str());
    int available_value = atoi(available.c_str());

    memory = get_memory_string(total_value);
    memory_used = QString::number((total_value - available_value) *100 / total_value);
    memory_free = get_memory_string(available_value);

//    obj_memory.insert("total", memory);
    obj_memory.insert("total", total_value);
//    obj_memory.insert("total_value", total_value);
    obj_memory.insert("free", memory_free);
    obj_memory.insert("load", memory_used);

    //-------

    obj_sys_data.insert("uptime", uptime);
    obj_sys_data.insert("CPU", obj_cpu);
    obj_sys_data.insert("memory", obj_memory);

    return obj_sys_data;
}

QString LinuxDiagnostic::get_running(char* pid)
{
    char tbuf[32];
    char *cp;
    int fd;
    char c;

    sprintf(tbuf, "/proc/%s/stat", pid);
    fd = open(tbuf, O_RDONLY, 0);
    if (fd == -1) return QString("no open");

    memset(tbuf, '\0', sizeof tbuf); // didn't feel like checking read()
    read(fd, tbuf, sizeof tbuf - 1);

    cp = strrchr(tbuf, ')');
    if(!cp) return QString("no read");

    c = cp[2];
    close(fd);
    qDebug()<<c;

    if (c=='R') {
      return "running";
    }else
    if (c=='D') {
      return "blocked";
    }
    return QString("blocked");
}


QString LinuxDiagnostic::get_proc_path(long pid) // work with root
{
    char exePath[PATH_MAX];
    char arg1[20];
    sprintf( arg1, "/proc/%ld/exe", pid );
    ssize_t len = ::readlink(arg1, exePath, sizeof(exePath));
    if (len == -1 || len == sizeof(exePath))
        len = 0;
    exePath[len] = '\0';
    return QString::fromUtf8(exePath);
}

std::vector<size_t> LinuxDiagnostic::get_cpu_times() {
    std::ifstream proc_stat("/proc/stat");
    proc_stat.ignore(5, ' '); // Skip the 'cpu' prefix.
    std::vector<size_t> times;
    for (size_t time; proc_stat >> time; times.push_back(time));
    return times;
}

bool LinuxDiagnostic::get_cpu_times(size_t &idle_time, size_t &total_time) {
    const std::vector<size_t> cpu_times = get_cpu_times();
    if (cpu_times.size() < 4)
        return false;
    idle_time = cpu_times[3];
    total_time = std::accumulate(cpu_times.begin(), cpu_times.end(), 0);
    return true;
}


/// ---------------------------------------------------------------
///        Process info
/// ---------------------------------------------------------------
QJsonObject LinuxDiagnostic::get_process_info(long proc_id, int totalRam)
{
   using std::ios_base;
   using std::ifstream;
   using std::string;

//   vm_usage     = 0.0;
//   resident_set = 0.0;

   // 'file' stat seems to give the most reliable results
   char arg1[20];
   sprintf( arg1, "/proc/%ld/stat", proc_id );
   ifstream stat_stream(arg1,ios_base::in);

   // dummy vars for leading entries in stat that we don't care about
   //
   string pid, comm, state, ppid, pgrp, session, tty_nr;
   string tpgid, flags, minflt, cminflt, majflt, cmajflt;
   string utime, stime, cutime, cstime, priority, nice;
   string O, itrealvalue;

   // the two fields we want
   //
   unsigned long vsize;
   long rss;
   double starttime;

   stat_stream >> pid >> comm >> state >> ppid >> pgrp >> session >> tty_nr
               >> tpgid >> flags >> minflt >> cminflt >> majflt >> cmajflt
               >> utime >> stime >> cutime >> cstime >> priority >> nice
               >> O >> itrealvalue >> starttime >> vsize >> rss; // don't care about the rest

   stat_stream.close();

   long page_size_kb = sysconf(_SC_PAGE_SIZE) / 1024; // in case x86-64 is configured to use 2MB pages
//   vm_usage     = (vsize/1024.0);
   long resident_set = rss * page_size_kb;

   int precentUseRss = (resident_set * 100) / totalRam;

   QProcess proc;
   QString program = "ps";
   QStringList arguments;
   arguments << "-p" << pid.c_str() << "-o" << "etimes";
   proc.start(program, arguments);
   proc.waitForFinished(1000);
   QString res = proc.readAll();

   static QRegularExpression rx(R"([0-9]+)");

   QJsonObject process_info;
   QString status = "Offline";
   process_info.insert("status", "Offline");

   QString node_dir = "/opt/cellframe-node/";

   QString log_size, db_size, chain_size;
   log_size = get_memory_string(get_file_size("log", node_dir) / 1024);
   db_size = get_memory_string(get_file_size("DB", node_dir) / 1024);
   chain_size = get_memory_string(get_file_size("chain", node_dir) / 1024);

   if(log_size.isEmpty()) log_size = "0";
   if(db_size.isEmpty()) db_size = "0";
   if(chain_size.isEmpty()) chain_size = "0";

   process_info.insert("log_size", log_size);
   process_info.insert("DB_size", db_size);
   process_info.insert("chain_size", chain_size);

   if(QString::fromLocal8Bit(comm.c_str()).contains("cellframe-node"))
   {
       int uptime_sec = rx.match(res).captured(0).toInt();

       QString uptime= get_uptime_string(uptime_sec);

       QString memory_use_value = get_memory_string(resident_set);

//       process_info.insert("PPID",QString::fromLocal8Bit(ppid.c_str()));
//       process_info.insert("priory",QString::fromLocal8Bit(priority.c_str()));
//       process_info.insert("start_time",QString::number(((starttime/100)/60)));
       process_info.insert("memory_use",precentUseRss);
       process_info.insert("memory_use_value",memory_use_value);
       process_info.insert("uptime",uptime);
       process_info.insert("name","cellframe-node");

       status = "Online";
   }

   if(status == "Offline")
   {
       process_info.insert("memory_use","0");
       process_info.insert("memory_use_value","0 Kb");
       process_info.insert("uptime","00:00:00");
   }

   s_node_status = status == "Online" ? true : false;

   process_info.insert("status", status);

   return process_info;
}

/// ---------------------------------------------------------------
///        Cli info
/// ---------------------------------------------------------------
QJsonObject LinuxDiagnostic::get_cli_info()
{
    QStringList networks = get_networks();

    QJsonObject netObj;

    for(QString net : networks)
    {
        QJsonObject dataObj;

        dataObj.insert("net_info", get_net_info(net));
        dataObj.insert("mempool" , get_mempool_count(net));
//        dataObj.insert("ledger"  , get_ledger_count(net));
        dataObj.insert("blocks"  , get_blocks_count(net));
        dataObj.insert("events"  , get_events_count(net));

        netObj.insert(net, dataObj);
    }

    return netObj;
}

QStringList LinuxDiagnostic::get_networks()
{
    QProcess proc;
    proc.start(QString("/opt/cellframe-node/bin/cellframe-node-cli"), QStringList()<<"net"<<"list");
    proc.waitForFinished(5000);
    QString result = proc.readAll();

    QStringList listNetworks;
    result.remove(' ');
    result.remove("\r");
    result.remove("\n");
    result.remove("Networks:");
    if(!(result.isEmpty() || result.isNull() || result.contains('\'') || result.contains("error") || result.contains("Error") || result.contains("err")))
    {
        listNetworks = result.split("\t", QString::SkipEmptyParts);
    }

    return listNetworks;
}

QJsonObject LinuxDiagnostic::get_net_info(QString net)
{
    QProcess proc;
    proc.start(QString("/opt/cellframe-node/bin/cellframe-node-cli"),
               QStringList()<<"net"<<"-net"<<QString(net)<<"get"<<"status");
    proc.waitForFinished(5000);
    QString result = proc.readAll();

    // ---------- State & TargetState ----------------

    QRegularExpression rx(R"***(^Network "(\S+)" has state (\S+) \(target state (\S*)\), .*cur node address ([A-F0-9]{4}::[A-F0-9]{4}::[A-F0-9]{4}::[A-F0-9]{4}))***");
    QRegularExpressionMatch match = rx.match(result);
    if (!match.hasMatch()) {
        return {};
    }

    QJsonObject resultObj({
                                {"state"              , match.captured(2)},
                                {"target_state"       , match.captured(3)},
                                {"node_address"       , match.captured(4)}
                            });

    // ---------- Links count ----------------
    QRegularExpression rxLinks(R"(\), active links (\d+) from (\d+),)");
    match = rxLinks.match(result);
    if (!match.hasMatch()) {
        return resultObj;
    }

    resultObj.insert("active_links_count", match.captured(1));
    resultObj.insert("links_count"       , match.captured(2));

    return resultObj;
}

QJsonObject LinuxDiagnostic::get_mempool_count(QString net)
{
    QProcess proc;
    proc.start(QString("/opt/cellframe-node/bin/cellframe-node-cli"),
               QStringList()<<"mempool_list"<<"-net"<<QString(net));
    proc.waitForFinished(5000);
    QString result = proc.readAll();

    QRegularExpression rx(R"(\.(.+): Total (.+) records)");

    ///TODO: bug in requests. Always returns both chains
//    QRegularExpressionMatch match = rx.match(result);
//    if (!match.hasMatch()) {
//        return {};
//    }

//    proc.start(QString("/opt/cellframe-node/bin/cellframe-node-cli"),
//               QStringList()<<"mempool_list"<<"-net"<<QString(net)<<"-chain"<<"zero");
//    proc.waitForFinished(5000);
//    result = proc.readAll();

    QJsonObject resultObj;

    QRegularExpressionMatchIterator matchItr = rx.globalMatch(result);

    while (matchItr.hasNext())
    {
        QRegularExpressionMatch match = matchItr.next();
        resultObj.insert(match.captured(1), match.captured(2));
    }

    return resultObj;
}

QJsonObject LinuxDiagnostic::get_ledger_count(QString net)
{
    //TODO: legder tx -all -net   NOT WORKING
    return {};
}

QJsonObject LinuxDiagnostic::get_blocks_count(QString net)
{
    QProcess proc;
    proc.start(QString("/opt/cellframe-node/bin/cellframe-node-cli"),
               QStringList()<<"block"<<"list"<<"-net"<<QString(net) <<"-chain" << "main");
    proc.waitForFinished(5000);
    QString result = proc.readAll();

    QRegularExpression rx(R"(\.(.+): Have (.+) blocks)");
    QRegularExpressionMatch match = rx.match(result);
    if (!match.hasMatch()) {
        return {};
    }

    QJsonObject resultObj;
    resultObj.insert(match.captured(1), match.captured(2));

    return resultObj;

}

QJsonObject LinuxDiagnostic::get_events_count(QString net)
{
    QProcess proc;
    proc.start(QString("/opt/cellframe-node/bin/cellframe-node-cli"),
               QStringList()<<"dag"<<"event"<<"list"<<"-net"<<QString(net) <<"-chain" << "zerochain");
    proc.waitForFinished(5000);
    QString result = proc.readAll();

    QRegularExpression rx(R"(\.(.+) have total (.+) events)");
    QRegularExpressionMatch match = rx.match(result);
    if (!match.hasMatch()) {
        return {};
    }

    QJsonObject resultObj;
    resultObj.insert(match.captured(1), match.captured(2));

    return resultObj;
}


