 #ifdef __linux__ 

#include "service.h"
#include "../commands/abstractcommand.h"

bool CServiceControl::enable(){
    std::string cmd = "systemctl enable " + variable_storage["SERVICE_FILE_PATH"] + " > /dev/null";
    int res = std::system(cmd.c_str());
    
    return res == 0 ? true : false;
}

bool CServiceControl::disable()
{
    std::string cmd = "systemctl disable " + variable_storage["SERVICE_NAME"] +" > /dev/null";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

unsigned int CServiceControl::serviceStatus()
{
    unsigned int status = 0;
    
    std::string cmd = "systemctl is-enabled " +  variable_storage["SERVICE_NAME"] + " > /dev/null";
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
    std::string cmd = "systemctl start " + variable_storage["SERVICE_NAME"] + " > /dev/null";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

bool CServiceControl::stop()
{
    std::string cmd = "systemctl stop "  + variable_storage["SERVICE_NAME"] + " > /dev/null";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}

bool CServiceControl::restart()
{
    std::string cmd = "systemctl restart " + variable_storage["SERVICE_NAME"] + " > /dev/null";
    int res = std::system(cmd.c_str());    
    return res == 0 ? true : false;
}    

 #endif
