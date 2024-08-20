#pragma once
#include "AbstractCommand.h"

class CConfigCommand : public CAbstractScriptCommand {
    public:
        CConfigCommand(std::vector <std::string> cmd_tokens);
        static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CConfigCommand>(cmd_tokens); }
        bool execute(bool non_interactive, int flags);
        
    private:
        std::string cfg_name;
        std::string group;
        std::string param;
        std::string value;
        std::string action;
};
