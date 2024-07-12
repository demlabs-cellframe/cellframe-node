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
        if (CServiceControl(NODE).enable()) {
            std::cout << "enabled" <<std::endl;
        }
        else{
            std::cout << "error" <<std::endl;
        }
    }
    
    if (this->action == "disable")
    {
       if (CServiceControl(NODE).disable()) {
            std::cout << "disabled" <<std::endl;
        }
        else{
            std::cout << "error" <<std::endl;
        }
    }

    if (this->action == "status")
    {
        std::cout << (CServiceControl(NODE).serviceStatus() == ENABLED?"enabled":"disabled")<<std::endl;
    }

    if (this->action == "start")
    {
        if (CServiceControl(NODE).start())
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
        if (CServiceControl(NODE).stop())
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
        if (CServiceControl(NODE).restart())
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
