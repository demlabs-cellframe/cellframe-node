#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <conio.h>

#include "dap_common.h"

LONG ExceptionFilter( EXCEPTION_POINTERS *ep );

void  S_SetExceptionFilter( void )
{
    SetErrorMode( SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX );

#ifdef WIN64
    AddVectoredExceptionHandler( 1, ExceptionFilter );
#else
    SetUnhandledExceptionFilter( (LPTOP_LEVEL_EXCEPTION_FILTER) ExceptionFilter );
#endif
}

LONG ExceptionFilter( EXCEPTION_POINTERS *ep )
{
    return Beep( 1000, 200 );
}
