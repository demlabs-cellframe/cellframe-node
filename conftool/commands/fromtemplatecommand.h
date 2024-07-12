#pragma once
#include "abstractcommand.h"

class CFromTemplateCommand : public CAbstractScriptCommand {
    public:
        CFromTemplateCommand(std::vector <std::string> cmd_tokens);
        static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CFromTemplateCommand>(cmd_tokens); }
        bool execute(bool non_interactive, int flags);
        
    private:
        std::string cfg_name;
        std::string action;
};
