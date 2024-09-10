#include "AbstractCommand.h"

class CNetworkCommand : public CAbstractScriptCommand {
    public:
        CNetworkCommand(std::vector <std::string> cmd_tokens);
        static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CNetworkCommand>(cmd_tokens); }
        bool execute(bool non_interactive, int flags);
    
    private:
        std::string net_name;
        std::string action;
        std::string default_val;
};
