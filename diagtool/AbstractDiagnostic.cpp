#include "AbstractDiagnostic.h"

#ifdef Q_OS_LINUX

#elif defined(Q_OS_WIN)
#include "registry.h"
#elif defined(Q_OS_MACOS)
#include "dap_common.h"
#endif

AbstractDiagnostic::AbstractDiagnostic(QObject *parent)
    :QObject(parent)
{
#ifdef Q_OS_LINUX
    s_nodeDataPath = "/opt/cellframe-node";
#elif defined(Q_OS_WIN)
    s_nodeDataPath = QString("%1/cellframe-node").arg(regGetUsrPath());
#elif defined(Q_OS_MACOS)
    s_nodeDataPath = QString("/Users/%1/Applications/Cellframe.app/Contents/Resources/").arg(getenv("USER"));
#endif
    s_timer_update = new QTimer();
    s_mac = get_mac();
}

AbstractDiagnostic::~AbstractDiagnostic()
{
    delete s_timer_update;
}

void AbstractDiagnostic::set_timeout(int timeout){
    s_timer_update->stop();
    s_timeout = timeout;
    s_timer_update->start(s_timeout);
}

void AbstractDiagnostic::start_diagnostic()
{
    s_timer_update->start(s_timeout);
}

void AbstractDiagnostic::stop_diagnostic()
{
    s_timer_update->stop();
}

QJsonValue AbstractDiagnostic::get_mac()
{
    QString MAC{"unknown"};
    foreach(QNetworkInterface netInterface, QNetworkInterface::allInterfaces())
    {
        // Return only the first non-loopback MAC Address
        if (!(netInterface.flags() & QNetworkInterface::IsLoopBack))
        {
            qDebug()<<netInterface.hardwareAddress();
            if(!netInterface.hardwareAddress().isEmpty())
            {
                MAC = netInterface.hardwareAddress();
                break;
            }
        }
    }

    return MAC;
}

QString AbstractDiagnostic::get_uptime_string(long sec)
{
    QTime time(0, 0);
    time = time.addSecs(sec);
    int fullHours = sec/3600;

    QString uptime = QString("%1:").arg(fullHours) + time.toString("mm:ss");

    return uptime;
}

quint64 AbstractDiagnostic::get_file_size (QString flag, QString path ) {

    if(flag == "log")
        path += "/var/log";
    else
    if (flag == "DB")
        path += "/var/lib/global_db";
    else
    if (flag == "chain")
        path += "/var/lib/network";
    else
        path += "";

    QDir currentFolder( path );

    quint64 totalsize = 0;

    currentFolder.setFilter( QDir::Dirs | QDir::Files | QDir::NoSymLinks );
    currentFolder.setSorting( QDir::Name );

    QFileInfoList folderitems( currentFolder.entryInfoList() );

    foreach ( QFileInfo i, folderitems ) {
        QString iname( i.fileName() );
        if ( iname == "." || iname == ".." || iname.isEmpty() )
            continue;
        if(flag == "log" && i.suffix() != "log" && !i.isDir())
            continue;
        else
        if(flag == "DB" && (i.suffix() != "dat" && !i.suffix().isEmpty()) && !i.isDir())
            continue;
        else
        if(flag == "chain" && i.suffix() != "dchaincell" && !i.isDir())
            continue;

        if ( i.isDir() )
            totalsize += get_file_size("", path+"/"+iname);
        else
            totalsize += i.size();
    }

    return totalsize;
}

QString AbstractDiagnostic::get_memory_string(long num)
{
    QString result = QString::number(num);
    return result;

    int gb = (num / 1024) / 1024;
    int mb = (num-gb*1024*1024) /1024;
    int kb = (num - (gb*1024*1024+mb*1024));
    if (gb > 0)
       result = QString::number(gb) + QString(" Gb ");
    else
       result = QString("");
    if (mb > 0)
       result += QString::number(mb) + QString(" Mb ");
    if (kb > 0)
       result += QString::number(kb) + QString(" Kb ");

    return result;
}

QJsonObject AbstractDiagnostic::roles_processing()
{
    QJsonObject rolesObject;

    QDir currentFolder(s_nodeDataPath + "/etc/network");

    currentFolder.setFilter( QDir::Dirs | QDir::Files | QDir::NoSymLinks );
    currentFolder.setSorting( QDir::Name );

    QFileInfoList folderitems( currentFolder.entryInfoList() );

    foreach ( QFileInfo i, folderitems ) {
        QString iname( i.fileName() );
        if ( iname == "." || iname == ".." || iname.isEmpty() )
            continue;
        if(i.suffix() == "cfg" && !i.isDir())
        {
            QSettings config(i.absoluteFilePath(), QSettings::IniFormat);

            rolesObject.insert(i.completeBaseName(), config.value("node-role", "unknown").toString());
        }
    }

    return rolesObject;
}

/// ---------------------------------------------------------------
///        Cli info
/// ---------------------------------------------------------------
QJsonObject AbstractDiagnostic::get_cli_info()
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
        dataObj.insert("nodelist"  , get_nodelist(net));

        netObj.insert(net, dataObj);
    }

    return netObj;
}

QStringList AbstractDiagnostic::get_networks()
{
    QProcess proc;
    proc.start(QString(CLI_PATH), QStringList()<<"net"<<"list");
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

QJsonObject AbstractDiagnostic::get_net_info(QString net)
{
    QProcess proc;
    proc.start(QString(CLI_PATH),
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
    resultObj.insert("balancer", get_balancer_links(net));

    return resultObj;
}

QJsonObject AbstractDiagnostic::get_mempool_count(QString net)
{
    QProcess proc;
    proc.start(QString(CLI_PATH),
               QStringList()<<"mempool_list"<<"-net"<<QString(net));
    proc.waitForFinished(5000);
    QString result = proc.readAll();

    QRegularExpression rx(R"(\.(.+): Total (.+) records)");

    ///TODO: bug in requests. Always returns both chains
//    QRegularExpressionMatch match = rx.match(result);
//    if (!match.hasMatch()) {
//        return {};
//    }

//    proc.start(QString(CLI_PATH),
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

QJsonObject AbstractDiagnostic::get_ledger_count(QString net)
{
    //TODO: legder tx -all -net   NOT WORKING
    return {};
}

QJsonObject AbstractDiagnostic::get_blocks_count(QString net)
{
    QProcess proc;
    proc.start(QString(CLI_PATH),
               QStringList()<<"block"<<"list"<<"-net"<<QString(net) <<"-chain" << "main");
    proc.waitForFinished(5000);
    QString result = proc.readAll();

    QRegularExpression rx(R"(\.(.+): Have (.+) blocks)");
    QRegularExpression rx_creation(R"(.*(0x.*): ts_create=(.*))");
    

    QRegularExpressionMatch match = rx.match(result);

    if (!match.hasMatch()) {
        return {};
    }

    QJsonObject resultObj;
    resultObj.insert(match.captured(1), match.captured(2));

    
    QRegularExpressionMatchIterator matchItr = rx_creation.globalMatch(result);
    
    //rewind to end
    QRegularExpressionMatch match_date;
    
    while (matchItr.hasNext()){ 
        match_date = matchItr.next();
    }

    QJsonObject last_block;
    last_block.insert("hash", match_date.captured(1));
    QDateTime dt = QDateTime::fromString(match_date.captured(2));
    qint64 timestamp = dt.toSecsSinceEpoch();
    last_block.insert("timestamp", QString::number(timestamp));

    resultObj.insert("last_block", last_block);
    qDebug() << resultObj;

    return resultObj;

}

QJsonObject AbstractDiagnostic::get_events_count(QString net)
{
    QProcess proc;
    proc.start(QString(CLI_PATH),
               QStringList()<<"dag"<<"event"<<"list"<<"-net"<<QString(net) <<"-chain" << "zerochain");
    proc.waitForFinished(5000);
    QString result = proc.readAll();

    QRegularExpression rx_event_count(R"(\.(.+) have total (.+) events)");
    QRegularExpression rx_creation(R"(.*(0x.*): ts_create=(.*))");

    QRegularExpressionMatch match = rx_event_count.match(result);
        
    if (!match.hasMatch()) {
        return {};
    }

    QJsonObject resultObj;
    
    resultObj.insert(match.captured(1), match.captured(2));

    QRegularExpressionMatchIterator matchItr = rx_creation.globalMatch(result);
    
    //rewind to end
    QRegularExpressionMatch match_date;
    
    while (matchItr.hasNext()){ 
        match_date = matchItr.next();
    }

    QJsonObject last_block;
    last_block.insert("hash", match_date.captured(1));
    QDateTime dt = QDateTime::fromString(match_date.captured(2));
    qint64 timestamp = dt.toSecsSinceEpoch();
    last_block.insert("timestamp", QString::number(timestamp));

    resultObj.insert("last_event", last_block);
    qDebug() << resultObj;

    
    return resultObj;
}


QJsonArray AbstractDiagnostic::get_nodelist(QString net)
{
    QProcess proc;
    proc.start(QString(CLI_PATH),
               QStringList()<<"node"<<"dump"<<"-net"<<QString(net));
    proc.waitForFinished(5000);
    QString result = proc.readAll();

    QJsonArray res;
    for (auto l : result.split("\n"))
        res.push_back(QJsonValue(l));

    return res;
}

QJsonObject AbstractDiagnostic::get_balancer_links(QString net)
{
    QProcess proc;
    proc.start(QString(CLI_PATH),
                QStringList()<<"node"<<"connections"<<"-net"<<QString(net));


    proc.waitForFinished(5000);
    QString result = proc.readAll();

    QJsonObject resultObj;
    for (auto line : result.split("\n"))
    {
        if (line.split(":").length() < 2)
            continue;

        if(line.startsWith("Uplinks:"))
            resultObj.insert("uplinks", line.split(":")[1].trimmed());
        if(line.startsWith("Downlinks:"))
            resultObj.insert("downlinks", line.split(":")[1].trimmed());
    }

    qDebug() << resultObj;

    return resultObj;
}
