#include <algorithm>
#include <map>
#include <string>
#include <iostream>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>
#include <stdexcept>

enum EServiceStatus{
    ENABLED,
    DISABLED,
};

struct CServiceControl
{
    static bool enable();
    static bool disable();
    static EServiceStatus serviceStatus();
    static bool start();
    static bool stop();
    static bool restart();    
};