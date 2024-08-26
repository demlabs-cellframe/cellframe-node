#pragma once
#include "AbstractCommand.h"

class CVariableCommand : public CAbstractScriptCommand {
    public:
        CVariableCommand(std::vector <std::string> cmd_tokens);
        static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CVariableCommand>(cmd_tokens); }
        bool execute(bool non_interactive, int flags);
        
    private:
        std::string var;
        std::string val;
};
