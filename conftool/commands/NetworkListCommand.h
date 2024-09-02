#pragma once
#include "AbstractCommand.h"

class CNetworkListCommand : public CAbstractScriptCommand {

    enum NetworState{
        ALL = 0,
        ON,
        OFF
    };

    struct NetworkInfo
    {
        std::string networkName = "";
        std::string state = "";
    };

    public:
        CNetworkListCommand(std::vector <std::string> cmd_tokens);
        static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CNetworkListCommand>(cmd_tokens); }
        bool execute(bool non_interactive, int flags);
        
    private:
        NetworState m_state = ALL;
};
