#pragma once
#include "abstractcommand.h"

enum E_COND_OPS {
    COND_EQUAL,
    COND_NOT_EQUAL,
    COND_IS_SET
};


class CConditionOpenCommand : public CAbstractScriptCommand {
    public:
        CConditionOpenCommand(std::vector <std::string> cmd_tokens);
        static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CConditionOpenCommand>(cmd_tokens); }
        bool execute(bool non_interactive, int flags);
        bool is_condition_open();

        E_COND_OPS cond_op;
        std::string arg1;
        std::string arg2;
};


class CConditionCloseCommand : public CAbstractScriptCommand {
    public:
        CConditionCloseCommand(std::vector <std::string> cmd_tokens);
        static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CConditionCloseCommand>(cmd_tokens); }
        bool execute(bool non_interactive, int flags);
        bool is_condition_close();
    
};