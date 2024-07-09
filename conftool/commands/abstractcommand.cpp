#include "abstractcommand.h"
#include "networkcommand.h"
#include <string>



std::vector<std::string> tokenize(const std::string &str, const std::regex re)
{
    std::regex_token_iterator it{ str.begin(), str.end(), re, -1 };
    std::vector<std::string> tokenized{ it, {} };
 
    tokenized.erase(
        std::remove_if(tokenized.begin(), 
                        tokenized.end(),
                        [](std::string const& s) {
                            return s.size() == 0;
                        }),
        tokenized.end());
 
    return tokenized;
}

std::string string_join(const std::vector<std::string>& vec, const char* delim)
{
    std::stringstream res;
    copy(vec.begin(), vec.end(), std::ostream_iterator<std::string>(res, delim));
    return res.str();
}


CAbstractScriptCommand::CAbstractScriptCommand(std::vector<std::string> tokens)
{
    this->cmd_tokens = tokens;
}

std::unordered_map<std::string, CAbstractScriptCommand::create_f *> & CAbstractScriptCommand::registry()
{
    static std::unordered_map<std::string, CAbstractScriptCommand::create_f *> impl;
    return impl;
}

std::unique_ptr<CAbstractScriptCommand>  CAbstractScriptCommand::build(const std::string &line)
{
    auto tokens = tokenize(line, std::regex("\\s+"));
    auto cmd = tokens[0];
    if (!CAbstractScriptCommand::exists(cmd)) return NULL;
    return CAbstractScriptCommand::instantiate(cmd, tokens);
}

std::string CAbstractScriptCommand::represent()
{
    return string_join(this->cmd_tokens, " ");
}

bool CAbstractScriptCommand::is_condition_open(){
    return false;
}
bool CAbstractScriptCommand::is_condition_close(){
    return false;
}

std::map<std::string, std::string> variable_storage;