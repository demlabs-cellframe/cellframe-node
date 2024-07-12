 #ifdef __linux__ 

#include "service.h"
#include "../commands/abstractcommand.h"

std::string getServiceFile(EServiceType service){
    switch (service)
    {
        case NODE:
            return (std::filesystem::path{variable_storage["CONFIGS_PATH"]}/"share"/"cellframe-node.service").string();
        case DIAG:
            return (std::filesystem::path{variable_storage["CONFIGS_PATH"]}/"share"/"cellframe-diagtool.service").string();
        
        default:
            return "";
    }
}

std::string getServiceName(EServiceType service){
    switch (service)
    {
        case NODE:
            return "cellframe-node.service";
        case DIAG:
            return "cellframe-diagtool.service";
        default:
            return "";
    }
}

bool CServiceControl::enable()
{
    std::string servicefile = getServiceFile(service);

    std::string cmd = "systemctl enable " + servicefile;
    int res = std::system(cmd.c_str());
    
    return res == 0 ? true : false;
}

bool CServiceControl::disable()
{
    std::string servicename = getServiceName(service);
    std::string cmd = "systemctl disable " + servicename;
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

EServiceStatus CServiceControl::serviceStatus()
{
    std::string servicename = getServiceName(service);
    std::string cmd = "systemctl is-enabled "+ servicename;
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
    std::string servicename = getServiceName(service);
    std::string cmd = "systemctl start " + servicename ;
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

bool CServiceControl::stop()
{
    std::string servicename = getServiceName(service);
    std::string cmd = "systemctl stop "+servicename;
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

bool CServiceControl::restart()
{
    std::string servicename = getServiceName(service);
    std::string cmd = "systemctl restart "+servicename;
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}    

 #endif