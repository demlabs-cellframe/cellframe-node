#ifdef __APPLE__

#include "service.h"
#include "../commands/abstractcommand.h"

bool CServiceControl::enable()
{
    //starts too
    int res = std::system("launchctl load -w /Library/LaunchDaemons/com.demlabs.cellframe-node.plist");
    return res == 0 ? true : false;
}

bool CServiceControl::disable()
{
    //stops too
    int res = std::system("launchctl unload -w /Library/LaunchDaemons/com.demlabs.cellframe-node.plist");
    return res == 0 ? true : false;
}

EServiceStatus CServiceControl::serviceStatus()
{
    std::string cmd = std::string();
    int res = std::system("launchctl list com.demlabs.cellframe-node");
    return res == 0 ? ENABLED : DISABLED;
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