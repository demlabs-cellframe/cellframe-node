#include "AbstractCommand.h"

class CServiceCommand : public CAbstractScriptCommand {
    public:
        CServiceCommand(std::vector <std::string> cmd_tokens);
        static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CServiceCommand>(cmd_tokens); }
        bool execute(bool non_interactive, int flags);
    
    private:
        std::string action;
};
