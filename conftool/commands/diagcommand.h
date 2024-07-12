#include "abstractcommand.h"

class CDiagCommand : public CAbstractScriptCommand {
    public:
        CDiagCommand(std::vector <std::string> cmd_tokens);
        static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CDiagCommand>(cmd_tokens); }
        bool execute(bool non_interactive, int flags);
    
    private:
        std::string action;
};
