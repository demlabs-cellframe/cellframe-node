#include "diagcommand.h"
#include <stdexcept>
#include <filesystem>

#include "../build_config.h"
#include "../config/cellframeconfigfile.h"
#include "../service/service.h"

namespace fs = std::filesystem;

CAbstractScriptCommand::Registrar<CDiagCommand> diag_registrar("diag");


CDiagCommand::CDiagCommand(std::vector <std::string> cmd_tokens): CAbstractScriptCommand(cmd_tokens)
{   
    //zero token is always a command (network)
    
    if (cmd_tokens.size() < 2)
        throw std::invalid_argument("diag command require action argument");
    
    this->action = cmd_tokens[1];
}

bool CDiagCommand::execute(bool non_intercative, int flags)
{ 
    if (this->action == "enable"){
        if (CServiceControl(DIAG).enable()) {
            std::cout << "enabled" <<std::endl;
        }
        else{
            std::cout << "error" <<std::endl;
        }
    }
    
    if (this->action == "disable")
    {
       if (CServiceControl(DIAG).disable()) {
            std::cout << "disabled" <<std::endl;
        }
        else{
            std::cout << "error" <<std::endl;
        }
    }

    if (this->action == "status")
    {
        std::cout << (CServiceControl(DIAG).serviceStatus() == ENABLED?"enabled":"disabled")<<std::endl;
    }

    if (this->action == "start")
    {
        if (CServiceControl(DIAG).start())
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
        if (CServiceControl(DIAG).stop())
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
        if (CServiceControl(DIAG).restart())
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
