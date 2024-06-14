#pragma once

#include <algorithm>
#include <string>
#include <iostream>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>
#include <regex>
#include <unordered_map>

#include <memory>
#include <string>
#include <stdexcept>
#include <sstream>
#include <iostream>
#include <iterator>
#include <numeric>
#include "../build_config.h"


enum E_FLAGS {

    F_VERBOSE = 1 << 0,
    F_FORCE =   1 << 1,
    F_DRYRUN =  1 << 2
};

template<typename ... Args>
std::string string_format( const std::string& format, Args ... args )
{
    int size_s = std::snprintf( nullptr, 0, format.c_str(), args ... ) + 1; // Extra space for '\0'
    if( size_s <= 0 ){ throw std::runtime_error( "Error during formatting." ); }
    auto size = static_cast<size_t>( size_s );
    std::unique_ptr<char[]> buf( new char[ size ] );
    std::snprintf( buf.get(), size, format.c_str(), args ... );
    return std::string( buf.get(), buf.get() + size - 1 ); // We don't want the '\0' inside
}

// trim from start (in place)
inline void ltrim(std::string &s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](unsigned char ch) {
        return !std::isspace(ch);
    }));
}

// trim from end (in place)
inline void rtrim(std::string &s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) {
        return !std::isspace(ch);
    }).base(), s.end());
}

inline void trim(std::string &s) {
    rtrim(s);
    ltrim(s);
}


std::string string_join(const std::vector<std::string>& vec, const char* delim);

std::vector<std::string> tokenize(const std::string &str, const std::regex re);

struct CAbstractScriptCommand {

    CAbstractScriptCommand(std::vector<std::string> tokens);
    
    virtual ~CAbstractScriptCommand() = default;

    using create_f = std::unique_ptr<CAbstractScriptCommand>(std::vector <std::string> cmd_tokens);

    static void registrate(std::string const & name, create_f * fp)
    {
        registry()[name] = fp;
    }
    
    static bool exists(std::string const & name)
    {
        auto it = registry().find(name);
        return it != registry().end();
    }
    
    static std::unique_ptr<CAbstractScriptCommand> instantiate(std::string const & name, std::vector <std::string> cmd_tokens)
    {
        auto it = registry().find(name);
        return it == registry().end() ? nullptr : (it->second)(cmd_tokens);
    }

    template <typename D>
    struct Registrar
    {
        explicit Registrar(std::string const & name)
        {
            CAbstractScriptCommand::registrate(name, &D::create);
        }
        // make non-copyable, etc.
    };

private:
    static std::unordered_map<std::string, create_f *> & registry();
    CAbstractScriptCommand();
    std::vector<std::string> cmd_tokens;
    
public:
        
        virtual bool execute(bool non_interactive, int flags) = 0;

        static std::unique_ptr<CAbstractScriptCommand>  build(const std::string &line);  
        virtual bool is_condition_open();
        virtual bool is_condition_close();
        virtual std::string represent();
};


extern std::map<std::string, std::string> variable_storage;