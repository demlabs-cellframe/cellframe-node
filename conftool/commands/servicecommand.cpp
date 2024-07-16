#include "servicecommand.h"
#include <stdexcept>
#include <filesystem>

#include "../build_config.h"
#include "../config/cellframeconfigfile.h"
#include "../service/service.h"

namespace fs = std::filesystem;

CAbstractScriptCommand::Registrar<CServiceCommand> service_registrar("service");


CServiceCommand::CServiceCommand(std::vector <std::string> cmd_tokens): CAbstractScriptCommand(cmd_tokens)
{   
    //zero token is always a command (network)
    
    if (cmd_tokens.size() < 2)
        throw std::invalid_argument("service command require action argument");
    
    this->action = cmd_tokens[1];
}

bool CServiceCommand::execute(bool non_intercative, int flags)
{ 
    if (this->action == "enable"){
        if (CServiceControl::enable()) {
            std::cout << "enabled" <<std::endl;
        }
        else{
            std::cout << "error" <<std::endl;
        }
    }
    
    if (this->action == "disable")
    {
       if (CServiceControl::disable()) {
            std::cout << "disabled" <<std::endl;
        }
        else{
            std::cout << "error" <<std::endl;
        }
    }

    if (this->action == "status")
    {
        unsigned int status = CServiceControl::serviceStatus();
        if (status & SERVICE_ENABLED)
            std::cout << "service: enabled" << std::endl;
        else
            std::cout << "service: disabled" << std::endl;

        if (status & PROCESS_RUNNING)
            std::cout << "process: running" << std::endl;
        else
            std::cout << "process: notfound" << std::endl;
    }

    if (this->action == "start")
    {
        if (CServiceControl::start())
        {
            std::cout << "started" << std::endl;
        }
        else
        {
            std::cout << "error" << std::endl;
        }
    }
    
    if (this->action == "stop")
    {
        if (CServiceControl::stop())
        {
            std::cout << "stoped" << std::endl;
        }
        else
        {
            std::cout << "error" << std::endl;
        }
    }

    if (this->action == "restart")
    {
        if (CServiceControl::restart())
        {
            std::cout << "restarted" << std::endl;
        }
        else
        {
            std::cout << "error" << std::endl;
        }
    }
   
    return true;
}
