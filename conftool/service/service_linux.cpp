 #ifdef __linux__ 

#include "service.h"
#include "../commands/abstractcommand.h"

bool CServiceControl::enable(){
    std::string cmd = "systemctl enable " + (std::filesystem::path{variable_storage["CONFIGS_PATH"]}/"share"/"cellframe-node.service > /dev/null").string();
    int res = std::system(cmd.c_str());
    
    return res == 0 ? true : false;
}

bool CServiceControl::disable()
{
    std::string cmd = "systemctl disable cellframe-node.service > /dev/null";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

unsigned int CServiceControl::serviceStatus()
{
    unsigned int status = 0;
    
    std::string cmd = "systemctl is-enabled cellframe-node.service > /dev/null";
    int res = std::system(cmd.c_str());
    
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
    std::string cmd = "systemctl start cellframe-node.service > /dev/null";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

bool CServiceControl::stop()
{
    std::string cmd = "systemctl stop cellframe-node.service > /dev/null";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

bool CServiceControl::restart()
{
    std::string cmd = "systemctl restart cellframe-node.service > /dev/null";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}    

 #endif
