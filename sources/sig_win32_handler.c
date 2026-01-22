
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <memory.h>

#include <windows.h>

#include "dap_common.h"

#include "sig_win32_handler.h"

#define LOG_TAG "sig_win32_handler"

BOOL WINAPI sig_exit_handler( DWORD fdwCtrlType )
{
    HANDLE hConOut = GetStdHandle( STD_OUTPUT_HANDLE );
    SetConsoleTextAttribute( hConOut, 12 );

    switch (fdwCtrlType)
    {
        // Handle the CTRL-C signal. 
    case CTRL_C_EVENT:
        printf("Ctrl-C event\n\n");
        Beep(750, 300);
    break;

        // CTRL-CLOSE: confirm that the user wants to exit. 
    case CTRL_CLOSE_EVENT:
        Beep(600, 200);
        printf("Ctrl-Close event\n\n");
    break;

        // Pass other signals to the next handler. 
    case CTRL_BREAK_EVENT:
        Beep(900, 200);
        printf("Ctrl-Break event\n\n");
    break;

    case CTRL_LOGOFF_EVENT:
        Beep(1000, 200);
        printf("Ctrl-Logoff event\n\n");
    break;

    case CTRL_SHUTDOWN_EVENT:
        Beep(750, 500);
        printf("Ctrl-Shutdown event\n\n");
    break;
    }

  SetConsoleTextAttribute( hConOut, 7 );

  ExitProcess( 2 );
}

int sig_win32_handler_init( const char *pid_path ) {

    if ( !SetConsoleCtrlHandler( sig_exit_handler, TRUE ) ) return 1;

    return 0;
}

int sig_win32_handler_deinit() {

    SetConsoleCtrlHandler( sig_exit_handler, FALSE );

    return 0;
}
