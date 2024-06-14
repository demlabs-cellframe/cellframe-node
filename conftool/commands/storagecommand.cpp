#include "storagecommand.h"


CAbstractScriptCommand::Registrar<CVariableCommand> var_registrar("var");


CVariableCommand::CVariableCommand(std::vector <std::string> cmd_tokens):CAbstractScriptCommand(cmd_tokens)
{   
    std::string joined_condition = string_join(std::vector<std::string>(cmd_tokens.begin()+1,cmd_tokens.end()), "");
    
    std::vector < std::string> tokens = tokenize(joined_condition, std::regex("="));
    
    if (tokens.size() != 2) throw std::invalid_argument("var command uses exactly VAR=VAL syntax");

    this->var = tokens[0];
    this->val = tokens[1];
}

bool CVariableCommand::execute(bool non_intercative, int flags)
{   
    std::string real_val = this->val;
    if (real_val[0] == '$') real_val = variable_storage[real_val];
    variable_storage[this->var] = real_val;
    if (flags & F_VERBOSE)
    {
        std::cout <<"[VC] Set "<<real_val<< " as " << this->var << ", current stor = {";
        for (auto a: variable_storage) {
            std::cout << a.first << " : " << a.second<<", ";
        }
        std::cout << "}"<<std::endl;
    }
    return true;
}
