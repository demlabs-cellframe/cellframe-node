#include <QCoreApplication>
#include "DiagnosticWorker.h"

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);
    DiagnosticWorker * wrkr = new DiagnosticWorker();

    return a.exec();
}
