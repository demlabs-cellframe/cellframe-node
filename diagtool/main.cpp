#include <QCoreApplication>
#include "DiagnosticWorker.h"

int main(int argc, char *argv[])
{
    qSetMessagePattern("%{type} %{if-category}%{category}: %{endif}%{function}: %{message}");
    QCoreApplication a(argc, argv);
    DiagnosticWorker * wrkr = new DiagnosticWorker();

    return a.exec();
}
