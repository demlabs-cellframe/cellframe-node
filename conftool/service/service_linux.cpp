 #ifdef __linux__ 

#include "service.h"
#include "../commands/abstractcommand.h"

bool CServiceControl::enable(){
    std::string cmd = "systemctl enable " + (std::filesystem::path{variable_storage["CONFIGS_PATH"]}/"share"/"cellframe-node.service").string();
    int res = std::system(cmd.c_str());
    
    return res == 0 ? true : false;
}

bool CServiceControl::disable()
{
    std::string cmd = "systemctl disable cellframe-node.service";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

EServiceStatus CServiceControl::serviceStatus()
{
    std::string cmd = "systemctl is-enabled cellframe-node.service";
    int res = std::system(cmd.c_str());
    switch (res)
    {
    case 0:
        return ENABLED;
    default:
        return DISABLED;
    }
}

bool CServiceControl::start()
{
    std::string cmd = "systemctl start cellframe-node.service";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

bool CServiceControl::stop()
{
    std::string cmd = "systemctl stop cellframe-node.service";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

bool CServiceControl::restart()
{
    std::string cmd = "systemctl restart cellframe-node.service";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}    

 #endif