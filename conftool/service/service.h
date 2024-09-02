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
    SERVICE_ENABLED = 1 << 0,
    PROCESS_RUNNING = 1 << 2,
};

struct CServiceControl
{
    static bool enable();
    static bool disable();
    static unsigned int serviceStatus();
    static bool start();
    static bool stop();
    static bool restart();    
};