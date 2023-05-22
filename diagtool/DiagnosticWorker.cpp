#include "DiagnosticWorker.h"
#include <QNetworkAccessManager>
#include <QHttpPart>
#include <QHttpMultiPart>
#include <QNetworkReply>
static QString group = "global.users.statistic";

DiagnosticWorker::DiagnosticWorker(QObject * parent)
    : QObject{parent}
{
    s_uptime_timer = new QTimer(this);
    connect(s_uptime_timer, &QTimer::timeout,
            this, &DiagnosticWorker::slot_uptime,
            Qt::QueuedConnection);
    s_uptime_timer->start(1000);

    s_elapsed_timer = new QElapsedTimer();
    s_elapsed_timer->start();

    m_diagnostic = new LinuxDiagnostic();

    connect(m_diagnostic, &AbstractDiagnostic::data_updated,
            this, &DiagnosticWorker::slot_diagnostic_data,
            Qt::QueuedConnection);

    m_diagnostic->start_diagnostic();
    m_diagnostic->set_timeout(30000); //3minutes
}
DiagnosticWorker::~DiagnosticWorker()
{
    delete s_uptime_timer;
    delete s_elapsed_timer;
    delete m_diagnostic;
}

void DiagnosticWorker::slot_diagnostic_data(QJsonDocument data)
{
    //insert uptime dashboard and more into system info
    QJsonObject obj = data.object();
    QJsonObject system = data["system"].toObject();
    QJsonObject proc = data["process"].toObject();

    system.insert("uptime_dashboard", s_uptime);
    system.insert("time_update_unix", QDateTime::currentSecsSinceEpoch());

//    system.insert("time_update", QDateTime::currentDateTime().toString("dd.MM.yyyy hh:mm"));
    obj.insert("system",system);

    if(proc["status"].toString() == "Offline") //if node offline - clear version
        m_node_version = "";
    else
    if(m_node_version.isEmpty())
    {
        QProcess proc;
        proc.start(QString("/opt/cellframe-node/bin/cellframe-node-cli"), QStringList()<<"version");
        proc.waitForFinished(5000);
        QString result = proc.readAll();
        if(result.contains("version"))
        {
            result = result.split("version")[1];
            m_node_version = result.split('\n', QString::SkipEmptyParts).first().trimmed();
        }
    }

    proc.insert("version", m_node_version);
    obj.insert("process",proc);
    data.setObject(obj);

    write_data(data);
}

void DiagnosticWorker::slot_uptime()
{
    s_uptime = m_diagnostic->get_uptime_string(s_elapsed_timer->elapsed()/1000);
}

void DiagnosticWorker::write_data(QJsonDocument data)
{
    QString urls = "https://engine-minkowski.kelvpn.com/diag_report";
    QUrl url = QUrl(urls);

    QNetworkAccessManager * mgr = new QNetworkAccessManager(this);

    connect(mgr, &QNetworkAccessManager::finished, this, [=](QNetworkReply*r) {qDebug() << "data sent " << urls << " " << r->error();});
    connect(mgr,SIGNAL(finished(QNetworkReply*)),mgr,  SLOT(deleteLater()));

    auto req = QNetworkRequest(url);
    req.setHeader(QNetworkRequest::ContentTypeHeader,"application/x-www-form-urlencoded");
    QString key = m_diagnostic->s_mac.toString();
    QJsonObject obj = data.object();
    obj.insert("mac",key);
    data.setObject(obj);
    mgr->post(req, data.toJson());

    //diabled GDB write for now cause of big load of neteork in this case

    /*
    QString key = m_diagnostic->s_mac.toString();

    QProcess proc;
    QString program = "/opt/cellframe-node/bin/cellframe-node-cli";
    QStringList arguments;
    arguments << "global_db" << "write" << "-group" << QString(group)
              << "-key" << QString(key) << "-value" << QByteArray(data.toJson());
    proc.start(program, arguments);
    proc.waitForFinished(5000);
    QString res = proc.readAll();

    qDebug()<<res;*/
}
