#include "conditioncommand.h"
#include <sstream>
#include <iostream>
#include <iterator>
#include <numeric>
#include "../config/cellframeconfigfile.h"

CAbstractScriptCommand::Registrar<CConditionOpenCommand> if_registrar("if");
CAbstractScriptCommand::Registrar<CConditionCloseCommand> endif_registrar("endif");

bool CConditionOpenCommand::is_condition_open() {return true;}

bool CConditionCloseCommand::is_condition_close() {return true;}


CConditionOpenCommand::CConditionOpenCommand(std::vector <std::string> cmd_tokens):CAbstractScriptCommand(cmd_tokens)
{   
    std::string joined_condition = string_join(std::vector<std::string>(cmd_tokens.begin()+1,cmd_tokens.end()), "");
    
    auto eq_token = joined_condition.find("==");
    auto neq_token = joined_condition.find("!=");
    
    if (eq_token != std::string::npos)
        this->cond_op = COND_EQUAL;
    if (neq_token != std::string::npos)
        this->cond_op = COND_NOT_EQUAL;
    if (eq_token == std::string::npos && neq_token == std::string::npos)
        this->cond_op = COND_IS_SET;

    std::vector < std::string> tokens = tokenize(joined_condition, std::regex("==|!="));
    if (this->cond_op == COND_IS_SET && tokens.size() != 1)
        throw std::invalid_argument("IS_SET condition requre only one variable for check");
    
    if (this->cond_op != COND_IS_SET && tokens.size() != 2)
        throw std::invalid_argument("CONDITION EQ | NEQ requre only two tokens");
    

    this->arg1 = tokens[0];
    if (this->cond_op != COND_IS_SET)
        this->arg2 = tokens[1];
    //auto neq_token = std::find(joined_condition.begin(), joined_condition.end(), "!=");
}

CConditionCloseCommand::CConditionCloseCommand(std::vector <std::string> cmd_tokens):CAbstractScriptCommand(cmd_tokens)
{   
}

bool CConditionOpenCommand::execute(bool non_intercative, int flags)
{   
    std::string a1val = this->arg1;
    std::string a2val = this->arg2;
    
    if (flags & F_VERBOSE) std::cout << "[VE] Condition exec: " << a1val << " " << this->cond_op << " "<<a2val << " -> ";

    a1val = substitute_variables(arg1);
    a2val = substitute_variables(arg2);
 
    bool res = false;
    std::string opsym = "";

    switch (this->cond_op)
    {
        case COND_EQUAL:
        {
            opsym = "==";
            res = a1val == a2val;
            break;
        }
        case COND_NOT_EQUAL:
        {
            opsym = "!=";
            res = a1val != a2val;
            break;
        }
        case COND_IS_SET:
        {
            opsym = "exists";
            res =  a1val.empty();
            break;
        }
        
        default:
            throw std::invalid_argument("Unknown condition type");
    }
    
    if (flags & F_VERBOSE) std::cout  << a1val << " " << opsym << " " <<a2val << " -> " << res << std::endl;
    return res;
}

bool CConditionCloseCommand::execute(bool non_intercative, int flags)
{   
    return true;
}
std::map<std::string, std::string> variable_storage;