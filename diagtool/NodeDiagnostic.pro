QT -= gui
QT += core network

CONFIG += c++17 console
CONFIG -= app_bundle

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

#LIBS += -L$$NODE_BUILD_PATH/dap-sdk/core/ -ldap_core
#include (../dap-sdk/core/libdap.pri)

SOURCES += \
        AbstractDiagnostic.cpp \
        DiagnosticWorker.cpp \
        main.cpp
HEADERS += \
    AbstractDiagnostic.h \
    DiagnosticWorker.h

win32 {
    DEFINES += CLI_PATH=\\\"cellframe-node-cli.exe\\\"
    HEADERS += WinDiagnostic.h
    SOURCES += WinDiagnostic.cpp
}

mac {
    DEFINES += CLI_PATH=\\\"./cellframe-node-cli\\\"
    HEADERS += MacDiagnostic.h
    SOURCES += MacDiagnostic.cpp
}

else: !win32 {
    DEFINES += CLI_PATH=\\\"/opt/cellframe-node/bin/cellframe-node-cli\\\"
    HEADERS += LinuxDiagnostic.h
    SOURCES += LinuxDiagnostic.cpp
}

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target
