#ifdef __APPLE__

#include "service.h"
#include "../commands/abstractcommand.h"
#include "macos_auth.h"

bool CServiceControl::enable()
{
    char *args[] = {"/bin/launchctl","load", "-w", "/Library/LaunchDaemons/com.demlabs.cellframe-node.plist", NULL};
    int res = callSec("/usr/bin/sudo", args);
    return res == 0 ? true : false;
}

bool CServiceControl::disable()
{
    char *args[] = {"/bin/launchctl", "unload", "-w", "/Library/LaunchDaemons/com.demlabs.cellframe-node.plist", NULL};
    int res = callSec("/usr/bin/sudo", args);
    return res == 0 ? true : false;
}

unsigned int CServiceControl::serviceStatus()
{
    unsigned int status = 0;
    std::string cmd = std::string();
    int res = std::system("launchctl print system/com.demlabs.cellframe-node > /dev/null");
    if (res == 0)
    {
        status |= SERVICE_ENABLED;
    }

    cmd = "pgrep -x cellframe-node > /dev/null";
    res = std::system(cmd.c_str());

    if (res == 0)
    {
        status |= PROCESS_RUNNING;
    }

    return (unsigned int)status;
}

bool CServiceControl::start()
{
    return enable();
}

bool CServiceControl::stop()
{
    return disable();
}

bool CServiceControl::restart()
{
    stop();
    start();
    return true;
}    

#endif
