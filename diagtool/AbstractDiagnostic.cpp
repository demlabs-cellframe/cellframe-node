#include "AbstractDiagnostic.h"

AbstractDiagnostic::AbstractDiagnostic(QObject *parent)
    :QObject(parent)
{
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

    QDir currentFolder("/opt/cellframe-node/etc/network");

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
